#!/usr/bin/env bash
# 为 10~90 内容目录的 Markdown 注入最小 frontmatter（title/layer/section/doc-path）
# 幂等：已带 frontmatter（首行为 ---）的文件自动跳过
# 用法: bash tools/inject_frontmatter.sh
set -uo pipefail
cd "$(dirname "$0")/.."

layer_of() {
  case "$1" in
    10-*) echo "树干" ;;
    20-*) echo "枝干/设备类协议" ;;
    30-*) echo "枝干/接口与供电" ;;
    40-*) echo "枝干/高速演进" ;;
    50-*) echo "枝干/无线关联" ;;
    60-*) echo "枝干/主机侧与实现" ;;
    70-*) echo "枝干/调试测试与安全" ;;
    90-*) echo "附录" ;;
    *) echo "" ;;
  esac
}

injected=0; skipped=0
while IFS= read -r f; do
  if head -1 "$f" | grep -q '^---$'; then
    skipped=$((skipped+1)); continue
  fi
  title=$(head -1 "$f" | sed -E 's/^#[[:space:]]*//; s/"/\\"/g; s/[[:space:]]+$//')
  d=${f%%/*}
  layer=$(layer_of "$d")
  rest="${f#*/}"
  section=""
  case "$rest" in */*) section="${rest%/*}" ;; esac
  tmp="$f.fm.tmp"
  {
    echo "---"
    echo "title: \"$title\""
    echo "layer: $layer"
    [ -n "$section" ] && echo "section: $section"
    echo "doc-path: $f"
    echo "---"
    cat "$f"
  } > "$tmp" && mv "$tmp" "$f"
  injected=$((injected+1))
done < <(find 10-* 20-* 30-* 40-* 50-* 60-* 70-* 90-* -name '*.md' -type f 2>/dev/null | sort)

echo "frontmatter 注入完成：新注入 $injected 篇，跳过（已有） $skipped 篇"
