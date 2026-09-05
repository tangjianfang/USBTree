#!/usr/bin/env bash
# USBTree 全库一致性校验：链接 / 代码围栏 / 图谱引用 / frontmatter 覆盖
# 用法: bash tools/validate.sh   （退出码 0 = 全部通过）
set -uo pipefail
cd "$(dirname "$0")/.."
rc=0

echo "== 1/4 Markdown 相对链接 =="
broken=0
while IFS= read -r f; do
  dir=$(dirname "$f")
  while IFS= read -r link; do
    [ -n "$link" ] || continue
    case "$link" in http*|\#*) continue ;; esac
    if [ ! -e "$dir/$link" ]; then
      echo "  断链: [$f] -> $link"; broken=$((broken+1))
    fi
  done < <(grep -oE '\]\([^)#][^)]*\)' "$f" 2>/dev/null | sed -E 's/^\]\(//; s/\)$//')
done < <(find . -name '*.md' -type f)
[ "$broken" -eq 0 ] && echo "  通过" || rc=1

echo "== 2/4 代码围栏闭合 =="
unbalanced=0
while IFS= read -r f; do
  n=$(grep -c '^```' "$f")
  if [ $((n % 2)) -ne 0 ]; then echo "  未闭合: $f"; unbalanced=$((unbalanced+1)); fi
done < <(find . -name '*.md' -type f)
[ "$unbalanced" -eq 0 ] && echo "  通过" || rc=1

echo "== 3/4 图谱引用完整性（实体 docs 与边 evidence 必须真实存在） =="
badref=0
while IFS= read -r p; do
  [ -n "$p" ] || continue
  if [ ! -e "$p" ]; then echo "  引用不存在: $p"; badref=$((badref+1)); fi
done < <(grep -E '^[[:space:]]*(docs|evidence):' graph/entities.yaml graph/relations.yaml | sed -E 's/^[^:]*:[[:space:]]*//; s/^(docs|evidence):[[:space:]]*//')
[ "$badref" -eq 0 ] && echo "  通过" || rc=1

echo "== 4/4 frontmatter 覆盖（10~90 内容目录） =="
total=0; missing=0
for d in 10-* 20-* 30-* 40-* 50-* 60-* 70-* 90-*; do
  [ -d "$d" ] || continue
  while IFS= read -r f; do
    total=$((total+1))
    if ! head -1 "$f" | grep -q '^---$'; then
      echo "  缺 frontmatter: $f"; missing=$((missing+1))
    fi
  done < <(find "$d" -name '*.md' -type f)
done
echo "  内容文件 $total 篇，缺 frontmatter $missing 篇"
[ "$missing" -eq 0 ] || rc=1

echo ""
if [ "$rc" -eq 0 ]; then echo "✔ 校验全部通过"; else echo "✘ 存在问题，请修复后重跑"; fi
exit "$rc"
