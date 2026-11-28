#!/usr/bin/env python3
"""检查 10~70（含 65）、78 与 90 的内容页：每篇都有来自其他文件的入链，且能从 README 或总图走到。

退出码 0 = 通过。问题打印到 stdout，由 tools/validate.sh 调用。
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
CONTENT_TOP = ("10-", "20-", "30-", "40-", "50-", "60-", "65-", "70-", "78-", "90-")
SEEDS = ("README.md", "00-知识树总图.md")
LINK = re.compile(r"\]\(([^)#][^)]*)\)")


def is_content(rel: str) -> bool:
    return rel.startswith(CONTENT_TOP)


def iter_md():
    for p in ROOT.rglob("*.md"):
        rel = p.relative_to(ROOT)
        # ai-kb/ 与 tech-doc/ 是派生产物，不参与内容页入链/可达性，避免改写入链后掩盖孤页。
        if rel.parts[:1] in {("ai-kb",), ("tech-doc",), ("site",)} or any(part.startswith(".") for part in rel.parts):
            continue
        yield p


def outbound(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    found = []
    for m in LINK.finditer(text):
        raw = unquote(m.group(1).strip().split()[0]).split("#", 1)[0]
        if not raw or raw.startswith(("http://", "https://", "mailto:")):
            continue
        target = (path.parent / raw).resolve()
        if not target.is_file() or target.suffix != ".md":
            continue
        try:
            rel = target.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        found.append(rel)
    return found


def main() -> int:
    files = {}
    for p in iter_md():
        rel = p.relative_to(ROOT).as_posix()
        files[rel] = outbound(p)

    inbound = {rel: set() for rel in files}
    for src, outs in files.items():
        for dst in outs:
            if dst in inbound and dst != src:
                inbound[dst].add(src)

    content = sorted(rel for rel in files if is_content(rel))
    orphans = [rel for rel in content if not inbound.get(rel)]

    seen = set()
    stack = [s for s in SEEDS if s in files]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for nxt in files.get(cur, []):
            if nxt not in seen:
                stack.append(nxt)
    unreachable = [rel for rel in content if rel not in seen]

    bad = False
    if orphans:
        bad = True
        print(f"  无入链 {len(orphans)} 篇:")
        for rel in orphans:
            print(f"    {rel}")
    if unreachable:
        bad = True
        print(f"  从 README / 总图走不到 {len(unreachable)} 篇:")
        for rel in unreachable:
            print(f"    {rel}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
