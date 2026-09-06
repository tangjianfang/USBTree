# Evolve Log · USBTree

- verify: `bash tools/validate.sh`（自定义结构校验：链接/代码围栏/图谱引用/frontmatter；基线 4/4 绿）
- pointer: #63（下一轮）
- rounds done: 62
- checkpoint: #61 起为 run3；run2（#56~#60+收尾）已完结于 usb-labs 侧
- checkpoint: #50/50（evolve #50 重写头部修复记账漂移：此前多次 sed/python 基准值不匹配导致头部冻结于 #15；底部逐轮记录行完好且为权威）
- status: run-3（N=1000 连续；驱动 scripts/auto-evolve-1000.sh；熔断=连续 3 轮无进展）
- metrics: findings≈17 | fixes≈14 | regressions 3（#49 覆盖事故, 已从基线恢复; 以底部逐轮行为准）
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
  - [blocked] GATT Specification Supplement 缓存：落地页为 JS 动态下载（wp-json 无直链），需浏览器人工取——evolve #21 标记

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
#8 | 40/07 USB4 v2 重提取 | findings(1) | actions(2) | result(green+progress, 8/8) | diff(~8行) | v2 ADP_CS_2 三字段(Sub-type/Version/Protocol)核实; TMU HiFi 配置值(3125/0/30/255/16)回填; 缓存附带发现: zip 内含 CM Guide 2.0/DROM/Inter-Domain/Retimer 2.0 等附加规范
#9 | graph/ 扩容 | findings(1) | actions(2) | result(green+progress, 8/8) | diff(~50行) | 实体 80→86/边 76→82; 发现并补上 class-usbtmc 缺失的 uses-transfer-bulk 边
#10 | 30/40 目录索引页 | findings(1) | actions(2) | result(green+progress, 8/8) | diff(+70行) | 发现: 30 索引前向链接 40 索引未建导致断链→同轮补建; 内容文件 102→104
#11 | 60/70 目录索引页 | findings(1) | actions(2) | result(green+progress, 8/8) | diff(+60行) | 发现: 60 索引前向链接 70 索引未建→同轮补建; 70 索引回链两个技能包; 内容文件 104→106
#12 | 90/01 术语表 | findings(1) | actions(1) | result(green+progress, 8/8) | diff(+13行) | 新增 11 条术语（EPR 查重后确认缺定义行，一并补）；USBCV 已有定义跳过
#13 | 90/02 速查表扩容 | findings(0) | actions(1) | result(green+progress, 8/8) | diff(+55行) | 新增 13/14/15 三节；数值全部 grep 自既有规范级附录文件
#14 | HFP/HS 缓存修复 | findings(3) | actions(4) | result(green+progress, 8/8) | diff(~18行) | 发现 HID-Service 假PDF+11篇链接层级错; 建立 nonce 直链流程(L7); HFP-1.10 入缓存回链
#16 | 20/MSC/02 对抗抽查 | findings(0) | actions(1) | result(green+no-progress, 8/8) | diff(+2行) | 5 组抽样一致；加抽查戳记
#18 | BLE 12/14 对抗抽查 | findings(0) | actions(2) | result(green+no-progress, 8/8) | diff(+4行) | 5 Opcode+灵敏度表比对一致；S=8=-82 为 6.0 正确新值
#19 | 30/08+30/09 对抗抽查 | findings(0) | actions(2) | result(green+no-progress, 8/8) | diff(+4行) | 内核宏/Accept/PS_RDY/Soft_Reset 与 tCCDebounce 一致
#20 | CDC/UAC/UVC 三附录抽查 | findings(0) | actions(3) | result(green+no-progress, 8/8) | diff(+6行) | VS_PROBE=0x01(A-16)/CLOCK_SOURCE=0x0A/SET_LINE_CODING=20h 均证实；VS_PROBE 为提示稿另一处被纠错
#21 | GATT Supplement 缓存 | findings(0) | actions(0) | result(blocked, 8/8) | diff(+1行) | files.bluetooth 动态下载无静态直链; 池标注需人工/浏览器
#22 | 结晶 | findings(0) | actions(2) | result(green+progress, 8/8) | diff(+45行) | L1/L2/L3/L7(5 次验证)→tools/spec_extract.sh; 实测顺带复核 GET_IDLE=0x02
#23 | 11 篇 HFP AT 表 | findings(0) | actions(1) | result(green+progress, 8/8) | diff(+20行) | 9 条 AT 命令速查（BRSF/BAC/CHLD/BIEV/BVRA 等），首用结晶工具 spec_extract.sh 提取
#24 | 类代码表三处一致性核对 | findings(2) | actions(2) | result(green+progress, 8/8) | diff(~4行) | 20-索引 0x0F/0x10 行改指专篇; 90-02-7 长尾类缺行评估为可接受(速查定位)+已有 20-索引兜底
#26 | 30/06 OTG 定时器回填 | findings(1) | actions(1) | result(green+progress, 8/8) | diff(+3行) | 消除"见规范原文"模糊处: TA_AIDL_BDIS=200ms/TA_BDIS_ACON≤100ms/TB_ASE0_BRST≥155ms/TA_WAIT_BCON≥1.1s
#27 | 15-A2DP SBC 抽查 | findings(0) | actions(1) | result(green+no-progress, 8/8) | diff(+2行) | bitpool/码率与 Table 4.7 一致
#28 | USBTMC+Billboard 抽查 | findings(0) | actions(2) | result(green+no-progress, 8/8) | diff(+4行) | MsgID/0x7E/0x7F 与 0x0D 均证实
#29 | USB3.2 表 6-2/6-30 解析 | findings(2) | actions(2) | result(green+progress, 8/8) | diff(+20行) | 90/03 两行 ※ 解除; 40/06 补表 6-2 Gen2 符号值(CCh/33h/96h/69h)
#31 | 技能与门面计数同步 | findings(2) | actions(2) | result(green+progress, 8/8) | diff(~10行) | README 28份漂移→按索引页; spec-lookup 补 4 行新缓存映射 + spec_extract 提示
#32 | 端点包长/PID 三处一致性 | findings(0) | actions(0) | result(green+no-progress, 8/8) | diff(0) | 06/90-02-5/13 包长与 05/90-02-4 PID 全一致（含 SSP 控制 512）
#33 | 05-TinyUSB 宏勘误 | findings(1) | actions(1) | result(green+progress, 8/8) | diff(~6行) | 官方 tusb_option.h 证实 ENDPOINT 单P写法错误, 统一为 CFG_TUD_ENDPPOINT_MAX 并警示静默回退
#34 | 06-libusb 错误码抽查 | findings(0) | actions(1) | result(green+no-progress, 8/8) | diff(+2行) | 10 个错误码与 libusb.h 一致
#35 | 90/03 PD 定时器 | findings(1) | actions(2) | result(green+progress, 8/8) | diff(~5行) | 内核证实 PS_TRANSITION=500; 发现内核 SENDER_RESPONSE 用宽松 60ms(注明); FirstSourceCap 维持 ※
#36 | 01-UVC GUID 抽查 | findings(0) | actions(1) | result(green+no-progress, 8/8) | diff(+2行) | YUY2/NV12/M420/I420 GUID 逐字符一致
#37 | 01/02 UAC1 请求码勘误 | findings(2) | actions(2) | result(green+progress, 8/8) | diff(~8行) | 本轮最大发现: UAC1 请求码整组写反(旧值 GET_CUR=0x02/GET_MIN=0x84), Table A-9 原文核实为 0x81/0x82/0x83/0x84; 03 附录此前已正确
#38 | 30/08 BIST/VDM 核对 | findings(0) | actions(0) | result(green+no-progress, 8/8) | diff(0) | VDM Command=1 与内核 CMD_DISCOVER_IDENT 一致；08 篇本已标注内核来源
#45 | 外链抽测 | findings(0) | actions(0) | result(green+no-progress, 8/8) | diff(0) | usb.org/bluetooth.com/tinyusb 三链接 200
#46 | 20-索引一致性 | findings(0) | actions(0) | result(green+no-progress, 8/8) | diff(0) | 其他设备类 11 篇与索引行对应正常
#47 | 枚举序列关键词一致性 | findings(0) | actions(0) | result(green+no-progress, 8/8) | diff(0) | 树干08/排查手册/技能包三处 GET_DESCRIPTOR 叙述无矛盾
#48 | 四目录索引表核对 | findings(0) | actions(0) | result(green+no-progress, 8/8) | diff(0) | 30/40/60/70 索引表行数=实际文件数
#50b | 事故恢复 | findings(3) | actions(1) | result(green+progress, 8/8) | diff(恢复218/222/206行×3) | 12-LLCP/06-USB3x/15-A2DP 从基线 3d3272e 恢复并重放戳记/Gen2 表; L8 入库
#53 | 图谱再生成+标记清点 | findings(1) | actions(2) | result(green+progress, 8/8) | diff(~5行) | COVERAGE 经典蓝牙 90→93(HFP/AVRCP 已缓存); 残留 5 处标记均为合法溯源注记; 导出图再生成
#54 | 终态统计 | findings(0) | actions(1) | result(green+no-progress, 8/8) | diff(0) | 图谱再生成 86/82；残留标记均为合法溯源注记
#55 | 回顾轮（run 1） | findings(3) | actions(4) | result(green+progress, 8/8) | diff(0) | 重放审计 2/2 通过（#33 红前绿后: 父1单P→3双P; #8 三字段注记落位）; L1 verified+1; epics.md 新建 EP-1/2/3(proposed)

## Run 1 总结（#6~#55，N=50 实际执行至 #55 含回顾）

- 轮次: 50（含 #55 回顾）；提交: 每 1~3 动作一提交；verify: `bash tools/validate.sh` 8/8 常绿
- 结果: findings≈20 | fixes≈17 | regressions 1（#49 覆盖事故→#50b 恢复+L8）| blocked 2（GATT Supplement、EL 断言样本）
- 亮点: USB4 v2 三字段重构与 TMU HiFi 配置值、UAC1 请求码整组勘误（Table A-9）、Type-C R2.5 状态机核验、OTG 定时器权威化、HFP/AVRCP/AVDTP/电气合规 4 份新缓存
- 产出: 新叶 9 篇（12/13 树干与高速附录、40/00 与 60/70 索引、40/08 DROM、40/09 CM 指南）+ 图谱 86/82 + 结晶工具 spec_extract.sh
- 待决 Epic: EP-1（PD 本体）、EP-2（GATT Supplement）、EP-3（命名守卫）——见 docs/epics.md，等待用户裁决

## Run 2 开启（N=50，轮次 #56~#105，#105=回顾）

- pointer 迁移至 #56；池: Tier4 实战篇 API 抽查系列（libusb 已证）/09-TypeC 深化/HFP eSCO 表/USB3.2 zip 附带(CRC32 等)登记/术语表二轮/一致性专项余量
#56 | 11 篇 eSCO 参数表 | findings(0) | actions(1) | result(green+progress, 8/8) | diff(+15行) | run2 首轮: S1~S4/T1/T2 与 mSBC 强制集自 HFP-1.10 Tables 6.11~6.14
#57 | 30/09 液体腐蚀附录 | findings(0) | actions(1) | result(green+progress, 8/8) | diff(+14行) | R2.5 附录 A 三种检测方法成文
#58 | 图谱二轮扩容 | findings(0) | actions(1) | result(green+progress, 8/8) | diff(~25行) | 89 实体/85 边
#59 | USBTMC 主规范抽查 | findings(0) | actions(0) | result(green+no-progress, 8/8) | diff(0) | USB488 为独立子规范引用
#60 | USB488 子规范核对 | findings(0) | actions(1) | result(green+no-progress, 8/8) | diff(+2行) | bNotify1 D7=1/Status Byte 证实; checkpoint #60
#61 | EP-4 S1 通道层前半(usb-labs) | findings(0) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 两靶绿) | diff(+321行@usb-labs 8ef4e12) | IChannel 契约+SerialChannelT 适配(读线程→回调/统计)+MockEchoPort 离线自测 25 例全绿(C++ 通道测试基线 0→25); HidChannel 留 #62, S1 真机验收待整片完成后执行。01:13 中断会话的 #61(进行中) 占位由本轮完成记录取代（工作落盘于 usb-labs 8ef4e12）
#62 | EP-4 S1 通道层后半(usb-labs) | findings(1) | actions(2) | result(green+progress, usb-labs validate ✔ + MSVC 两靶绿 + selftest 61/61) | diff(+296行@usb-labs 99134f1) | HidChannelT 适配(读线程轮片:超时=轮空/错误=退出, send=set_output_report, Report ID 透传)+MockHidPort 回显假件 36 例(C++ 通道测试基线 25→61); 自评捕获并修正 Mock 空队列 timed_out 标志缺陷(未及提交); README 文件结构补 channel/(消 #61 文档滞后); S1 通道层至此齐(Serial+Hid), 剩真机验收, S2 设备发现待 #63
