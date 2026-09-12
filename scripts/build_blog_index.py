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

Drafts are kept out of the listing by git-ignoring them: any blog/*.md that
git reports as ignored is skipped, since an entry for a file that never gets
pushed would render a listing item whose link 404s.

Usage:
    python scripts/build_blog_index.py
"""
import glob
import json
import os
import re
import subprocess

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


def ignored_paths(paths):
    """Subset of `paths` that git ignores (empty if git isn't usable here)."""
    if not paths:
        return set()
    try:
        proc = subprocess.run(
            ["git", "check-ignore", "-z", "--stdin"],
            input="\0".join(paths),
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
    except OSError:
        return set()
    # exit 0 = some matched, 1 = none matched; anything else means git failed
    # (not a repo, no git), in which case fall back to including everything.
    # -z also stops git from quoting paths it would otherwise escape.
    if proc.returncode not in (0, 1):
        return set()
    return {p for p in proc.stdout.split("\0") if p}


def main():
    paths = sorted(glob.glob(os.path.join(BLOG_DIR, "*.md")))
    rel = {p: os.path.relpath(p, REPO_ROOT).replace(os.sep, "/") for p in paths}
    skip = ignored_paths(sorted(rel.values()))

    posts = []
    for path in paths:
        if rel[path] in skip:
            print(f"Skipping git-ignored draft: {os.path.basename(path)}")
            continue
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
