"""
Streams the full raw wiktextract dump (all languages, piped in via stdin so the
23GB uncompressed file is never fully materialized on disk) and writes a much
smaller local index of English lemmas we can use as a candidate source.

Keeps only entries where:
  - lang_code == "en"
  - pos in KEEP_POS (drops "name" (proper nouns), "character", "symbol",
    "particle", etc. -- confirmed via a real data sample that wiktextract
    tags proper nouns with pos == "name", distinct from "noun")
  - word is a single alphabetic token (no phrases/multi-word entries, no
    apostrophes/hyphens-only artifacts)
  - has non-empty etymology_text (no point candidate-listing a word we can't
    source etymology for -- this replaces the old per-batch "no etymology
    found" dead-end/recovery-file dance entirely)
  - not on the profanity blocklist (content_filters.py) -- a correctness/
    reputational hard exclusion, not a difficulty judgment call
  - first gloss isn't a stub redirect like "Alternative form of X" or
    "Plural of X" (content_filters.py) -- these have real etymology but no
    independent definition to compose an entry from

For each surviving entry, records: word, pos, etymology_text, glosses (from
senses), ipa (from sounds), and its wordfreq zipf score (for later difficulty
tiering, not filtering).

Usage:
    curl -s https://kaikki.org/dictionary/raw-wiktextract-data.jsonl.gz \
      | gunzip -c \
      | python build_wiktextract_index.py > wiktextract_en_index.jsonl
"""
import json
import re
import sys

from wordfreq import zipf_frequency

from content_filters import is_blocked, is_stub_gloss

KEEP_POS = {"noun", "verb", "adj", "adv"}
WORD_RE = re.compile(r"^[a-z]+$")


def extract_glosses(senses):
    out = []
    for sense in senses or []:
        for g in sense.get("glosses") or []:
            if g:
                out.append(g)
    return out


def extract_ipa(sounds):
    for s in sounds or []:
        ipa = s.get("ipa")
        if ipa:
            return ipa
    return None


def main():
    kept = 0
    seen_total = 0
    out = sys.stdout

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        seen_total += 1
        if seen_total % 500000 == 0:
            print(f"...{seen_total} lines scanned, {kept} kept", file=sys.stderr)

        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue

        if d.get("lang_code") != "en":
            continue
        pos = d.get("pos")
        if pos not in KEEP_POS:
            continue

        word = d.get("word", "")
        word_l = word.lower()
        if not WORD_RE.match(word_l):
            continue
        # Only keep the lowercase headword form -- skip if this specific
        # entry's word field is capitalized (that's the "name" sense's
        # sibling entries showing up under a different pos in rare cases,
        # or sentence-initial-only capitalization artifacts).
        if word != word_l:
            continue

        if is_blocked(word_l):
            continue

        etymology_text = d.get("etymology_text") or ""
        if not etymology_text.strip():
            continue

        glosses = extract_glosses(d.get("senses"))
        if not glosses:
            continue
        if is_stub_gloss(glosses[0]):
            continue

        ipa = extract_ipa(d.get("sounds"))
        zipf = zipf_frequency(word_l, "en")

        out.write(json.dumps({
            "word": word_l,
            "pos": pos,
            "etymology_text": etymology_text,
            "glosses": glosses[:3],
            "ipa": ipa,
            "zipf": zipf,
        }, ensure_ascii=False) + "\n")
        kept += 1

    print(f"done: {seen_total} lines scanned, {kept} kept", file=sys.stderr)


if __name__ == "__main__":
    main()
