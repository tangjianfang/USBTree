#!/usr/bin/env bash
# USBTree 全库一致性校验：链接 / 代码围栏 / 图谱引用 / frontmatter 覆盖 / 关系边端点 /
# title≡H1 / 导出新鲜度 / H1 唯一 / 命名区块 / 孤页可达 / 统计数字
# 用法: bash tools/validate.sh   （退出码 0 = 全部通过）
# ai-kb/ 与 tech-doc/ 是派生产物，不参与内容页检查与篇数统计（见 check_orphans.py、gen_stats.py）。
# site/ 是静态站点工程（Astro Starlight，正文在构建时从仓库生成，含 node_modules），不参与任何检查。
# ai-kb/ 沿用原规则，不参与链接与围栏检查。tech-doc/ 的 Markdown 参与这两项；
# 其 HTML 阅读版在第 1 项里检查站内链接（.html → .html）。
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
rc=0

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  PY=""
fi

echo "== 1/11 Markdown 相对链接 =="
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
done < <(find . -name '*.md' -type f -not -path './ai-kb/*' -not -path './site/*')
# tech-doc HTML：跳过 http/锚点；相对链接必须存在，且不得指向 .md（阅读版链到 .html）。
if [ -d ./tech-doc ]; then
  while IFS= read -r f; do
    dir=$(dirname "$f")
    while IFS= read -r link; do
      [ -n "$link" ] || continue
      case "$link" in
        http://*|https://*|mailto:*|data:*|\#*) continue ;;
      esac
      path="${link%%#*}"
      path="${path%%\?*}"
      [ -n "$path" ] || continue
      case "$path" in
        *.md)
          echo "  HTML 链接应指向 .html: [$f] -> $link"; broken=$((broken+1)); continue ;;
      esac
      if [ ! -e "$dir/$path" ]; then
        echo "  断链: [$f] -> $link"; broken=$((broken+1))
      fi
    done < <(grep -oE 'href="[^"]*"' "$f" 2>/dev/null | sed -E 's/^href="//; s/"$//')
  done < <(find ./tech-doc -name '*.html' -type f)
fi
[ "$broken" -eq 0 ] && echo "  通过（另有 $specinfo 条规范二进制引用，按预期仅存在于本地缓存）" || rc=1

echo "== 2/11 代码围栏闭合 =="
unbalanced=0
while IFS= read -r f; do
  n=$(grep -c '^```' "$f")
  if [ $((n % 2)) -ne 0 ]; then echo "  未闭合: $f"; unbalanced=$((unbalanced+1)); fi
done < <(find . -name '*.md' -type f -not -path './ai-kb/*' -not -path './site/*')
[ "$unbalanced" -eq 0 ] && echo "  通过" || rc=1

echo "== 3/11 图谱引用完整性（实体 docs 与边 evidence 必须真实存在） =="
badref=0
while IFS= read -r p; do
  [ -n "$p" ] || continue
  if [ ! -e "$p" ]; then echo "  引用不存在: $p"; badref=$((badref+1)); fi
done < <(grep -E '^[[:space:]]*(docs|evidence):' graph/entities.yaml graph/relations.yaml | sed -E 's/^[^:]*:[[:space:]]*//; s/^(docs|evidence):[[:space:]]*//')
[ "$badref" -eq 0 ] && echo "  通过" || rc=1

echo "== 4/11 frontmatter 覆盖（10~90 内容目录） =="
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

echo "== 5/11 关系边端点存在性（relations from/to ⊆ entities id） =="
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

echo "== 6/11 frontmatter title 与正文 H1 一致 =="
mismatch=0
for d in 10-* 20-* 30-* 40-* 50-* 60-* 70-* 90-*; do
  [ -d "$d" ] || continue
  while IFS= read -r f; do
    fmtitle=$(awk '
      NR==1 { if ($0 != "---") exit }
      NR>1 && $0 == "---" { exit }
      $0 ~ /^title:/ {
        sub(/^title:[[:space:]]*/, "")
        if (sub(/^"/, "")) sub(/"$/, "")
        print
        exit
      }
    ' "$f")
    h1=$(grep -m1 '^# ' "$f" | sed 's/^#[[:space:]]*//; s/[[:space:]]*$//')
    if [ "$fmtitle" != "$h1" ]; then
      echo "  title≠H1: $f (fm='$fmtitle' h1='$h1')"; mismatch=$((mismatch+1))
    fi
  done < <(find "$d" -name '*.md' -type f)
done
[ "$mismatch" -eq 0 ] && echo "  通过" || rc=1

echo "== 7/11 graph/export.mmd 新鲜度（与数据源重新生成结果一致） =="
if bash tools/gen_graph.sh /tmp/usbtree_export_check.mmd >/dev/null 2>&1; then
  if diff -q /tmp/usbtree_export_check.mmd graph/export.mmd >/dev/null 2>&1; then
    echo "  通过"; rm -f /tmp/usbtree_export_check.mmd
  else
    echo "  过期：graph/export.mmd 与数据源不一致，请运行 bash tools/gen_graph.sh"; rc=1
  fi
else
  echo "  生成失败"; rc=1
fi

echo "== 8/11 内容文件 H1 标题唯一性 =="
list=$(mktemp)
dups=$(mktemp)
for d in 10-* 20-* 30-* 40-* 50-* 60-* 70-* 90-*; do
  [ -d "$d" ] || continue
  while IFS= read -r f; do
    h1=$(grep -m1 '^# ' "$f" | sed 's/^#[[:space:]]*//; s/[[:space:]]*$//')
    printf '%s\t%s\n' "$h1" "$f"
  done < <(find "$d" -name '*.md' -type f)
done > "$list"
cut -f1 "$list" | sort | uniq -d > "$dups"
if [ -s "$dups" ]; then
  rc=1
  while IFS= read -r t; do
    echo "  重复标题: $t"
    awk -F '\t' -v t="$t" '$1==t {print "    "$2}' "$list"
  done < "$dups"
else
  echo "  通过"
fi
rm -f "$list" "$dups"

echo "== 9/11 命名区块新鲜度（graph/naming.yaml 单一事实源，只读比对） =="
T90="90-附录/02-速查表大全.md"
naming_out=$(mktemp)
naming_err=$(mktemp)
if [ -z "$PY" ]; then
  echo "  未找到 python3 或 python"; rc=1
elif "$PY" tools/gen_naming.py --stdout > "$naming_out" 2>"$naming_err"; then
  if diff -q "$naming_out" "$T90" >/dev/null 2>&1; then
    echo "  通过"
  else
    echo "  过期：命名区块与 graph/naming.yaml 不一致，请运行 $PY tools/gen_naming.py 后提交"; rc=1
  fi
else
  echo "  gen_naming 执行失败"; cat "$naming_err"; rc=1
fi
rm -f "$naming_out" "$naming_err"

echo "== 10/11 孤页与入口可达性 =="
if [ -z "$PY" ]; then
  echo "  未找到 python3 或 python"; rc=1
elif "$PY" tools/check_orphans.py; then
  echo "  通过"
else
  rc=1
fi

echo "== 11/11 文档统计与仓库一致（篇数/图谱/清单/检查项） =="
if [ -z "$PY" ]; then
  echo "  未找到 python3 或 python"; rc=1
elif "$PY" tools/gen_stats.py --check; then
  echo "  通过"
else
  rc=1
fi

echo ""
if [ "$rc" -eq 0 ]; then echo "✔ 校验全部通过"; else echo "✘ 存在问题，请修复后重跑"; fi
exit "$rc"
