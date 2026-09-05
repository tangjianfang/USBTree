---
title: "打印机类（USB Printing Support 1.1）"
layer: 枝干/设备类协议
section: 其他设备类
doc-path: 20-枝干-设备类协议/其他设备类/04-Printer打印机类.md
---
# 打印机类（USB Printing Support 1.1）

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[其他设备类] → 叶[Printer]
> ⬆️ 父节点: 枝干[设备类]，与 [../HID-人机接口设备/00-HID概述与定位.md] 等同类兄弟分枝同级；批量传输与标准请求见 [../../10-树干-USB核心/06-四种传输类型.md]、[../../10-树干-USB核心/08-枚举流程与标准请求.md]

## 1. 定位

USB 打印机类规范（USB-IF "Printer Class" / Universal Serial Bus Printer Device Class, 1.1）的设计哲学是**极简**：USB 只负责一条"透明管道"，把主机生成的页面数据原样灌进打印机；理解数据的不是 USB 栈，而是打印机自己的命令解释器。设备识别、状态查询则由三个类专属控制请求完成。

因此 USB 打印机类几乎不增加打印机固件负担，成为从喷墨/激光一体机到小票机、标签机全面普及的类。

## 2. 接口标识

| 字段 | 取值 | 说明 |
|---|---|---|
| bInterfaceClass | 0x07 | Printer（打印类） |
| bInterfaceSubClass | 0x01 | 打印机 |
| bInterfaceProtocol | 0x01 | 单向（Unidirectional）：仅批量 OUT |
| bInterfaceProtocol | 0x02 | 双向（Bidirectional）：批量 OUT + 批量 IN |
| bInterfaceProtocol | 0x04 | IPP over USB（PWG IPP-USB 规范新增，见第 7 节） |

Windows 老设备管理器里显示的"USB 打印支持（USB Printing Support）"即为此类驱动。

## 3. 端点构成

| 协议 | 端点 | 用途 |
|---|---|---|
| 0x01 单向 | 批量 OUT | 页面描述/打印数据流 |
| 0x02 双向 | 批量 OUT | 打印数据流 |
| 0x02 双向 | 批量 IN | 回读状态、通道级回传数据 |

## 4. 类专属请求（共 3 个）

| bRequest | bmRequestType | 名称 | wValue | wIndex | 数据 | 作用 |
|---|---|---|---|---|---|---|
| 0x00 | 0xA1（IN、类、接口） | GET_DEVICE_ID | 高字节=配置序号（通常 0），低字节=接口号（典型用法） | 语言 ID（常见 0x0409） | 返回 IEEE 1284 设备 ID 字符串 | 设备识别：厂商/型号/命令集 |
| 0x01 | 0xA1 | GET_PORT_STATUS | 0 | 接口号 | 返回 1 字节状态位图 | 纸尽/选中/错误 |
| 0x02 | 0x21（OUT、类、接口） | SOFT_RESET | 0 | 接口号 | 无 | 软复位打印通道（清缓冲，保留已配置状态） |

### 4.1 IEEE 1284 设备 ID（GET_DEVICE_ID 返回）

格式：前 2 字节为**大端长度**（含长度字节自身），随后是 `分号` 分隔的 `KEY:VALUE;` 键值串。USB 打印机规范中的示例：

```
00 37 "MFG:HEWLETT-PACKARD;MDL:DESKJET 990C;CMD:MLC,PCL,PML;"
│ │
│ └─字符串53字节 + 2字节长度 = 55 = 0x37
└─大端长度高字节
```

常用键：

| 键 | 含义 | 示例 |
|---|---|---|
| MFG / MANUFACTURER | 制造商 | EPSON |
| MDL / MODEL | 型号 | TM-T20III |
| CMD | **支持的打印机语言（命令集）**，分号内逗号分隔 | `CMD:ESCPL2,BDC;`、`CMD:PCL6,PS;` |
| CLS | 设备类别 | PRINTER |

主机驱动正是凭 CMD 字段匹配打印机语言，再决定用什么驱动/过滤程序生成数据。

### 4.2 端口状态（GET_PORT_STATUS 返回 1 字节）

| 位 | 名称 | 含义 |
|---|---|---|
| bit5 | Paper Empty | 1=缺纸 |
| bit4 | Select | 1=联机选中 |
| bit3 | Not Error | 1=无错误 |
| 其余 | 保留/未用 | 读作 0 |

示例 `0x18`（0b0001_1000）= 已选中且无错误；`0x10`（bit3=1、bit4=0）= 未选中；缺纸则 bit5=0。

## 5. 数据通道：打印机语言直通

批量 OUT 上的字节流就是打印机语言本身，USB 层不做任何加工：

| 语言 | 厂商/定位 | 常见 CMD 标识 |
|---|---|---|
| ESC/P、ESC/P2 | 爱普生针打/喷墨经典 | ESCPL2 |
| ESC/POS | 爱普生收银小票/热敏标准 | ESC/POS |
| PCL 5/6 | 惠普激光事实标准 | PCL、PCL6 |
| PostScript | 印刷级页面描述 | PS |
| ZPL / EPL | 斑马（Zebra）标签打印机 | ZPL、EPL |
| 厂商私有 | 多数厂商的增强通道（如 HP MLC） | MLC、BDC 等 |

正因为是直通，任何会"说"这些语言的程序（CUPS 过滤链、Zebra 设计软件、收银系统）都能直接写批量 OUT 完成打印，无需经过操作系统打印框架。

### 5.1 字节级示例：一次完整的识别与打印

主机枚举后先识别设备，再灌入数据：

```
① GET_DEVICE_ID（控制读取）
   请求: A1 00  00 00  00 00  09 04  FF 00
         │请求   │wValue │wIndex │wLength
         │0x00   │配置0/接口0 │LangID │255字节
   响应: 00 37 "MFG:EPSON;MDL:TM-T20III;CMD:ESC/POS;CLS:PRINTER;"

② GET_PORT_STATUS
   请求: A1 01  00 00  00 00  00 00  01 00   → 响应: 18（选中+无错+有纸）

③ 打印数据（批量 OUT，直接是 ESC/POS 指令流）
   1B 40          ; ESC @ 初始化
   1D 68 50       ; GS h 80   (条码高度)
   1B 61 01       ; ESC a 1   (居中)
   "Hello USB" 0A ; 文本 + 换行
   1D 56 42 00    ; GS V 66 0 (切纸)
```

## 6. 主机侧：CUPS 与 usb:// 寻址

```mermaid
flowchart LR
    APP[应用] --> CUPS[CUPS 打印框架] -->|过滤链生成 PCL/PS/ZPL| BE[usb 后端 libusb]
    BE -->|批量OUT| P[打印机 0x07/0x01]
    P -->|批量IN 状态| BE
```

- Linux 内核传统驱动 `usblp` 把设备暴露为 `/dev/usb/lp0`（字符设备）；现代 CUPS 默认改用 **libusb 用户态 usb 后端**（需屏蔽 usblp 抢占设备）。
- 协议 0x01（单向）是历史遗留：早期 1.0 规范只有打印方向；如今设备普遍实现 0x02，主机可回读状态（缺纸/卡纸上报）让打印队列给出有意义的提示。
- CUPS 设备 URI 形如：`usb://EPSON/TM-T20III?serial=XZ1234`，即"usb://厂商/型号[?serial=...]"，厂商/型号取自 IEEE 1284 设备 ID。
- Windows 由"USB 打印支持"驱动在 USB 端口之上虚拟出 LPT 风格端口（USB001…），老式 GDI 驱动无需感知 USB。
- 双向模式下主机通过批量 IN 回读状态与错误（缺纸、卡纸），支撑打印队列的反馈。

## 7. 新趋势：ipp-usb（IPP over USB）

PWG（打印机工作组）的 **IPP Over USB** 规范让 USB 打印机直接跑 HTTP + IPP（Internet Printing Protocol）——即网络打印机的协议栈搬到 USB 上：

- 接口仍为类 0x07 / 子类 0x01，但 bInterfaceProtocol = **0x04**；
- 使用**多对批量端点**承载并发 HTTP 通道（IPP/HTTP 消息分段在批量管道上封送）；
- 意义：打印机呈现为标准 IPP 打印机后，系统可用**无驱动打印（driverless）**——基于 IPP Everywhere/eSCL（扫描走 IPP 的 AirPrint 体系），不再需要厂商专有驱动或老打印类通道；
- Linux 上的 `ipp-usb` 守护进程把这类设备桥接成 IPP 网络打印机供 CUPS 无驱动使用；macOS/Windows 新版均已支持。

老协议（0x01/0x02）与新协议（0x04）可在同一设备上并存为不同接口，供新旧系统各取所需。

## 8. 典型场景

| 场景 | 说明 |
|---|---|
| 共享打印 dongle | USB 转并口/串口打印适配器把老并口打印机伪装成 USB 打印机类设备，老打印机获得"USB 免驱"能力 |
| 标签/条码打印机 | Zebra、Brother 等标签机直通 ZPL/EPL；仓储与物流系统常绕过打印框架直接批量写指令 |
| 小票/收银打印机 | ESC/POS 热敏机广泛使用 0x07 类（部分廉价机型用厂商自定义类或串口桥）；收银 POS 软件直接吐指令流 |
| 一体机扫描通道 | 打印接口（0x07）与扫描接口（常见为厂商私有或 WIA/图像类）在同一配置中并列，打印与扫描各走各的接口 |

## 9. 实践要点

- GET_DEVICE_ID 的返回是**字节串**（非 USB 字符串描述符），其前 2 字节长度为 IEEE 1284 约定的大端。
- SOFT_RESET 复位的是数据通道缓冲，不清除打印机面板设置。
- 廉价"USB 小票机"若枚举为 0xFF 厂商类，多半是私有 ESC/POS 封装，需厂商 SDK 或社区驱动（参见 [06-WebUSB与厂商自定义类.md]）。
- 批量传输的可靠性（NAK 流控、错误恢复）见 [../../10-树干-USB核心/11-错误处理与可靠性.md]。

## 相关节点

- [../../10-树干-USB核心/06-四种传输类型.md]（批量传输）
- [../../10-树干-USB核心/08-枚举流程与标准请求.md]（类请求在标准请求框架中的位置）
- [../../10-树干-USB核心/07-描述符详解.md]（接口描述符）
- [06-WebUSB与厂商自定义类.md]（厂商类 0xFF 的廉价小票机变体）
- [../HID-人机接口设备/00-HID概述与定位.md]（同类兄弟分枝）
