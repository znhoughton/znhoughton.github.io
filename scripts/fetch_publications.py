import json
import os
from scholarly import scholarly

SCHOLAR_ID = "39mxHGIAAAAJ"

def fetch_publications():
    print(f"Fetching publications for Scholar ID: {SCHOLAR_ID}")
    author = scholarly.search_author_id(SCHOLAR_ID)
    scholarly.fill(author, sections=["publications"])

    pubs = []
    for pub in author.get("publications", []):
        try:
            scholarly.fill(pub)
        except Exception as e:
            print(f"Warning: could not fill pub details: {e}")
        bib = pub.get("bib", {})
        pubs.append({
            "title": bib.get("title", ""),
            "year": bib.get("pub_year", ""),
            "venue": (
                bib.get("venue", "")
                or bib.get("journal", "")
                or bib.get("booktitle", "")
                or ""
            ),
            "authors": bib.get("author", ""),
            "url": pub.get("pub_url", ""),
            "citations": pub.get("num_citations", 0),
        })

    # Sort by year descending, with missing years at the bottom
    pubs.sort(key=lambda x: str(x.get("year") or 0), reverse=True)

    os.makedirs("data", exist_ok=True)
    with open("data/publications.json", "w", encoding="utf-8") as f:
        json.dump(pubs, f, indent=2, ensure_ascii=False)

    print(f"Done. Wrote {len(pubs)} publications to data/publications.json")

if __name__ == "__main__":
    fetch_publications()
