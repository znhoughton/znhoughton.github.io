"""
Backfills two display fields onto every entry in data/words.json, computed
from each word's existing zipf score:

  - rarity_percentile: "this word is rarer than N% of English words," derived
    from a real reference distribution (wordfreq's top 300,000 English words
    by frequency), not a guess -- see zipf_reference_distribution.json. This
    is explicitly a corpus-frequency statistic, not a claim about how many
    people know the word (those are different things; frequency data can't
    support the latter claim).
  - rarity_tier: a four-band badge label (Legendary/Rare/Uncommon/Common)
    for a quick visual read, using the same zipf boundaries as the badge
    design: <=1.8 Legendary, <=2.2 Rare, <=2.6 Uncommon, else Common.
    Core (non-discovery_only) words in the Legendary band are exactly the
    pool the "Feeling like a challenge?" feature draws from.

Usage:
    python backfill_rarity.py
"""
import bisect
import json
import os

WORDPOOL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(WORDPOOL_DIR))
WORDS_JSON = os.path.join(REPO_ROOT, "data", "words.json")
REFERENCE_DIST = os.path.join(WORDPOOL_DIR, "zipf_reference_distribution.json")

TIER_BOUNDARIES = [
    (1.8, "Legendary"),
    (2.2, "Rare"),
    (2.6, "Uncommon"),
    (float("inf"), "Common"),
]


def rarity_tier(zipf):
    for boundary, name in TIER_BOUNDARIES:
        if zipf <= boundary:
            return name
    return "Common"


def main():
    with open(REFERENCE_DIST, "r", encoding="utf-8") as f:
        # Saved sorted descending (most common first); bisect needs ascending.
        ref_zipfs = sorted(json.load(f))
    n_ref = len(ref_zipfs)

    with open(WORDS_JSON, "r", encoding="utf-8") as f:
        words = json.load(f)

    for w in words:
        z = w["zipf"]
        # Fraction of the reference vocabulary strictly more common (higher
        # zipf) than this word == "rarer than N% of English words."
        idx = bisect.bisect_right(ref_zipfs, z)
        more_common_count = n_ref - idx
        percentile = round(100 * more_common_count / n_ref)
        w["rarity_percentile"] = percentile
        w["rarity_tier"] = rarity_tier(z)

    with open(WORDS_JSON, "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2, ensure_ascii=False)

    tier_counts = {}
    for w in words:
        tier_counts[w["rarity_tier"]] = tier_counts.get(w["rarity_tier"], 0) + 1
    print(f"Backfilled rarity_percentile + rarity_tier on {len(words)} words")
    print("Tier counts:", tier_counts)


if __name__ == "__main__":
    main()
