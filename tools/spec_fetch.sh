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
  "usb-core/USB3.2-Rev1.1-2022-06.zip|https://www.usb.org/sites/default/files/usb_32_202206_1.zip"
  "usb-core/USB-PD-3.3-V1.0.zip|https://www.usb.org/sites/default/files/USB_PD_R3.3_V1.0.zip"
  "usb-core/UCSI-3.2.zip|https://usb.org/sites/default/files/USB%20Type-C%20Connector%20System%20Software%20Interface%20Revision_3.2%20OR.zip"
  "usb-core/BC-1.2.zip|https://www.usb.org/sites/default/files/BCv1.2_070312_0.zip"
  "usb-core/eUSB2-PHY-Supplement-1.2.zip|https://www.usb.org/sites/default/files/eUSB2_0_20240927.zip"
  "usb-core/USB-Authentication-1.0-2019.zip|https://www.usb.org/sites/default/files/USB%20Authentication%20Specification%20Rev%201.0%20with%20ECN%20and%20Errata%20through%20January%207%2C%202019.zip"
  "host-controllers/xHCI-1.2.pdf|https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/extensible-host-controler-interface-usb-xhci.pdf"
  "host-controllers/EHCI-1.0.pdf|https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/ehci-specification-for-usb.pdf"
  "usb-core/USB-TypeC-Spec-R2.0.pdf|https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf"
  "usb-core/UCSI-3.1.zip|https://www.usb.org/sites/default/files/USB%20Type-C%20Connector%20System%20Software%20Interface%20UCSI%20Revision_3.1.zip"
  "usb-core/USB-PD-3.2-V1.2.zip|https://www.usb.org/sites/default/files/USB_PD_R3.2_V1.2_2.zip"
  "usb-core/USB2-Electrical-Compliance-v1.08.pdf|https://www.usb.org/sites/default/files/USB2%20Electrical%20Compliance%20Specification%20v1.08.pdf"
  "device-classes/HID-1.11.pdf|https://www.usb.org/sites/default/files/hid1_11.pdf"
  "device-classes/HID-UsageTables-1.3.pdf|https://www.usb.org/sites/default/files/hut1_3_0.pdf"
  "device-classes/HID-UsageTables-1.7.pdf|https://www.usb.org/sites/default/files/hut1_7.pdf"
  "device-classes/HID-PowerDevices-1.1.pdf|https://usb.org/sites/default/files/pdcv11.pdf"
  "device-classes/HID-PID-1.01.pdf|https://www.usb.org/sites/default/files/pid1_01_0.pdf"
  "device-classes/CDC-NCM-1.0.zip|https://www.usb.org/sites/default/files/NCM10_012011.zip"
  "device-classes/CDC-NCM-1.1.zip|https://www.usb.org/sites/default/files/NCM11_20260205.zip"
  "device-classes/CDC-EEM-1.0.pdf|https://usb.org/sites/default/files/CDC_EEM10.pdf"
  "device-classes/CDC-MBIM-1.0-Errata1.zip|https://www.usb.org/sites/default/files/MBIM10Errata1_073013.zip"
  "device-classes/CDC-1.2-WMC-1.1-Errata-2013.zip|https://www.usb.org/sites/default/files/CDC1.2_WMC1.1_052013.zip"
  "device-classes/MSC-Overview-1.4.pdf|https://www.usb.org/sites/default/files/Mass_Storage_Specification_Overview_v1.4_2-19-2010.pdf"
  "device-classes/MSC-Bootability-1.0.pdf|https://www.usb.org/sites/default/files/usb_msc_boot_1.0.pdf"
  "device-classes/UAC-2.0-Errata-2026-09.pdf|https://www.usb.org/sites/default/files/Audio2_with_Errata_and_ECN_through_Sep_14_2026.pdf"
  "device-classes/UAC-3.0.zip|https://www.usb.org/sites/default/files/USB_Audio_v3.0.zip"
  "device-classes/UAC-4.0-current.zip|https://www.usb.org/sites/default/files/USB%20Audio%20v4.0_0_0.zip"
  "device-classes/MIDI-2.0.pdf|https://www.usb.org/sites/default/files/USB%20MIDI%20v2_0.pdf"
  "device-classes/Printer-1.1.pdf|https://www.usb.org/sites/default/files/usbprint11a021811.pdf"
  "device-classes/IPP-USB-1.0.zip|https://www.usb.org/sites/default/files/IPP_0.zip"
  "device-classes/MTP-1.1.zip|https://www.usb.org/sites/default/files/MTPv1_1.zip"
  "device-classes/StillImage-1.0.zip|https://www.usb.org/sites/default/files/usb_still_img10.zip"
  "device-classes/ICCD-1.0.pdf|https://www.usb.org/sites/default/files/DWG_Smart-Card_USB-ICC_ICCD_rev10.pdf"
  "device-classes/I3C-1.1.pdf|https://www.usb.org/sites/default/files/USB%20I3C%20Device%20Class%20Revision%201.1.pdf"
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
  "bluetooth/Bluetooth-Core-7.0.pdf|https://files.bluetooth.com/download/core_v7-0/"
  "bluetooth/HOGP-latest.pdf|https://files.bluetooth.com/download/hid-over-gatt-profile/"
  "bluetooth/BAS-latest.pdf|https://www.bluetooth.org/DocMan/handlers/DownloadDoc.ashx?doc_id=554952"
  "bluetooth/DIS-latest.pdf|https://www.bluetooth.org/DocMan/handlers/DownloadDoc.ashx?doc_id=570273"
  "bluetooth/Assigned_Numbers.pdf|https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/Assigned_Numbers.pdf"
  "bluetooth/HOGP-1.0.pdf|https://www.bluetooth.org/docman/handlers/downloaddoc.ashx?doc_id=245141"
  "bluetooth/Bluetooth-HID-Profile-1.1.1.pdf|https://www.bluetooth.org/docman/handlers/downloaddoc.ashx?doc_id=309012"
  "bluetooth/HID-Service-1.1.pdf|https://files.bluetooth.com/download/hid-service-specification/"
  "bluetooth/HFP-1.10.pdf|https://files.bluetooth.com/download/hfp_v1-10/"
  "MANUAL:bluetooth/AVRCP-1.6.3.pdf|https://www.bluetooth.com/specifications/specs/a-v-remote-control-profile1-6-3/"
  "MANUAL:bluetooth/A2DP-1.4.1.pdf|https://www.bluetooth.com/specifications/specs/a2dp-1-4-1/"
  "bluetooth/AVDTP-1.3.pdf|https://www.bluetooth.org/DocMan/handlers/DownloadDoc.ashx?doc_id=260860"
  "bluetooth/GATT_Specification_Supplement.pdf|https://btprodspecificationrefs.blob.core.windows.net/gatt-specification-supplement/GATT_Specification_Supplement.pdf"
)

ok=0; fail=0; skipped=0; manual_n=0
dl() { curl -fsSL -c /tmp/sf_cj -b /tmp/sf_cj --max-time 900 -o "$2" "$1" 2>/dev/null; }

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
  curl -sL -c /tmp/sf_cj -b /tmp/sf_cj --max-time 60 "$1" -o /tmp/sf_page.html || return 1
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
