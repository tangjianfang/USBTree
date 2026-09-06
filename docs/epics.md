# Epics · 升级提案登记

> 1.4.0 协议：轮次只提案、不执行；`proposed → approved | rejected` 由用户裁决。批准后走独立 spec→plan 流程，切片可回注 Tier 4。

## EP-1 · PD 规范本体获取与全表化

- **type**: refactor（材料补全型）
- **trigger**: (a) cannot fix——`30/08-USBPD消息全表` 的 EPR 消息编号、PPS Power Limited 位、PD 定时器完整表因 **PD 规范本体被 Adopters Agreement 门控** 无法核实（evolve #21/#35/#37 多轮标注"见规范 §6.x"）
- **hypothesis**: 拿到 PD 3.1/3.2 原文后，≤2 个轮次即可完成 EPR 消息表与定时器全表的权威化，消除本库最大的一处"二手来源"依赖
- **sketch**: 用户以 Adopter 身份从 usb.org 下载 PDF → 放入 `80-参考资料/usb-core/` → `tools/spec_extract.sh` 提取 → 30/08 逐表替换内核口径 → COVERAGE 更新
- **verification**: validate 8/8 + PD 表逐条标注规范表号
- **rollback**: 不需要（纯增补）
- **预估**: 2 轮
- **status**: **completed**（2026-09-05：发现 usb.org 公开直链 USB_PD_R3.2_V1.2_2.zip，已缓存并回填 EPR 消息编号 0x09/0x0A/0x0B；定时器精确 min/max 见缓存 Table 7.10）

## EP-2 · GATT Supplement 与 Assigned Numbers 缓存

- **type**: refactor（材料补全型）
- **trigger**: (a)+(f)——`skills/usb-spec-lookup` 与 `50/04-ATT与GATT` 需要标准特征/描述符 UUID 全表；GATT Supplement 落地为 JS 动态下载（evolve #21 blocked），Assigned Numbers 为 Web DB
- **hypothesis**: 经浏览器人工下载 GATT Supplement PDF（及按需导出 Assigned Numbers 页）后，`50/04-ATT与GATT` 可补"标准服务/特征 UUID 全表"叶
- **sketch**: 浏览器下载 → 入 `80-参考资料/bluetooth/` → spec_extract 提取 → 新叶或扩 04 篇
- **verification**: validate + UUID 抽样比对
- **rollback**: 不需要
- **预估**: 2 轮
- **status**: approved → **blocked-pending-manual**（2026-09-05 复核：GSS 下载页为 JS 渲染无静态直链，需浏览器人工保存 PDF 至 80-参考资料/bluetooth/ 后告知即可完成回填）

## EP-3 · 命名规范自动化守卫（远期）

- **type**: innovate
- **trigger**: (e)——USB-IF 营销命名（5G/10G/20G/40G/80Gbps）与规范名映射散布在 01/03-各版本对比/速查表 等多处，曾出现漂移风险；validate 无法校验语义
- **hypothesis**: 将"规范名↔营销名↔速率"做成 `graph/naming.yaml` 单一事实源 + validate 检查，杜绝多处手抄漂移
- **sketch**: 数据文件 → validate 新检查项 → 各篇改为引用而非复抄
- **verification**: validate 新检查 + 抽样比对
- **rollback**: 保留旧表一版
- **预估**: 3 轮
- **status**: approved（2026-09-05，立即执行）

## EP-4 · 工程师通信控制台（Communication Console）

- **type**: innovate
- **trigger**: (f) 用户指令——现工具面向产线验收，工程师日常四大高频操作（找设备/开通道/收发/解析）无工具支撑（用户原话：上千个 path 选到什么时候）
- **hypothesis**: 统一 IChannel 抽象（HID/串口/WinUSB/MSC 四通道）+ 即时过滤设备发现 + 多会话收发台 + 可插拔解析面板，覆盖工程师 90% 日常调试操作（对标 Bus Hound + 串口助手）
- **sketch**: 完整设计见 usb-labs 仓库 `apps/设计-工程师通信控制台.md`（三区布局/IChannel 抽象/交互清单/切片 S1~S6）
- **verification**: 每切片真机收发验收（S2 验收标准: 输入关键词 3 秒内定位目标设备）
- **rollback**: 独立新页面，不影响产测模式
- **预估**: 6~8 轮
- **status**: approved（用户指令触发）
