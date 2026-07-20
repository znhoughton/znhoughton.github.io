"""
Scans blog/*.md for a leading front-matter block:

    ---
    title: Post Title
    date: 2026-03-14
    summary: One or two sentence teaser.
    ---

and writes data/blog-index.json as a list of {title, slug, date, summary}
sorted by date descending. The slug is the filename stem, and blog.html
fetches blog/<slug>.md directly and renders whatever follows the closing
front-matter delimiter -- this script only builds the listing metadata.

Usage:
    python scripts/build_blog_index.py
"""
import glob
import json
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(REPO_ROOT, "blog")
OUT_PATH = os.path.join(REPO_ROOT, "data", "blog-index.json")

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_front_matter(text):
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        fields[key.strip()] = value
    return fields


def main():
    posts = []
    for path in glob.glob(os.path.join(BLOG_DIR, "*.md")):
        slug = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        fields = parse_front_matter(text)
        posts.append({
            "title": fields.get("title", slug),
            "slug": slug,
            "date": fields.get("date", ""),
            "summary": fields.get("summary", ""),
        })

    posts.sort(key=lambda p: p["date"], reverse=True)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(posts)} posts to data/blog-index.json")


if __name__ == "__main__":
    main()
