---
id: 10-class-index
title: "设备类代码索引与驱动映射"
topic: class
level: 入门
keywords: ["class code 类代码", "bDeviceClass", "bInterfaceClass", "0x03 HID", "0x08 MSC", "0x0E UVC", "0x01 Audio", "0x02 CDC", "0xEF misc", "0xFF vendor", "0xE0 wireless"]
sources:
  - path: "20-枝干-设备类协议/00-设备类索引.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/20-枝干-设备类协议/00-设备类索引.md"
spec_refs: ["USB-IF Defined Class Codes"]
related: ["11-hid-core", "14-cdc", "15-msc", "16-uvc", "17-uac", "18-other-classes-a", "19-other-classes-b"]
usbtree_commit: d8dc27d
generated: 2026-11-29
---

# 设备类代码索引与驱动映射

> 层级 入门 · 主题 `class` · 相关：[HID 核心：类描述符、报告描述符 Item、Usage、类请求](11-hid-core.md)、[CDC：ACM 虚拟串口、ECM/NCM/RNDIS 网络、请求与通知全表](14-cdc.md)、[MSC：BOT、CBW/CSW、SCSI 命令与 Sense 全表](15-msc.md)、[UVC：视频类控制、格式、Probe/Commit 全表](16-uvc.md)、[UAC：音频类 1.0/2.0/3.0、实体与请求全表](17-uac.md)、[其他设备类 A：DFU、CCID、PTP/MTP、Printer](18-other-classes-a.md)、[其他设备类 B：蓝牙 HCI、WebUSB/厂商类、MIDI、USBTMC、长尾类、AV、PHDC](19-other-classes-b.md)

## 核心事实 Key Facts

> 由维护者整理并与规范核对；与下方 USBTree 原文冲突时以本节为准。

| 类代码 | 类 | 使用层级 | Windows 内置驱动 | Linux 驱动 |
|---|---|---|---|---|
| 0x00 | 按接口定义 | Device | — | — |
| 0x01 | Audio (UAC) | Interface | usbaudio.sys / usbaudio2.sys | snd-usb-audio |
| 0x02 | CDC Control | Both | usbser.sys / UsbNcm.sys | cdc_acm / cdc_ether / cdc_ncm |
| 0x03 | HID | Interface | hidusb.sys + hidclass.sys | usbhid (+hidraw) |
| 0x05 | Physical | Interface | — | — |
| 0x06 | Still Image (PTP/MTP) | Interface | WPD (WpdMtp) | 用户态 libmtp/libgphoto2 |
| 0x07 | Printer | Interface | usbprint.sys | usblp |
| 0x08 | Mass Storage | Interface | usbstor.sys / uaspstor.sys | usb-storage / uas |
| 0x09 | Hub | Device | usbhub.sys / usbhub3.sys | hub (usbcore) |
| 0x0A | CDC Data | Interface | (同 CDC) | |
| 0x0B | Smart Card (CCID) | Interface | usbccid / WUDFUsbccidDriver | pcscd + libccid |
| 0x0D | Content Security | Interface | | |
| 0x0E | Video (UVC) | Interface | usbvideo.sys | uvcvideo |
| 0x0F | Personal Healthcare (PHDC) | Interface | | |
| 0x10 | Audio/Video Devices | Interface | | |
| 0x11 | Billboard | Device | | |
| 0x12 | USB Type-C Bridge | Interface | | |
| 0x3C | I3C | Interface | | |
| 0xDC | Diagnostic | Both | | |
| 0xE0 | Wireless Controller（Bluetooth 0xE0/0x01/0x01） | Interface | BthUsb.sys | btusb |
| 0xEF | Miscellaneous（0xEF/0x02/0x01 = IAD 复合） | Both | usbccgp.sys | usbcore |
| 0xFE | Application Specific（0x01 DFU, 0x02 IrDA, 0x03 USBTMC） | Interface | | usbtmc |
| 0xFF | Vendor Specific | Both | WinUSB / 厂商驱动 | libusb / 厂商驱动 |

## 原文：00-设备类索引

> Source: [20-枝干-设备类协议/00-设备类索引.md](https://github.com/tangjianfang/USBTree/blob/main/20-枝干-设备类协议/00-设备类索引.md)

> 上一级: [知识树总图](92-spec-references.md) · 基础: [描述符详解](06-descriptors.md)

设备类 (Device Class) 是 USB 知识树最大的枝干群：USB 核心只解决"怎么传"，设备类回答"传的是什么"。主机靠接口描述符的 `bInterfaceClass / bInterfaceSubClass / bInterfaceProtocol` 三元组绑定类驱动（详见[描述符详解](06-descriptors.md)）。

### 类代码总表

| bInterfaceClass | 名称 | 本库位置 | 典型设备 |
|---|---|---|---|
| 0x00 | 类在设备级声明 | — | 特殊布局设备 |
| 0x01 | Audio | [Audio-UAC/](17-uac.md) | 声卡、麦克风、MIDI |
| 0x02 | CDC-Control | [CDC-通信设备类/](14-cdc.md) | 虚拟串口、调制解调器 |
| 0x03 | HID | [HID-人机接口设备/](11-hid-core.md) | 键鼠、手柄、触摸、传感器 |
| 0x05 | Physical | [其他设备类/09-长尾设备类](19-other-classes-b.md) | 康复/运动设备 |
| 0x06 | Image (Still Capture) | [其他设备类/03-PTP与MTP](18-other-classes-a.md) | 相机、手机 MTP |
| 0x07 | Printer | [其他设备类/04-Printer打印机类](18-other-classes-a.md) | 打印机 |
| 0x08 | Mass Storage | [MSC-大容量存储/](15-msc.md) | U 盘、读卡器、硬盘 |
| 0x09 | Hub | 树干: [集线器与连接管理](02-architecture-topology.md) | 集线器 |
| 0x0A | CDC-Data | [CDC-通信设备类/](14-cdc.md) | CDC 的数据接口 |
| 0x0B | Smart Card | [其他设备类/02-CCID智能卡](18-other-classes-a.md) | YubiKey、读卡器 |
| 0x0E | Video | [Video-UVC/](16-uvc.md) | 摄像头、采集卡 |
| 0x0F | Personal Healthcare (PHDC) | [其他设备类/11-PHDC健康医疗类](19-other-classes-b.md)（概览见 [09](19-other-classes-b.md)） | 血压计、健康秤 |
| 0x10 | Audio/Video | [其他设备类/10-AV设备类详解](19-other-classes-b.md)（概览见 [09](19-other-classes-b.md)） | AV 设备（少用） |
| 0x11 | Billboard | [其他设备类/09-长尾设备类](19-other-classes-b.md) | Type-C 拓扑告示牌 |
| 0x12 | Type-C Bridge | [其他设备类/09-长尾设备类](19-other-classes-b.md) | 双口桥接调试 |
| 0x3C | I3C Device Class | [其他设备类/09-长尾设备类](19-other-classes-b.md) | I3C 隧道化调试 |
| 0xE0 | Wireless Controller | [其他设备类/05-蓝牙控制器类](19-other-classes-b.md) | **蓝牙适配器（HCI over USB）** |
| 0xEF | Miscellaneous | [其他设备类/06-WebUSB与厂商自定义类](19-other-classes-b.md) | RNDIS、IAD 复合声明 |
| 0xFE | Application Specific | [其他设备类/01-DFU固件升级](18-other-classes-a.md) · [08-USBTMC](19-other-classes-b.md) | DFU（协议 0x01）、USBTMC（子类 0x03） |
| 0xFF | Vendor Specific | [其他设备类/06-WebUSB与厂商自定义类](19-other-classes-b.md) | FTDI/CH340、私有协议 |

设备级类代码 (bDeviceClass) 的特殊值：0x00=类在各接口声明（最常见）、0x09=集线器、0xEF/0x02/0x01=带 IAD 的复合设备、0x02/0x00/0x00=CDC 设备级声明。

### 分枝导航

| 分枝 | 一句话定位 | 核心概念 |
|---|---|---|
| [HID](11-hid-core.md) | 自我描述的人机接口 | 报告描述符、Usage、Boot 协议、跨传输 |
| [CDC](14-cdc.md) | 串口/网络通信 | ACM 虚拟串口、ECM/NCM/RNDIS、[请求与通知全表](14-cdc.md) |
| [MSC](15-msc.md) | 块设备存储 | BOT/CBW/CSW、SCSI 命令、UAS、[操作码与 Sense 全表](15-msc.md) |
| [UAC](17-uac.md) | 数字音频 | 实体图、时钟同步、反馈端点 |
| [UVC](16-uvc.md) | 视频流 | Probe/Commit、帧描述符、格式、[控制与格式全表](16-uvc.md) |
| [其他设备类](18-other-classes-a.md) | DFU/CCID/PTP/打印机/蓝牙控制器/WebUSB/MIDI | 各类专用机制 |

### 复合设备：一根树干上多根分枝

一台真实设备往往是复合设备 (Composite Device)——一个设备、多个接口、每个接口是一个设备类：

```
无线键鼠接收器 (composite)
├── 接口0: HID/键盘 (0x03)
├── 接口1: HID/鼠标 (0x03)
└── 接口2: 厂商自定义 0xFF (配置私有通道)
蓝牙适配器: 单接口 Wireless Controller (0xE0)
手机: MTP (0x06) + ADB (0xFF) + Audio (0x01) 复合
```

多接口功能的组合需要 **IAD** 描述符捆扎（[描述符详解](06-descriptors.md)），固件构造方法见[设备端固件栈](43-device-firmware.md)。
