# 参考资料缓存索引

> 📎 本目录是知识树所依赖的**官方规范原文下载缓存**，按枝干分目录存放。下载日期：2026-09-05。
> 法律提示：USB-IF 规范按其 Adopters Agreement 分发，蓝牙规范按 SIG 许可分发——此处缓存仅用于个人学习与工程参考，商用/再分发请阅读各规范附带的许可条款。

## 一、usb-core/ —— 核心规范

| 本地文件 | 规范 | 官方来源 | 知识树对应 |
|---|---|---|---|
| USB2.0-Specification.zip | USB 2.0 Specification（2025-06-03 修订版，zip 内含 PDF） | [usb.org 文档库](https://www.usb.org/documents?search=USB+2.0) | [10-树干](../10-树干-USB核心/01-概述与版本演进.md) 全部 |
| USB3.2-Specification-2018.zip | USB 3.2 Specification rev 1.0（2018-09-12，含 3.0/3.1 历史合并） | [usb.org](https://www.usb.org/sites/default/files/documents/usb_32_20180912.zip) | [高速演进](../40-枝干-高速演进/01-USB3x与SuperSpeed.md)、[包格式与LTSSM](../40-枝干-高速演进/04-USB3x包格式与LTSSM.md) |
| USB4-Specification-v2-2025-11.zip | USB4 Specification Version 2.0（2025-11） | [usb.org 文档库](https://www.usb.org/documents) | [USB4 深入](../40-枝干-高速演进/05-USB4深入-路由隧道与配置.md) |
| USB-TypeC-Spec-2.5-2026.zip | USB Type-C Cable and Connector Release 2.5（2026-03，**现行最新**） | [usb.org](https://www.usb.org/sites/default/files/USB%20Type-C%202.5%20Release%20202603.zip) | [Type-C 详解](../30-枝干-接口与供电/02-USBType-C详解.md) |
| USB-TypeC-Spec-R2.0.pdf | Type-C Release 2.0（2019-08，可读性好的单 PDF，历史参考） | [usb.org](https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf) | 同上 |
| UCSI-3.1.zip | USB Type-C Connector System Software Interface (UCSI) 3.1 | [usb.org](https://www.usb.org/sites/default/files/USB%20Type-C%20Connector%20System%20Software%20Interface%20UCSI%20Revision_3.1.zip) | [PD 深入](../30-枝干-接口与供电/07-USBPD深入-状态机与消息全表.md)（OS 侧接口） |
| USB2-Electrical-Compliance-v1.08.pdf | USB2 电气合规测试规范 v1.08（2026-04） | [usb.org](https://www.usb.org/sites/default/files/USB2%20Electrical%20Compliance%20Specification%20v1.08.pdf) | [合规测试实操](../70-枝干-调试测试与安全/05-合规测试实操.md) |

## 二、device-classes/ —— 设备类规范

| 本地文件 | 规范 | 官方来源 | 知识树对应 |
|---|---|---|---|
| HID-1.11.pdf | Device Class Definition for HID 1.11 | [usb.org](https://www.usb.org/sites/default/files/hid1_11.pdf) | [HID 子树](../20-枝干-设备类协议/HID-人机接口设备/00-HID概述与定位.md) |
| HID-UsageTables-1.3.pdf | HID Usage Tables 1.3 | [usb.org](https://www.usb.org/sites/default/files/hut1_3_0.pdf) | [Usage 体系](../20-枝干-设备类协议/HID-人机接口设备/03-Usage体系与集合.md)（注：v1.4/1.5 起官网仅发布 docx，请按需到[文档库](https://www.usb.org/documents?search=usage+tables)取最新） |
| CDC-1.2.zip | Class Definitions for Communication Devices 1.2（含 PSTN/WMC 等子规范） | [usb.org](https://www.usb.org/sites/default/files/CDC1.2_WMC1.1_012011_0.zip) | [CDC 枝干](../20-枝干-设备类协议/CDC-通信设备类/00-CDC概述.md) |
| MSC-BOT-1.0.pdf | MSC Bulk-Only Transport 1.0 | [usb.org](https://www.usb.org/sites/default/files/usbmassbulk_10.pdf) | [BOT](../20-枝干-设备类协议/MSC-大容量存储/00-MSC概述与BOT.md) |
| MSC-UFI-1.0.pdf | MSC UFI 1.0（软盘命令子集） | [usb.org](https://www.usb.org/sites/default/files/usbmass-ufi10.pdf) | [SCSI 与 UFI](../20-枝干-设备类协议/MSC-大容量存储/01-SCSI命令与UFI.md) |
| UASP-1.0.zip | USB Attached SCSI Protocol (UASP) 1.0 | [usb.org](https://www.usb.org/document-library/usb-attached-scsi-protocol-uasp-v10-and-adopters-agreement) | 同上（UAS 一节） |
| UAC-1.0.pdf / -Formats.pdf / -Terminals.pdf | USB Audio Class 1.0 + 数据格式 + 终端类型三件套 | [usb.org](https://www.usb.org/sites/default/files/audio10.pdf) | [UAC1.0 详解](../20-枝干-设备类协议/Audio-UAC/01-UAC1.0详解.md) |
| UAC-2.0-final.zip | USB Audio Class 2.0 原始发布包 | [usb.org](https://www.usb.org/document-library/audio-devices-rev-20-and-adopters-agreement) | [UAC2 与 UAC3](../20-枝干-设备类协议/Audio-UAC/02-UAC2与UAC3.md) |
| UAC-2.0-Errata-2025.pdf | UAC 2.0 含勘误与 ECN（至 2025-04-02，**推荐阅读版**） | [usb.org 文档库](https://www.usb.org/documents?search=audio) | 同上 |
| UAC-4.0.zip | USB Audio Class Release 4.0（2025，含 ECN 至 2025-10-31） | [usb.org](https://www.usb.org/document-library/usb-audio-devices-release-40-and-adopters-agreement) | 同上（4.0 为最新代际，本库暂未单列章节） |
| UVC-1.5.zip | USB Video Class 1.5（含载荷/协议/ 电子补充文档） | [usb.org](https://www.usb.org/sites/default/files/USB_Video_Class_1_5.zip) | [UVC 详解](../20-枝干-设备类协议/Video-UVC/00-UVC详解.md) |
| DFU-1.1.pdf | Device Firmware Upgrade 1.1 | [usb.org](https://www.usb.org/sites/default/files/DFU_1.1.pdf) | [DFU](../20-枝干-设备类协议/其他设备类/01-DFU固件升级.md) |
| CCID-1.1.pdf | ICCD/CCID 智能卡类 1.1 | [usb.org](https://www.usb.org/sites/default/files/DWG_Smart-Card_CCID_Rev110.pdf) | [CCID](../20-枝干-设备类协议/其他设备类/02-CCID智能卡.md) |
| USBTMC-USB488-1.0.zip | USB Test & Measurement Class 1.0（含 USB488 子类） | [usb.org](https://www.usb.org/document-library/test-measurement-class-specification) | [USBTMC](../20-枝干-设备类协议/其他设备类/08-USBTMC测试测量类.md) |
| Billboard-1.2.2.zip | USB Billboard Device Class 1.2.2 | [usb.org](https://www.usb.org/document-library/billboard-device-class-spec-revision-122-and-adopters-agreement) | [长尾设备类](../20-枝干-设备类协议/其他设备类/09-长尾设备类-AV-Billboard-Healthcare-I3C.md) |
| AV-1.0.zip（+AV-BDP-1.0.pdf） | USB Audio/Video Devices 1.0（AVFunction/AVFormat1~3 + Basic Device Profile） | [usb.org 文档库](https://www.usb.org/documents?search=audio+video) | [AV 设备类详解](../20-枝干-设备类协议/其他设备类/10-AV设备类详解.md) |
| PHDC-1.0.zip | Personal Healthcare Devices 1.0（含勘误） | [usb.org 文档库](https://www.usb.org/documents?search=healthcare) | [PHDC 健康医疗类](../20-枝干-设备类协议/其他设备类/11-PHDC健康医疗类.md) |
| *注* | 上表部分 zip 附 `*.txt`（pdftotext 提取文本，便于 grep 检索） | — | — |

## 三、bluetooth/ —— 蓝牙 SIG 规范

| 本地文件 | 规范 | 官方来源 | 知识树对应 |
|---|---|---|---|
| Bluetooth-Core-6.0.pdf | Bluetooth Core Specification 6.0（2024，全 6 卷） | [bluetooth.com](https://www.bluetooth.com/specifications/specs/core-specification-6-0/) | [BLE 子树](../50-枝干-无线关联/BLE-低功耗蓝牙/00-BLE概述.md) 全部 |
| Bluetooth-Core-6.0-Errata-List.pdf | Core 6.0 勘误清单 | 同上 | 同上 |
| HOGP-1.0.pdf | HID over GATT Profile (HOGP) 1.0 | [bluetooth.com](https://www.bluetooth.com/specifications/specs/hid-over-gatt-profile-1-0/) | [HOGP](../50-枝干-无线关联/BLE-低功耗蓝牙/07-HOGP-HIDoverGATT.md) |
| HID-Service-1.1.pdf | HID Service (GATT) 1.1 | [bluetooth.com](https://www.bluetooth.com/specifications/specs/hid-service-specification/) | 同上 |
| Bluetooth-HID-Profile-1.1.1.pdf | Human Interface Device Profile 1.1.1（经典蓝牙 HID） | [bluetooth.com](https://www.bluetooth.com/specifications/specs/human-interface-device-profile-1-1-1/) | [经典蓝牙 Profile 详解](../50-枝干-无线关联/BLE-低功耗蓝牙/11-经典蓝牙Profile详解.md) |
| A2DP-1.4.1.pdf | Advanced Audio Distribution Profile 1.4.1（2025-06-30） | [bluetooth.com](https://www.bluetooth.com/specifications/specs/a2dp-1-4-1/) | [A2DP 编解码与 AVDTP 参数](../50-枝干-无线关联/BLE-低功耗蓝牙/15-A2DP编解码与AVDTP参数.md) |

## 四、未能直连下载的规范（门控/付费）与官方在线替代

| 规范 | 状态 | 获取途径 |
|---|---|---|
| **USB PD 3.1/3.2** | Adopters Agreement 门控，无公开直链 | 在 [usb.org 文档库](https://www.usb.org/documents?search=power+delivery) 检索下载（需接受协议）；本库 [PD 深入](../30-枝干-接口与供电/07-USBPD深入-状态机与消息全表.md) 的消息编号已与 [Linux 内核 pd.h](https://github.com/torvalds/linux/blob/master/include/linux/usb/pd_01.h) 交叉验证 |
| xHCI 规范 | USB-IF 会员限定 | 公开替代：[osdev xHCI 页](https://wiki.osdev.org/XHCI)、内核 [xhci.c](https://github.com/torvalds/linux/tree/master/drivers/usb/host) |
| PTP (ISO 15740) | ISO 付费标准 | 免费近似：[CIPA DC-009 (PTP-IP)](https://www.cipa.jp/std/documents_e/DC-009_E.pdf)、[Microsoft MTP 文档](https://learn.microsoft.com/windows/win32/wmdm/) |
| HID over I2C | 微软规范，在线文档形态 | [HID over I2C Guide](https://learn.microsoft.com/windows-hardware/drivers/hid/hid-over-i2c-guide) |
| Microsoft OS 2.0 Descriptors | 在线文档形态 | [Microsoft OS descriptors](https://learn.microsoft.com/windows-hardware/drivers/usbcon/microsoft-os-2-0-descriptors-specification) |
| WebUSB | WICG 草案（在线） | [webusb spec](https://wicg.github.io/webusb/) |
| Wireless USB / MA-USB（历史） | 文档库可下但意义有限 | [文档库检索](https://www.usb.org/documents?search=wireless+usb)；本库说明见 [Wireless USB 历史](../50-枝干-无线关联/99-WirelessUSB与MA-USB历史.md) |
| BillBoard/AV/Healthcare 等长尾类 | Billboard 已缓存；AV/Healthcare 可从文档库下载 | [定义类码总表](https://www.usb.org/defined-class-codes) + [文档库检索](https://www.usb.org/documents)；本库见 [长尾设备类](../20-枝干-设备类协议/其他设备类/09-长尾设备类-AV-Billboard-Healthcare-I3C.md) |

## 五、官方工具与代码库（在线资源）

| 工具 | 用途 | 链接 |
|---|---|---|
| Wireshark + USBPcap | USB 软件层抓包 | [wireshark.org](https://www.wireshark.org/) / [USBPcap](https://desowin.org/usbpcap/) |
| TinyUSB | 跨平台设备/主机固件栈 | [github.com/hathach/tinyusb](https://github.com/hathach/tinyusb) |
| libusb 1.0 | 跨平台用户态 USB 访问 | [libusb.info](https://libusb.info/) |
| usbipd-win | Windows 侧 USB/IP 服务 | [github.com/dorssel/usbipd-win](https://github.com/dorssel/usbipd-win) |
| dfu-util | DFU 升级工具 | [dfu-util.sourceforge.net](https://dfu-util.sourceforge.net/) |
| USBTreeView | Windows 描述符树查看 | [uwe-sieber.de](https://www.uwe-sieber.de/usbtreeview_e.html) |
| USBHSET / USBCV | USB-IF Hub/Chapter9 测试工具 | [usb.org 文档库](https://www.usb.org/documents?search=HSET) 检索 |
| USB-IF 定义类码表 | 官方 Class/SubClass/Protocol 编码 | [defined-class-codes](https://www.usb.org/defined-class-codes) |
| Bluetooth GATT 规范目录 | 全部 GATT Service/Characteristic UUID | [bluetooth.com specifications](https://www.bluetooth.com/specifications/specs/) |

## 六、如何更新缓存

```bash
# 示例：重新下载 USB 4 规范（URL 以官网文档库当前为准）
curl -fL -o usb-core/USB4-Specification-v2-2025-11.zip \
  "https://www.usb.org/sites/default/files/USB4%20Specification%20November%202025.zip"
```

注意：usb.org 直链命名随版本变化（如 USB 2.0 从 `usb2.0.pdf` 变为 `usb_20_YYYYMMDD.zip`），失效时以 [文档库](https://www.usb.org/documents) 页面为准；蓝牙规范直链格式为 `bluetooth.org/DocMan/handlers/DownloadDoc.ashx?doc_id=NNNNN`，可从各规范落地页获取。
