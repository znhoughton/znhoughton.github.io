"""Rebuild data/publications.json from Google Scholar.

Scholar supplies the list, the author strings and the citation counts. It is
unreliable about *where* something was published: preprints stay at
"arXiv preprint arXiv:XXXX.XXXXX" long after the paper is out, and conference
papers and theses often arrive with no venue at all. So every entry whose
venue is missing or still looks like a preprint gets a second lookup through
venue_resolver (Semantic Scholar by arXiv ID, then OpenAlex by title), and
data/publication_overrides.json beats both when it has something to say.

Usage, from the repo root:

    python scripts/fetch_publications.py              # the weekly job
    python scripts/fetch_publications.py --dry-run    # print, write nothing
    python scripts/fetch_publications.py --from-existing --dry-run
                                                      # re-resolve venues only,
                                                      # no Scholar request at all
"""

import argparse
import json
import os
import sys

import venue_resolver as vr

SCHOLAR_ID = "39mxHGIAAAAJ"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "data", "publications.json")
OVERRIDES_PATH = os.path.join(ROOT, "data", "publication_overrides.json")
CACHE_PATH = os.path.join(ROOT, "scripts", ".venue_cache.json")

# Scholar files the venue under different keys depending on the item type.
VENUE_KEYS = ("journal", "conference", "booktitle", "venue", "publisher", "school")

# Fields the resolver owns, carried forward if a later run comes back empty.
RESOLVED_FIELDS = ("venue", "venue_kind", "status", "doi", "venue_source")


# -- small IO helpers --------------------------------------------------------

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return default


def save_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


# -- building one record -----------------------------------------------------

def scholar_venue(bib):
    """First non-empty venue-ish field Scholar gave us."""
    for key in VENUE_KEYS:
        value = (bib.get(key) or "").strip()
        if value:
            return value, key
    return "", None


def base_record(pub):
    """Turn a scholarly publication into our JSON shape, before venue resolution."""
    bib = pub.get("bib", {})
    venue, venue_key = scholar_venue(bib)
    url = pub.get("pub_url", "") or ""
    arxiv_id = vr.extract_arxiv_id(venue, url, bib.get("eprint"))

    record = {
        "title": bib.get("title", ""),
        "year": bib.get("pub_year", ""),
        "authors": bib.get("author", ""),
        "url": url,
        "citations": pub.get("num_citations", 0),
        "venue": "" if vr.looks_unpublished(venue) else venue,
        "venue_kind": "thesis" if venue_key == "school" else vr.guess_kind(venue),
        "status": "preprint" if arxiv_id else "published",
        "doi": None,
        "arxiv_id": arxiv_id,
        "venue_source": "scholar" if venue else None,
    }
    if not record["venue"]:
        record["venue_kind"] = "preprint" if arxiv_id else "other"
        record["venue_source"] = None
    return record


def apply_resolution(record, resolution):
    for field in RESOLVED_FIELDS:
        if resolution.get(field):
            record[field] = resolution[field]
    record["status"] = "published"


def override_key(record):
    """Overrides may be keyed by arXiv ID or by the normalized title."""
    if record.get("arxiv_id"):
        return record["arxiv_id"]
    return vr.normalize_title(record.get("title"))


def apply_overrides(record, overrides):
    entries = overrides.get("entries", {})
    by_arxiv = record.get("arxiv_id")
    entry = None
    if by_arxiv and by_arxiv in entries:
        entry = entries[by_arxiv]
    else:
        wanted = vr.normalize_title(record.get("title"))
        for key, value in entries.items():
            if vr.normalize_title(key) == wanted:
                entry = value
                break
    if not entry:
        return False
    for field, value in entry.items():
        if field.startswith("_"):
            continue
        record[field] = value
    record.setdefault("venue_source", "override")
    record["venue_source"] = "override"
    return True


def apply_alias(record, overrides):
    """Shorten long official venue names for display (e.g. ACL proceedings titles)."""
    venue = record.get("venue") or ""
    for long_name, short_name in (overrides.get("venue_aliases") or {}).items():
        if long_name.lower() in venue.lower():
            record["venue"] = short_name
            return


# -- the pipeline ------------------------------------------------------------

def fetch_from_scholar():
    from scholarly import scholarly

    print(f"Fetching publications for Scholar ID: {SCHOLAR_ID}")
    author = scholarly.search_author_id(SCHOLAR_ID)
    scholarly.fill(author, sections=["publications"])

    records = []
    for pub in author.get("publications", []):
        try:
            scholarly.fill(pub)
        except Exception as err:
            print(f"Warning: could not fill pub details: {err}")
        records.append(base_record(pub))
    return records


def resolve_venues(records, cache, use_network=True):
    """Fill in venues Scholar could not, asking the open APIs where needed."""
    resolved_count = 0
    for record in records:
        cache_key = record.get("arxiv_id") or vr.normalize_title(record.get("title"))

        cached = cache.get(cache_key)
        if cached:
            apply_resolution(record, cached)
            continue

        # Only spend a request on entries left preprint-y or blank. Anything
        # with a real venue is already settled and is never re-queried.
        if not vr.looks_unpublished(record.get("venue")):
            continue
        if not use_network:
            continue

        print(f"  resolving: {record.get('title', '')[:70]}")
        resolution = vr.resolve(
            title=record.get("title"),
            arxiv_id=record.get("arxiv_id"),
            doi=record.get("doi"),
        )
        if resolution:
            apply_resolution(record, resolution)
            cache[cache_key] = resolution
            resolved_count += 1
            print(f"    -> {resolution['venue']} ({resolution['venue_source']})")
        else:
            print("    -> still a preprint / no published record found")
    return resolved_count


def carry_forward(records, previous):
    """Keep venue info an earlier run established if this run came back empty.

    The updater runs unattended every week; a flaky API call should never
    silently strip a venue that is already on the site.
    """
    by_title = {vr.normalize_title(p.get("title")): p for p in previous}
    for record in records:
        old = by_title.get(vr.normalize_title(record.get("title")))
        if not old:
            continue
        # Never carry a stale preprint venue forward over a blank: a blank
        # renders as "arXiv preprint", which is the truthful fallback.
        if not record.get("venue") and not vr.looks_unpublished(old.get("venue")):
            for field in RESOLVED_FIELDS:
                if old.get(field):
                    record[field] = old[field]
        if not record.get("arxiv_id") and old.get("arxiv_id"):
            record["arxiv_id"] = old["arxiv_id"]


def finalize(record):
    """Derived fields the page renders."""
    if record.get("arxiv_id"):
        record["arxiv_url"] = f"https://arxiv.org/abs/{record['arxiv_id']}"
    if record.get("doi"):
        record["doi_url"] = f"https://doi.org/{record['doi']}"
    if not record.get("url"):
        record["url"] = record.get("doi_url") or record.get("arxiv_url") or ""

    # An override may have set a status by hand ("in press"); otherwise the
    # venue decides. Only a non-"published" status shows a badge on the page.
    if record.get("venue_source") != "override" or not record.get("status"):
        if not vr.looks_unpublished(record.get("venue")):
            record["status"] = "published"
        elif record.get("arxiv_id"):
            record["status"] = "preprint"
        else:
            record["status"] = None  # unknown: show no badge rather than guess
    return record


def sort_records(records):
    def year_of(record):
        year = str(record.get("year") or "")
        return int(year) if year.isdigit() else -1

    records.sort(key=lambda r: (r.get("title") or "").lower())
    records.sort(key=year_of, reverse=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the result instead of writing data/publications.json")
    parser.add_argument("--from-existing", action="store_true",
                        help="skip Google Scholar and re-resolve the current JSON")
    parser.add_argument("--no-resolve", action="store_true",
                        help="skip the Semantic Scholar / OpenAlex lookups")
    args = parser.parse_args()

    overrides = load_json(OVERRIDES_PATH, {})
    cache = load_json(CACHE_PATH, {})
    previous = load_json(OUT_PATH, [])

    if args.from_existing:
        print(f"Re-resolving {len(previous)} existing publications (no Scholar request)")
        records = [dict(p) for p in previous]
        for record in records:
            if not record.get("arxiv_id"):
                record["arxiv_id"] = vr.extract_arxiv_id(record.get("venue"), record.get("url"))
            if vr.looks_unpublished(record.get("venue")):
                record["venue"] = ""
    else:
        records = fetch_from_scholar()

    # A truncated Scholar response (block, captcha, network) must not wipe the page.
    if previous and len(records) < 0.6 * len(previous):
        print(f"Refusing to write: got {len(records)} publications, "
              f"but {len(previous)} were there before. Nothing changed.")
        return 1

    if not args.no_resolve:
        resolved = resolve_venues(records, cache, use_network=True)
        print(f"Resolved {resolved} venue(s) via Semantic Scholar / OpenAlex")

    carry_forward(records, previous)
    for record in records:
        apply_overrides(record, overrides)
        apply_alias(record, overrides)
        finalize(record)

    sort_records(records)

    missing = [r["title"] for r in records if not r.get("venue")]
    if missing:
        print(f"\n{len(missing)} publication(s) still have no venue. "
              f"Add them to data/publication_overrides.json if you want one shown:")
        for title in missing:
            print(f"  - {title}")

    if args.dry_run:
        print("\n--- dry run, nothing written ---")
        for record in records:
            badge = "" if record.get("status") == "published" else f"  [{record.get('status')}]"
            print(f"{record.get('year') or '????'}  {record.get('venue') or '(no venue)'}{badge}")
            print(f"        {record.get('title')}")
        return 0

    save_json(OUT_PATH, records)
    save_json(CACHE_PATH, cache)
    print(f"\nDone. Wrote {len(records)} publications to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
