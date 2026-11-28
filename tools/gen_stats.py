#!/usr/bin/env python3
"""从仓库计算篇数、行数、图谱规模、规范清单份数和 validate 检查项数，并核对文档。

用法:
  python3 tools/gen_stats.py           # 打印统计
  python3 tools/gen_stats.py --check   # 文档与统计不一致时退出码 1
"""
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
# 只统计知识树正文。ai-kb/ 与 tech-doc/ 是派生产物，不在 CONTENT_TOP 里，不计入篇数与行数。
CONTENT_TOP = ("10-", "20-", "30-", "40-", "50-", "60-", "65-", "70-", "78-", "90-")
STATS_FILES = ("README.md", "COVERAGE.md", "00-知识树总图.md")


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def content_files():
    files = []
    for p in ROOT.iterdir():
        if p.is_dir() and p.name.startswith(CONTENT_TOP):
            files.extend(sorted(x for x in p.rglob("*.md") if x.is_file()))
    return files


def manifest_count() -> int:
    text = read("tools/spec_fetch.sh")
    m = re.search(r"MANIFEST=\((.*?)\)\n", text, re.S)
    if not m:
        sys.exit("spec_fetch.sh 中找不到 MANIFEST")
    return len(re.findall(r'^\s*"(?:MANUAL:)?[^"]+\|https?://', m.group(1), re.M))


def yaml_ids(rel: str) -> int:
    return len(re.findall(r"(?m)^[ ]*- id:", read(rel)))


def check_headers():
    text = read("tools/validate.sh")
    return re.findall(r'(?m)^echo "== (\d+)/(\d+) ', text)


def stats() -> dict:
    files = content_files()
    lines = 0
    for f in files:
        with f.open(encoding="utf-8", errors="replace") as fh:
            lines += sum(1 for _ in fh)
    headers = check_headers()
    return {
        "articles": len(files),
        "lines": lines,
        "entities": yaml_ids("graph/entities.yaml"),
        "edges": yaml_ids("graph/relations.yaml"),
        "specs": manifest_count(),
        "checks": len(headers),
        "headers": headers,
    }


def comment(s: dict) -> str:
    return (
        "<!-- usbtree-stats: "
        f"articles={s['articles']} lines={s['lines']} entities={s['entities']} "
        f"edges={s['edges']} specs={s['specs']} checks={s['checks']} -->"
    )


def badge_url(s: dict) -> str:
    label = quote(f"内容-{s['articles']} 篇·{s['lines']}行", safe="")
    return f"https://img.shields.io/badge/{label}-blue"


def expect(s: dict):
    a, n, e, g, spec, c = (
        s["articles"], s["lines"], s["entities"], s["edges"], s["specs"], s["checks"]
    )
    must = [
        ("README.md", comment(s)),
        ("README.md", badge_url(s)),
        ("README.md", f"({a} in-depth articles"),
        ("README.md", f"({e} entities / {g} relations)"),
        ("README.md", f"{spec} cached official specifications"),
        ("README.md", f"USB 核心协议（13 篇）"),
        ("README.md", "(9 篇 + 00-索引"),
        ("README.md", "DROM/CM指南"),
        ("README.md", "(17 篇:"),
        ("README.md", "标准UUID全表"),
        ("README.md", "(5 篇 + 00-索引"),
        ("README.md", f"官方规范原文缓存: {spec} 份"),
        ("README.md", f"{e} 个实体"),
        ("README.md", f"{g} 条类型化关系边"),
        ("README.md", f"{c} 项检查"),
        ("README.md", "docs/"),
        ("README.md", "scripts/"),
        ("README.md", "naming.yaml"),
        ("README.md", "gen_naming.py"),
        ("README.md", "spec_fetch.sh"),
        ("COVERAGE.md", comment(s)),
        ("COVERAGE.md", f"{e} 实体/{g} 边"),
        ("COVERAGE.md", f"{spec} 份（与 tools/spec_fetch.sh 清单一致"),
        ("COVERAGE.md", "高速演进 9 篇"),
        ("COVERAGE.md", "BLE 17 篇"),
        ("00-知识树总图.md", comment(s)),
        ("00-知识树总图.md", f"{e} 实体/{g} 边"),
        ("00-知识树总图.md", f"实体表 {e} 节点"),
        ("00-知识树总图.md", f"关系表 {g} 边"),
        ("00-知识树总图.md", f"官方规范 {spec} 份"),
        ("00-知识树总图.md", "USB4 DROM"),
        ("00-知识树总图.md", "USB4 CM 指南"),
        ("00-知识树总图.md", "标准 UUID 全表"),
        ("CONTRIBUTING.md", f"{c}/{c} 通过"),
        ("CONTRIBUTING.md", f"{c} 项检查"),
        (".github/PULL_REQUEST_TEMPLATE.md", f"{c}/{c} 通过"),
    ]
    forbid = [
        ("README.md", "117"),
        ("README.md", "（12 篇）"),
        ("README.md", "86 个实体"),
        ("README.md", "四项检查"),
        ("README.md", "36 份"),
        ("COVERAGE.md", "80 实体/76 边"),
        ("COVERAGE.md", "272M"),
        ("COVERAGE.md", "37 份"),
        ("00-知识树总图.md", "80 实体/76 边"),
        ("00-知识树总图.md", "36 份"),
        ("CONTRIBUTING.md", "8/8"),
        (".github/PULL_REQUEST_TEMPLATE.md", "8/8"),
    ]
    return must, forbid


def check_validate_headers(s: dict, problems: list):
    headers = s["headers"]
    c = s["checks"]
    if not headers:
        problems.append("tools/validate.sh 没有 == N/M 检查标题")
        return
    for i, (num, den) in enumerate(headers, 1):
        if int(num) != i or int(den) != c:
            problems.append(
                f"tools/validate.sh 检查标题 {num}/{den} 与实际第 {i} 项、共 {c} 项不一致"
            )


def check_evolve(s: dict, problems: list):
    for line in read("docs/evolve-log.md").splitlines():
        if line.startswith("- verify:"):
            token = f"{s['checks']}/{s['checks']}"
            if token not in line:
                problems.append(f"docs/evolve-log.md 开头 verify 行应包含 {token}: {line}")
            return
    problems.append("docs/evolve-log.md 缺少 - verify: 行")


def main(argv) -> int:
    s = stats()
    if "--check" not in argv:
        print(comment(s))
        print("badge:", badge_url(s))
        for k in ("articles", "lines", "entities", "edges", "specs", "checks"):
            print(f"{k}={s[k]}")
        return 0
    problems = []
    must, forbid = expect(s)
    cache = {}
    for rel, needle in must:
        cache.setdefault(rel, read(rel))
        if needle not in cache[rel]:
            problems.append(f"缺少 [{rel}] {needle}")
    for rel, needle in forbid:
        cache.setdefault(rel, read(rel))
        if needle in cache[rel]:
            problems.append(f"仍含过期表述 [{rel}] {needle}")
    # 9 篇 + 索引 同时出现在 30/40/60，缺一则计数不足
    if cache["README.md"].count("(9 篇 + 00-索引") < 3:
        problems.append("README 目录树里「(9 篇 + 00-索引」应至少出现 3 次（30/40/60）")
    check_validate_headers(s, problems)
    check_evolve(s, problems)
    if problems:
        print("  统计与文档不一致:")
        for p in problems:
            print(f"    {p}")
        print("  当前统计:", comment(s))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
