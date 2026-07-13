"""
Generate candidate words for the word-of-the-day pool.

Uses wordfreq (frequency data drawn from modern corpora: news, Wikipedia,
subtitles, Reddit, etc.) to find words that are rare enough to be a real
vocabulary gap for an educated adult, but still attested in current usage.

Frequency alone can't distinguish "obscure but current" from "archaic" --
forsooth and pareidolia score similarly low -- so this only narrows the
field. Every candidate still needs a human read before it's enriched.

Candidates are grouped by lemma (via WordNet) before the frequency band is
applied, so e.g. "men"/"man's" contribute to the frequency mass of "man"
rather than being scored as separate, rarer-looking words.

Usage:
    python generate_candidates.py [--min-zipf 1.8] [--max-zipf 2.8] [--n 80000]

Writes wordpool/candidates.csv (lemma, zipf, forms), sorted by zipf
descending (most common of the rare words first). Excludes anything already
present in data/words.json or wordpool/rejected.json.
"""
import argparse
import csv
import json
import math
import re
import os
from collections import defaultdict

import nltk
from nltk.corpus import names as nltk_names
from nltk.corpus import words as nltk_words
from nltk.stem import WordNetLemmatizer
from wordfreq import top_n_list, zipf_frequency

WORDPOOL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(WORDPOOL_DIR))
WORDS_JSON = os.path.join(REPO_ROOT, "data", "words.json")
REJECTED_JSON = os.path.join(WORDPOOL_DIR, "rejected.json")
CANDIDATES_CSV = os.path.join(WORDPOOL_DIR, "candidates.csv")

WORD_RE = re.compile(r"^[a-z]+(-[a-z]+)*$")

_LEMMATIZER = WordNetLemmatizer()
_LEMMA_POS_ORDER = ["n", "v", "a", "r"]


def get_lemma(word):
    """Approximate lemma by trying noun/verb/adj/adv WordNet lemmatization,
    preferring the first POS that actually reduces the word. Good enough for
    grouping inflectional variants under one headword; not meant to be a
    fully accurate morphological analysis."""
    for pos in _LEMMA_POS_ORDER:
        lemma = _LEMMATIZER.lemmatize(word, pos)
        if lemma != word:
            return lemma
    return word


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
    parser.add_argument("--min-length", type=int, default=4)
    parser.add_argument("--n", type=int, default=320000)
    args = parser.parse_args()

    existing = load_existing_words()
    rejected = load_rejected()
    dictionary_words = {w.lower() for w in nltk_words.words()}
    proper_names = {n.lower() for n in nltk_names.words()}

    ranked = top_n_list("en", args.n, wordlist="best")

    # Group surface forms by lemma, summing linear frequency mass so e.g.
    # "men" contributes to "man"'s aggregate rather than scoring separately.
    lemma_forms = defaultdict(dict)  # lemma -> {surface_form: zipf}
    lemma_best_rank = {}
    for rank, word in enumerate(ranked):
        if len(word) < args.min_length:
            continue
        if not WORD_RE.match(word):
            continue
        if word in proper_names:
            continue
        lemma = get_lemma(word)
        zipf = zipf_frequency(word, "en")
        lemma_forms[lemma][word] = zipf
        lemma_best_rank[lemma] = min(lemma_best_rank.get(lemma, rank), rank)

    candidates = []
    for lemma, forms in lemma_forms.items():
        if lemma in existing or lemma in rejected:
            continue
        if not WORD_RE.match(lemma):
            continue
        linear_sum = sum(10 ** z for z in forms.values())
        agg_zipf = math.log10(linear_sum)
        if args.min_zipf <= agg_zipf <= args.max_zipf:
            forms_str = ";".join(f"{w}:{z}" for w, z in sorted(forms.items(), key=lambda kv: -kv[1]))
            in_dict = lemma in dictionary_words or any(w in dictionary_words for w in forms)
            candidates.append((lemma, round(agg_zipf, 2), lemma_best_rank[lemma], in_dict, forms_str))

    candidates.sort(key=lambda c: c[1], reverse=True)

    with open(CANDIDATES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "zipf", "rank", "in_dict", "forms"])
        writer.writerows(candidates)

    print(f"Wrote {len(candidates)} candidates to {CANDIDATES_CSV}")
    print(f"Zipf band: [{args.min_zipf}, {args.max_zipf}], min length: {args.min_length}")


if __name__ == "__main__":
    main()
