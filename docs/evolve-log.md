# Evolve Log · USBTree

- verify: `bash tools/validate.sh`（自定义结构校验：链接/代码围栏/图谱引用/frontmatter；基线 4/4 绿）
- pointer: #4（下一轮）
- rounds done: 3
- status: initialized
- metrics: findings 6 | fixes 6 | regressions 0
- boundary: USB/BLE 领域知识系统（纯文档 + bash 工具 + 图谱/技能包）。红线：不改 80-参考资料 下规范原文内容（只增不改）；不做应用代码；不自动 push；破坏性命令需确认。
- note: 项目无 CLAUDE.md/AGENTS.md；边界由用户会话历史确立。git 于剖析阶段初始化（协议要求每轮一提交）。

## 目标池（剖析于 2026-09-05）

- **T1 已知缺陷**
  - [09-长尾设备类] AV 小节与新篇 [10-AV设备类详解] 矛盾（09 称"AVC 命令经中断承载"，10 已按 AV 1.0 原文纠偏为 Bulk CBP 16 字节定长头）——来源：子任务 D 报告
  - [COVERAGE] 已知残余空白 5 项；其中 #2 "AVDTP 独立规范未缓存"本周期可行动
- **T2 校验覆盖缺口**
  - [tools/validate.sh] 现仅 4 项检查：缺"relations 边的 from/to 必须存在于 entities.yaml"、"frontmatter title 必须与正文 H1 一致"
- **T3 模块轮换清单**（src 等价物 = 内容目录 + 工具）
  - 90-附录/02-速查表大全（写成时间早于 5 篇规范级附录，无交叉链接，可能有过时表述）→ tools/ → graph/ → 80-参考资料/README.md
- **T4 待办扩展**
  - AVDTP 1.3.x 规范补缓存 + 回填 [15-A2DP] 的信令码值占位（对应 COVERAGE 空白 #2）
  - 30/40 目录无 00-索引页（20 目录有）
  - PD EPR 消息编号（规范门控，挂起直至拿到原文）

## 轮次记录

（每轮一行：`#N | 目标 | findings(n) | actions(n) | result(..., 检查数) | diff(行) | 备注`）
#1 | 09-长尾设备类 AV 小节 | findings(2) | actions(2) | result(green+progress, 4/4) | diff(~8行) | 与 10-AV详解 对齐: AVC误传→AV1.0 CBP/AVDD; 类代码表协议码 0x00→0x10
#2 | tools/validate.sh 校验覆盖 | findings(0) | actions(2) | result(green+progress, 6/6) | diff(~40行) | 检查基线 4→6: 关系边端点⊆实体表、title≡H1；两项新检查全库即绿
#3 | 90-附录/02 轮换审查→发现 Chirp 全库性错误 | findings(4) | actions(6) | result(green+progress, 6/6) | diff(~30行) | 04/02排查/02速查 Chirp 17~20ms/6~100ms→TUCH 1~7ms; KJ序列单位 ms→µs/拍; 02 五处交叉链接新附录; 附勘误注记
