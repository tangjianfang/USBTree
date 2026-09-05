#!/usr/bin/env bash
# 从 graph/relations.yaml + graph/entities.yaml 生成 graph/export.mmd（Mermaid 全景关系图）
# 用法: bash tools/gen_graph.sh
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=graph/export.mmd

{
  echo "%% 由 tools/gen_graph.sh 自动生成，勿手改；数据源: graph/entities.yaml + graph/relations.yaml"
  echo "graph LR"
  # 节点声明: id["中文名 (编码)"]
  awk '
    /^[[:space:]]*- id:/ { if (id != "") print_node(); id=$0; sub(/.*- id:[[:space:]]*/, "", id); sub(/[[:space:]]+$/, "", id); name=""; code="" }
    /^[[:space:]]*name:/ { name=$0; sub(/.*name:[[:space:]]*/, "", name) }
    /^[[:space:]]*code:/ { code=$0; sub(/.*code:[[:space:]]*/, "", code) }
    function print_node() {
      label = name
      if (code != "") label = label " (" code ")"
      gsub(/"/, "", label)
      printf "    %s[\"%s\"]\n", id, label
    }
    END { if (id != "") print_node() }
  ' graph/entities.yaml
  # 边: from -- "type: note" --> to
  awk '
    /^[[:space:]]*- id:/ { flush() }
    /^[[:space:]]*from:/ { from=$0; sub(/.*from:[[:space:]]*/, "", from) }
    /^[[:space:]]*type:/ { t=$0; sub(/.*type:[[:space:]]*/, "", t) }
    /^[[:space:]]*to:/ { to=$0; sub(/.*to:[[:space:]]*/, "", to) }
    /^[[:space:]]*note:/ { note=$0; sub(/.*note:[[:space:]]*/, "", note) }
    function flush() {
      if (from != "" && to != "" && t != "") {
        label = t
        if (note != "") label = label ": " note
        gsub(/"/, "", label)
        printf "    %s -->|%s| %s\n", from, label, to
      }
      from = to = t = note = ""
    }
    END { flush() }
  ' graph/relations.yaml
} > "$OUT"

edges=$(grep -c -- '-->|\||-->' "$OUT" 2>/dev/null || grep -c -- '|' "$OUT")
echo "已生成 $OUT（节点 $(grep -c '\["' "$OUT") 个，边 $(grep -c -- '-->|' "$OUT") 条）"
