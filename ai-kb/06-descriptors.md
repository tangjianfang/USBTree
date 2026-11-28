---
id: 06-descriptors
title: "标准描述符字段全表"
topic: core
level: 进阶
keywords: ["device descriptor 设备描述符", "configuration descriptor", "interface descriptor", "endpoint descriptor", "string descriptor", "IAD", "BOS", "device qualifier", "bMaxPacketSize0", "wTotalLength", "bmAttributes", "bMaxPower"]
sources:
  - path: "10-树干-USB核心/07-描述符详解.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/10-树干-USB核心/07-描述符详解.md"
spec_refs: ["USB 2.0 Specification §9.5–9.6", "USB 3.2 Specification §9.6", "IAD ECN"]
related: ["07-enumeration-requests", "11-hid-core", "14-cdc"]
usbtree_commit: d8dc27d
generated: 2026-11-29
---

# 标准描述符字段全表

> 层级 进阶 · 主题 `core` · 相关：[枚举流程、Setup 包与标准请求](07-enumeration-requests.md)、[HID 核心：类描述符、报告描述符 Item、Usage、类请求](11-hid-core.md)、[CDC：ACM 虚拟串口、ECM/NCM/RNDIS 网络、请求与通知全表](14-cdc.md)

## 核心事实 Key Facts

> 由维护者整理并与规范核对；与下方 USBTree 原文冲突时以本节为准。

描述符类型码 bDescriptorType：

| 值 | 描述符 | 长度 |
|---|---|---|
| 0x01 | Device | 18 |
| 0x02 | Configuration | 9（+ wTotalLength 子树） |
| 0x03 | String | 可变，UTF-16LE；索引 0 = LANGID 列表（0x0409 en-US） |
| 0x04 | Interface | 9 |
| 0x05 | Endpoint | 7（SS 后跟 SS Endpoint Companion 0x30，6 B） |
| 0x06 | Device Qualifier | 10 |
| 0x07 | Other Speed Configuration | 9 |
| 0x0B | Interface Association (IAD) | 8 |
| 0x0F | BOS | 5 + 能力描述符 |
| 0x10 | Device Capability | 可变（0x02 USB 2.0 Extension/LPM，0x03 SS USB，0x05 Platform：MS OS 2.0 / WebUSB） |
| 0x21 / 0x22 / 0x23 | HID / Report / Physical（类描述符） | |
| 0x24 / 0x25 | CS_INTERFACE / CS_ENDPOINT（CDC/UAC/UVC 类特定） | |

Device Descriptor（18 B）：bLength(1)=0x12, bDescriptorType(1)=0x01, bcdUSB(2), bDeviceClass(1), bDeviceSubClass(1), bDeviceProtocol(1), bMaxPacketSize0(1), idVendor(2), idProduct(2), bcdDevice(2), iManufacturer(1), iProduct(1), iSerialNumber(1), bNumConfigurations(1)。多字节字段小端。

- bMaxPacketSize0：**USB 2.0 及以下为字节数**（LS 8；FS 8/16/32/64；HS 64）；**USB 3.x SuperSpeed 为 2 的指数**，固定 0x09 表示 2^9 = 512。
- bcdUSB：0x0200 = USB 2.0；0x0201/0x0210 = 支持 BOS（LPM、MS OS 2.0 平台能力需要）；0x0300/0x0320 = USB 3.x。
- Configuration bmAttributes：D7 必须 1，D6 Self-powered，D5 Remote Wakeup；bMaxPower 单位 2 mA（USB 2.0）/ 8 mA（SS）。
- Endpoint bmAttributes bit1:0：00 Control / 01 Isochronous / 10 Bulk / 11 Interrupt；同步端点 bit3:2 同步类型（异步/自适应/同步），bit5:4 用途（数据/反馈/隐式反馈）。
- USB 2.0 spec Table 9-8 / §5.5.3 与 USB 3.2 spec §9.6.1（Table 9-11）对 bMaxPacketSize0 的编码不同，读描述符时必须先看 bcdUSB 与当前速率，不能把 0x09 当成 9 字节。

## 原文：07-描述符详解

> Source: [10-树干-USB核心/07-描述符详解.md](https://github.com/tangjianfang/USBTree/blob/main/10-树干-USB核心/07-描述符详解.md)

### 1. 描述符：设备的"自我介绍文本"

设备把自身结构编码为一串结构化数据（描述符，Descriptor），主机通过标准请求逐级读取。这是即插即用的根基：**主机驱动不需要认识设备，只需要读它的自我描述**。

层级嵌套关系（俄罗斯套娃）：

```
设备描述符 (Device)
└── 配置描述符 (Configuration) ×N
    └── 接口描述符 (Interface) ×M        ← 功能所在（类代码写在这里）
        ├── (类特定描述符, 如 HID 报告)   ← 各设备类枝干的入口
        └── 端点描述符 (Endpoint) ×K      ← 真正传数据的端点
        └── 字符串描述符 (String, 由索引引用)
```

读取时嵌套展开：读配置描述符头部 9 字节得到 wTotalLength，再一次性读全（含所有接口/端点）。

### 2. 设备描述符 (bDescriptorType=0x01, 18 字节)

| 偏移 | 字段 | 长度 | 含义与要点 |
|---|---|---|---|
| 0 | bLength | 1 | 0x12 |
| 1 | bDescriptorType | 1 | 0x01 |
| 2 | bcdUSB | 2 | 规范版本 BCD，如 0x0200、0x0210（LPM）、0x0300/0x0320 |
| 4 | bDeviceClass | 1 | 设备级类代码：0x00=在接口级声明（最常见）；0x09=集线器；0xEF=Misc（复合/IAD）；0x02=CDC（特殊：类在设备级） |
| 5 | bDeviceSubClass | 1 | 同上 |
| 6 | bDeviceProtocol | 1 | 如 HS 设备 0x01=单 TT 集线器、0x02=多 TT |
| 7 | bMaxPacketSize0 | 1 | 端点 0 最大包。USB 2.0 及更早为**字节数**：只允许 8/16/32/64（HS 必须 64）。仅 USB 3.x 在 SuperSpeed（Gen X）运行为**指数**：0x09 = 2^9 = 512 |
| 8 | idVendor | 2 | VID，USB-IF 分配 |
| 10 | idProduct | 2 | PID，厂商自定义 |
| 12 | bcdDevice | 2 | 设备版本号（固件升级时递增它，驱动可据此区分） |
| 14 | iManufacturer / iProduct / iSerialNumber | 3 | 字符串索引（0=无；**iSerialNumber 非零时同一 VID/PID 靠序列号区分多台**） |
| 17 | bNumConfigurations | 1 | 配置数 |

实例（某全速鼠标）：

```
12 01 00 02 00 00 00 40 41 23 01 00 00 01 01 02 00 01
│  │  │─│  │  │  │  │─│─ │─│─ └┬┘ └┬┘ └┬┘ │  │  │  └ 1 个配置
│  │  │ │  │  │  │  │ │ │ │ │   │   │   │  │  └ 产品名=串2
│  │  │ │  │  │  │  │ │ │ │ │   │   │   └ 厂商=串1, 序列号=无(0)
│  │  │ │  │  │  │  │ └─┴─┴─┘   │   └ bcdDevice=0x0100
│  │  │ │  │  │  │  └ VID=0x2341, PID=0x0001
│  │  │ │  │  │  └ 端点0 = 64 字节
│  │  │ │  │  └ 设备协议/子类 = 0
│  │  │ │  └ 设备类 = 0 (类在接口级)
│  │  │ └ USB 2.00
│  │  └ 类型 0x01
│  └ 长度 18
```

>  勘误：此前把 `bMaxPacketSize0` 写成「唯一以 2^n 编码而非直接数值的字段」，对 USB 2.0 及更早不成立。USB 2.0 spec Table 9-8：该字段就是端点 0 最大包的**字节数**，合法值只有 8、16、32、64；高速设备必须为 64（§5.5.3）。只有在 SuperSpeed / Gen X 运行时才改成指数——USB 3.2 spec §9.6.1（Table 9-11）：`bMaxPacketSize0` 用作 2^bMaxPacketSize0 的指数，Gen X 唯一合法值 **09H**，表示 512 字节。上例 `0x40` 是全速设备的字节数，不是指数。

### 3. 配置描述符 (0x02, 头部 9 字节)

| 偏移 | 字段 | 要点 |
|---|---|---|
| 0/1 | bLength / bDescriptorType | 9 / 0x02 |
| 2 | wTotalLength | **配置+全部接口+全部端点+类特定描述符的总长**，主机据此一次性读取整包 |
| 4 | bNumInterfaces | 接口数 |
| 5 | bConfigurationValue | SET_CONFIGURATION 的参数（多配置设备如"固件升级配置/正常配置"） |
| 6 | iConfiguration | 字符串索引 |
| 7 | bmAttributes | bit7=1(必须，历史保留)；bit6=自供电；bit5=支持远程唤醒；bit4~0 保留 |
| 8 | bMaxPower | **单位 2 mA**：500 mA 写 0xFA=250——常被乘错的字段（[合规](51-compliance-security.md)常见不合规点） |

### 4. 接口描述符 (0x04, 9 字节) —— 功能的户口本

| 偏移 | 字段 | 要点 |
|---|---|---|
| 4 | bInterfaceNumber | 接口编号（0 起） |
| 5 | bAlternateSetting | **备用设置**：同号接口的多套端点方案（带宽换挡，典型：UVC 零带宽 Alt0 / 常速 Alt1） |
| 6 | bNumEndpoints | 本设置的端点数（不含端点 0） |
| 7 | **bInterfaceClass** | 类代码——主机按它挑类驱动（[设备类索引](10-class-index.md)） |
| 8 | bInterfaceSubClass | 子类 |
| 9 | bInterfaceProtocol | 协议（如 HID 的 Boot 协议位） |
| 9 | iInterface | 字符串索引 |

类代码速查：0x01 音频、0x02 CDC 控制、0x03 HID、0x06 图像(PTP)、0x07 打印机、0x08 MSC、0x09 集线器、0x0A CDC 数据、0x0B 智能卡、0x0E 视频、0xE0 无线控制器(蓝牙)、0xEF Misc、0xFF 厂商自定义。

### 5. 端点描述符 (0x05, 7 字节)

| 偏移 | 字段 | 要点 |
|---|---|---|
| 2 | bEndpointAddress | bit7=方向(IN=0x80)，bit3~0=端点号 |
| 3 | bmAttributes | bit1~0：00 控制 / 01 同步 / 10 批量 / 11 中断；bit5~3 是同步类型（同步端点专用） |
| 4 | wMaxPacketSize | bit10~0=包长；**bit12~11 仅 HS 同步端点**：每微帧附加事务数（1/2/3 次） |
| 6 | bInterval | 轮询间隔，语义随速率与传输类型变（换算表见[四种传输类型](05-transfer-types-bandwidth.md)） |

### 6. 其它标准描述符

| 描述符 | 类型码 | 用途与要点 |
|---|---|---|
| 字符串 String | 0x03 | UTF-16LE；索引 0 是 LANGID 表（通常 0x0409 美式英语）；iSerialNumber 用于多台同型号区分与安全策略（[USBGuard](51-compliance-security.md)） |
| 设备限定 Device Qualifier | 0x06 | 描述"另一速率下我是什么样"（HS 设备必给，供回退 FS 时查询） |
| 其它速度配置 Other Speed Configuration | 0x07 | 与限定符配套的另一速率配置 |
| **IAD 接口关联** | 0x0B | 把多个接口捆成一个功能（CDC、UVC、UAC2 复合设备的必需品；避免 Windows 给每个接口单独装驱动） |
| **BOS** | 0x0F | 二进制设备对象存储：bcdUSB≥0x0201/3.x 设备必备，内含**设备能力描述符 (0x10)** 链：USB 2.0 Extension（LPM 声明）、SuperSpeed、Container ID、Platform Capability（挂 MS OS 2.0 描述符与 WebUSB）、Power Delivery 能力等 |
| OTG | 0x09 | OTG 能力声明（HNP/SRP 支持） |

类特定描述符（HID 描述符 0x21、报告 0x22、CDC 功能描述符、UVC 终端/单元……）是各枝干的正题：从[设备类索引](10-class-index.md)进入。

### 7. 描述符编码通用规则

1. **每个描述符第一个字节永远是自己的长度**，第二个字节永远是类型码——解析器靠这两字节游走；
2. 多字节字段一律**小端 (Little-Endian)**；
3. 主机第一次 GET_DESCRIPTOR(DEVICE) 时 wLength 可能只有 64（甚至 8）：设备应**截断返回**（bLength 超出 wLength 部分不发），这是设备端必须实现的语义；
4. bLength 与实际不符 → 枚举失败，主机会拒绝整个配置（[排查手册](50-debug-troubleshooting.md)症状 B）。
