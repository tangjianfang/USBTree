#!/usr/bin/env bash
# spec_extract.sh —— 从本地缓存的官方规范（PDF/ZIP）提取文本并检索
# 结晶自 docs/lessons.md L1/L2/L3/L7（"一切规范数值以缓存 PDF 提取为准"主题）
# 用法: bash tools/spec_extract.sh 80-参考资料/usb-core/USB3.2-Specification-2018.zip "header packet"
#       bash tools/spec_extract.sh 80-参考资料/device-classes/HID-1.11.pdf          # 仅提取
# 说明: 自动解压 zip（取最大的 PDF 为主规范）、-layout 提取、grep -a 输出前 20 条命中。
#       文本缓存于 /tmp/<文件名>.txt，重复调用秒回。
set -uo pipefail
f="${1:?用法: spec_extract.sh <规范.pdf|.zip> [检索词]}"
q="${2:-}"
base=$(basename "$f"); name="${base%.*}"
out="/tmp/spec_extract_${name}.txt"
case "$f" in
  *.zip)
    d="/tmp/spec_extract_${name}_unpacked"
    if [ ! -d "$d" ]; then
      python -m zipfile -e "$f" "$d" 2>/dev/null || unzip -oq "$f" -d "$d"
    fi
    pdf=$(find "$d" -name "*.pdf" -size +2M | head -1)
    [ -z "${pdf:-}" ] && pdf=$(find "$d" -name "*.pdf" | head -1)
    [ -z "${pdf:-}" ] && { echo "zip 内未找到 PDF: $f" >&2; exit 1; }
    echo "主 PDF: $(basename "$pdf")" >&2
    pdftotext -layout "$pdf" "$out"
    ;;
  *.pdf)
    pdftotext -layout "$f" "$out"
    ;;
  *) echo "不支持的类型: $f" >&2; exit 1 ;;
esac
echo "文本就绪: $out（$(wc -l < "$out") 行）"
if [ -n "$q" ]; then
  grep -ain "$q" "$out" | head -20
fi
