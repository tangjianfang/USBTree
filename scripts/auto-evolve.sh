#!/usr/bin/env bash
# auto-evolve.sh —— evolve 1.4.0 自主模式驱动（过夜运行）
# 每次派发一个 headless claude 会话执行一轮；单写者原则：启动后请勿手动改动工作树。
# 时间闸: 07:45 后停止派发新会话（08:00 由收尾任务接管）。
# 熔断: 连续 3 轮 green+no-progress → 停止（收敛判定，不硬凑轮数）。
# 用法: bash scripts/auto-evolve.sh [最大轮数，默认 1000]
set -uo pipefail

WORK="C:/tjf/github/usb-labs"
STATE_LOG="C:/tjf/github/USBTree/docs/evolve-log.md"
DRIVER_LOG="$WORK/docs/auto-evolve-driver.log"
STOP_TIME="0745"
MAX="${1:-1000}"
LOCK="$WORK/.auto-evolve.lock"

[ -e "$LOCK" ] && { echo "已有驱动实例在运行（锁存在）"; exit 1; }
touch "$LOCK"
trap 'rm -f "$LOCK"' EXIT

echo "$(date '+%F %T') [driver] 启动：上限 $MAX 轮；$STOP_TIME 后停止派发新会话" >> "$DRIVER_LOG"

ROUND_PROMPT='在 C:/tjf/github/usb-labs（工作仓库）执行一轮 evolve 协议（1.4.0）。协议状态必读: C:/tjf/github/USBTree/docs/evolve-log.md（头部 pointer=本轮序号；文内目标池与 Run 2 池说明）与 C:/tjf/github/USBTree/docs/epics.md（EP-1 完成/EP-2 blocked-需人工/EP-3 完成/EP-4 approved 可实施，切片 S1~S6 设计见 apps/设计-工程师通信控制台.md）。流程: (1) 读 pointer 确定本轮序号; (2) 按池优先级选 1 个目标，执行 1~3 个动作（每动作一个 git 提交亦可）: (3) 在 usb-labs 根目录 bash tools/validate.sh 必须 9/9 通过; (4) git commit（不 push）; (5) 向 C:/tjf/github/USBTree/docs/evolve-log.md 底部追加一行轮次记录（#序号 | 目标 | findings | actions | result | diff | 备注）并把头部 pointer 推进到下一序号、rounds done +1。纪律: 无实质进展则如实记 result(green+no-progress)；连续 3 次无进展则在日志声明"收敛，驱动应停止"；禁止伪造进展、禁止 push、禁止改动 80-参考资料 二进制、禁止执行 docs/epics.md 中未批准事项（EP-2 需人工材料）。全部文件操作用绝对路径或先 cd C:/tjf/github/usb-labs。完成后仅输出一行: ROUND <序号> DONE|NOPROGRESS|BLOCKED'

n=0; noprog=0
while [ "$n" -lt "$MAX" ]; do
  now=$(date +%H%M)
  if [ "$((10#$now))" -ge "$((10#$STOP_TIME))" ]; then
    echo "$(date '+%F %T') [driver] 到达 $STOP_TIME，停止派发（今日共 $n 轮）" >> "$DRIVER_LOG"
    break
  fi
  n=$((n+1))
  out=$(claude -p "$ROUND_PROMPT" --max-turns 60 --dangerously-skip-permissions 2>&1 | tail -1)
  echo "$(date '+%F %T') [round $n] $out" >> "$DRIVER_LOG"
  case "$out" in
    *NOPROGRESS*) noprog=$((noprog+1)) ;;
    *BLOCKED*)    noprog=$((noprog+1)) ;;
    *DONE*)       noprog=0 ;;
    *)            noprog=$((noprog+1)) ;;
  esac
  if [ "$noprog" -ge 3 ]; then
    echo "$(date '+%F %T') [driver] 熔断：连续 $noprog 轮无进展，按协议停止" >> "$DRIVER_LOG"
    break
  fi
  sleep 15
done

rm -f "$LOCK"
echo "$(date '+%F %T') [driver] 结束：共派发 $n 轮" >> "$DRIVER_LOG"
