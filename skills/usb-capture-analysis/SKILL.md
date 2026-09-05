---
name: usb-capture-analysis
description: 分析一份 USB 抓包/trace（Wireshark+usbmon/USBPcap 或硬件分析仪导出）。当用户给出 .pcap/.pcapng 抓包文件或粘贴的 USB trace，要求定位协议问题、解释枚举序列、统计 NAK/STALL、提取描述符或报告数据时使用。
---

# USB trace 分析方法论

## 适用场景（触发条件）

- 给出 usbmon/USBPcap/硬件分析仪的抓包文件，要求"看看哪里出了问题"；
- 要求解释一段枚举序列、找描述符内容、确认某类请求的参数；
- 要求统计设备行为（NAK 率、轮询间隔、实际带宽占用）。

## 第 0 步：建立抓包环境（若用户还没有抓包）

| 平台 | 方法 | 关键点 |
|---|---|---|
| Linux | `modprobe usbmon` → Wireshark 选 usbmonN 接口 | N 对应总线号（lsusb 的 Bus N） |
| Windows | 安装 USBPcap 后 Wireshark 选 USBPcapN | 需重插设备才开始捕获 |
| 硬件层 | 逻辑分析仪看 D+/D- 或专业分析仪 | 软件抓包看不到电气错误 |

详见 [协议分析仪与抓包](../../70-枝干-调试测试与安全/01-协议分析仪与抓包.md)。

## 第 1 步：结构化阅读顺序（不要顺着时间流硬看）

1. **先看枚举段**（通常在捕获开头）：对照标准序列逐包核对——复位 → GET_DESCRIPTOR(Device,64) → SET_ADDRESS → GET_DESCRIPTOR(18B) → 读配置(9B 再全长) → SET_CONFIGURATION。标准序列见 [枚举流程与标准请求](../../10-树干-USB核心/08-枚举流程与标准请求.md)；
2. **再找异常特征**（见下表）；
3. **最后看稳态数据流**，按事务三段式（Token→Data→Handshake）逐个事务判读，基础见 [包格式与事务](../../10-树干-USB核心/05-包格式与事务.md)。

## 第 2 步：异常特征对照表

| trace 特征 | 诊断方向 | 背景知识 |
|---|---|---|
| 同一 SETUP 重复多次 | 设备 STALL 后主机重试或请求被拒 | [STALL 语义](../../10-树干-USB核心/11-错误处理与可靠性.md) |
| 大量 NAK 无进展 | 设备端缓冲/固件卡死（流控失灵） | [四种传输类型](../../10-树干-USB核心/06-四种传输类型.md) |
| 数据包后无 ACK 且重发同 toggle | 接收方 CRC 错，重传正常但持续失败=电气问题 | [数据触发](../../10-树干-USB核心/11-错误处理与可靠性.md) |
| GET_DESCRIPTOR(config) 返回长度 ≠ wTotalLength | 描述符自相矛盾 → 枚举必败 | [描述符详解](../../10-树干-USB核心/07-描述符详解.md) |
| SET_ADDRESS 后主机仍用地址 0 | 设备提前/滞后切换地址（固件 bug） | [枚举](../../10-树干-USB核心/08-枚举流程与标准请求.md) |
| 中断 IN 长时间无查询 | 主机挂起了该设备（选择性挂起） | [电源管理](../../10-树干-USB核心/10-电源管理与挂起唤醒.md) |
| CSW Status=0x02（MSC） | 阶段错误，主机将做复位恢复 | [BOT](../../20-枝干-设备类协议/MSC-大容量存储/00-MSC概述与BOT.md) |
| 同步端点每微帧包长骤变 | 带宽挤占或设备时钟异常 | [UAC 概述](../../20-枝干-设备类协议/Audio-UAC/00-UAC概述.md) |

## 第 3 步：常用过滤与提取

```
usb.transfer_type == 0x02        # 中断传输
usb.transfer_type == 0x03        # 批量传输
usb.bmRequestType == 0x80 && usb.setup.bRequest == 6   # GET_DESCRIPTOR IN
usb.src == "1.2.1"               # 总线1.端口2.地址1 的设备
usb.capdata                      # 原始数据载荷
```

导出载荷：`tshark -r trace.pcapng -T fields -e usb.capdata`。

## 第 4 步：按设备类深入

识别出设备类后，切换到对应枝干的"抓包读法"章节：HID（[类请求](../../20-枝干-设备类协议/HID-人机接口设备/04-传输与类特定请求.md)）、MSC（[CBW/CSW 三段式](../../20-枝干-设备类协议/MSC-大容量存储/00-MSC概述与BOT.md)）、UVC（[Probe/Commit](../../20-枝干-设备类协议/Video-UVC/00-UVC详解.md)）、UAC（[反馈端点](../../20-枝干-设备类协议/Audio-UAC/01-UAC1.0详解.md)）、蓝牙适配器（[HCI over USB 端点映射](../../20-枝干-设备类协议/其他设备类/05-蓝牙控制器类-HCIoverUSB.md)）。

## 验证收尾

结论必须落到三选一：①根因+修复建议；②需电气层硬件分析仪升级抓取；③协议行为符合规范（问题在别处）。涉及规范原文判定的，转 [usb-spec-lookup](../usb-spec-lookup/SKILL.md)。
