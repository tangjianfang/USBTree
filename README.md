# USBTree · USB/BLE 领域知识系统

> **知识树 × 关系图谱 × 可执行技能 × 官方规范缓存**

以 **USB** 为树干、把所有依赖/关联 USB 的协议（HID、CDC、MSC、UAC、UVC、Type-C/PD、USB4、BLE……）作为枝干，层层递进到分枝与树叶知识点的中文知识系统。四种形态各司其职：正文知识树供人研读，`graph/` 关系图谱供机器查询，`skills/` 技能包供 Agent 执行，`80-参考资料/` 官方规范缓存作为最终裁判；`tools/validate.sh` 一键校验全库一致性，`COVERAGE.md` 记录覆盖率。

## 🌳 树的比喻

| 部位 | 内容 | 位置 |
|---|---|---|
| 🌱 根 | 总览与地图 | 本文件、[知识树总图](00-知识树总图.md) |
| 🌳 树干 | USB 核心协议（12 篇） | [10-树干-USB核心/](10-树干-USB核心/01-概述与版本演进.md) |
| 🌿 主枝 | 六大枝干：设备类 / 接口与供电 / 高速演进 / 无线关联 / 主机侧实现 / 调试安全 | `20~70` 目录 |
| 🍃 分枝→叶 | HID 报告描述符、BOT 传输、PD 协商、GATT 服务……直到单个字段/命令/电阻值 | 各枝干内的文件与小节 |

## 📂 目录结构

```
USBTree/
├── README.md · 00-知识树总图.md
├── 10-树干-USB核心/                  ← 一切的基础 (13 篇)
│   ├── 01 概述与版本演进   02 体系架构与分层模型
│   ├── 03 物理层与电气特性 04 信号编码与比特流
│   ├── 05 包格式与事务     06 四种传输类型
│   ├── 07 描述符详解       08 枚举流程与标准请求
│   ├── 09 集线器与连接管理 10 电源管理与挂起唤醒
│   ├── 11 错误处理与可靠性 12 TestMode与调试模式
│   └── 13 总线带宽与调度计算
├── 20-枝干-设备类协议/
│   ├── 00-设备类索引.md
│   ├── HID-人机接口设备/      (13 篇: 描述符/报告/Usage/键鼠/触摸/跨传输 + 规范级附录)
│   ├── CDC-通信设备类/        (4 篇: 概述/ACM 虚拟串口/ECM-NCM-RNDIS/请求通知全表)
│   ├── MSC-大容量存储/        (3 篇: BOT/SCSI 与 UFI/操作码与 Sense 全表)
│   ├── Audio-UAC/             (4 篇: 概述/UAC1/UAC2-3/实体与请求全表)
│   ├── Video-UVC/             (2 篇: UVC 详解/控制与格式全表)
│   └── 其他设备类/            (11 篇: DFU/CCID/PTP-MTP/打印机/蓝牙控制器/WebUSB/MIDI/USBTMC/长尾类/AV/PHDC)
├── 30-枝干-接口与供电/        (9 篇: 接口形态/Type-C/BC1.2/USB PD/AltMode/OTG与HNP/PD深入/PD消息全表/TypeC状态机)
├── 40-枝干-高速演进/          (7 篇: USB3.x/USB4 与雷电/版本对比/USB3x包格式与LTSSM/USB4深入/USB3x规范级/USB4规范级)
├── 50-枝干-无线关联/
│   ├── 00-无线概览与USB交汇.md · 99-WirelessUSB与MA-USB历史.md
│   └── BLE-低功耗蓝牙/        (16 篇: 架构HCI/链路层/广播/ATT-GATT/GAP/SMP/HOGP/对比/LEAudio/Mesh/经典Profile/LLCP全表/测向与信道探测/RF参数全表/A2DP参数)
├── 60-枝干-主机侧与实现/      (9 篇: 主机控制器栈/操作系统/固件栈/libusb/实战TinyUSB/实战libusb/实战Gadget与usbip/Windows驱动开发/macOS与Linux主机开发)
├── 70-枝干-调试测试与安全/    (5 篇: 抓包/排查手册/合规认证/USB 安全与 BadUSB/合规测试实操)
├── 80-参考资料/               (官方规范原文缓存: 34 份 223MB + 索引 README + 提取文本)
├── 90-附录/                   (3 篇: 术语表/速查表大全/时序参数全表)
├── graph/                     (知识图谱: entities.yaml 实体表 · relations.yaml 关系表 · export.mmd 全景图)
├── skills/                    (Agent 技能包: 枚举排查/抓包分析/规范检索/设备构建)
├── tools/                     (validate.sh · gen_graph.sh · inject_frontmatter.sh)
└── COVERAGE.md                (覆盖率记分卡: 分领域百分比与维护规则)
```

## 🧭 快速导航

**我想…**

- 从零学 USB → [概述与版本演进](10-树干-USB核心/01-概述与版本演进.md) 按编号顺序读完树干
- 做键鼠/手柄固件 → [HID 概述](20-枝干-设备类协议/HID-人机接口设备/00-HID概述与定位.md)
- 做虚拟串口 → [CDC-ACM](20-枝干-设备类协议/CDC-通信设备类/01-虚拟串口ACM.md)
- 理解 U 盘/读卡器 → [MSC 与 BOT](20-枝干-设备类协议/MSC-大容量存储/00-MSC概述与BOT.md)
- 做声卡/麦克风 → [UAC 概述](20-枝干-设备类协议/Audio-UAC/00-UAC概述.md)
- 做摄像头/采集卡 → [UVC 详解](20-枝干-设备类协议/Video-UVC/00-UVC详解.md)
- 玩充电头/快充/线缆 → [Type-C](30-枝干-接口与供电/02-USBType-C详解.md) → [USB PD](30-枝干-接口与供电/04-USBPD协议.md)
- 搞蓝牙/BLE → [无线概览：USB 与 BLE 的交汇](50-枝干-无线关联/00-无线概览与USB交汇.md) → [BLE 子树](50-枝干-无线关联/BLE-低功耗蓝牙/00-BLE概述.md)
- 设备枚举不出来 → [枚举失败排查手册](70-枝干-调试测试与安全/02-枚举失败排查手册.md)
- 抓 USB 包 → [协议分析仪与抓包](70-枝干-调试测试与安全/01-协议分析仪与抓包.md)
- 写主机程序操作设备 → [libusb 与用户态访问](60-枝干-主机侧与实现/04-libusb与用户态访问.md)
- 查官方规范原文 → [80-参考资料/README.md](80-参考资料/README.md)（28 份官方规范本地缓存 + 直链索引）
- 深入 USB PD 状态机/消息全表 → [USBPD 深入](30-枝干-接口与供电/07-USBPD深入-状态机与消息全表.md)
- 深入 USB3 信号与 LTSSM → [USB3x 包格式与 LTSSM](40-枝干-高速演进/04-USB3x包格式与LTSSM.md)
- 学 LE Audio / Auracast → [LEAudio 与 LC3](50-枝干-无线关联/BLE-低功耗蓝牙/09-LEAudio与LC3.md)
- 做仪器/示波器通信 → [USBTMC](20-枝干-设备类协议/其他设备类/08-USBTMC测试测量类.md)
- 从零跑通固件/主机程序 → [实战 TinyUSB](60-枝干-主机侧与实现/05-实战-TinyUSB设备固件.md) · [实战 libusb](60-枝干-主机侧与实现/06-实战-libusb主机程序.md)
- 查一个缩写/编码 → [术语表](90-附录/01-术语表.md) · [速查表大全](90-附录/02-速查表大全.md)

## 🎯 三条阅读路径

1. **驱动/内核**: 树干 → [主机控制器栈](60-枝干-主机侧与实现/01-主机控制器栈全景.md) → [抓包](70-枝干-调试测试与安全/01-协议分析仪与抓包.md)
2. **嵌入式固件**: 树干 06/07/08 → 目标设备类 → [固件栈](60-枝干-主机侧与实现/03-设备端固件栈.md) → [排查手册](70-枝干-调试测试与安全/02-枚举失败排查手册.md)
3. **硬件/电源**: 树干 03/10 → [接口与供电](30-枝干-接口与供电/01-接口形态演进.md) → [高速演进](40-枝干-高速演进/01-USB3x与SuperSpeed.md)

## 📌 两条主干交汇说明

- **BLE 并不依赖 USB**。它与 USB 的真实交汇在：USB 蓝牙适配器（HCI over USB）、HID 报告描述符跨传输复用（HOGP）、2.4G 私有无线 dongle。详见[无线概览](50-枝干-无线关联/00-无线概览与USB交汇.md)。
- **Type-C ≠ USB 速率**：接口形态与数据速率、供电协议三者解耦，详见[Type-C 详解](30-枝干-接口与供电/02-USBType-C详解.md)。

## 🤖 Agent 使用指南（Graph + Skill 双引擎）

- **Graph 回答"知道什么"**：`graph/entities.yaml`（80 个实体：协议/类/机制，带类码与主文档）+ `graph/relations.yaml`（82 条类型化关系边：carries/reuses/supersedes/tunnels/enables…，每条边带 evidence 指向正文）。查询示例："HOGP reuses HID-ReportDescriptor"——跨传输复用、代际更替（BOT→UAS、ECM→NCM、OTG→DRP）、隧道承载（USB4→USB3/PCIe/DP）全部结构化可查；全景图见 `graph/export.mmd`。
- **Skill 回答"怎么做"**：`skills/` 下四个技能包，均含触发条件、分步动作、验证命令与回退路径——
  1. [usb-enum-troubleshoot](skills/usb-enum-troubleshoot/SKILL.md)：枚举失败分阶段排查；
  2. [usb-capture-analysis](skills/usb-capture-analysis/SKILL.md)：trace 分析方法论与异常特征表；
  3. [usb-spec-lookup](skills/usb-spec-lookup/SKILL.md)：速查表→知识树→缓存规范 PDF 的四级检索策略；
  4. [build-usb-device](skills/build-usb-device/SKILL.md)：TinyUSB/libusb/gadget 三路工程模板路由。
- **激活方式**：将 `skills/<name>/` 拷贝到所用 Agent 平台的技能目录（如 ZCode 的 skills 目录），或直接把 SKILL.md 作为系统提示的一部分引用。
- **一致性保障**：`bash tools/validate.sh`（链接/围栏/图谱引用/frontmatter 四项检查）；`bash tools/gen_graph.sh` 在改动关系表后重新生成全景图。

## 🧾 声明

基于 USB-IF / Bluetooth SIG 公开规范整理，供学习与速查；规范原文（usb.org、bluetooth.com）为唯一权威依据。标注"见规范原文"处表示本库未固化不确定的编码细节。

## 🔧 如何扩展这棵树

新增节点规则：
1. 判断层级：核心机制 → 树干；协议族 → 新枝干目录；协议族内子模块 → 子目录；单点知识 → 文件内小节；
2. 文件开头按统一格式标注知识树位置与父节点链接，文末挂"相关节点"；
3. 更新 [00-知识树总图](00-知识树总图.md) 的 mindmap 与本 README 的目录树。
