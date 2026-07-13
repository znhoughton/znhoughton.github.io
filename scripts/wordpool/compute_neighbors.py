"""
Compute nearest-neighbor words in embedding space for every word in
data/words.json, for the "related words" visualization on word-cabinet.html.

Uses word2vec-google-news-300 (preferred) or glove-wiki-gigaword-300 (fallback,
for words missing from word2vec -- e.g. very recent coinages). All of the
actual ML runs here, offline, once; the site only ever fetches the small
precomputed result (neighbor words + a 2D PCA projection), never a model.

Neighbors are filtered to:
  - alphabetic, lowercase, single tokens (no phrases/proper nouns/junk)
  - real, current English words (wordfreq zipf > 1.0) -- this is what
    catches embedding neighbors that are actually spam/foreign tokens
    (observed for "sonder", whose GloVe neighborhood is mostly garbage
    since it has almost no training-corpus presence)
  - not a trivial morphological variant of the query word (shared prefix
    heuristic, e.g. "admixed"/"admixture", "dendrite"/"dendritic")
  - already present as a word in data/words.json (core or discovery_only)
    -- every dot in the visualization must be something a click can
    actually resolve to a definition, never a dead end. This means the
    web gets denser for free as the pool grows, and requires pulling a
    much larger raw candidate list (TOPN_RAW) since most of any given
    word's true nearest neighbors won't be in our ~500-word vocabulary yet.
  - deduplicated

If fewer than MIN_NEIGHBORS survive filtering, neighbors is left empty and
the frontend should skip the visualization for that word rather than show
a sparse, low-quality plot.

Usage:
    python compute_neighbors.py
"""
import json
import os
import re

import gensim.downloader as api
import numpy as np
from wordfreq import zipf_frequency

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORDS_JSON = os.path.join(REPO_ROOT, "data", "words.json")

WORD_RE = re.compile(r"^[a-z]+$")
TOPN_RAW = 500
MIN_NEIGHBORS = 4
MAX_NEIGHBORS = 8
MIN_ZIPF = 1.0


def is_morphological_variant(word, candidate):
    shorter = min(len(word), len(candidate))
    prefix_len = 0
    for a, b in zip(word, candidate):
        if a != b:
            break
        prefix_len += 1
    return prefix_len >= 5 or prefix_len >= 0.7 * shorter


def get_neighbors(word, w2v, glove, known_words):
    if word in w2v.key_to_index:
        model, model_name = w2v, "word2vec"
    elif word in glove.key_to_index:
        model, model_name = glove, "glove"
    else:
        return None, None, []

    raw = model.most_similar(word, topn=TOPN_RAW)
    seen = {word}
    kept = []
    for cand, sim in raw:
        cand_l = cand.lower()
        if cand_l in seen:
            continue
        if cand_l not in known_words:
            continue
        if not WORD_RE.match(cand_l):
            continue
        if is_morphological_variant(word, cand_l):
            continue
        if zipf_frequency(cand_l, "en") < MIN_ZIPF:
            continue
        seen.add(cand_l)
        # Keep the original-cased form too: the model's vocab may only have
        # e.g. "Propionibacterium" capitalized, not the lowercase display form.
        kept.append((cand_l, cand, float(sim)))
        if len(kept) >= MAX_NEIGHBORS:
            break

    if len(kept) < MIN_NEIGHBORS:
        return model_name, model[word], []

    return model_name, model[word], kept


def resolve_label_overlap(points, min_dist, iterations=200):
    """Nudges points apart iteratively so labels don't collide, while
    keeping the layout as close as possible to the true PCA projection
    (only the minimum push needed to clear min_dist is applied)."""
    pts = points.copy()
    n = len(pts)
    for _ in range(iterations):
        moved = False
        for i in range(n):
            for j in range(i + 1, n):
                diff = pts[i] - pts[j]
                dist = np.linalg.norm(diff)
                if dist < min_dist:
                    moved = True
                    if dist < 1e-6:
                        diff = np.random.RandomState(i * n + j).randn(2) * 0.01
                        dist = 0.01
                    direction = diff / dist
                    push = (min_dist - dist) / 2
                    pts[i] += direction * push
                    pts[j] -= direction * push
        if not moved:
            break
    return pts


def local_pca_2d(vectors):
    mat = np.array(vectors)
    centered = mat - mat.mean(axis=0)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    projected = centered @ vt[:2].T

    # Normalize to a consistent scale *before* repulsion, so the minimum
    # separation enforced below is a fixed, meaningful amount regardless of
    # how tight or spread a given word's neighborhood happens to be. Scaling
    # min_dist to the data's own spread (e.g. its median pairwise distance)
    # fails precisely when a whole cluster is uniformly tight -- there's no
    # "loose" reference point left to scale against.
    scale = np.abs(projected).max()
    if scale > 0:
        projected = projected / scale

    # Labels are the point of this plot, so avoid overlap even if it means
    # deviating from the raw projection. No final rescale-to-fit after this
    # -- that would shrink everything back down and undo the separation.
    # The client fits each word's own bounding box into the plot dynamically
    # instead of assuming a fixed +/-1 coordinate range.
    projected = resolve_label_overlap(projected, min_dist=0.68)

    return projected


def main():
    print("Loading word2vec-google-news-300...")
    w2v = api.load("word2vec-google-news-300")
    print("Loading glove-wiki-gigaword-300...")
    glove = api.load("glove-wiki-gigaword-300")

    with open(WORDS_JSON, "r", encoding="utf-8") as f:
        entries = json.load(f)

    known_words = {e["word"].lower() for e in entries}

    for entry in entries:
        word = entry["word"]
        model_name, target_vec, neighbors = get_neighbors(word, w2v, glove, known_words)

        if not neighbors:
            entry["neighbors"] = []
            print(f"{word}: skipped (fewer than {MIN_NEIGHBORS} clean neighbors)")
            continue

        model = w2v if model_name == "word2vec" else glove
        vectors = [target_vec] + [model[orig] for _, orig, _ in neighbors]
        coords = local_pca_2d(vectors)

        entry["embedding_model"] = model_name
        entry["embedding_xy"] = [round(float(coords[0][0]), 4), round(float(coords[0][1]), 4)]
        entry["neighbors"] = [
            {
                "word": w,
                "similarity": round(sim, 3),
                "x": round(float(coords[i + 1][0]), 4),
                "y": round(float(coords[i + 1][1]), 4),
            }
            for i, (w, _orig, sim) in enumerate(neighbors)
        ]
        print(f"{word} ({model_name}): {[n['word'] for n in entry['neighbors']]}")

    with open(WORDS_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    print(f"Wrote neighbor data for {len(entries)} words to {WORDS_JSON}")


if __name__ == "__main__":
    main()
