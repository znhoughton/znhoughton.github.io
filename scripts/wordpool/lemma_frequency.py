"""
Shared "effective zipf" computation, used by both generate_candidates.py
(deciding whether a candidate is hard enough / not too hard to add to the
pool) and backfill_rarity.py (deciding the displayed rarity tier/percentile
for words already in the pool). Both need the same fix for the same reason:
raw surface-form zipf understates how familiar a word actually is when it's
a transparent derivation of a much more common root -- "deductively" reads
as obscure by raw token frequency (zipf 1.65) purely because the adverb form
is used less often in text than "deductive" (zipf 2.65), not because the
word itself is hard. This mirrors the psycholinguistic finding that
whole-word-family frequency, not just the exact surface token, is what
drives how easy a word actually is to process.

Effective zipf = the surface form's own frequency combined with its guessed
lemma's frequency, summed in linear frequency space (zipf is a log scale)
then converted back. If no plausible lemma is found, effective zipf is just
the surface zipf, unchanged.
"""
import math

from wordfreq import zipf_frequency

# Ordered longest-suffix-first so more specific patterns are tried before a
# shorter suffix that would also match.
DERIVATIONAL_SUFFIXES = [
    ("ness", 4),
    ("ity", 3),
    ("ly", 2),
]

# Words where a derivational suffix superficially matches but the "root" it
# would recover isn't the real, synchronically-felt derivation -- these are
# lexicalized/frozen forms, not live X+suffix derivations, so blending in the
# stripped root's frequency would be flatly wrong (e.g. "comely" is not
# "come" + "ly"; "probity" is not "prob" + "ity"). Hand-verified exceptions,
# extend as more turn up.
NOT_REALLY_DERIVED = {
    "comely", "gangly", "gingerly", "probity", "homely", "portly", "burly",
    "doolally",
}


def guess_lemma(word):
    """A deliberately simple suffix-stripping heuristic, not a real
    morphological analyzer -- good enough to catch the common derivational
    patterns (-ly, -ness, -ity) that cause surface-frequency false
    positives, without the complexity of a full lemmatizer for a handful of
    suffixes. Returns the single most-plausible root, or None."""
    if word in NOT_REALLY_DERIVED:
        return None

    candidates = []

    # "-ic" adjectives form their adverb as "-ic" + "ally" (frantic ->
    # frantically, not "franticly"), so plain "-ly" stripping recovers a
    # nonsense "-ical" pseudo-word ("frantical") instead of the real root.
    # Try both strips and let frequency decide which root is real: an
    # already-independently-real "-ical" word (dialectical, colloquial)
    # will still win on its own merits since the wrong candidate scores 0.
    if word.endswith("ally") and len(word) - 4 > 3:
        candidates.append(word[:-4])  # frantically -> frantic

    for suffix, strip in DERIVATIONAL_SUFFIXES:
        if word.endswith(suffix) and len(word) - strip > 3:
            candidates.append(word[:-strip])
            break  # only the longest-matching plain suffix, e.g. not both -ity and -ly

    valid = [(c, zipf_frequency(c, "en")) for c in candidates if c != word]
    valid = [(c, z) for c, z in valid if z > 0]
    if not valid:
        return None
    return max(valid, key=lambda t: t[1])[0]


def effective_zipf(word, own_zipf):
    lemma = guess_lemma(word)
    if not lemma:
        return own_zipf
    lemma_zipf = zipf_frequency(lemma, "en")
    if lemma_zipf <= 0:
        return own_zipf
    combined_freq = 10 ** own_zipf + 10 ** lemma_zipf
    return math.log10(combined_freq)
