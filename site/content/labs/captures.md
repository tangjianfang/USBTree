---
title: 抓包教学样本
description: 6 份按官方规范重构的逐包标注：全速枚举、控制传输三阶段、中断 IN 轮询、BOT 读扇区、同步流与反馈、PD 协商。CRC 实算并有脚本自动复核；另附真实抓包的三条获取路线。
level: 2
---

:::caution[先读这一段]
目录 [captures/](labtree:captures) · usb-labs @ `c990292`。这些帧序列是**按官方规范重构的教学样本，不是真实设备抓包**。它们回答“规范的字节应该长什么样”，不能替代真实 trace 中的时序抖动、重试、位填充与设备怪癖。设备身份（VID/PID、字符串）、采样数据、帧号等内容性字节均标为“示意值”。
:::

## 六份样本

| 样本 | 看什么 | 对应概念 |
|---|---|---|
| [00 · 全速枚举逐包标注](labsrc:captures/00-全速枚举逐包标注.md) | 复位 → GET_DESCRIPTOR(8) → SET_ADDRESS → 完整描述符 → 配置 | [枚举流程与标准请求](page:10-树干-USB核心/08-枚举流程与标准请求.md) |
| [01 · 控制传输三阶段](labsrc:captures/01-控制传输三阶段.md) | SETUP / DATA / STATUS 与 DATA0/DATA1 规则 | [包格式与事务](page:10-树干-USB核心/05-包格式与事务.md) |
| [02 · 中断 IN 轮询](labsrc:captures/02-中断IN轮询.md) | HID 鼠标报告与 NAK 节拍 | [四种传输类型](page:10-树干-USB核心/06-四种传输类型.md) · [鼠标详解](page:20-枝干-设备类协议/HID-人机接口设备/06-鼠标详解.md) |
| [03 · 批量 BOT 读扇区](labsrc:captures/03-批量BOT读扇区.md) | CBW → DATA 512 → CSW，以及出错场景 | [MSC 与 BOT](page:20-枝干-设备类协议/MSC-大容量存储/00-MSC概述与BOT.md) |
| [04 · 同步流与反馈](labsrc:captures/04-同步流与反馈.md) | UAC 异步播放的反馈端点 | [UAC 1.0 详解](page:20-枝干-设备类协议/Audio-UAC/01-UAC1.0详解.md) |
| [05 · PD 协商序列](labsrc:captures/05-PD协商序列.md) | Source_Capabilities → Request → Accept → PS_RDY，消息级标注 | [USB PD 协议](page:30-枝干-接口与供电/04-USBPD协议.md) |

## 字节是怎么保证正确的

- 结构性字段（PID、请求、描述符、CBW/CSW、Sense、PD Header/PDO/RDO）严格按规范取值；
- CRC5 / CRC16 由 [tools/_usbcalc.py](labsrc:tools/_usbcalc.py) 按 USB 2.0 §8.3.5 实算（脚本内嵌规范余数 `01100B` / `1000000000001101B` 与 CRC-16/USB 目录校验值 `0xB4C8` 双重断言）；
- [tools/_verify_captures.py](labsrc:tools/_verify_captures.py) 自动复核各 md 里的全部包字节。**本次复跑结果：DATA 44 通过 / 0 失败（3 处省略号跳过），TOKEN 14 通过 / 0 失败。**

```bash
python tools/_verify_captures.py
```

## 真实抓包从哪来

按成本从低到高（详见 [captures/README](labsrc:captures/README.md)）：

1. **下载现成的**：Wireshark 官方 SampleCaptures 页面里的 USB pcap、分析仪厂商的 demo 文件；
2. **软件抓**：Linux `usbmon`（[usbmon_howto.md](labsrc:tools/usbmon_howto.md)）、Windows USBPcap，配合 [Wireshark 过滤器速查](labsrc:tools/wireshark_filters.md)；
3. **硬件分析仪**：看电气层、精确时序与位填充时必须用。知识树里的对照：[协议分析仪与抓包](page:70-枝干-调试测试与安全/01-协议分析仪与抓包.md)。
