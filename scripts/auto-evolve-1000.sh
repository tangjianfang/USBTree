#!/usr/bin/env bash
# auto-evolve-1000.sh —— evolve N=1000 连续运行驱动（无每日时间闸）
# 停止条件（按 1.4.0 协议）: ①达 1000 轮; ②熔断（连续 3 轮无进展）; ③用户 Ctrl+C/删锁。
# 单写者锁: 与 auto-evolve.sh 共用 .auto-evolve.lock——本脚本会等待旧驱动退出后接管。
# 用法: bash scripts/auto-evolve-1000.sh
set -uo pipefail

WORK="C:/tjf/github/usb-labs"
DRIVER_LOG="$WORK/docs/auto-evolve-driver.log"
LOCK="$WORK/.auto-evolve.lock"
MAX=1000

echo "$(date '+%F %T') [1000] 启动：等待旧驱动锁释放（如在运行）…"
for i in $(seq 1 120); do
  [ ! -e "$LOCK" ] && break
  sleep 30
done

# 抢占锁（独占写者）
if [ -e "$LOCK" ]; then echo "$(date '+%F %T') [1000] 锁超时未释放，强制接管" >> "$DRIVER_LOG"; fi
touch "$LOCK"
trap 'rm -f "$LOCK"' EXIT
echo "$(date '+%F %T') [1000] 连续驱动启动（目标 1000 轮；熔断=连续 3 轮无进展）" >> "$DRIVER_LOG"

ROUND_PROMPT='在 C:/tjf/github/usb-labs（工作仓库）执行一轮 evolve 协议（1.4.0）。协议状态必读: C:/tjf/github/USBTree/docs/evolve-log.md（头部 pointer=本轮序号；文内目标池与 Run 2 池说明）与 C:/tjf/github/USBTree/docs/epics.md（EP-4 approved 可实施：切片 S1 通道层/S2 设备发现/S3 会话台/S4 解析面板，设计见 apps/设计-工程师通信控制台.md；EP-1 完成/EP-2 blocked-需人工/EP-3 完成）。流程: (1) 读 pointer 确定本轮序号; (2) 选 1 个目标执行 1~3 个动作; (3) usb-labs 根目录 bash tools/validate.sh 必须 9/9 通过; (4) git commit（不 push）; (5) 向 C:/tjf/github/USBTree/docs/evolve-log.md 底部追加轮次行（#序号 | 目标 | findings | actions | result | diff | 备注）并更新头部 pointer 与 rounds done。纪律: 无实质进展如实记 result(green+no-progress)；连续 3 轮无进展则在日志声明"收敛，停止驱动"；禁止伪造进展、禁止 push、禁止改动 80-参考资料 二进制。视觉review（仅当目标为 UI 且有截图机制时执行，否则跳过）: 子代理指定模型 GLM-5.3-Flash（用户指定，替代协议默认 haiku），返回问题清单后须经复核才动工。所有文件操作用绝对路径。完成后仅输出一行: ROUND <序号> DONE|NOPROGRESS|BLOCKED'

n=0; noprog=0
while [ "$n" -lt "$MAX" ]; do
  n=$((n+1))
  # 教训 L9（旧驱动 01:48 假熔断实证）: 会话输出末行可能是 SessionEnd hook 噪声,
  # tail -1 会抓到噪声而非 ROUND 标记 → 成功轮被误判无进展。改为全量捕获后 grep 标记。
  raw=$(claude -p "$ROUND_PROMPT" --max-turns 60 --dangerously-skip-permissions 2>&1)
  out=$(printf '%s\n' "$raw" | grep -Eo 'ROUND [0-9]+ (DONE|NOPROGRESS|BLOCKED)' | tail -1)
  echo "$(date '+%F %T') [1000-round $n] marker=[${out:-NONE}]" >> "$DRIVER_LOG"
  case "$out" in
    *DONE*) noprog=0 ;;
    *)      noprog=$((noprog+1)) ;;   # NOPROGRESS/BLOCKED/无标记(会话异常)均计入熔断
  esac
  if [ "$noprog" -ge 3 ]; then
    echo "$(date '+%F %T') [1000] 熔断：连续 $noprog 轮无进展，按协议停止（收敛）" >> "$DRIVER_LOG"
    break
  fi
  sleep 15
done

rm -f "$LOCK"
echo "$(date '+%F %T') [1000] 结束：累计派发 $n 轮" >> "$DRIVER_LOG"
