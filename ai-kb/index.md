---
title: "USB 知识库索引（AI 参考）"
topic: index
level: 入门
keywords: ["USB","index","knowledge base","USBTree"]
source_repo: "https://github.com/tangjianfang/USBTree"
usbtree_commit: 03306ba
generated: 2026-11-28
---

# USB 知识库索引（AI 参考）

用途：供 AI 代理检索 USB（及相关 Type-C/PD、USB4、BLE-HID）技术事实。每个文件 = 一个主题；frontmatter 含 level、keywords、sources（USBTree 原文路径与 URL）、spec_refs、related。
每个文件结构：`核心事实 Key Facts`（手工整理、已核对，含对 USBTree 原文的勘误）→ `原文：…`（USBTree 原文清洗版：去导航/emoji，链接改写为 KB 内链或 GitHub URL，保留表格、代码、Mermaid）。
冲突处理优先级：官方规范 > 本库 Key Facts > USBTree 原文。`llms-full.md` 为全部文件按顺序拼接的单文件版本。

## 文件列表

| 文件 | 标题 | 层级 | 主题 | 关键词 |
|---|---|---|---|---|
| [01-overview-versions.md](01-overview-versions.md) | USB 概述、版本演进与命名 | 入门 | `core` | USB 1.1, USB 2.0, USB 3.2 Gen 2x2, USB4, USB4 v2, 速率 speed, 命名 naming, USB-IF |
| [02-architecture-topology.md](02-architecture-topology.md) | 体系架构、拓扑、端点与管道、集线器 | 入门 | `core` | host, hub, function, tiered star 分层星型, endpoint 端点, pipe 管道, interface 接口, configuration 配置 |
| [03-physical-signaling.md](03-physical-signaling.md) | 物理层、电气特性与信号编码 | 进阶 | `core` | VBUS, D+/D-, pull-up 上拉 1.5k, speed detection 速度检测, chirp, NRZI, bit stuffing 位填充, SYNC |
| [04-packets-transactions.md](04-packets-transactions.md) | 包格式、PID、事务、帧与 Data Toggle | 进阶 | `core` | PID, token packet, data packet, handshake, ACK, NAK, STALL, NYET |
| [05-transfer-types-bandwidth.md](05-transfer-types-bandwidth.md) | 四种传输类型、bInterval 与带宽调度 | 进阶 | `core` | control transfer, bulk, interrupt, isochronous, bInterval, wMaxPacketSize, polling rate 回报率, 1000 Hz |
| [06-descriptors.md](06-descriptors.md) | 标准描述符字段全表 | 进阶 | `core` | device descriptor 设备描述符, configuration descriptor, interface descriptor, endpoint descriptor, string descriptor, IAD, BOS, device qualifier |
| [07-enumeration-requests.md](07-enumeration-requests.md) | 枚举流程、Setup 包与标准请求 | 进阶 | `core` | enumeration 枚举, setup packet, bmRequestType, GET_DESCRIPTOR, SET_ADDRESS, SET_CONFIGURATION, SET_INTERFACE, CLEAR_FEATURE |
| [08-power-management.md](08-power-management.md) | 电源管理：挂起、远程唤醒、LPM、U1/U2/U3 | 进阶 | `core` | suspend 挂起, resume, remote wakeup 远程唤醒, selective suspend 选择性挂起, LPM, L1, L2, U0 |
| [09-errors-testmode.md](09-errors-testmode.md) | 错误处理、可靠性、Test Mode 与调试模式 | 深入 | `core` | CRC, retry 三次重试, STALL, babble, timeout, toggle resync, PING/NYET, TEST_MODE |
| [10-class-index.md](10-class-index.md) | 设备类代码索引与驱动映射 | 入门 | `class` | class code 类代码, bDeviceClass, bInterfaceClass, 0x03 HID, 0x08 MSC, 0x0E UVC, 0x01 Audio, 0x02 CDC |
| [11-hid-core.md](11-hid-core.md) | HID 核心：类描述符、报告描述符 Item、Usage、类请求 | 进阶 | `class/hid` | HID, report descriptor 报告描述符, item, Usage Page, Usage, Collection, Report ID, Input/Output/Feature report |
| [12-hid-devices.md](12-hid-devices.md) | HID 典型设备：键盘、鼠标、消费控制、手柄、触控、跨传输、完整描述符 | 进阶 | `class/hid` | boot keyboard report, NKRO, modifier, boot mouse, polling rate, consumer control, gamepad, digitizer |
| [13-hid-spec-appendix.md](13-hid-spec-appendix.md) | HID 规范级附录（全表） | 深入 | `class/hid` | HID item table, usage tables, unit encoding, HID spec appendix, PID force feedback, sensor usages |
| [14-cdc.md](14-cdc.md) | CDC：ACM 虚拟串口、ECM/NCM/RNDIS 网络、请求与通知全表 | 进阶 | `class/cdc` | CDC, ACM, virtual COM, SET_LINE_CODING, SET_CONTROL_LINE_STATE, SERIAL_STATE, ECM, NCM |
| [15-msc.md](15-msc.md) | MSC：BOT、CBW/CSW、SCSI 命令与 Sense 全表 | 进阶 | `class/msc` | mass storage, BOT, bulk-only, CBW, CSW, SCSI, UFI, UAS |
| [16-uvc.md](16-uvc.md) | UVC：视频类控制、格式、Probe/Commit 全表 | 进阶 | `class/uvc` | UVC, VideoControl, VideoStreaming, Camera Terminal, Processing Unit, Extension Unit, probe commit, payload header |
| [17-uac.md](17-uac.md) | UAC：音频类 1.0/2.0/3.0、实体与请求全表 | 进阶 | `class/uac` | UAC, UAC1, UAC2, UAC3, AudioControl, AudioStreaming, Feature Unit, Clock Source |
| [18-other-classes-a.md](18-other-classes-a.md) | 其他设备类 A：DFU、CCID、PTP/MTP、Printer | 进阶 | `class/other` | DFU, DFU_DNLOAD, dfuIDLE, CCID, APDU, PC_to_RDR, PTP, MTP |
| [19-other-classes-b.md](19-other-classes-b.md) | 其他设备类 B：蓝牙 HCI、WebUSB/厂商类、MIDI、USBTMC、长尾类、AV、PHDC | 进阶 | `class/other` | Bluetooth HCI over USB, btusb, WebUSB, MS OS 2.0 descriptor, WinUSB compatible ID, vendor class, MIDI, USB-MIDI event packet |
| [20-connectors-typec.md](20-connectors-typec.md) | 连接器演进与 USB Type-C（含 CC 状态机与时序） | 进阶 | `phy/typec` | Type-A, Micro-B, Type-C, CC, Rp, Rd, Ra, VCONN |
| [21-charging-bc12-otg.md](21-charging-bc12-otg.md) | 充电：BC 1.2、专有快充；OTG 与角色切换 HNP/SRP | 进阶 | `power` | BC1.2, SDP, CDP, DCP, primary detection, secondary detection, QC, 快充 |
| [22-usb-pd.md](22-usb-pd.md) | USB Power Delivery：协议、状态机与消息全表 | 深入 | `power/pd` | USB PD, BMC, SOP, GoodCRC, Source_Capabilities, Request, Accept, PS_RDY |
| [23-altmode-emarker.md](23-altmode-emarker.md) | Alternate Mode、Structured VDM 与 E-marker | 深入 | `power/pd` | Alt Mode, DisplayPort Alt Mode, SVID, 0xFF01, Discover Identity, Discover SVIDs, Discover Modes, Enter Mode |
| [30-usb3-superspeed.md](30-usb3-superspeed.md) | USB 3.x SuperSpeed：包格式、LTSSM、定时器 | 深入 | `speed/usb3` | SuperSpeed, LTSSM, U0, U1, U2, U3, Polling, Recovery |
| [31-usb4.md](31-usb4.md) | USB4：路由器、隧道、配置空间、DROM、连接管理器 | 深入 | `speed/usb4` | USB4, router, adapter, tunnel 隧道, path, connection manager, CM, Thunderbolt 3 |
| [40-host-controller-os.md](40-host-controller-os.md) | 主机控制器栈与操作系统 USB 支持 | 进阶 | `host` | UHCI, OHCI, EHCI, xHCI, TRB, transfer ring, event ring, doorbell |
| [41-windows-driver.md](41-windows-driver.md) | Windows USB 驱动开发：选型、WinUSB、KMDF/UMDF、调试 | 深入 | `host/windows` | WinUSB, WinUsb_ReadPipe, WinUsb_ControlTransfer, KMDF, UMDF, WDFUSBDEVICE, WDFUSBPIPE, continuous reader |
| [42-linux-macos-libusb.md](42-linux-macos-libusb.md) | libusb 用户态访问、Linux Gadget/usbip、macOS 与 Linux 主机开发 | 进阶 | `host/linux-macos` | libusb, libusb_control_transfer, libusb_bulk_transfer, async transfer, hidapi, Zadig, usbfs, udev |
| [43-device-firmware.md](43-device-firmware.md) | 设备端固件栈与 TinyUSB 实战 | 进阶 | `device/firmware` | TinyUSB, tud_task, tud_descriptor_device_cb, tud_hid_report, tud_hid_set_report_cb, tusb_config.h, DCD, USBD |
| [50-debug-troubleshooting.md](50-debug-troubleshooting.md) | 协议分析仪、抓包与枚举失败排查 | 进阶 | `debug` | protocol analyzer, Beagle, Ellisys, USBPcap, usbmon, Wireshark filter usb., enumeration failure, device descriptor request failed |
| [51-compliance-security.md](51-compliance-security.md) | USB-IF 合规认证、合规测试实操与 USB 安全 | 深入 | `compliance/security` | USB-IF compliance, USBCV, Chapter 9 test, HID test, electrical test, eye diagram, PlugFest, TID |
| [60-usb-wireless-intersection.md](60-usb-wireless-intersection.md) | 无线与 USB 的交汇：HCI-over-USB、HOGP、Wireless USB/MA-USB 历史 | 进阶 | `wireless` | HOGP, HID over GATT, HID Service 0x1812, Report Map 0x2A4B, Report 0x2A4D, Protocol Mode 0x2A4E, HCI, btusb |
| [61-ble-core.md](61-ble-core.md) | BLE 核心：概述、链路层/物理层、广播与连接、ATT/GATT、GAP、SMP、经典蓝牙对比 | 进阶 | `wireless/ble` | BLE, link layer, PHY 1M 2M Coded, advertising, connection interval, ATT, GATT, GAP |
| [62-ble-advanced.md](62-ble-advanced.md) | BLE 进阶：LE Audio/LC3、Mesh、经典 Profile、LLCP、测向与信道探测、RF 参数、A2DP/AVDTP | 深入 | `wireless/ble` | LE Audio, LC3, CIS, BIS, Auracast, Mesh, A2DP, AVRCP |
| [63-ble-uuid.md](63-ble-uuid.md) | 蓝牙标准 UUID 全表 | 深入 | `wireless/ble` | UUID, 16-bit UUID, service UUID, characteristic UUID, descriptor UUID, assigned numbers |
| [90-quick-reference.md](90-quick-reference.md) | 速查表大全与时序参数全表 | 进阶 | `reference` | cheat sheet 速查, timing parameters 时序参数, constants, bInterval table, PID table, descriptor types, reset timing, resume timing |
| [91-glossary.md](91-glossary.md) | 术语表（中英对照） | 入门 | `reference` | glossary 术语, terminology, abbreviations 缩写 |
| [92-spec-references.md](92-spec-references.md) | 官方规范参考与缓存索引 | 入门 | `reference` | specifications, usb.org, Bluetooth SIG, spec cache, spec_fetch |

## 按问题找文件

| 问题类型 | 先看 |
|---|---|
| 字段偏移/长度、描述符类型码 | 06-descriptors, 11-hid-core |
| Setup 包、标准/类/厂商请求码 | 07-enumeration-requests, 11-hid-core, 14-cdc, 15-msc, 16-uvc |
| PID、事务、toggle、帧 | 04-packets-transactions |
| bInterval、回报率、带宽 | 05-transfer-types-bandwidth, 12-hid-devices |
| 枚举失败、代码 43、dmesg 错误 | 50-debug-troubleshooting, 07-enumeration-requests |
| Windows HID/WinUSB/KMDF API | 41-windows-driver, 11-hid-core |
| PD 消息、PDO、EPR | 22-usb-pd |
| Type-C 电阻、CC 时序 | 20-connectors-typec |
| USB3 LTSSM、包格式 | 30-usb3-superspeed |
| USB4 隧道 | 31-usb4 |
| 固件 TinyUSB | 43-device-firmware |
| BLE HOGP 与 USB HID 对应 | 60-usb-wireless-intersection |
| 数值/时序速查 | 90-quick-reference |

## 术语统一（中文 ↔ English）

| 中文 | English |
|---|---|
| 主机 | Host |
| 设备 / 功能 | Device / Function |
| 集线器 | Hub |
| 端点 | Endpoint (EP) |
| 管道 | Pipe |
| 接口 | Interface |
| 备用设置 | Alternate Setting |
| 配置 | Configuration |
| 描述符 | Descriptor |
| 枚举 | Enumeration |
| 事务 | Transaction |
| 传输 | Transfer |
| 控制/批量/中断/同步传输 | Control / Bulk / Interrupt / Isochronous |
| 帧 / 微帧 | Frame (1 ms) / Microframe (125 µs) |
| 数据翻转 | Data Toggle |
| 握手 | Handshake |
| 零长度包 | Zero-Length Packet (ZLP) |
| 复合设备 | Composite Device |
| 接口关联描述符 | Interface Association Descriptor (IAD) |
| 事务转换器 | Transaction Translator (TT) |
| 挂起 / 恢复 / 远程唤醒 | Suspend / Resume / Remote Wakeup |
| 报告描述符 | Report Descriptor |
| 顶层集合 | Top-Level Collection (TLC) |
| 供电方 / 受电方 | Source / Sink |
| 数据下行/上行端口 | DFP / UFP |
| 双角色端口 | Dual-Role Port (DRP) |
| 功率数据对象 | Power Data Object (PDO) |
| 请求数据对象 | Request Data Object (RDO) |
| 替代模式 | Alternate Mode |
| 电子标签线缆 | Electronically Marked Cable (E-marker) |
| 链路训练状态机 | LTSSM |
| 连接管理器 | Connection Manager (CM) |
| 隧道 | Tunnel |
| 主机控制器接口 | xHCI / EHCI / OHCI / UHCI |

## 已知 USBTree 原文勘误（已在对应 Key Facts 中更正）

- `30-枝干-接口与供电/08-USBPD消息全表.md` 开篇仍写「PD 规范本体未缓存（门控下载）」，同页文末以及 `80-参考资料/README.md`、`skills/usb-spec-lookup/SKILL.md` 已登记 `usb-core/USB-PD-3.2-V1.2.zip`。→ 22-usb-pd
- `90-附录/03-时序参数全表.md` §4 来源说明仍写「未缓存 USB PD 规范原文」，同表 tFirstSourceCap 行又写「PD 3.2 V1.2 已缓存」。→ 90-quick-reference
