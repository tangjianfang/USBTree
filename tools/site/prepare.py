#!/usr/bin/env python3
"""Stage USBTree content into a MkDocs docs_dir and generate nav.

Usage: python3 tools/site/prepare.py   (run from repo root; see build.sh)

Output (gitignored, rebuildable):
  _site_src/docs/          staged Markdown (links rewritten so they resolve on the site)
  _site_src/mkdocs.gen.yml generated config (INHERITs mkdocs.yml, adds nav)
Raw files (tech-doc/*.html|md, ai-kb/*.md, graph/*) are copied into the built
site by build.sh *after* mkdocs runs, so they are served verbatim.
"""
import os, re, shutil, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "_site_src"
DOCS = OUT / "docs"
GH = "https://github.com/tangjianfang/USBTree"
BRANCH = os.environ.get("USBTREE_BRANCH", "main")

CONTENT_DIRS = sorted(p.name for p in ROOT.iterdir()
                      if p.is_dir() and re.match(r"^\d\d-", p.name))
ROOT_PAGES = ["README.md", "00-知识树总图.md", "COVERAGE.md", "CONTRIBUTING.md"]
EXTRA_DIRS = ["skills", "docs"]           # rendered as pages
SPECIAL_README = ["tech-doc/README.md", "ai-kb/README.md"]  # rendered; siblings served raw
# raw-served prefixes (copied verbatim into site by build.sh)
RAW_PREFIXES = ("tech-doc/", "ai-kb/", "graph/")
RAW_FILES = {"LICENSE"}
RAW_EXCLUDE = ("tech-doc/build/",)

def spec_urls():
    """filename-under-80-参考资料 -> official URL, from tools/spec_fetch.sh."""
    m = {}
    txt = (ROOT / "tools/spec_fetch.sh").read_text(encoding="utf-8")
    for rel, url in re.findall(r'"(?:MANUAL:)?([^"|]+\.(?:pdf|zip|txt))\|(https?://[^"]+)"', txt):
        m["80-参考资料/" + rel] = url
    return m
SPECS = spec_urls()

def title_of(path: Path) -> str:
    t = path.read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if fm:
        mt = re.search(r'^title:\s*"?(.*?)"?\s*$', fm.group(1), re.M)
        if mt:
            return mt.group(1)
        t = t[fm.end():]
    mh = re.search(r"^#\s+(.+)$", t, re.M)
    return mh.group(1).strip() if mh else path.stem

# ---------------------------------------------------------------- staging
staged = {}   # repo-relative md path -> staged-relative md path

def stage(src_rel: str, dst_rel: str = None):
    dst_rel = dst_rel or src_rel
    staged[src_rel] = dst_rel

def collect():
    for p in ROOT_PAGES:
        stage(p, "index.md" if p == "README.md" else p)
    for d in CONTENT_DIRS + EXTRA_DIRS:
        for f in sorted((ROOT / d).rglob("*.md")):
            stage(f.relative_to(ROOT).as_posix())
    for p in SPECIAL_README:
        stage(p, p.replace("README.md", "index.md"))

def is_published_raw(rel: str) -> bool:
    if rel in RAW_FILES:
        return True
    return rel.startswith(RAW_PREFIXES) and not rel.startswith(RAW_EXCLUDE) \
        and (ROOT / rel).is_file()

LINK_RE = re.compile(r"(!?\[[^\]\n]*\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")

def rewrite_target(target: str, src_rel: str, dst_rel: str):
    if re.match(r"^[a-z]+:|^#|^/", target):
        return target
    path, _, frag = target.partition("#")
    frag = ("#" + frag) if frag else ""
    path_dec = urllib.parse.unquote(path)
    base = os.path.dirname(src_rel)
    rel = os.path.normpath(os.path.join(base, path_dec)).replace(os.sep, "/")
    if rel.startswith(".."):
        return target
    abs_src = ROOT / rel
    dst_dir = os.path.dirname(dst_rel)

    def relto(staged_target):
        return os.path.relpath(staged_target, dst_dir or ".").replace(os.sep, "/") + frag

    # 1) a staged page
    if rel in staged:
        return relto(staged[rel])
    # 2) directory link -> its index
    if abs_src.is_dir() or path.endswith("/"):
        for cand in (rel + "/README.md", rel + "/index.md"):
            if cand in staged:
                return relto(staged[cand])
        if rel in dir_index:
            return relto(dir_index[rel])
        return f"{GH}/tree/{BRANCH}/{urllib.parse.quote(rel)}"
    # 3) spec binaries -> official download page
    if rel in SPECS:
        return SPECS[rel]
    if rel.startswith("80-参考资料/") and rel.endswith((".pdf", ".zip", ".txt")):
        return "/80-参考资料/"
    # 4) raw-served files (tech-doc md -> its html twin)
    if rel.startswith("tech-doc/") and rel.endswith(".md") and (ROOT / rel[:-3]).with_suffix(".html").exists():
        return "/" + rel[:-3] + ".html" + frag
    if rel == "LICENSE":
        return "/LICENSE.txt"
    if is_published_raw(rel):
        return "/" + rel + frag
    # 5) anything else in the repo -> GitHub
    if abs_src.exists():
        return f"{GH}/blob/{BRANCH}/{urllib.parse.quote(rel)}{frag}"
    return target  # genuinely broken; left for the link checker to report

dir_index = {}

def write_page(src_rel, dst_rel, text):
    out = DOCS / dst_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    def sub(m):
        return m.group(1) + rewrite_target(m.group(2), src_rel, dst_rel) + m.group(3)
    # don't rewrite inside fenced code blocks
    parts = re.split(r"(^```.*?^```[ \t]*$)", text, flags=re.S | re.M)
    for i in range(0, len(parts), 2):
        parts[i] = LINK_RE.sub(sub, parts[i])
    out.write_text("".join(parts), encoding="utf-8")

def gen_dir_indexes():
    """Every directory without README/index gets a generated index.md."""
    dirs = set()
    for src in staged:
        d = os.path.dirname(src)
        while d:
            dirs.add(d)
            d = os.path.dirname(d)
    for d in sorted(dirs):
        if d + "/README.md" in staged or d + "/index.md" in staged:
            continue
        dir_index[d] = d + "/index.md"
    return dirs

def build_dir_index_text(d):
    name = d.split("/")[-1]
    lines = [f"# {name}", "", f"> 本页由站点构建自动生成，列出 `{d}/` 下的全部内容。", ""]
    subs = sorted({s.split("/")[len(d.split('/'))] for s in staged
                   if s.startswith(d + "/") and s.count("/") > d.count("/") + 1})
    if subs:
        lines += ["## 子目录", ""]
        for s in subs:
            lines.append(f"- [{s}/]({s}/index.md)")
        lines.append("")
    files = sorted(s for s in staged if os.path.dirname(s) == d)
    if files:
        lines += ["## 页面", ""]
        for f in files:
            lines.append(f"- [{title_of(ROOT / f)}]({os.path.basename(staged[f])})")
    return "\n".join(lines) + "\n"

def build_graph_page():
    mmd = (ROOT / "graph/export.mmd").read_text(encoding="utf-8")
    return ("# 知识图谱\n\n"
            "> 由 `graph/entities.yaml` + `graph/relations.yaml` 经 `tools/gen_graph.sh` 生成。"
            "机器可读原文：[entities.yaml](/graph/entities.yaml) · [relations.yaml](/graph/relations.yaml) · "
            "[naming.yaml](/graph/naming.yaml) · [export.mmd](/graph/export.mmd)\n\n"
            "```mermaid\n" + mmd.strip() + "\n```\n")

AI_PAGE = """# 给 AI 的原始文件

站点同时以**原样文本**提供以下文件，方便大模型/检索工具直接抓取（UTF-8 Markdown）：

| 文件 | 说明 |
|---|---|
| [/ai-kb/llms-full.md](/ai-kb/llms-full.md) | ai-kb 全量合并版（单文件） |
| [/ai-kb/index.md](/ai-kb/index.md) | ai-kb 索引（38 个主题文件） |
| [/tech-doc/llms-full.md](/tech-doc/llms-full.md) | tech-doc 13 篇规范可追溯文档合并版 |
| [/llms.txt](/llms.txt) | 站点概要与入口（llms.txt 约定） |
| [/graph/entities.yaml](/graph/entities.yaml) · [/graph/relations.yaml](/graph/relations.yaml) | 知识图谱实体与关系 |

- ai-kb 目录说明：[ai-kb](ai-kb/index.md)
- tech-doc 规范知识库（HTML）：[tech-doc](tech-doc/index.md)
"""

def nav_for_dir(d):
    items = []
    idx = staged.get(d + "/README.md") or dir_index.get(d)
    if idx:
        items.append(idx)
    for f in sorted(s for s in staged if os.path.dirname(s) == d and staged[s] != idx):
        items.append({title_of(ROOT / f): staged[f]})
    subs = sorted({s.split("/")[d.count("/") + 1] for s in staged
                   if s.startswith(d + "/") and s.count("/") > d.count("/") + 1})
    for s in subs:
        items.append({s: nav_for_dir(d + "/" + s)})
    return items

def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

def dump_nav(items, indent=2):
    out = []
    pad = " " * indent
    for it in items:
        if isinstance(it, str):
            out.append(f"{pad}- {q(it)}")
        else:
            (k, v), = it.items()
            if isinstance(v, list):
                out.append(f"{pad}- {q(k)}:")
                out += dump_nav(v, indent + 4)
            else:
                out.append(f"{pad}- {q(k)}: {q(v)}")
    return out

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    DOCS.mkdir(parents=True)
    collect()
    gen_dir_indexes()
    for src, dst in staged.items():
        write_page(src, dst, (ROOT / src).read_text(encoding="utf-8"))
    for d, idx in dir_index.items():
        write_page(idx, idx, build_dir_index_text(d))
    write_page("graph/index.md", "graph/index.md", build_graph_page())
    write_page("for-ai.md", "for-ai.md", AI_PAGE)
    # static assets
    shutil.copytree(ROOT / "tools/site/overrides", OUT / "overrides")
    shutil.copytree(ROOT / "tools/site/assets", DOCS / "assets")

    nav = [{"首页": "index.md"}, {"知识树总图": "00-知识树总图.md"}]
    for d in CONTENT_DIRS:
        nav.append({d: nav_for_dir(d)})
    nav.append({"tech-doc 规范知识库": [{"目录": "tech-doc/index.md"}] +
                [{title_of(ROOT / h.with_suffix('.md')): "/tech-doc/" + h.name}
                 for h in sorted((ROOT / "tech-doc").glob("*.html"))]})
    nav.append({"知识图谱": "graph/index.md"})
    nav.append({"Agent 技能": nav_for_dir("skills")})
    nav.append({"AI 参考": [{"给 AI 的原始文件": "for-ai.md"}, {"ai-kb 说明": "ai-kb/index.md"}]})
    nav.append({"维护记录": nav_for_dir("docs")})
    nav.append({"关于": [{"覆盖率": "COVERAGE.md"}, {"贡献指南": "CONTRIBUTING.md"}]})
    cfg = ["INHERIT: ../mkdocs.yml", "docs_dir: docs", "site_dir: ../_site", "theme:",
           "  name: material", "  custom_dir: overrides", "nav:"] + dump_nav(nav)
    (OUT / "mkdocs.gen.yml").write_text("\n".join(cfg) + "\n", encoding="utf-8")
    print(f"staged {len(staged)} pages + {len(dir_index)} generated indexes -> {DOCS}")

if __name__ == "__main__":
    main()
