"""
Generate candidate words for the word-of-the-day pool, sourced from a local
Wiktionary index (see build_wiktextract_index.py) instead of raw wordfreq
frequency lists.

Every candidate here is guaranteed to be a real English lemma (noun, verb,
adjective, or adverb -- proper nouns already excluded via wiktextract's
distinct pos == "name" tag, confirmed against real sample data) with a real
Wiktionary etymology and definition already attached. That's why this
pipeline no longer needs the per-batch "no etymology found" recovery dance
(base_etym_check*.json, filter_drafts.py exclusions) that the old
wordfreq-sampled pipeline required -- every candidate here already cleared
that bar during the one-time index build.

Zipf frequency (wordfreq) is still used as a cutoff -- excluding both words
common enough that most readers already know them, and words so rare they
risk being archaic/dialectal noise -- and is carried through to the output
so it can double as the "how rare is this word" info surfaced on the site.

The min/max band is applied to *effective* zipf (surface form blended with
its guessed lemma's frequency, see lemma_frequency.py), not raw surface
zipf. Otherwise a transparent derivation of a common root (e.g.
"deductively" from "deductive") looks artificially rare by raw token
frequency and either gets accepted as a candidate for the wrong reason, or
-- for a word just above max-zipf on the raw scale -- wrongly rejected as
"too easy" when blending would have pushed it over. The raw zipf is still
what's written to candidates.csv, since that's the true corpus-frequency
number for the word itself; only the accept/reject decision uses the
blended value.

Usage:
    python generate_candidates.py [--min-zipf 1.5] [--max-zipf 2.8]
"""
import argparse
import csv
import json
import os

from lemma_frequency import effective_zipf

WORDPOOL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(WORDPOOL_DIR))
WORDS_JSON = os.path.join(REPO_ROOT, "data", "words.json")
REJECTED_JSON = os.path.join(WORDPOOL_DIR, "rejected.json")
CANDIDATES_CSV = os.path.join(WORDPOOL_DIR, "candidates.csv")
DEFAULT_INDEX = os.environ.get(
    "WIKTEXTRACT_INDEX", r"D:\wiktextract_data\wiktextract_en_index.jsonl"
)


def load_existing_words():
    if not os.path.exists(WORDS_JSON):
        return set()
    with open(WORDS_JSON, "r", encoding="utf-8") as f:
        entries = json.load(f)
    return {e["id"] for e in entries}


def load_rejected():
    if not os.path.exists(REJECTED_JSON):
        return set()
    with open(REJECTED_JSON, "r", encoding="utf-8") as f:
        entries = json.load(f)
    return {e["word"] for e in entries}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-zipf", type=float, default=1.5)
    parser.add_argument("--max-zipf", type=float, default=2.8)
    parser.add_argument("--index", default=DEFAULT_INDEX)
    args = parser.parse_args()

    existing = load_existing_words()
    rejected = load_rejected()

    best_by_word = {}  # word -> first-seen row dict (has zipf/glosses/etc)
    pos_seen = {}  # word -> set of pos values, since a lemma can appear as
                   # both e.g. "noun" and "verb" as separate wiktextract entries

    with open(args.index, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            word = d["word"]
            zipf = d["zipf"]
            if not (args.min_zipf <= effective_zipf(word, zipf) <= args.max_zipf):
                continue
            if word in existing or word in rejected:
                continue
            pos_seen.setdefault(word, set()).add(d["pos"])
            best_by_word.setdefault(word, d)

    candidates = []
    for word, d in best_by_word.items():
        gloss = d["glosses"][0] if d["glosses"] else ""
        candidates.append((
            word,
            d["zipf"],
            "/".join(sorted(pos_seen[word])),
            gloss[:120],
        ))

    candidates.sort(key=lambda c: c[1], reverse=True)

    with open(CANDIDATES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "zipf", "pos", "gloss_preview"])
        writer.writerows(candidates)

    print(f"Wrote {len(candidates)} candidates to {CANDIDATES_CSV}")
    print(f"Zipf band: [{args.min_zipf}, {args.max_zipf}]")
    print(f"Source index: {args.index}")


if __name__ == "__main__":
    main()
