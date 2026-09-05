---
name: usb-spec-lookup
description: 查询 USB/BLE 规范级事实（字段编码、请求码、时序参数、类代码、规范条文）。当用户问"某个 bRequest/wValue 怎么编码""某字段的取值含义""规范第几章规定什么"，或知识树正文标注"见规范原文"需要溯源时使用。检索顺序：本地速查表 → 知识树章节 → 本地缓存的官方规范 PDF → 联网官方源。
---

# USB/BLE 规范事实检索

## 检索顺序（从快到权威，逐级升级）

> 🛠 一键提取缓存规范文本：`bash tools/spec_extract.sh <缓存文件> [检索词]`（自动解压 zip→pdftotext→grep）。

1. **[速查表大全](../../90-附录/02-速查表大全.md)** —— 12 张高频表（描述符类型码、标准请求、PID、最大包长、类代码、键值、GATT UUID、PD 档位、时序参数、命名对照），80% 的编码问题到此为止；
2. **[术语表](../../90-附录/01-术语表.md)** —— 缩写展开与一句话定义；
3. **知识树章节** —— 按下方"主题→章节"映射直达；
4. **本地官方规范缓存（`80-参考资料/`，最终权威）** —— 按下方"主题→缓存文件"映射打开 PDF；
5. 都没有 → 联网官方源（usb.org 文档库 / bluetooth.com specifications），并把新事实回填知识树。

## 主题 → 知识树章节 → 本地缓存规范

| 主题 | 知识树章节 | 本地缓存（80-参考资料/） |
|---|---|---|
| USB 2.0 电气/包/传输/枚举/集线器 | [10-树干](../../10-树干-USB核心/01-概述与版本演进.md) 对应篇 | `usb-core/USB2.0-Specification.zip`（解压后 PDF；第 5/8/9 章为核心） |
| USB 3.x 链路层/LTSSM/Header | [USB3x 包格式与 LTSSM](../../40-枝干-高速演进/04-USB3x包格式与LTSSM.md) | `usb-core/USB3.2-Specification-2018.zip` |
| USB4 路由/隧道/配置空间 | [USB4 深入](../../40-枝干-高速演进/05-USB4深入-路由隧道与配置.md) | `usb-core/USB4-Specification-v2-2025-11.zip` |
| Type-C 引脚/CC/Rp/Rd | [Type-C 详解](../../30-枝干-接口与供电/02-USBType-C详解.md) | `usb-core/USB-TypeC-Spec-2.5-2026.zip`（最新）或 `USB-TypeC-Spec-R2.0.pdf` |
| PD 消息/PDO/RDO/状态机 | [PD 深入](../../30-枝干-接口与供电/07-USBPD深入-状态机与消息全表.md) | ⚠️ PD 规范本体被门控未缓存；替代权威：[Linux 内核 pd.h](https://github.com/torvalds/linux/blob/master/include/linux/usb/pd_01.h) |
| OTG/SRP/HNP | [OTG 与角色切换](../../30-枝干-接口与供电/06-OTG与角色切换-HNP-SRP.md) | USB2.0 zip 内含 OTG 补充章节 |
| HID 描述符/Item/类请求 | [HID 枝干](../../20-枝干-设备类协议/HID-人机接口设备/00-HID概述与定位.md) | `device-classes/HID-1.11.pdf`；Usage ID 查 `HID-UsageTables-1.3.pdf` |
| CDC/ACM/ECM/NCM | [CDC 枝干](../../20-枝干-设备类协议/CDC-通信设备类/00-CDC概述.md) | `device-classes/CDC-1.2.zip`（含 PSTN 子规范） |
| MSC/BOT/UFI/UASP | [MSC 枝干](../../20-枝干-设备类协议/MSC-大容量存储/00-MSC概述与BOT.md) | `MSC-BOT-1.0.pdf`、`MSC-UFI-1.0.pdf`、`UASP-1.0.zip` |
| 音频 UAC1/2 | [Audio 枝干](../../20-枝干-设备类协议/Audio-UAC/00-UAC概述.md) | `UAC-1.0.pdf`(+Formats/Terminals)、`UAC-2.0-Errata-2025.pdf`（推荐阅读版） |
| 视频 UVC | [UVC 详解](../../20-枝干-设备类协议/Video-UVC/00-UVC详解.md) | `device-classes/UVC-1.5.zip` |
| DFU 状态机/请求 | [DFU](../../20-枝干-设备类协议/其他设备类/01-DFU固件升级.md) | `device-classes/DFU-1.1.pdf` |
| CCID 消息 | [CCID](../../20-枝干-设备类协议/其他设备类/02-CCID智能卡.md) | `device-classes/CCID-1.1.pdf` |
| USBTMC/USB488 | [USBTMC](../../20-枝干-设备类协议/其他设备类/08-USBTMC测试测量类.md) | `device-classes/USBTMC-USB488-1.0.zip` |
| Billboard | [长尾设备类](../../20-枝干-设备类协议/其他设备类/09-长尾设备类-AV-Billboard-Healthcare-I3C.md) | `device-classes/Billboard-1.2.2.zip` |
| BLE 链路层/GATT/SMP/HOGP | [BLE 子树](../../50-枝干-无线关联/BLE-低功耗蓝牙/00-BLE概述.md) | `bluetooth/Bluetooth-Core-6.0.pdf`（Vol 6=BLE，Vol 3=Host）；HOGP 单行本 `HOGP-1.0.pdf` |
| 经典蓝牙 Profile（HID/HFP/AVRCP） | [经典 Profile 详解](../../50-枝干-无线关联/BLE-低功耗蓝牙/11-经典蓝牙Profile详解.md) | `bluetooth/Bluetooth-HID-Profile-1.1.1.pdf`、`HFP-1.10.pdf`、`AVRCP-1.6.3.pdf` |
| A2DP/AVDTP 编解码与信令 | [A2DP 编解码与 AVDTP 参数](../../50-枝干-无线关联/BLE-低功耗蓝牙/15-A2DP编解码与AVDTP参数.md) | `bluetooth/A2DP-1.4.1.pdf`、`bluetooth/AVDTP-1.3.pdf`（Table 8.6 信令码） |
| 合规测试（眼图/TestMode/USBCV） | [合规测试实操](../../70-枝干-调试测试与安全/05-合规测试实操.md) | `usb-core/USB2-Electrical-Compliance-v1.08.pdf` |
| 类代码总表 | [设备类索引](../../20-枝干-设备类协议/00-设备类索引.md) | 联网：[USB-IF defined-class-codes](https://www.usb.org/defined-class-codes) |

## 缓存 PDF 打开提示

- 多个 `.zip` 内含 PDF，先解压到临时目录再检索（可 `python -m zipfile -e` 或资源管理器）；
- 大 PDF 用 `Ctrl+F` 搜英文术语（如 `bInterval`、`Chirp`、`CBW`），规范无中文；
- 知识树各篇"相关节点"已给出规范章节号引用的，优先按章节号跳转。

## 诚实原则

- 知识树与规范原文冲突时，**以规范原文为准**，并在知识树对应文件处提出修正；
- 检索不到的编码细节，回答"规范未固化/需实测"，严禁编造数值。
