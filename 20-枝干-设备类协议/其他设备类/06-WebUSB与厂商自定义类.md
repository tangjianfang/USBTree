---
title: "WebUSB 与厂商自定义类（Vendor Class 0xFF / WinUSB / WebUSB）"
layer: 枝干/设备类协议
section: 其他设备类
doc-path: 20-枝干-设备类协议/其他设备类/06-WebUSB与厂商自定义类.md
---
# WebUSB 与厂商自定义类（Vendor Class 0xFF / WinUSB / WebUSB）

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[其他设备类] → 叶[厂商类/WebUSB]
> ⬆️ 父节点: 枝干[设备类]，与 [../HID-人机接口设备/00-HID概述与定位.md] 等同类兄弟分枝同级；用户态访问细节见 [../../60-枝干-主机侧与实现/04-libusb与用户态访问.md]

## 1. 厂商自定义类：自由与代价

当设备不适合套用任何标准类时，接口可以声明为**厂商自定义类**（Vendor-Specific Class）：

| 字段 | 取值 | 说明 |
|---|---|---|
| bInterfaceClass | 0xFF | Vendor Specific |
| bInterfaceSubClass | 任意 | 厂商自定 |
| bInterfaceProtocol | 任意 | 厂商自定 |

**自由**：端点数量/类型、请求语义、数据格式完全自定，固件实现成本最低（一个批量 OUT + 一个批量 IN 就能干活）。

**代价**：操作系统不会自动绑定任何功能驱动——厂商必须自己提供驱动，或借助下文的免驱机制。主机侧能看到的只是"不明设备"，没有 `VID:PID → 驱动` 的映射就只能等用户装驱动。

## 2. 老式代表：USB 串口桥芯片

历史最悠久的厂商类大军是 USB 转串口桥（UART bridge）芯片，它们各自定义私有批量协议（寄存器读写 + 数据流），靠内核/厂商驱动暴露出串口：

| 芯片 | 厂商 | Linux 内核驱动 | 备注 |
|---|---|---|---|
| FT232 系列 | FTDI | ftdi_sio | 业界老牌，协议私有，驱动内置大量 PID 表 |
| CP210x | Silicon Labs | cp210x | 常见小封装桥，配置存于芯片 |
| CH340/CH341 | 沁恒 WCH | ch341 | 国产低价桥，Arduino 兼容板大量使用 |
| PL2303 | Prolific | pl2303 | 老牌桥；近年假货泛滥，新驱动屏蔽仿冒品 |

对比：这些芯片若改用 **CDC-ACM**（USB 通信设备类的抽象控制模型）实现，即可在三大系统免驱枚举成标准串口——代价是固件要实现 CDC 的管理/通知机制。二者的取舍（私有协议 + 驱动表 vs 标准类 + 免驱）正是本文件主题的缩影。CDC 细节见 [../CDC-通信设备类/](../CDC-通信设备类/)。

## 3. WinUSB 方案：让 Windows 自动免驱

微软提供两代机制，让设备**在固件里声明**"请给我绑定 winusb.sys"（通用 USB 客户端驱动），应用通过 WinUSB API 访问，厂商零驱动。

### 3.1 MS OS 1.0 描述符

第一代机制由三部分组成：

1. **MS OS 1.0 字符串描述符**：挂在字符串索引 **0xEE**，设备插入 Windows 时被自动读取：

```
bLength=0x12  bDescriptorType=0x03(字符串)
qwSignature="MSFT100"(UTF-16LE: 4D 00 53 00 46 00 54 00 31 00 30 00 30 00)
bMS_VendorCode=0x01   bPad=0x00
```

2. **扩展兼容 ID 描述符**（Extended Compat ID OS Feature Descriptor）：主机以 GET 描述符方式经厂商码请求（wIndex=0x0004），函数级条目给出兼容 ID `"WINUSB"`；
3. **扩展属性描述符**（Extended Properties OS Feature Descriptor，wIndex=0x0005）：声明注册表属性 `DeviceInterfaceGUID`（REG_SZ）/ `DeviceInterfaceGUIDs`（REG_MULTI_SZ，类型 7），供应用按 GUID 打开设备接口。

### 3.2 MS OS 2.0 描述符

第二代机制挂在 **BOS 描述符**的 Platform Capability（平台能力）上，避免 0xEE 字符串被某些系统误读，并支持更多能力声明：

- 平台能力 UUID：`D8DD60DF-4589-4CC7-9CD2-659D9E648A9F`（Microsoft OS 2.0 Platform Capability ID）；
- 主机经厂商码读取描述符集（MS OS 2.0 Descriptor Set，wIndex=0x0007），集合内含头描述符、配置/函数子集与特性条目：**兼容 ID 条目**（类型编号见 MS OS 2.0 规范）声明 `"WINUSB"`，**注册表属性条目**声明 DeviceInterfaceGUID；
- 描述符框架基于 USB 2.0 BOS/平台能力扩展，属 USB 2.1+ 生态（BOS 机制见 [../../10-树干-USB核心/07-描述符详解.md]）。

两代机制可同时实现（新系统读 2.0、老系统回退 1.0），这是主流固件库（如 TinyUSB、libopencm3、ESP-IDF）的标准做法。

### 3.3 字节级示例

MS OS 1.0 扩展兼容 ID 描述符（单接口设备绑定 WinUSB）的典型内容：

```
头:  28 00 00 00                    ; dwLength = 0x28(40)
     00 01                          ; bcdVersion = 0x0100
     04 00                          ; wIndex = 0x0004 (Extended Compat ID)
     01                             ; bCount = 1 个函数条目
     00*7                           ; 保留
条目: 00                             ; bFirstInterfaceNumber = 0
     00                             ; 保留
     57 49 4E 55 53 42 53 00        ; compatibleID = "WINUSB"
     00*8                           ; subCompatibleID = 空
```

0xEE 字符串描述符的完整字节（共 0x12=18 字节）：

```
12 03 4D 00 53 00 46 00 54 00 31 00 30 00 30 00 01 00
│  │  └─"MSFT100" UTF-16LE──────────────────────┘  │  └─bPad
│  └─字符串描述符                                   └─bMS_VendorCode=0x01
└─bLength
```

## 4. WebUSB：浏览器直达 USB 设备

**WebUSB** 是 Google 提出的 W3C/WHATWG 生态提案规范：让网页 JavaScript 在用户授权下直接收发 USB 数据，目标是"插上设备 → 打开网页 → 即可配置/升级/调试"，把厂商工具（含 DFU 刷机，见 [01-DFU固件升级.md]）搬进浏览器。

### 4.1 设备侧声明

WebUSB 复用 MS OS 2.0 同款的 BOS Platform Capability 机制，但使用自己的能力 UUID `3408B638-09A9-47A0-8BFD-A0768815B665`，字段包括：

| 字段 | 说明 |
|---|---|
| bcdVersion | 0x0100 |
| bVendorCode | 厂商请求码（主机用它发两条额外请求） |
| iLandingPage | 落地页 URL 描述符索引（0 表示无） |

主机随后用该厂商码请求 **URL 描述符**（类型编号 0x0002）：首字节为方案前缀（0x00=`http://`、0x01=`https://`、0xFF=无前缀），后接 UTF-8 URL。设备还可声明允许的来源（allowed origins）域名列表，只允许指定网站访问。

### 4.2 主机侧 JavaScript API

```javascript
// 必须在用户手势（点击等）中调用
const device = await navigator.usb.requestDevice({
  filters: [{ vendorId: 0x2e8a, productId: 0x000a }]
});
await device.open();
await device.claimInterface(0);            // 类似 libusb 的 claim
await device.transferOut(0x01, data);      // 批量 OUT
const res = await device.transferIn(0x81, 64); // 批量 IN
await device.controlTransferOut({          // 控制传输(厂商请求)
  requestType: 'vendor', recipient: 'interface',
  request: 0x01, value: 0x00, index: 0
}, payload);
```

### 4.3 安全模型

| 机制 | 说明 |
|---|---|
| 用户手势 + 选择器 | `requestDevice` 必须由点击触发，并弹出设备选择对话框，用户显式勾选 |
| Origin 绑定 | 权限按网站来源授予并持久化；设备可声明允许的 origin，陌生站点即使知道 VID:PID 也无法静默连接 |
| 浏览器支持 | Chromium 系（Chrome/Edge/Opera）实现；Firefox/Safari 未实现 |
| 职责边界 | 不能访问系统保留接口（含声卡/网卡/HID 键盘等由内核占用的接口） |

## 5. libusb：桌面端免驱访问

libusb 是跨平台用户态 USB 库，免驱访问的接口匹配策略随系统而异：

| 平台 | 免驱条件 |
|---|---|
| Linux | 设备接口未被内核驱动占用即可直接访问；被占用时可 `detach_kernel_driver`（需 udev 权限规则授权普通用户） |
| Windows | 设备需绑定 WinUSB/libusb/winusb 兼容驱动——正是第 3 节 MS OS 描述符的用武之地；存量设备可用 Zadig 工具手动换绑 |
| macOS | 系统不会为未知厂商类自动加载驱动，libusb 天然可直接打开 |

libusb 的 API（open/claimInterface/bulk transfer）与 WebUSB 高度同构——WebUSB 本质上是"进了浏览器的 libusb"。工程细节见 [../../60-枝干-主机侧与实现/04-libusb与用户态访问.md]。

## 6. 免驱/低驱方案选型对比

| 方案 | 免驱程度 | 吞吐/时延 | 固件成本 | 适合场景 |
|---|---|---|---|---|
| HID | 全平台免驱 | 受报告速率与端点轮询限制（约每毫秒千字节级，远低于批量） | 需报告描述符 | 配置工具、低速率传感、传感器面板（见 [../HID-人机接口设备/00-HID概述与定位.md]） |
| CDC-ACM | Linux/macOS/Win10+ 免驱 | 批量级吞吐 | 需实现 CDC 接口组 | 虚拟串口、日志口、AT 命令通道 |
| WinUSB + MS OS 描述符 | Windows 免驱（其他系统配 libusb） | 批量级 | 描述符工作量小 | 自定义协议设备、产测/调试工具 |
| WebUSB | Chromium 浏览器内免驱 | 批量级 | BOS 能力 + 厂商码 | 网页版刷机/配置器、在线示波器 |
| 厂商类 + 专有驱动 | 需装驱动 | 无限制（可用等时/高速大包） | 协议自由但驱动开发昂贵 | 高吞吐专有设备（采集卡、调试器） |

选型口诀：**能用标准类就用标准类；确需自定义协议时，叠加 WinUSB 描述符 +（可选）WebUSB 能力**，让同一台设备在桌面用 libusb、在浏览器用 WebUSB、在手机上用 OTG 应用三线通吃。

## 7. 实践要点

- 0xEE 字符串描述符对非 Windows 系统是"多余"的，某些 Linux 工具会将其打印为乱码——属正常现象。
- MS OS 2.0 的兼容 ID 条目是**函数级**的，要正确挂在对应接口子集下，否则 Windows 只会绑定设备级默认驱动。
- WebUSB 的 `claimInterface` 与内核驱动互斥：若设备被 CDC/HID 内核驱动占用，浏览器将无法 claim，设计固件时应把 WebUSB 接口设为 0xFF。
- WebUSB 规范要求落地页可被主机校验，避免恶意站冒名；发布前用 `chrome://usb-internals` 测试描述符。

## 相关节点

- [../../60-枝干-主机侧与实现/04-libusb与用户态访问.md]（libusb 工程细节）
- [../../10-树干-USB核心/07-描述符详解.md]（BOS/平台能力/字符串描述符）
- [../../10-树干-USB核心/08-枚举流程与标准请求.md]（厂商控制请求）
- [01-DFU固件升级.md]（WebUSB 的杀手级应用之一）
- [../HID-人机接口设备/00-HID概述与定位.md]（免驱方案对照）
- [../CDC-通信设备类/](../CDC-通信设备类/)（串口桥的免驱替代）
