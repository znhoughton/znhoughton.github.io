"""
Fetch raw sourced data for one candidate word: ARPABET (CMU Pronouncing
Dictionary via NLTK, offline, falling back to the g2p_en predictive model
for words CMUdict doesn't have), IPA/POS/definitions (dictionaryapi.dev,
falling back to Wiktionary's Pronunciation section), and the raw English
Etymology section wikitext (Wiktionary API).

This does NOT write a finished data/words.json entry. It writes a draft to
wordpool/drafts/<word>.json with the raw fetched fields so a human can write
the final clean definition/etymology prose directly from a real source,
rather than generating it from memory.

Usage:
    python enrich_word.py <word> [<word2> ...]
"""
import argparse
import json
import os
import re
import sys

import requests
from nltk.corpus import cmudict

# Standard General American ARPABET -> IPA mapping, used only to mechanically
# reformat CMUdict entries (a real dictionary source) into IPA when
# dictionaryapi.dev has no phonetic transcription -- never used to invent a
# pronunciation from scratch.
ARPABET_TO_IPA = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ",
    "B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "EH": "ɛ", "ER": "ɝ",
    "EY": "eɪ", "F": "f", "G": "ɡ", "HH": "h", "IH": "ɪ", "IY": "i",
    "JH": "dʒ", "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ŋ",
    "OW": "oʊ", "OY": "ɔɪ", "P": "p", "R": "ɹ", "S": "s", "SH": "ʃ",
    "T": "t", "TH": "θ", "UH": "ʊ", "UW": "u", "V": "v", "W": "w",
    "Y": "j", "Z": "z", "ZH": "ʒ",
}
_ARPABET_PHONE_RE = re.compile(r"^([A-Z]+)([0-2])?$")


def arpabet_to_ipa(arpabet_str):
    out = []
    for phone in arpabet_str.split():
        m = _ARPABET_PHONE_RE.match(phone)
        if not m:
            continue
        base, stress = m.group(1), m.group(2)
        # CMUdict doesn't distinguish stressed /ʌ/ from unstressed schwa --
        # both are "AH". Convention: unstressed AH0 is schwa.
        if base == "AH" and stress == "0":
            ipa = "ə"
        else:
            ipa = ARPABET_TO_IPA.get(base, base)
        out.append(("ˈ" if stress == "1" else "ˌ" if stress == "2" else "") + ipa)
    return "/" + "".join(out) + "/"

WORDPOOL_DIR = os.path.dirname(os.path.abspath(__file__))
DRAFTS_DIR = os.path.join(WORDPOOL_DIR, "drafts")

DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
WIKT_API = "https://en.wiktionary.org/w/api.php"
# Wikimedia's API rejects requests with no descriptive User-Agent (403).
HEADERS = {"User-Agent": "znhoughton-wordpool-tool/1.0 (contact: znhoughton@gmail.com)"}

_CMUDICT = None
_G2P = None


def get_arpabet(word):
    """Returns (arpabet_string, source). Prefers CMUdict (a real reference
    dictionary); falls back to g2p_en (a predictive model) for OOV words,
    which should be flagged as lower-confidence when used."""
    global _CMUDICT, _G2P
    if _CMUDICT is None:
        _CMUDICT = cmudict.dict()
    pronunciations = _CMUDICT.get(word.lower())
    if pronunciations:
        # cmudict may list multiple pronunciations; return all, joined by " OR "
        return " OR ".join(" ".join(p) for p in pronunciations), "cmudict"

    if _G2P is None:
        from g2p_en import G2p
        _G2P = G2p()
    predicted = [p for p in _G2P(word) if p.strip()]
    if predicted:
        return " ".join(predicted), "g2p_en (predicted, not dictionary-sourced)"
    return None, None


def get_dictionary_entry(word):
    try:
        resp = requests.get(DICT_API.format(word=word), timeout=10)
    except requests.RequestException as e:
        return {"error": str(e)}
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}"}
    return resp.json()


def _find_english_section_index(sections, heading_prefix):
    current_language = None
    for sec in sections:
        if sec["toclevel"] == 1:
            current_language = sec["line"]
        elif current_language == "English" and sec["line"].startswith(heading_prefix):
            return sec["index"]
    return None


def get_wiktionary_section_wikitext(word, heading_prefix):
    try:
        resp = requests.get(
            WIKT_API,
            params={"action": "parse", "page": word, "prop": "sections", "format": "json"},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        sections = resp.json().get("parse", {}).get("sections", [])
    except (requests.RequestException, KeyError) as e:
        return {"error": str(e)}

    section_index = _find_english_section_index(sections, heading_prefix)
    if section_index is None:
        return {"error": f"No English {heading_prefix} section found"}

    try:
        resp = requests.get(
            WIKT_API,
            params={"action": "parse", "page": word, "prop": "wikitext", "section": section_index, "format": "json"},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        wikitext = resp.json()["parse"]["wikitext"]["*"]
    except (requests.RequestException, KeyError) as e:
        return {"error": str(e)}

    anchor = heading_prefix
    return {"raw_wikitext": wikitext, "source_url": f"https://en.wiktionary.org/wiki/{word}#{anchor}"}


def enrich(word):
    arpabet, arpabet_source = get_arpabet(word)
    dict_entry = get_dictionary_entry(word)
    draft = {
        "id": word,
        "arpabet_raw": arpabet,
        "arpabet_source": arpabet_source,
        "dictionaryapi_raw": dict_entry,
        "etymology_raw": get_wiktionary_section_wikitext(word, "Etymology"),
    }
    # Wiktionary Pronunciation section as a fallback/supplement when
    # dictionaryapi.dev has no entry (it 404s on some recent coinages).
    has_phonetic = isinstance(dict_entry, list) and any(
        e.get("phonetic") or any(p.get("text") for p in e.get("phonetics", []))
        for e in dict_entry
    )
    if not has_phonetic:
        draft["pronunciation_wikitext_raw"] = get_wiktionary_section_wikitext(word, "Pronunciation")
        if arpabet_source == "cmudict":
            draft["ipa_derived_from_cmudict"] = arpabet_to_ipa(arpabet.split(" OR ")[0])

    os.makedirs(DRAFTS_DIR, exist_ok=True)
    out_path = os.path.join(DRAFTS_DIR, f"{word}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path}")
    return draft


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("words", nargs="+")
    args = parser.parse_args()
    for word in args.words:
        enrich(word.lower())


if __name__ == "__main__":
    main()
