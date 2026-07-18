"""
Shared automated filters for the wiktextract-sourced candidate pipeline.

Both filters exist to avoid manual per-word vetting for things that are
mechanically detectable rather than judgment calls:

  - STUB_GLOSS_RE catches "dictionary redirect" entries (e.g. "pease" ->
    "Alternative form of pea") that technically have real etymology (so they
    passed the etymology-text filter in build_wiktextract_index.py) but
    whose primary gloss doesn't actually describe the word's meaning.

  - PROFANITY_BLOCKLIST is a starting list of vulgar/crude terms that should
    never surface as a public Word of the Day regardless of how they score
    on frequency -- this is a correctness/reputational concern, not a
    difficulty-calibration one, so it's a hard exclusion, not a zipf-band
    question. Not exhaustive; extend as more turn up.
"""
import re

STUB_GLOSS_RE = re.compile(
    r"^(alternative|obsolete|archaic|dated|eye dialect|pronunciation|"
    r"superseded|nonstandard|informal|dialectal)\s+(form|spelling)\s+of\b",
    re.IGNORECASE,
)

# Also catches bare "Plural of X" / "Synonym of X" style non-definitions.
REDIRECT_GLOSS_RE = re.compile(
    r"^(plural|synonym|misspelling|clipping|abbreviation|initialism|"
    r"contraction)\s+of\b",
    re.IGNORECASE,
)

PROFANITY_BLOCKLIST = {
    "arsehole", "asshole", "bastard", "bitch", "bollocks", "bugger",
    "bullshit", "clit", "cock", "cocksucker", "cum", "cunt", "dickhead",
    "dyke", "fag", "faggot", "fuck", "fucker", "goddamn", "handjob",
    "horseshit", "jackass", "jerkoff", "jizz", "motherfucker", "negro",
    "nigger", "nigga", "paki", "perv", "pervert", "piss", "prick", "pussy",
    "queer", "retard", "shit", "shithead", "slut", "spic", "tit", "tits",
    "twat", "wank", "wanker", "whore",
}


def is_stub_gloss(gloss):
    """True if this gloss is a redirect to another headword rather than an
    independent definition."""
    if not gloss:
        return True
    return bool(STUB_GLOSS_RE.match(gloss) or REDIRECT_GLOSS_RE.match(gloss))


def is_blocked(word):
    return word.lower() in PROFANITY_BLOCKLIST
