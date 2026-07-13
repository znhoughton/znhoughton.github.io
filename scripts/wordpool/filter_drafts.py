"""
Lists which drafts in wordpool/drafts/ are usable vs. should be excluded.

Standing rule: if a word has no real English Wiktionary Etymology section,
drop it. This is a cheap, principled filter against non-words, foreign-only
terms, and words without established English documentation -- it also
catches cases like a word being classified as a different language on
Wiktionary (e.g. Scots, French) rather than English.

Also rejects entries whose "etymology" is just a stub/cleanup placeholder
like {{rfe|en}} ("request for etymology") or {{pwd|...}} ("please
Wiktionarify derivation"), with no real content -- the section exists
structurally but nobody has written the etymology yet. This slipped through
undetected more than once before this check existed (e.g.
"propionibacterium", "aeolian").

Note this can't be "strip every template, require leftover prose": a great
many *real*, correctly-sourced etymologies are expressed entirely through
content templates with no surrounding prose at all (e.g. cosmologist:
"{{ety|en|:af|cosmology|-ist|text=+|tree=1}}" is a complete, valid "cosmology
+ -ist" derivation with zero free text). So this only strips known
placeholder/cleanup template names, not content templates like {{ety}},
{{suffix}}, {{af}}, {{compound}}, etc., which themselves carry the claim.

Usage:
    python filter_drafts.py
"""
import json
import os
import re

DRAFTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drafts")

# Known Wiktionary placeholder/cleanup templates meaning "not written yet",
# as opposed to content templates that themselves state the etymology.
STUB_TEMPLATE_NAMES = ("rfe", "pwd", "etystub", "rfelite", "rfv-etym", "rfc-etym")
STUB_TEMPLATE_RE = re.compile(
    r"\{\{(?:" + "|".join(re.escape(n) for n in STUB_TEMPLATE_NAMES) + r")\b[^}]*\}\}",
    re.IGNORECASE,
)
HEADING_RE = re.compile(r"^===?Etymology[^=]*===?\s*", re.IGNORECASE)


def has_real_etymology(wikitext):
    body = HEADING_RE.sub("", wikitext)
    body = STUB_TEMPLATE_RE.sub("", body)
    # After removing only placeholder templates, anything non-trivial left
    # (real prose, or a real content template) counts as a real etymology.
    # A lone period/whitespace left over from "{{rfe|en}}." doesn't count.
    return bool(re.search(r"[A-Za-z]{2,}|\{\{", body))


def main():
    usable, excluded = [], []
    for fname in sorted(os.listdir(DRAFTS_DIR)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(DRAFTS_DIR, fname), "r", encoding="utf-8") as f:
            draft = json.load(f)
        etym = draft.get("etymology_raw", {})
        if isinstance(etym, dict) and "raw_wikitext" in etym and has_real_etymology(etym["raw_wikitext"]):
            usable.append(draft["id"])
        else:
            excluded.append(draft["id"])

    print(f"Usable ({len(usable)}): {usable}")
    print(f"Excluded, no English Wiktionary etymology ({len(excluded)}): {excluded}")


if __name__ == "__main__":
    main()
