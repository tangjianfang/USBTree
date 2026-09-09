@echo off
rem AutoEvolve1000 —— evolve 连续运行驱动（run3，N=1000，无每日时间闸）
rem 由 Windows 计划任务在 07:50 调用；停止条件=1000 轮上限/熔断/手动删锁
"C:\Program Files\Git\bin\bash.exe" -c "cd /c/tjf/github/usb-labs && bash /c/tjf/github/USBTree/scripts/auto-evolve-1000.sh"
