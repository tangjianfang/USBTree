#!/usr/bin/env python3
"""把 tech-doc HTML 阅读版里的同库文档链接从 .md 改成 .html。

tech-doc 技能的 export_html 按 Markdown 链接写出 href。人在浏览器里打开的是
HTML，站内链接应指向同名 .html。本脚本只改 href 与链接文字都是「文件名.md」
的锚点，不改代码示例、页脚「导出自 …md」和 Markdown 源。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.environ.get("TECH_DOC_OUT") or os.path.dirname(HERE)
PAT = re.compile(
    r'href="((?:0\d|1[0-2])-[A-Za-z0-9._-]+\.md)(#[^"]*)?">\1</a>'
)
LEFTOVER = re.compile(r"""href=["'][^"']+\.md["']""")


def repl(m):
    html = m.group(1)[:-3] + ".html"
    frag = m.group(2) or ""
    return f'href="{html}{frag}">{html}</a>'


def main():
    nfiles = 0
    nlinks = 0
    for name in sorted(os.listdir(DOC)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(DOC, name)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        new, k = PAT.subn(repl, text)
        left = LEFTOVER.findall(new)
        if left:
            print(f"仍有指向 .md 的 HTML 链接: {name} {left}", file=sys.stderr)
            return 1
        if k:
            open(path, "w", encoding="utf-8").write(new)
            nfiles += 1
            nlinks += k
    print(f"relink: {nlinks} links in {nfiles} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
