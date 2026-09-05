#!/usr/bin/env bash
# USBTree 全库一致性校验：链接 / 代码围栏 / 图谱引用 / frontmatter 覆盖 / 关系边端点 / title≡H1
# 用法: bash tools/validate.sh   （退出码 0 = 全部通过；9 项检查）
set -uo pipefail
cd "$(dirname "$0")/.."
rc=0

echo "== 1/9 Markdown 相对链接 =="
broken=0; specinfo=0
while IFS= read -r f; do
  dir=$(dirname "$f")
  while IFS= read -r link; do
    [ -n "$link" ] || continue
    case "$link" in http*|\#*) continue ;; esac
    if [ ! -e "$dir/$link" ]; then
      case "$dir/$link" in
        *80-参考资料*)
          # 指向本地规范缓存二进制的链接：gitignore 排除属预期，CI 环境用 tools/spec_fetch.sh 重建
          echo "  规范二进制(本地缓存, 可 bash tools/spec_fetch.sh 重建): $link"; specinfo=$((specinfo+1)) ;;
        *) echo "  断链: [$f] -> $link"; broken=$((broken+1)) ;;
      esac
    fi
  done < <(grep -oE '\]\([^)#][^)]*\)' "$f" 2>/dev/null | sed -E 's/^\]\(//; s/\)$//')
done < <(find . -name '*.md' -type f)
[ "$broken" -eq 0 ] && echo "  通过（另有 $specinfo 条规范二进制引用，按预期仅存在于本地缓存）" || rc=1

echo "== 2/8 代码围栏闭合 =="
unbalanced=0
while IFS= read -r f; do
  n=$(grep -c '^```' "$f")
  if [ $((n % 2)) -ne 0 ]; then echo "  未闭合: $f"; unbalanced=$((unbalanced+1)); fi
done < <(find . -name '*.md' -type f)
[ "$unbalanced" -eq 0 ] && echo "  通过" || rc=1

echo "== 3/9 图谱引用完整性（实体 docs 与边 evidence 必须真实存在） =="
badref=0
while IFS= read -r p; do
  [ -n "$p" ] || continue
  if [ ! -e "$p" ]; then echo "  引用不存在: $p"; badref=$((badref+1)); fi
done < <(grep -E '^[[:space:]]*(docs|evidence):' graph/entities.yaml graph/relations.yaml | sed -E 's/^[^:]*:[[:space:]]*//; s/^(docs|evidence):[[:space:]]*//')
[ "$badref" -eq 0 ] && echo "  通过" || rc=1

echo "== 4/9 frontmatter 覆盖（10~90 内容目录） =="
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

echo "== 5/9 关系边端点存在性（relations from/to ⊆ entities id） =="
grep -E '^[[:space:]]*- id:' graph/entities.yaml | sed -E 's/.*- id:[[:space:]]*//' | sort -u > /tmp/usbtree_ids.$$
bad5=0
while IFS= read -r v; do
  [ -n "$v" ] || continue
  if ! grep -qxF "$v" /tmp/usbtree_ids.$$; then
    echo "  端点不在实体表: $v"; bad5=$((bad5+1))
  fi
done < <(grep -E '^[[:space:]]*(from|to):' graph/relations.yaml | sed -E 's/.*:[[:space:]]*//')
rm -f /tmp/usbtree_ids.$$
[ "$bad5" -eq 0 ] && echo "  通过" || rc=1

echo "== 6/9 frontmatter title 与正文 H1 一致 =="
mismatch=0
for d in 10-* 20-* 30-* 40-* 50-* 60-* 70-* 90-*; do
  [ -d "$d" ] || continue
  while IFS= read -r f; do
    fmtitle=$(sed -n '2s/^title: "\(.*\)"$/\1/p' "$f")
    h1=$(grep -m1 '^# ' "$f" | sed 's/^#[[:space:]]*//; s/[[:space:]]*$//')
    if [ "$fmtitle" != "$h1" ]; then
      echo "  title≠H1: $f (fm='$fmtitle' h1='$h1')"; mismatch=$((mismatch+1))
    fi
  done < <(find "$d" -name '*.md' -type f)
done
[ "$mismatch" -eq 0 ] && echo "  通过" || rc=1

echo "== 7/9 graph/export.mmd 新鲜度（与数据源重新生成结果一致） =="
if bash tools/gen_graph.sh /tmp/usbtree_export_check.mmd >/dev/null 2>&1; then
  if diff -q /tmp/usbtree_export_check.mmd graph/export.mmd >/dev/null 2>&1; then
    echo "  通过"; rm -f /tmp/usbtree_export_check.mmd
  else
    echo "  过期：graph/export.mmd 与数据源不一致，请运行 bash tools/gen_graph.sh"; rc=1
  fi
else
  echo "  生成失败"; rc=1
fi

echo "== 8/9 内容文件 H1 标题唯一性 =="
dupfile=$(mktemp)
for d in 10-* 20-* 30-* 40-* 50-* 60-* 70-* 90-*; do
  [ -d "$d" ] || continue
  find "$d" -name '*.md' -type f -exec grep -h -m1 '^# ' {} \;
done | sed 's/^#[[:space:]]*//' | sort | uniq -d > "$dupfile"
if [ -s "$dupfile" ]; then rc=1; else echo "  通过"; fi
rm -f "$dupfile"

echo "== 9/9 命名区块新鲜度（graph/naming.yaml 单一事实源） =="
T90="90-附录/02-速查表大全.md"
cp "$T90" /tmp/naming_before.md 2>/dev/null
if python tools/gen_naming.py >/dev/null 2>&1; then
  if diff -q /tmp/naming_before.md "$T90" >/dev/null 2>&1; then
    echo "  通过"
  else
    echo "  过期：命名区块已按 graph/naming.yaml 自动重写，请提交更新"; rc=1
  fi
  rm -f /tmp/naming_before.md
else
  echo "  gen_naming 执行失败"; rc=1
fi

echo ""
if [ "$rc" -eq 0 ]; then echo "✔ 校验全部通过"; else echo "✘ 存在问题，请修复后重跑"; fi
exit "$rc"
