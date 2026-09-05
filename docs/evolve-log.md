# Evolve Log · USBTree

- verify: `bash tools/validate.sh`（自定义结构校验：链接/代码围栏/图谱引用/frontmatter；基线 4/4 绿）
- pointer: #8（下一轮）
- rounds done: 7
- status: resumed-run（N=50，轮次 #6~#55，#55=回顾）
- checkpoint: #5 完成于 39d0aca；池已刷新（见下）
- metrics: findings 8 | fixes 8 | regressions 0
- pool-refresh: 2026-09-05（#6 内执行）
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
  - ~~AVDTP 1.3.x 规范补缓存 + 回填 15-A2DP 信令码表~~（#4 已完成：AVDTP-1.3.pdf 入缓存，Table 8.6 核对一致）
  - AVDTP 1.3.x 规范补缓存 + 回填 [15-A2DP] 的信令码值占位（对应 COVERAGE 空白 #2）
  - 30/40 目录无 00-索引页（20 目录有）
  - PD EPR 消息编号（规范门控，挂起直至拿到原文）

## 轮次记录

（每轮一行：`#N | 目标 | findings(n) | actions(n) | result(..., 检查数) | diff(行) | 备注`）
#1 | 09-长尾设备类 AV 小节 | findings(2) | actions(2) | result(green+progress, 4/4) | diff(~8行) | 与 10-AV详解 对齐: AVC误传→AV1.0 CBP/AVDD; 类代码表协议码 0x00→0x10
#2 | tools/validate.sh 校验覆盖 | findings(0) | actions(2) | result(green+progress, 6/6) | diff(~40行) | 检查基线 4→6: 关系边端点⊆实体表、title≡H1；两项新检查全库即绿
#3 | 90-附录/02 轮换审查→发现 Chirp 全库性错误 | findings(4) | actions(6) | result(green+progress, 6/6) | diff(~30行) | 04/02排查/02速查 Chirp 17~20ms/6~100ms→TUCH 1~7ms; KJ序列单位 ms→µs/拍; 02 五处交叉链接新附录; 附勘误注记
#4 | AVDTP 补缓存+15-A2DP 回填 | findings(1) | actions(3) | result(green+progress, 6/6) | diff(~6行) | AVDTP-1.3.pdf 入缓存(缓存 33→34)；信令码表与 Table 8.6 核对全一致(0 错)；两处"未缓存"占位清除

## 回顾（Round #5 · 2026-09-05）

- **重放审计**：抽样 #2（检查基线 4→6：父提交 164aa0f 中 "== 5/6" 0 次 → #2 提交 1 次 ✅）与 #3（错误值 "17~20 ms 的 K"：父提交 1 次 → #3 提交 0 次，正确值 "1~7 ms 的 K 电平" 1 次 ✅）。两轮均通过，无 gamed。
- **结果**：5 轮 findings 7 / fixes 7 / regressions 0；提交 3d3272e→#5；verify 从 4/4 增强到 6/6。
- **教训入库**：docs/lessons.md 新建，L1~L6（规范数值必提取、pdftotext 坑、直链漂移、子任务以磁盘为准、交叉引用探错、bash CWD）。
- **空白变化**：COVERAGE 空白 #2（AVDTP）关闭；经典蓝牙 88%→90%。
- **池刷新提示**（下轮开始前执行）：T1 重新核对 COVERAGE 空白清单；T3 轮换到 tools/gen_graph.sh 或 graph/ 边质量抽查。
#6 | 池刷新+30-02音频配件R2.5弃用注记 | findings(1) | actions(2) | result(green+progress, 6/6) | diff(~6行) | 池:T1重核(COVERAGE空白1/3/4/5仍在,2已闭),T3模块表含graph/skills/tools;新增池项:HFP/AVRCP/GATT补编缓存、30/40目录索引、USB4错位表重提取
#7 | tools/validate.sh | findings(0) | actions(2) | result(green+progress, 8/8) | diff(~40行) | +检查7 export.mmd 新鲜度(gen_graph 支持自定义输出); +检查8 H1 唯一性; 全库即绿
