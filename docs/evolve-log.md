# Evolve Log · USBTree

- verify: `bash tools/validate.sh`（自定义结构校验：链接/代码围栏/图谱引用/frontmatter；基线 4/4 绿）
- pointer: #73（下一轮）
- rounds done: 72
- checkpoint: #72/1000——#71 遗留缺陷池 4/4 落地（HID 写路径有界化/MSC 默认 3s+探测 3s/周期传输失败自动 disarm/假件签名对齐+12 例），对抗复核一轮：①主路②③未驳倒、④"透传默认 3s"断言驳倒为空钉→当轮以 channel.h kSendTimeoutMs 显式透传修正（MSC 两断言变异实验证实真钉）；自测基线 405→417；残余（对抗列出）: HID 回退路径 HidD_SetOutputReport 控制传输不可取消（中，README #20 自认）/慢成功设备不 disarm（低）/disarm 分支 UI 层零离线覆盖（验收表 B10/B11 人工钉）/后台盘扫描仍 10s 探测·不冻结 UI（低）；工作落盘 usb-labs 0598a52；EP-4 代码侧唯余整片真机验收；usb-labs 暂无截图机制，视觉 review 即便 UI 目标亦跳过
- checkpoint: #71/1000——EP-4 收尾审查轮（WinUSB/HID 挂死防线+超时回收边界竞态修复，经受两轮独立对抗复核确认，工作落盘 usb-labs 0ed5e4c，自测基线 405）；真机验收执行表已建（usb-labs apps/验收-工程师通信控制台.md，人工按表逐项过）；遗留缺陷池（对抗复核列出，属审查修复非新切片、可排码侧轮）: HID send 零超时（HidD_SetOutputReport 同步+双句柄重试）/MSC send·开会话 UI 线程同步 10~20s（SessionPane 未调 set_read_timeout）/周期发送失败不 disarm（NAK 时 UI 近乎持续冻结）/MockWinUsbPort::write_pipe 签名漂移致新逻辑离线零覆盖；usb-labs 暂无截图机制，视觉 review 即便 UI 目标亦跳过
- checkpoint: #70/1000——EP-4 S5 后半完成（MscChannel 只读 SCSI 直通+目录四通道接线，工作落盘 usb-labs 4d09687，自测基线 405）；EP-4 代码侧 S1~S5 全齐，唯余整片真机验收（S1 通道/S2 三秒定位/S3 收发/S4 解码/S5 U盘读扇区+WinUSB 收发——需真机与工装，自主会话无法执行，验收前 EP-4 不再排码侧切片）；S6 PD 面板依赖 Lab5 遥测契约固件（设计即挂起）；usb-labs 暂无截图机制，视觉 review 即便 UI 目标亦跳过
- checkpoint: #69/1000——EP-4 S5 前半完成（WinUsbPort 管道层+WinUsbChannelT 适配+Mock 自测，工作落盘 usb-labs 3c38921，自测基线 335）；S5 后半（MscChannel+目录接线 usb 行→通道）待 #70；整片真机验收（S1 通道/S2 定位/S3 收发/S4 解码/S5 U盘读扇区）待执行；usb-labs 暂无截图机制，视觉 review 即便 UI 目标亦跳过
- checkpoint: run3 驱动运维（2026-09-07 02:51）——驱动一晚两次假熔断已根治（L9：tail-1 抓 hook 噪声 + 大切片耗尽 max-turns 吞标记；改为仓库状态判定+turns 100）；无时间闸连续驱动运行中，指针 #67 续跑，目标 1000 轮
- checkpoint: #50/50（evolve #50 重写头部修复记账漂移：此前多次 sed/python 基准值不匹配导致头部冻结于 #15；底部逐轮记录行完好且为权威）
- status: run-3（N=1000 连续；驱动 scripts/auto-evolve-1000.sh；熔断=连续 3 轮无进展）
- metrics: findings≈42 | fixes≈31 | regressions 3（#49 覆盖事故, 已从基线恢复; 以底部逐轮行为准）
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
#63 | EP-4 S2 设备发现前半(usb-labs) | findings(0) | actions(2) | result(green+progress, usb-labs validate ✔ + MSVC 三靶绿 + selftest 61/61 & 36/36) | diff(+307行@usb-labs c9c6e10) | device_catalog 即时过滤核心(多关键词AND/ASCII大小写折叠/协议kind掩码/保序)+serial_enum COM枚举(SERIALCOMM注册表,数字序); 新靶 discovery_selftest 36 例(控制台自测基线 61→97); S2 后半(DeviceInfo→目录适配+UI表格+双击开会话)待 #64; 轮中观察到并发提交 cef2eb0(驱动头部状态同步,仅 checkpoint 行,线性无冲突)
#64 | EP-4 S2 设备发现后半(usb-labs) | findings(2) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 三靶绿零告警 + selftest 61/61 & 50/50) | diff(+571行@usb-labs 49a4d32) | catalog_build(DeviceInfo→目录适配·名称回退链/USB·HID+COM 合流/会话工厂 hid→HidChannel·serial→SerialChannel·usb 待 S5)+console_window(--console 独立窗口,产测模式旁路:EN_CHANGE 即时过滤/复选框掩码/F5 后台扫描/双击开会话,收发台 UI 为 S3)+PerMonitorV2 DPI; 自测基线 36→50(+14); 轮内自纠 2 处(头文件缺 windows.h 自含性/自测夹具断言错位,均为构建·运行验证暴露后即修); 571 行超 ~300 软帽(Win32 窗口骨架占比大,单提交可整体回退); S2 逻辑+UI 至此齐(真机"3 秒定位+双击真开"验收随整片), S3 会话台待 #65
#65 | EP-4 S3 会话台前半(usb-labs) | findings(0) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 四靶绿零告警 + selftest 61/61 & 50/50 & 78/78) | diff(+632行@usb-labs 4c258a5) | session_codec(发送框智能识别 auto/hex/ascii 锁定·奇数位补前导 0·UTF-8 中文可发 + 双视图 + 绝对/相对时间戳 + IN/OUT 行格式)+session_core(周期节拍 100ms~60s 钳制/发送历史 50 条·草稿态游标/帧日志环形·清屏不清账/SessionCore 时间基准); 新靶 session_selftest 78 例(控制台自测基线 111→189); 轮内自纠 4 处自测断言笔误(运行暴露即修,实现零改动——纯空白按 ASCII 原文/空格仅分隔非字节边界/interval 未重设/hex_view 误传 false); README 文件结构同步; 632 行超 ~300 软帽(纯逻辑头文件+自测占比大,单提交可整体回退); S3 后半(UI 标签页/收发区接线)待 #66
#66 | EP-4 S3 会话台后半(usb-labs) | findings(3) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 四靶绿零告警 + selftest 61/61 & 50/50 & 95/95) | diff(+874/-19行@usb-labs 5a5525f) | session_view(RenderCursor 渲染游标:poll 增量/暂停停走/恢复补齐/环形淘汰跳过/rebuild 口径切换全量重渲染)+session_pane(每会话一面板:发送区智能识别+编码锁定+Ctrl+↵/↑↓历史草稿态+周期即改即生效,接收区暂停/清屏/Hex↔ASCII/相对↔绝对+行数封顶滞回剪头,读线程 PostMessage 载荷投递 UI 线程入账)+console_window(下区标签台:增删/切换/右键关闭+100ms 共享定时器驱动周期发送+45/55 分区+DPI 联动); 自测 78→95(+17); findings=收编 02:39 中断会话在途工作后 review 出 3 处文档滞后(console_window.cpp 头注释仍称 S2 单区/README 缺 session_view·session_pane/selftest 头注释)同轮修; 874 行超 ~300 软帽(新 UI 文件 601 行占比大,单提交可整体回退); S3 至此齐(真机收发验收随整片), S4 解析面板待 #67
#67 | EP-4 S4 解析面板前半(usb-labs) | findings(3) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 五靶绿零告警 + selftest 61/61 & 50/50 & 95/95 & 62/62) | diff(+364行@usb-labs ca9e25e) | hid_parser 解码核心(键盘页键码表 0x04~0x65/修饰键位图 bit0 LCtrl…bit7 RGui/boot 8 字节行格式含 0x01~0x03 错误码/鼠标按钮位图+X·Y 有符号位移+滚轮+宽轴 LE/消费页 B0~B8·CD·E2·E9·EA/Report ID 剥离统一入口/AsciiParser 委托 session_codec 口径不二), 码表全部核对自缓存 PDF 原文; findings=HUT 消费页 -layout 提取行漂移 1 行(B5~B8 段, -table 模式+库内 07-消费控制 篇交叉裁决, L2/L5 现场再证)+keycode_name 初版索引错位(自审发现即修)+自测夹具 2 处鼠标字节序笔误(运行暴露即修); 新靶 parser_selftest 62 例(控制台自测基线 206→268); S4 后半(UI 面板接线+原始|解析切换)待 #68
#68 | EP-4 S4 解析面板后半(usb-labs) | findings(2) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 五靶绿零告警 + selftest 61/61 & 50/50 & 95/95 & 85/85) | diff(+284/-19行@usb-labs ff2b69b) | parser_select 纯逻辑(通道描述→选型: HID 顶层 usage page/usage——GD 0x01+06/07 键盘·+02 鼠标·0x0C 消费页, 数值核对自缓存 HUT-1.3 §4/§15; 串口/环回→ASCII 委托; 未收录→none 回退原始)+帧解析调度(mouse 按剥离 Report ID 后长度猜格式); 通道层 HidPort::fill_caps 遍历输入 Value/Button caps 判 has_report_id(HIDP_CAPS 无直接字段, ReportID≠0 即带前缀)+ChannelDesc 增 HID 能力透传; 会话层 RenderCursor 增 parsed_view/parser(§4.7 跟随协议: HID 已收录默认开)+frame_line 同一行装配两视图只差正文; UI 接收工具条"解析视图"开关(切换即 rebuild, 选型 none 置灰)+状态行解析器名; 自测 62→85(选型 11+调度 6+行装配 2 含 S3 口径回归+游标切换 4); findings=轮内自纠 2 处(ChannelDesc 字段名与选型实现不一致·编译暴露即修/自测鼠标 4 字节预期漏滚轮字节·运行暴露即修); 已知边界: 多顶层集合复合 HID 按首集合 usage 选型, 逐 Report ID 分流待真机样本; EP-4 代码侧 S1~S4 齐, S5 待 #69, 整片真机验收待执行
#69 | EP-4 S5 WinUSB 通道前半(usb-labs) | findings(1) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 五靶绿零告警 + selftest 105/105 & 50/50 & 95/95 & 85/85) | diff(+717/-8行@usb-labs 3c38921) | winusb_port(CreateFile 重叠+WinUsb_Initialize 接口0+QueryPipe 遍历+select_data_pipes 选型纯逻辑: 批量优先/中断回退/同型编号最小+ReadPipe 超时 AbortPipe+GetOverlappedResult 回收·口径同 HidPort+WritePipe 同步完成短写检测+parse_vid_pid 路径 VID/PID 解析·大小写不敏感 1~4 位十六进制)+winusb_channel(IChannel 适配: IN 传输=帧/无 IN 管道不起读线程/无 OUT 管道 send 拒绝/desc 含 VID:PID+管道型别)+MockWinUsbPort 回显假件·纯逻辑 9 例+会话契约 35 例(61→105)+README 架构/文件结构/不确定 API #15~16; findings=自审即修 1 处(select_data_pipes 防御检查反逻辑会滤掉全部中断管道, 提交前发现); 717 行超 ~300 软帽(OS 层+自测占比大, 单提交可整体回退); 口径注记: 驱动提示词称 usb-labs validate 9/9, 实际脚本为链接+围栏两项(✔ 即过), 按实际输出记账; 真机 WinUSB 收发随整片, MSC 通道+目录接线待 #70
#70 | EP-4 S5 MSC 通道+目录接线后半(usb-labs) | findings(3) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 五靶干净重建零告警 + selftest 163/163 & 62/62 & 95/95 & 85/85) | diff(+644/-40行@usb-labs 4d09687) | msc_channel(MscChannelT 适配 MscScsi: 发送框即 CDB·msc_plan_cdb 操作码方向/响应长度表——INQUIRY/SENSE/MODE_SENSE/CAPACITY/READ(10,12,16) 为 IN·FORMAT/MODE_SELECT/WRITE(10,12,16) 拒收(只读红线)·未收录操作码按无数据直通·响应封顶 1MiB; CHECK CONDITION 以 18B 固定格式 SENSE 帧经回调呈现·status==0xFF 方算 OS 层失败; 无异步 IN 流→不起读线程·回调在 send 线程同步触发(SessionPane 回调只 Post 载荷·口径兼容); parse_drive_index 三形态解析)+msc_enum(PhysicalDrive0..9 只读扫描·BusTypeUsb+READ_CAPACITY 过滤·同 auto_detect 口径→msc 目录行·INQUIRY 身份尽力)+接线(DeviceKind::msc/build_catalog 三参合流/make_channel 四通道 usb→WinUsbChannel·msc→MscChannel/控制台 MSC 复选框+F5 纳入+双击 S5 占位提示退役); SCSI_IOCTL_DATA_* 数值以本机 SDK 头核值(OUT=0/IN=1/UNSPEC=2——与记忆直觉相反, 防了一次方向反写); 自测 channel 105→163(MockMscPort: 直通方向/缓冲/超时记录+CHECK CONDITION/OS 失败/拒写/非法 CDB 分径) & discovery 50→62(msc 行形态/同义词/掩码/合流次序/四通道工厂)·基线 335→405; findings=轮内自纠 3 处(parse_drive_index 大小写折叠方向反——自测红→绿即修/READ12 测试块数字节错位/拒收后 tx 断言预期错·后二为测试笔误); 644 行超 ~300 软帽(新通道+自测占比大, 单提交可整体回退); EP-4 代码侧 S1~S5 至此全齐, 唯余整片真机验收(需真机与工装, 自主会话不可执行), S6 PD 面板依赖 Lab5 遥测契约固件(设计挂起项)
#71 | EP-4 收尾审查: S5 通道挂死防线+边界竞态+真机验收准备(usb-labs) | findings(5) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 五靶干净重建零告警 + selftest 163/163 & 62/62 & 95/95 & 85/85=405 基线持平) | diff(+139/-18行@usb-labs 0ed5e4c) | 发现: ①WinUsbPort::write_pipe INFINITE 等待——do_send 三入口均在 UI 线程, 固件不收 OUT(NAK 永续)时控制台永久冻结且关会话不可恢复(CloseHandle 不点亮 OVERLAPPED 事件); ②独立对抗复核(2 轮)追加实锤: 超时边界竞态——GOR(TRUE) 结果被丢, 传输恰在超时判定与中止生效间完成时写已成功报失败(重发→设备收重复命令)/读边界帧丢弃(设备不重发即丢帧), wait 失败分支 GetLastError 被回收序列覆写; ③read 路径 wait!=WAIT_OBJECT_0 分支留孤儿 IO(RAII 关事件时 IRP 仍挂起); ④winusb_channel set_read_timeout 缺 override; ⑤msc_scsi.cpp 头注释"未真机编译"过期(#64 起五靶已编); 修复=①~④全落: write 有界 3s 默认参+AbortPipe 回收+边界竞态 GOR 成功即按成功(写)/交付帧(读, HID 同修·顺带改善产测 HID 环回与回报率测量的边界误判)+先取码再回收+孤儿 IO 守卫(双文件); 新增 apps/验收-工程师通信控制台.md 真机验收执行表(准备+A 发现/B 收发/C 解析/D MSC·WinUSB 分组+记录表, MSC READ(10) 示例 CDB 块序自纠, 设计 §五 挂链)+README 不确定清单 #19; 属审查修复非新切片, 与 #70"验收前不排码侧切片"决策相容(降低验收会话自身失败风险); 遗留下轮缺陷池: HID send 零超时/MSC send·open UI 线程同步 10~20s/周期发送失败不 disarm/MockWinUsbPort::write_pipe 签名漂移(新逻辑离线零覆盖)
#72 | EP-4 遗留缺陷池: 会话台发送路径挂死防线收口(usb-labs) | findings(11) | actions(3) | result(green+progress, usb-labs validate ✔ + MSVC 五靶干净重建零告警 + selftest 175/62/95/85=417·基线 405→417) | diff(+184/-32行@usb-labs 0598a52) | 池 4 项全落地: ①HID send 零超时→WriteFile 重叠有界主路(默认 3s, CancelIoEx+GOR 边界竞态兜底, 口径同 #71 write_pipe)+立即失败(无 OUT 管道/蓝牙 HID, MSDN/hidapi 口径经检索证实)回退 HidD_SetOutputReport; ②MSC 通道默认直通超时 3s+open 探测(scsi_inquiry/read_capacity 增 timeout_s 参)同界, 产测默认参行为逐位不变; ③周期传输层失败自动 disarm(transport_failed 出参, 解析错误/空内容不触发)+取消勾选+状态行提示; ④MockWinUsbPort::write_pipe/MockHidPort::set_output_report 签名对齐+fail_write 假件+12 例(163→175); 独立对抗复核(变异实验验证断言): ①主②③未驳倒, ④"透传默认 3s"断言驳倒为空钉(靠 mock 默认参巧合对齐, 防不住真件默认漂移)→当轮修正: channel.h 增 kSendTimeoutMs 常量, HID/WinUSB 通道显式透传变真钉; 残余(对抗列出, 低危为主): HID 回退路径控制传输不可取消且二次尝试(中, README #20 自认)/慢成功设备不 disarm(低)/disarm 分支 UI 层零离线覆盖→验收表 B10/B11 人工钉/后台盘扫描仍 10s 探测不冻结 UI(低)/set_read_timeout(0) 回落 10s 埋雷(低); 顺带纠正 README 过期"未在真机编译"声明(#64 起五靶已编, 属 #71⑤同类文档滞后)
