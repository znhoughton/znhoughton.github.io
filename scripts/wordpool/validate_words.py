"""
Schema/sanity check for data/words.json. Run before committing changes.

Usage:
    python validate_words.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORDS_JSON = os.path.join(REPO_ROOT, "data", "words.json")

REQUIRED_FIELDS = [
    "id", "word", "pos", "ipa", "arpabet",
    "definition", "etymology", "etymology_source", "examples",
    "zipf", "date_added",
]


def main():
    with open(WORDS_JSON, "r", encoding="utf-8") as f:
        entries = json.load(f)

    errors = []
    seen_ids = set()

    for i, entry in enumerate(entries):
        label = entry.get("id", f"entry #{i}")

        for field in REQUIRED_FIELDS:
            if field not in entry or entry[field] in (None, ""):
                errors.append(f"{label}: missing or empty field '{field}'")

        if entry.get("id") in seen_ids:
            errors.append(f"{label}: duplicate id")
        seen_ids.add(entry.get("id"))

        examples = entry.get("examples", [])
        if entry.get("discovery_only"):
            if not isinstance(examples, list) or not (2 <= len(examples) <= 3):
                errors.append(f"{label}: discovery_only entries expect 2-3 examples, got {len(examples) if isinstance(examples, list) else 'non-list'}")
        else:
            if not isinstance(examples, list) or len(examples) != 5:
                errors.append(f"{label}: expected exactly 5 examples, got {len(examples) if isinstance(examples, list) else 'non-list'}")

    if errors:
        print(f"{len(errors)} problem(s) found in {WORDS_JSON}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    discovery_count = sum(1 for e in entries if e.get("discovery_only"))
    core_count = len(entries) - discovery_count
    print(f"OK: {len(entries)} words validated ({core_count} core / eligible for Word of the Day, {discovery_count} discovery-only).")


if __name__ == "__main__":
    main()
