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
    """GET JSON, backing off once on a 429. Returns None on any failure."""
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
            # Semantic Scholar throttles unauthenticated callers aggressively.
            if err.code == 429 and attempt < retries:
                time.sleep(THROTTLE_BACKOFF)
                continue
            print(f"    ! HTTP {err.code} from {url}")
            return None
        except Exception as err:  # network down, timeout, malformed JSON
            print(f"    ! request failed ({err}) for {url}")
            return None
        finally:
            time.sleep(REQUEST_PAUSE)
    return None


# -- Semantic Scholar --------------------------------------------------------

S2_FIELDS = "title,year,venue,publicationVenue,externalIds,journal,publicationTypes,url"


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
                  "select": "title,container-title,type,DOI,issued"}
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
