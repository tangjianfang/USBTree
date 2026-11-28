#!/usr/bin/env bash
# 重生成 tech-doc/ 的 07–12（Markdown + HTML）。前置条件见同目录 README.md。
set -eu
BUILD="$(cd "$(dirname "$0")" && pwd)"
DOC="$(cd "$BUILD/.." && pwd)"
SKILL="${TECH_DOC_SKILL:-}"
if [ -z "$SKILL" ] || [ ! -f "$SKILL/scripts/check_doc.py" ] || [ ! -f "$SKILL/scripts/mermaid-tools/export_html.mjs" ]; then
  echo "需要 tech-doc 技能：https://github.com/tangjianfang/tech-doc" >&2
  echo "克隆后执行：export TECH_DOC_SKILL=/path/to/tech-doc" >&2
  echo "该目录下要有 scripts/check_doc.py 与 scripts/mermaid-tools/export_html.mjs。" >&2
  exit 1
fi
SRC="${USB_OS_KB:-$BUILD/os-kb}"
if [ ! -f "$SRC/01-linux.md" ]; then
  echo "需要 07–12 的源笔记目录（不在本仓库内）。" >&2
  echo "export USB_OS_KB=/path/to/dir   # 内含 01-linux.md … 06-cross-platform-comparison.md" >&2
  exit 1
fi
export USB_OS_KB="$SRC"
cd "$BUILD"
python3 run.py
cd "$DOC"
S="$SKILL/scripts"
for f in 0[7-9]*.md 1*.md; do
  python3 -I "$S/check_doc.py" "$f" --fix-style 2>&1 | grep "WARN\|ERROR\|total" | sed "s|^|$f: |" | cut -c1-200
done
rm -f ./*.bak
for f in 0[7-9]*.md 1*.md; do
  node "$S/mermaid-tools/export_html.mjs" "$f" | tail -1
done
python3 "$BUILD/relink_html.py"
