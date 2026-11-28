#!/usr/bin/env python3
"""Check internal links (href/src) in a built static site. Exit 1 if any are broken.
Usage: python3 tools/site/check_links.py _site"""
import html.parser, os, sys, urllib.parse
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
ids_cache = {}

class P(html.parser.HTMLParser):
    def __init__(s):
        super().__init__(); s.links = []; s.ids = set()
    def handle_starttag(s, tag, attrs):
        a = dict(attrs)
        if "id" in a: s.ids.add(a["id"])
        if tag == "a" and "name" in a: s.ids.add(a["name"])
        for k in ("href", "src"):
            if a.get(k) and not (tag == "link" and a.get("rel") in ("canonical", "alternate")):
                s.links.append(a[k])

def parse(f):
    if f not in ids_cache:
        p = P(); p.feed(f.read_text(encoding="utf-8", errors="replace")); ids_cache[f] = p
    return ids_cache[f]

def resolve(page, url):
    u = urllib.parse.urlsplit(url)
    if u.scheme or u.netloc:
        if u.netloc in ("usbtree.gumuhub.com",):
            path = u.path
        else:
            return None, None
    else:
        path = u.path
    if not path:
        return page, u.fragment
    path = urllib.parse.unquote(path)
    target = (root / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
    target = Path(os.path.normpath(target))
    if target.is_dir():
        target = target / "index.html"
    return target, u.fragment

broken, checked, badanchor = [], 0, []
for page in sorted(root.rglob("*.html")):
    p = parse(page)
    for url in p.links:
        if url.startswith(("mailto:", "javascript:", "data:", "tel:")):
            continue
        t, frag = resolve(page, url)
        if t is None:
            continue
        checked += 1
        if not t.exists() or not str(t).startswith(str(root)):
            broken.append((page.relative_to(root), url))
        elif frag and t.suffix == ".html" and frag not in parse(t).ids:
            badanchor.append((page.relative_to(root), url))
for pg, u in broken:
    print(f"BROKEN  {pg} -> {u}")
for pg, u in badanchor:
    print(f"ANCHOR  {pg} -> {u}")
print(f"checked {checked} internal links: {len(broken)} broken, {len(badanchor)} missing anchors")
sys.exit(1 if broken else 0)
