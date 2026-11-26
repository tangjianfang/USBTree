#!/usr/bin/env bash
# spec_fetch.sh —— 依据内置清单重建 80-参考资料/ 规范缓存
# 注意：USB-IF / Bluetooth SIG 规范按各自许可分发，下载后请遵守附带条款；
#       本脚本仅做"直链下载"，不破解任何访问限制（files.bluetooth.com 走官方中转页 nonce 流程）。
# 下载结果必须是真 PDF（魔数 %PDF）或 ZIP（魔数 PK）。登录页/中转 HTML 一律判失败并删除，
# 不把网页留成假 PDF（docs/lessons.md L7）。MANUAL: 条目不创建目录、不发请求，只打印手工步骤。
# 用法: bash tools/spec_fetch.sh            # 下载全部
#       bash tools/spec_fetch.sh HID-1.11   # 只下载名称含 HID-1.11 的条目
# 退出码: 有下载失败为 1；仅剩 MANUAL 缺口时为 0（缺口已在日志中单独列出）。
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="80-参考资料"
filter="${1:-}"

# 清单: 目标路径|URL
# MANUAL: 前缀表示没有可用的公开直链，需浏览器登录/点选后按目标路径保存。
MANIFEST=(
  "usb-core/USB2.0-Specification.zip|https://www.usb.org/sites/default/files/usb_20_20250603.zip"
  "usb-core/USB3.2-Specification-2018.zip|https://www.usb.org/sites/default/files/documents/usb_32_20180912.zip"
  "usb-core/USB4-Specification-v2-2025-11.zip|https://www.usb.org/sites/default/files/USB4%20Specification%20November%202025.zip"
  "usb-core/USB-TypeC-Spec-2.5-2026.zip|https://www.usb.org/sites/default/files/USB%20Type-C%202.5%20Release%20202603.zip"
  "usb-core/USB-TypeC-Spec-R2.0.pdf|https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf"
  "usb-core/UCSI-3.1.zip|https://www.usb.org/sites/default/files/USB%20Type-C%20Connector%20System%20Software%20Interface%20UCSI%20Revision_3.1.zip"
  "usb-core/USB-PD-3.2-V1.2.zip|https://www.usb.org/sites/default/files/USB_PD_R3.2_V1.2_2.zip"
  "usb-core/USB2-Electrical-Compliance-v1.08.pdf|https://www.usb.org/sites/default/files/USB2%20Electrical%20Compliance%20Specification%20v1.08.pdf"
  "device-classes/HID-1.11.pdf|https://www.usb.org/sites/default/files/hid1_11.pdf"
  "device-classes/HID-UsageTables-1.3.pdf|https://www.usb.org/sites/default/files/hut1_3_0.pdf"
  "device-classes/CDC-1.2.zip|https://www.usb.org/sites/default/files/CDC1.2_WMC1.1_012011_0.zip"
  "device-classes/MSC-BOT-1.0.pdf|https://www.usb.org/sites/default/files/usbmassbulk_10.pdf"
  "device-classes/MSC-UFI-1.0.pdf|https://www.usb.org/sites/default/files/usbmass-ufi10.pdf"
  "device-classes/UASP-1.0.zip|https://www.usb.org/sites/default/files/uasp_1_0.zip"
  "device-classes/UAC-1.0.pdf|https://www.usb.org/sites/default/files/audio10.pdf"
  "device-classes/UAC-1.0-Formats.pdf|https://www.usb.org/sites/default/files/frmts10.pdf"
  "device-classes/UAC-1.0-Terminals.pdf|https://www.usb.org/sites/default/files/termt10.pdf"
  "device-classes/UAC-2.0-final.zip|https://www.usb.org/sites/default/files/Audio2.0_final.zip"
  "device-classes/UAC-2.0-Errata-2025.pdf|https://www.usb.org/sites/default/files/Audio2_with_Errata_and_ECN_through_Apr_2_2025.pdf"
  "device-classes/UAC-4.0.zip|https://www.usb.org/sites/default/files/USB%20Audio%20v4.0_0.zip"
  "device-classes/UVC-1.5.zip|https://www.usb.org/sites/default/files/USB_Video_Class_1_5.zip"
  "device-classes/DFU-1.1.pdf|https://www.usb.org/sites/default/files/DFU_1.1.pdf"
  "device-classes/CCID-1.1.pdf|https://www.usb.org/sites/default/files/DWG_Smart-Card_CCID_Rev110.pdf"
  "device-classes/USBTMC-USB488-1.0.zip|https://www.usb.org/sites/default/files/USBTMC_1_006a.zip"
  "device-classes/Billboard-1.2.2.zip|https://www.usb.org/sites/default/files/USB%20Billboard%20Rev%201.2.2%2020210209.zip"
  "device-classes/AV-1.0.zip|https://www.usb.org/sites/default/files/USB_AV_Specification_Rev_1.0.zip"
  "device-classes/AV-BDP-1.0.pdf|https://www.usb.org/sites/default/files/AV_BDP_v1.0.pdf"
  "device-classes/PHDC-1.0.zip|https://www.usb.org/sites/default/files/Personal_Healthcare_1.zip"
  "bluetooth/Bluetooth-Core-6.0.pdf|https://www.bluetooth.org/DocMan/handlers/DownloadDoc.ashx?doc_id=588232"
  "MANUAL:bluetooth/Bluetooth-Core-6.0-Errata-List.pdf|https://www.bluetooth.com/specifications/specs/core-specification-6-0/"
  "bluetooth/HOGP-1.0.pdf|https://www.bluetooth.org/docman/handlers/downloaddoc.ashx?doc_id=245141"
  "bluetooth/Bluetooth-HID-Profile-1.1.1.pdf|https://www.bluetooth.org/docman/handlers/downloaddoc.ashx?doc_id=309012"
  "bluetooth/HID-Service-1.1.pdf|https://files.bluetooth.com/download/hid-service-specification/"
  "bluetooth/HFP-1.10.pdf|https://files.bluetooth.com/download/hfp_v1-10/"
  "bluetooth/AVRCP-1.6.3.pdf|https://files.bluetooth.com/download/avrcp_v1-6-3/"
  "MANUAL:bluetooth/A2DP-1.4.1.pdf|https://www.bluetooth.com/specifications/specs/a2dp-1-4-1/"
  "bluetooth/AVDTP-1.3.pdf|https://www.bluetooth.org/DocMan/handlers/DownloadDoc.ashx?doc_id=260860"
  "bluetooth/GATT_Specification_Supplement.pdf|https://btprodspecificationrefs.blob.core.windows.net/gatt-specification-supplement/GATT_Specification_Supplement.pdf"
)

ok=0; fail=0; skipped=0; manual_n=0
dl() { curl -fsSL --max-time 600 -o "$2" "$1" 2>/dev/null; }

# PDF 以 %PDF 开头，ZIP 以 PK 开头。HTML 登录页/中转页两者都不是。
magic_ok() {
  local f="$1" sig
  [ -s "$f" ] || return 1
  sig=$(head -c 5 "$f" 2>/dev/null || true)
  case "${f##*.}" in
    pdf|PDF) [[ "$sig" == %PDF* ]] ;;
    zip|ZIP) [[ "$sig" == PK* ]] ;;
    *) return 1 ;;
  esac
}

fail_kind() {
  local f="$1" b
  [ -s "$f" ] || { echo "空文件"; return; }
  b=$(head -c 256 "$f" 2>/dev/null || true)
  case "$b" in
    *"<html"*|*"<HTML"*|*"<!DOCTYPE"*|*"<!doctype"*|*"<head"*|*"<HEAD"* ) echo "HTML页面" ;;
    *) echo "魔数不符" ;;
  esac
}

files_nonce() { # files.bluetooth.com 中转页 → 带 nonce 的直链（lessons L7）
  curl -sL --max-time 60 "$1" -o /tmp/sf_page.html || return 1
  grep -oE 'href="https://files\.bluetooth\.com/download/[^"]*dlm-dp-dl-force[^"]*"' /tmp/sf_page.html |
    head -1 | sed 's/^href="//; s/"$//; s/&#038;/\&/g'
}

for line in "${MANIFEST[@]}"; do
  raw="${line%%|*}"; url="${line#*|}"
  manual=0
  dest="$raw"
  if [[ "$dest" == MANUAL:* ]]; then
    manual=1
    dest="${dest#MANUAL:}"
  fi
  [ -n "$filter" ] && [[ "$dest" != *"$filter"* ]] && { skipped=$((skipped+1)); continue; }
  target="$ROOT/$dest"
  if [ -e "$target" ] && magic_ok "$target"; then
    echo "SKIP(已有)  $dest"; skipped=$((skipped+1)); continue
  fi
  if [ -e "$target" ]; then
    echo "DROP($(fail_kind "$target")) $dest"
    rm -f "$target"
  fi
  if [ "$manual" -eq 1 ]; then
    echo "MANUAL      $dest"
    echo "            请用浏览器打开下面的页面，下载后保存为 $target"
    echo "            必须是真 PDF/ZIP（文件头 %PDF 或 PK），不要把登录页另存成假 PDF"
    echo "            $url"
    manual_n=$((manual_n+1))
    continue
  fi
  mkdir -p "$(dirname "$target")" || exit 1
  got=0
  case "$url" in
    https://files.bluetooth.com/*)
      u=$(files_nonce "$url") || u=""
      if [ -z "$u" ]; then
        rm -f "$target"
        echo "FAIL(取直链) $dest"
        fail=$((fail+1))
        continue
      fi
      dl "$u" "$target" && got=1
      ;;
    *) dl "$url" "$target" && got=1 ;;
  esac
  if [ "$got" -eq 1 ] && magic_ok "$target"; then
    printf "PASS %8s  %s\n" "$(du -h "$target" | cut -f1)" "$dest"
    ok=$((ok+1))
  else
    kind="下载失败"
    [ -e "$target" ] && kind=$(fail_kind "$target")
    rm -f "$target"
    echo "FAIL($kind) $dest"
    fail=$((fail+1))
  fi
done

echo ""
echo "完成：成功 $ok / 失败 $fail / 跳过 $skipped / 需手工 $manual_n"
[ "$fail" -eq 0 ] && echo "提示：下载后可用 bash tools/spec_extract.sh <文件> 检索规范文本"
[ "$manual_n" -gt 0 ] && echo "提示：MANUAL 条目未自动下载，按上面的路径手工放入后再跑本脚本会 SKIP(已有)"
if [ "$fail" -ne 0 ]; then
  exit 1
fi
exit 0
