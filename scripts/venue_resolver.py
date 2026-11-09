"""Work out where a paper was actually published.

Google Scholar supplies the publication list, but it is unreliable about the
venue: a paper can sit at "arXiv preprint arXiv:XXXX.XXXXX" for months (or
forever) after it has appeared in a journal or proceedings, and conference
papers often arrive with no venue string at all. This module asks two open
APIs that track the preprint -> published transition explicitly:

  1. Semantic Scholar, looked up by arXiv ID. S2 links a preprint record to
     its published version, so this is the lookup that catches "the preprint
     came out somewhere".
  2. Crossref, looked up by DOI or title. Broadest coverage of the three and
     the one that reliably names proceedings (ACL Anthology, IEEE, and so on).
  3. OpenAlex, looked up by title or DOI, for anything the first two miss.

None of them needs an API key. Set PUBLICATION_MAILTO to an email address to
join the Crossref and OpenAlex "polite pools" (faster, fewer throttles); it is
optional.
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "znhoughton.github.io publication updater (+https://znhoughton.github.io)"
REQUEST_PAUSE = 1.0  # be polite; these APIs are free and unauthenticated here
THROTTLE_BACKOFF = 5.0  # extra wait before retrying a 429
# The unauthenticated S2 search endpoint is throttled hardest of the three.
S2_SEARCH_RETRIES = 4

ARXIV_DOI_PREFIX = "10.48550"

PREPRINT_SERVERS = {
    "arxiv", "arxiv.org", "biorxiv", "medrxiv", "psyarxiv", "ssrn",
    "research square", "preprints.org", "osf preprints", "openreview",
    "openreview.net", "lingbuzz",
}

_ARXIV_RE = re.compile(
    r"arxiv[:/\s]*((?:\d{4}\.\d{4,5})(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)",
    re.I,
)


# -- helpers -----------------------------------------------------------------

def normalize_title(title):
    """Lowercase, punctuation-free form used to match records across sources."""
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def extract_arxiv_id(*candidates):
    """Pull an arXiv ID out of a venue string, URL, or anything else."""
    for text in candidates:
        if not text:
            continue
        match = _ARXIV_RE.search(str(text))
        if match:
            return re.sub(r"v\d+$", "", match.group(1))
    return None


def looks_unpublished(venue, doi=None):
    """True when a venue string is empty or names a preprint server."""
    name = (venue or "").strip().lower()
    if doi and _bare_doi(doi).lower().startswith(ARXIV_DOI_PREFIX):
        return True
    if not name:
        return True
    if "arxiv" in name or "preprint" in name:
        return True
    return name in PREPRINT_SERVERS


def guess_kind(venue):
    """Classify a venue string when the source does not label it."""
    name = (venue or "").lower()
    if any(word in name for word in ("dissertation", "thesis")):
        return "thesis"
    if any(word in name for word in
           ("proceedings", "conference", "workshop", "meeting", "symposium")):
        return "conference"
    if name:
        return "journal"
    return "other"


def _bare_doi(doi):
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", str(doi or "").strip())


def _clean_doi(doi):
    """Normalize a DOI, dropping arXiv DOIs (they are not evidence of publication)."""
    bare = _bare_doi(doi)
    if not bare or bare.lower().startswith(ARXIV_DOI_PREFIX):
        return None
    return bare


def _mailto():
    """Optional contact address for the Crossref / OpenAlex polite pools."""
    return os.environ.get("PUBLICATION_MAILTO") or os.environ.get("OPENALEX_MAILTO")


def _get_json(url, timeout=25, retries=1):
    """GET JSON, backing off on a 429. Returns None on any failure.

    Worth insisting on the retries: a throttled lookup and a genuinely
    unknown paper both come back empty, and treating the first as the second
    silently drops an author list that the source actually had.
    """
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return None
            # Semantic Scholar throttles unauthenticated callers aggressively,
            # so back off further on each attempt rather than at a fixed pace.
            if err.code == 429 and attempt < retries:
                time.sleep(THROTTLE_BACKOFF * (attempt + 1))
                continue
            print(f"    ! HTTP {err.code} from {url}")
            return None
        except Exception as err:  # network down, timeout, malformed JSON
            print(f"    ! request failed ({err}) for {url}")
            return None
        finally:
            time.sleep(REQUEST_PAUSE)
    return None


# -- author names ------------------------------------------------------------

# Tokens that belong to the surname rather than the given names.
NAME_PARTICLES = {
    "van", "von", "de", "del", "della", "der", "den", "da", "dos", "du",
    "la", "le", "bin", "ibn", "al", "ter", "ten", "af", "zu", "st",
}

NAME_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "phd", "md"}

SELF_SURNAME = "houghton"

# The sources disagree about how much of the site owner's name they carry
# ("Zachary Houghton", "Z Houghton", "Zachary Nicholas Houghton"), which would
# show up as the same person spelled three ways down the page. One spelling wins.
SELF_NAME = "Houghton, Z. N."

_SELF_RE = re.compile(r"^houghton,\s*z", re.I)


def _is_self(formatted_name):
    return bool(_SELF_RE.match(formatted_name.strip()))


def _initials(given):
    """'Zachary Nathan' -> 'Z. N.'; 'Jean-Pierre' -> 'J.-P.'"""
    out = []
    for part in re.split(r"[\s.]+", given or ""):
        if not part:
            continue
        if "-" in part:
            out.append("-".join(seg[0].upper() + "." for seg in part.split("-") if seg))
        else:
            out.append(part[0].upper() + ".")
    return " ".join(out)


def format_author_name(name=None, given=None, family=None):
    """Normalize any shape of author name to 'Surname, F. M.'.

    Handles the three forms the sources hand us: Crossref's structured
    given/family pair, a full 'Zachary Nathan Houghton' display string, and an
    already-inverted 'Houghton, Z. N.' string.
    """
    if family:
        surname, givens = family.strip(), (given or "").strip()
    else:
        raw = re.sub(r"\s+", " ", (name or "").strip())
        if not raw:
            return ""
        if "," in raw:
            surname, _, givens = raw.partition(",")
        else:
            tokens = raw.split(" ")
            suffix = ""
            while len(tokens) > 1 and tokens[-1].strip(".,").lower() in NAME_SUFFIXES:
                suffix = tokens.pop().strip(".,")
            if len(tokens) == 1:
                return tokens[0]
            # Walk left over particles so 'van der Berg' stays with the surname.
            start = len(tokens) - 1
            while start - 1 >= 1 and tokens[start - 1].strip(".").lower() in NAME_PARTICLES:
                start -= 1
            surname = " ".join(tokens[start:])
            givens = " ".join(tokens[:start])
            if suffix:
                surname = f"{surname} {suffix}"

    surname = surname.strip().strip(",")
    initials = _initials(givens)
    if not surname:
        return initials
    return f"{surname}, {initials}" if initials else surname


def parse_author_string(text):
    """Split an author string into individual names.

    Scholar joins names with ' and '; BibTeX does too. Plain comma-separated
    strings are left alone, because a comma is also the inversion marker and
    splitting on it would tear 'Houghton, Z. N.' in half.
    """
    text = (text or "").strip()
    if not text:
        return []
    parts = re.split(r"\s+and\s+|\s*;\s*", text)
    return [part.strip() for part in parts if part.strip()]


def format_author_list(authors, max_names=12):
    """Render a list of names as the display string the page shows.

    `authors` items may be strings or {'given', 'family'} dicts. Long author
    lists are truncated, but never before Houghton: on a personal site the
    one name that must survive is the site owner's.
    """
    formatted = []
    for author in authors or []:
        if isinstance(author, dict):
            name = format_author_name(
                given=author.get("given"), family=author.get("family"),
                name=author.get("name"),
            )
        else:
            name = format_author_name(name=author)
        if name:
            formatted.append(SELF_NAME if _is_self(name) else name)

    if not formatted:
        return ""

    if len(formatted) > max_names:
        self_index = next(
            (i for i, name in enumerate(formatted) if _is_self(name)),
            -1,
        )
        keep = max(max_names, self_index + 1)
        if keep < len(formatted):
            return ", ".join(formatted[:keep]) + ", et al."

    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + ", & " + formatted[-1]


# -- matching titles across sources ------------------------------------------

# Scholar truncates a long title and marks the cut with an ellipsis, so the
# stored title can be a prefix of the real one. Those need a prefix match, and
# they are worth repairing outright when a source hands back the full string.
TRUNCATION_MARKERS = ("…", "...")


def is_truncated_title(title):
    return (title or "").rstrip().endswith(TRUNCATION_MARKERS)


def _title_stem(title):
    """Normalized title with any trailing ellipsis removed."""
    text = (title or "").rstrip()
    for marker in TRUNCATION_MARKERS:
        if text.endswith(marker):
            text = text[: -len(marker)]
            break
    return normalize_title(text)


def titles_match(stored, candidate):
    """True when `candidate` is the same work as `stored`.

    Exact after normalization, or -- for a Scholar-truncated title -- the
    candidate starts with everything we do have. Callers pair a prefix match
    with has_self_author() so a merely similar title cannot pull in the wrong
    author list.
    """
    stem = _title_stem(stored)
    other = normalize_title(candidate)
    if not stem or not other:
        return False
    if stem == other:
        return True
    return is_truncated_title(stored) and other.startswith(stem)


def has_self_author(names):
    """True when the site owner appears in an author list."""
    for author in names or []:
        if isinstance(author, dict):
            text = author.get("family") or author.get("name") or ""
        else:
            text = author or ""
        if SELF_SURNAME in text.lower():
            return True
    return False


# -- Semantic Scholar --------------------------------------------------------

S2_FIELDS = ("title,year,venue,publicationVenue,externalIds,journal,publicationTypes,url,authors")


def from_semantic_scholar(arxiv_id=None, doi=None):
    """Look up a paper by arXiv ID (preferred) or DOI. None if still a preprint."""
    if arxiv_id:
        key = "arXiv:" + arxiv_id
    elif doi:
        key = "DOI:" + doi
    else:
        return None

    data = _get_json(
        "https://api.semanticscholar.org/graph/v1/paper/"
        + urllib.parse.quote(key, safe="")
        + "?fields="
        + S2_FIELDS
    )
    if not data:
        return None

    publication_venue = data.get("publicationVenue") or {}
    journal = data.get("journal") or {}
    venue = (
        publication_venue.get("name")
        or data.get("venue")
        or journal.get("name")
        or ""
    ).strip()

    if looks_unpublished(venue):
        return None

    return {
        "venue": venue,
        "venue_kind": (publication_venue.get("type") or guess_kind(venue)).lower(),
        "status": "published",
        "doi": _clean_doi((data.get("externalIds") or {}).get("DOI")),
        "year": data.get("year"),
        "venue_source": "semantic_scholar",
    }


# -- Crossref ----------------------------------------------------------------

# Crossref types that are not a real publication venue.
CROSSREF_SKIP_TYPES = {"posted-content", "component", "dataset", "peer-review"}

CROSSREF_KINDS = {
    "journal-article": "journal",
    "proceedings-article": "conference",
    "book-chapter": "book",
    "dissertation": "thesis",
}


def from_crossref(title=None, doi=None):
    """Look up a paper by DOI or title. None if Crossref only knows a preprint."""
    item = None

    if doi:
        data = _get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
        item = (data or {}).get("message")

    if item is None and title:
        params = {"query.bibliographic": title, "rows": 5,
                  "select": "title,container-title,type,DOI,issued,author"}
        mailto = _mailto()
        if mailto:
            params["mailto"] = mailto
        data = _get_json("https://api.crossref.org/works?" + urllib.parse.urlencode(params))
        wanted = normalize_title(title)
        for candidate in (((data or {}).get("message") or {}).get("items") or []):
            names = candidate.get("title") or [""]
            if normalize_title(names[0]) == wanted:
                item = candidate
                break

    if not item:
        return None

    item_type = (item.get("type") or "").lower()
    if item_type in CROSSREF_SKIP_TYPES:
        return None

    containers = item.get("container-title") or []
    venue = (containers[0] if containers else "").strip()
    if looks_unpublished(venue):
        return None

    year = None
    parts = ((item.get("issued") or {}).get("date-parts") or [[]])[0]
    if parts:
        year = parts[0]

    return {
        "venue": venue,
        "venue_kind": CROSSREF_KINDS.get(item_type, guess_kind(venue)),
        "status": "published",
        "doi": _clean_doi(item.get("DOI")),
        "year": year,
        "venue_source": "crossref",
    }


# -- OpenAlex ----------------------------------------------------------------

def _openalex_query(params):
    params = dict(params)
    mailto = _mailto()
    if mailto:
        params["mailto"] = mailto
    return urllib.parse.urlencode(params)


def _openalex_source(work):
    return ((work or {}).get("primary_location") or {}).get("source") or {}


def _openalex_is_published(work):
    work_type = (work.get("type") or "").lower()
    if work_type in {"preprint", "posted-content"}:
        return False
    if work_type == "dissertation":
        return True  # a thesis has no journal but is not a preprint either
    if (_openalex_source(work).get("type") or "").lower() == "repository":
        return False
    return not looks_unpublished(_openalex_source(work).get("display_name"))


def from_openalex(title=None, doi=None):
    """Look up a paper by DOI or title. None if OpenAlex only knows a preprint."""
    work = None

    if doi:
        work = _get_json(
            "https://api.openalex.org/works/doi:"
            + urllib.parse.quote(doi, safe="")
            + "?"
            + _openalex_query({})
        )

    if work is None and title:
        # OpenAlex chokes on punctuation inside a filter value, so search on words.
        query = re.sub(r"[^A-Za-z0-9 ]+", " ", title).strip()
        data = _get_json(
            "https://api.openalex.org/works?"
            + _openalex_query({"filter": "title.search:" + query, "per-page": 5})
        )
        wanted = normalize_title(title)
        matches = [
            candidate
            for candidate in (data or {}).get("results", [])
            if normalize_title(candidate.get("display_name")) == wanted
        ]
        # A preprint and its published version are often separate OpenAlex works.
        matches.sort(key=lambda candidate: 0 if _openalex_is_published(candidate) else 1)
        work = matches[0] if matches else None

    if not work or not _openalex_is_published(work):
        return None

    source = _openalex_source(work)
    venue = (source.get("display_name") or "").strip()
    work_type = (work.get("type") or "").lower()

    if not venue and work_type == "dissertation":
        venue = "Doctoral dissertation"
    if not venue:
        return None

    kind = {
        "journal": "journal",
        "conference": "conference",
        "book series": "book",
    }.get((source.get("type") or "").lower(), guess_kind(venue))
    if work_type == "dissertation":
        kind = "thesis"

    return {
        "venue": venue,
        "venue_kind": kind,
        "status": "published",
        "doi": _clean_doi(work.get("doi")),
        "year": work.get("publication_year"),
        "venue_source": "openalex",
    }


# -- authors -----------------------------------------------------------------
#
# Separate from the venue lookups above, which bail out on anything that still
# looks like a preprint. An author list is worth having either way, so these
# take whatever record they find.

def _authors_from_semantic_scholar(arxiv_id=None, doi=None, title=None):
    data = None
    if arxiv_id or doi:
        key = ("arXiv:" + arxiv_id) if arxiv_id else ("DOI:" + doi)
        data = _get_json(
            "https://api.semanticscholar.org/graph/v1/paper/"
            + urllib.parse.quote(key, safe="")
            + "?fields=authors"
        )
    names = [author.get("name", "") for author in ((data or {}).get("authors") or [])]
    if names:
        return names

    # No identifier, or S2 has no record under it: search by title instead.
    match = _s2_search_by_title(title, "title,authors")
    names = [author.get("name", "") for author in ((match or {}).get("authors") or [])]
    if names and (not is_truncated_title(title) or has_self_author(names)):
        return names
    return []


def _s2_search_by_title(title, fields):
    """Semantic Scholar title search. Covers the proceedings and theses that
    never get a DOI, which is most of what Crossref misses."""
    if not title:
        return None
    query = re.sub(r"[^A-Za-z0-9 ]+", " ", title).strip()
    data = _get_json(
        "https://api.semanticscholar.org/graph/v1/paper/search?"
        + urllib.parse.urlencode({"query": query, "limit": 5, "fields": fields}),
        retries=S2_SEARCH_RETRIES,
    )
    for candidate in (data or {}).get("data") or []:
        if titles_match(title, candidate.get("title")):
            return candidate
    return None


def _crossref_authors(item):
    names = []
    for author in (item or {}).get("author") or []:
        if author.get("family") or author.get("given"):
            names.append({"given": author.get("given"), "family": author.get("family")})
        elif author.get("name"):
            names.append({"name": author["name"]})
    return names


def _authors_from_crossref(title=None, doi=None):
    if doi:
        data = _get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
        names = _crossref_authors((data or {}).get("message"))
        if names:
            return names

    if not title:
        return []

    params = {"query.bibliographic": title, "rows": 5, "select": "title,author,DOI"}
    mailto = _mailto()
    if mailto:
        params["mailto"] = mailto
    data = _get_json("https://api.crossref.org/works?" + urllib.parse.urlencode(params))
    for candidate in (((data or {}).get("message") or {}).get("items") or []):
        names = candidate.get("title") or [""]
        if not titles_match(title, names[0]):
            continue
        authors = _crossref_authors(candidate)
        if authors and (not is_truncated_title(title) or has_self_author(authors)):
            return authors
    return []


def _openalex_authors(work):
    names = []
    for authorship in (work or {}).get("authorships") or []:
        author = authorship.get("author") or {}
        name = author.get("display_name") or authorship.get("raw_author_name") or ""
        if name:
            names.append(name)
    return names


def _authors_from_openalex(title=None, doi=None):
    if doi:
        work = _get_json(
            "https://api.openalex.org/works/doi:"
            + urllib.parse.quote(doi, safe="")
            + "?"
            + _openalex_query({})
        )
        names = _openalex_authors(work)
        if names:
            return names

    if not title:
        return []

    query = re.sub(r"[^A-Za-z0-9 ]+", " ", title).strip()
    data = _get_json(
        "https://api.openalex.org/works?"
        + _openalex_query({"filter": "title.search:" + query, "per-page": 5})
    )
    for candidate in (data or {}).get("results", []):
        if not titles_match(title, candidate.get("display_name")):
            continue
        names = _openalex_authors(candidate)
        if names and (not is_truncated_title(title) or has_self_author(names)):
            return names
    return []


def resolve_authors(title, arxiv_id=None, doi=None):
    """Author list for a work as a display string, or '' if nothing is found."""
    lookups = (
        lambda: _authors_from_crossref(title=title, doi=doi),
        lambda: _authors_from_semantic_scholar(arxiv_id=arxiv_id, doi=doi, title=title),
        lambda: _authors_from_openalex(title=title, doi=doi),
    )
    for lookup in lookups:
        try:
            names = lookup()
        except Exception as err:
            print(f"    ! author lookup error: {err}")
            names = []
        if names:
            return format_author_list(names)
    return ""


def resolve_full_title(title, arxiv_id=None, doi=None):
    """Recover a Scholar-truncated title, or '' if no source has the full one.

    Only ever called for a title that ends in an ellipsis. The replacement must
    start with the part we already have, so a near-miss cannot rename a paper.
    """
    if not is_truncated_title(title):
        return ""

    candidates = []

    if arxiv_id or doi:
        key = ("arXiv:" + arxiv_id) if arxiv_id else ("DOI:" + doi)
        data = _get_json(
            "https://api.semanticscholar.org/graph/v1/paper/"
            + urllib.parse.quote(key, safe="")
            + "?fields=title"
        )
        candidates.append((data or {}).get("title"))

    match = _s2_search_by_title(title, "title,authors")
    if match:
        candidates.append(match.get("title"))

    query = re.sub(r"[^A-Za-z0-9 ]+", " ", title).strip()
    data = _get_json(
        "https://api.openalex.org/works?"
        + _openalex_query({"filter": "title.search:" + query, "per-page": 5})
    )
    for work in (data or {}).get("results", []):
        candidates.append(work.get("display_name"))

    params = {"query.bibliographic": title, "rows": 5, "select": "title"}
    mailto = _mailto()
    if mailto:
        params["mailto"] = mailto
    data = _get_json("https://api.crossref.org/works?" + urllib.parse.urlencode(params))
    for item in (((data or {}).get("message") or {}).get("items") or []):
        for name in item.get("title") or []:
            candidates.append(name)

    for candidate in candidates:
        candidate = re.sub(r"\s+", " ", (candidate or "").strip())
        if not candidate or is_truncated_title(candidate):
            continue
        if titles_match(title, candidate) and len(candidate) > len(title.rstrip()):
            return candidate
    return ""


# -- public entry point ------------------------------------------------------

def resolve(title, arxiv_id=None, doi=None):
    """Best available published venue for a work, or None if it is still a preprint."""
    lookups = (
        lambda: from_semantic_scholar(arxiv_id=arxiv_id, doi=doi),
        lambda: from_crossref(title=title, doi=doi),
        lambda: from_openalex(title=title, doi=doi),
    )
    for lookup in lookups:
        try:
            result = lookup()
        except Exception as err:
            print(f"    ! resolver error: {err}")
            result = None
        if result:
            return result
    return None
