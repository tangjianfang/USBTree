---
id: 43-device-firmware
title: "设备端固件栈与 TinyUSB 实战"
topic: device/firmware
level: 进阶
keywords: ["TinyUSB", "tud_task", "tud_descriptor_device_cb", "tud_hid_report", "tud_hid_set_report_cb", "tusb_config.h", "DCD", "USBD", "STM32 USB device library", "Zephyr", "ZLP", "composite firmware"]
sources:
  - path: "60-枝干-主机侧与实现/03-设备端固件栈.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/03-设备端固件栈.md"
  - path: "60-枝干-主机侧与实现/05-实战-TinyUSB设备固件.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/05-实战-TinyUSB设备固件.md"
spec_refs: ["TinyUSB documentation", "USB 2.0 ch.9"]
related: ["07-enumeration-requests", "11-hid-core", "42-linux-macos-libusb"]
usbtree_commit: c987a96
generated: 2026-11-27
---

# 设备端固件栈与 TinyUSB 实战

> 层级 进阶 · 主题 `device/firmware` · 相关：[枚举流程、Setup 包与标准请求](07-enumeration-requests.md)、[HID 核心：类描述符、报告描述符 Item、Usage、类请求](11-hid-core.md)、[libusb 用户态访问、Linux Gadget/usbip、macOS 与 Linux 主机开发](42-linux-macos-libusb.md)

## 核心事实 Key Facts

> 由维护者整理并与规范核对；与下方 USBTree 原文冲突时以本节为准。

- 分层：DCD（设备控制器驱动，ISR）→ USBD 核心（EP0、标准请求、描述符回调）→ 类驱动（HID/CDC/MSC/MIDI/Audio/Vendor/DFU）→ 应用回调。
- TinyUSB 回调：tud_descriptor_device_cb、tud_descriptor_configuration_cb、tud_descriptor_string_cb、tud_hid_descriptor_report_cb、tud_hid_get_report_cb、tud_hid_set_report_cb、tud_mount_cb / tud_umount_cb / tud_suspend_cb / tud_resume_cb；发送 tud_hid_ready() + tud_hid_report(id, buf, len)；主循环 tud_task()；唤醒 tud_remote_wakeup()。
- 配置宏：CFG_TUSB_RHPORT0_MODE / CFG_TUD_ENDPOINT0_SIZE / CFG_TUD_HID / CFG_TUD_HID_EP_BUFSIZE / CFG_TUD_CDC / CFG_TUD_MSC。
- 固件铁律见 [07-enumeration-requests](07-enumeration-requests.md)。

## 原文：03-设备端固件栈

> Source: [60-枝干-主机侧与实现/03-设备端固件栈.md](https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/03-设备端固件栈.md)

设备端的 USB = **一片 USB 外设 IP + 一个固件协议栈 + 你的类逻辑**。本文聚焦 MCU 场景：外设 IP 概貌、主流开源栈选型、复合设备描述符组装、以及最易翻车的时序与缓冲细节。

### 一、常见 MCU 的 USB 外设 IP 概貌

| 厂商/系列 | 外设 | 速度 | 关键特征 |
|---|---|---|---|
| STM32 (F0/F1/F3/L0/G0 等) | `USB`（Device FS） | FS | 全速设备；部分型号支持 CRS 时钟恢复，可晶振-less 从 VBUS 帧 SOF 校准时钟 |
| STM32 (F4/L4/G4/F7/H7) | `OTG_FS` | FS | 设备+主机双角色 |
| STM32 (F4/F7/H7 等) | `OTG_HS` | **HS**（内置 PHY 仅 FS） | 真·高速必须外接 **ULPI** PHY（如 USB3300 类芯片）；内置 PHY 模式下只有 FS 能力 |
| ESP32-S2 / S3 | 内置 USB OTG | FS | Synopsys 设计的 OTG 外设；ESP-IDF 设备栈基于 TinyUSB；S3 另有 USB-Serial-JTAG 硬件通道 |
| RP2040 / Raspberry Pi Pico | 内置 USB 控制器 | FS | 设备+主机（软件辅助），Pico SDK 官方集成 TinyUSB；双 AHB 主控、端点缓冲可编程 |
| NXP (LPC55xx / i.MX RT / Kinetis) | ChipIdea 或 Synopsys IP | FS/HS | HS 通常需外部 PHY；SDK 自带完整 device/host 协议栈 |
| GD32 / CH32 (国产兼容生态) | 与 STM32 高度兼容 | FS/HS | GD32 的 USBFS/USBD、CH32F103/V103 与 STM32 对应外设寄存器级相似，迁移成本低；CH32V307 带高速 USBHS |

选型判断口诀：**查速度先问 PHY**——宣称 HS 却无外置 ULPI PHY 引脚的，基本都是 FS-only。

### 二、三大开源固件栈对比

| 维度 | TinyUSB | LUFA | Zephyr usb/device_next |
|---|---|---|---|
| 定位 | 跨平台通用栈，事实上的行业标准 | AVR 单片机经典栈 | Zephyr RTOS 内置的**新一代**设备栈（取代旧 `usb/device`） |
| 平台 | 极广：STM32/ESP32-S2/S3/RP2040/NXP/SAMD/nRF/SONY…，官方 BSP 数十种 | 仅 Atmel/Microchip AVR（ATmega32U4 等 USB AVR） | Zephyr 支持的所有 SoC |
| 角色 | device + host 双栈 | 仅 device（host 很弱） | device + host |
| 设备类 | CDC、HID、MSC、MIDI、DFU、WebUSB、UAC2、BT、Vendor、ECM/RNDIS 等 | CDC、HID、MSC、MIDI、DFU、RNDIS 等 | CDC、HID、MSC、BT、Loopback 等（新栈类支持持续扩充） |
| 编程模型 | **回调驱动**：`tud_cdc_rx_cb` / `tud_hid_get_report_cb`…，应用只填回调 | 同为事件回调，风格类似但 API 独立 | 设备栈 API + 类 API（DEVICEDTS 风格），与 Zephyr 设备模型绑定 |
| 示例生态 | 极丰富， boards 目录含各开发板工程 | 丰富（AVR 时代积累） | 随 Zephyr samples 提供 |
| 厂商背书 | ESP-IDF、Pico SDK、Adafruit 均以它为基础 | 无（社区经典） | Zephyr 官方路线 |

厂商闭源/半开源栈（备选）：**STM32 Cube USB Device Library**（CubeMX 生成，与 HAL 绑定）、**ESP-IDF usb 外设驱动**（主机侧 esp_usb 厂商驱动 + 设备侧 TinyUSB）、**NXP MCUXpresso SDK USB 栈**（device+host，含高速 PHY 配置）。当前主流建议：新项目优先 TinyUSB，厂商栈仅在需要深度集成厂商中间件（如 ST 的 UVC 摄像头例程）时选。

#### TinyUSB 应用骨架

TinyUSB 的使用形态固定：初始化 → 后台任务 → 类回调。所有类逻辑都发生在回调里，应用无阻塞轮询：

```c
#include "tusb.h"

/* 描述符集中回调：主机要什么给什么（返回长度） */
uint8_t const *tud_descriptor_device_cb(void)      { return dev_desc; }
uint8_t const *tud_descriptor_configuration_cb(uint8_t idx) { return cfg_desc; }
uint16_t const *tud_descriptor_string_cb(uint8_t idx, uint16_t langid) { return str_desc[idx]; }

/* 类回调示例：CDC 收到数据 → 原样回显 */
void tud_cdc_rx_cb(uint8_t itf) {
    uint8_t buf[64];
    uint32_t n = tud_cdc_read(buf, sizeof buf);
    tud_cdc_write(buf, n);
    tud_cdc_write_flush();
}

int main(void) {
    board_init();
    tusb_rhport_init_t dev_init = { .role = TUSB_ROLE_DEVICE,
                                    .speed = TUSB_SPEED_AUTO };
    tud_init(BOARD_TUD_RHPORT, &dev_init);   /* 栈初始化（不拉 D+） */
    board_usb_connect();                      /* 显式上拉，触发枚举 */

    while (1) {
        tud_task();          /* USB 事件泵：setup/传输/复位全在此分派 */
        led_blink_task();
    }
}
```

移植关注点只有三件：`tusb_config.h`（使能的类与端点数）、`board.h`（时钟/引脚/上拉控制）、DCache 一致性（H7/F7 类带缓存的 MCU 需对 EP 缓冲做对齐与 invalidate）。

### 三、复合设备(IAD)描述符组装骨架

HID + CDC-ACM 复合设备的关键：**CDC 的两个接口要用 IAD 绑定成一个功能**，且设备描述符的设备类字段必须设为 `0xEF/0x02/0x01`（Misc/Common/IAD），否则 Windows 的 `usbccgp.sys` 无法正确拆分（详见 [02-操作系统USB支持](40-host-controller-os.md)）。

```c
/* ===== 设备描述符：复合设备三件套 ===== */
const uint8_t dev_desc[18] = {
    18,    0x01,
    0x00, 0x02,          /* bcdUSB = 2.00 */
    0xEF, 0x02, 0x01,    /* bDeviceClass/SubClass/Protocol = Misc/Common/IAD  ← 关键 */
    64,                  /* bMaxPacketSize0 (FS) */
    VID_L, VID_H, PID_L, PID_H,
    0x00, 0x01,          /* bcdDevice */
    1, 2, 3,             /* iManufacturer / iProduct / iSerialNumber */
    1                    /* bNumConfigurations */
};

/* ===== 配置描述符：顺序拼接，wTotalLength = 全部长度之和 ===== */
const uint8_t cfg_desc[] = {
    /* 配置描述符 (9B) */
    9, 0x02, LEN_L, LEN_H,  /* wTotalLength：与数组总长严格一致 */
    3, 1, 0x80, 50, 0,      /* 3 接口, 配置值1, 总线供电, 100mA */

    /* -- IAD (8B)：把接口0+1打包成 CDC 功能 -- */
    8, 0x0B, 0, 2, 0x02, 0x02, 0x01, 0,
    /*        ^首接口0 ^接口数2 ^类=CDC */

    /* -- 接口0：CDC 通信类 (含功能描述符 + IN1 通知端点) -- */
    9, 0x04, 0, 0, 1, 0x02, 0x02, 0x01, 0,
    5, 0x24, 0x00, 0x10, 0x01,        /* Header 功能 */
    4, 0x24, 0x02, 0x06,              /* ACM 功能：支持 SET_LINE_CODING 等 */
    5, 0x24, 0x06, 0, 1,              /* Union：主0 从1 */
    7, 0x24, 0x01, 0, 1,              /* Call Management */
    7, 0x05, 0x81, 0x03, 8, 0, 16,    /* EP1 IN 通知端点，中断，16ms */

    /* -- 接口1：CDC 数据类 (Bulk 对) -- */
    9, 0x04, 1, 0, 2, 0x0A, 0, 0, 0,
    7, 0x05, 0x82, 0x02, 64, 0, 0,    /* EP2 IN  bulk 64B */
    7, 0x05, 0x02, 0x02, 64, 0, 0,    /* EP2 OUT bulk 64B */

    /* -- 接口2：HID（单接口功能，无需 IAD）-- */
    9, 0x04, 2, 0, 1, 0x03, 1, 1, 0,  /* Boot Keyboard */
    9, 0x21, 0x11, 0x01, 0, 1, 0x22, RPT_L, RPT_H,  /* HID 描述符 → 报告描述符 */
    7, 0x05, 0x83, 0x03, 8, 0, 10,    /* EP3 IN 中断 8B 10ms */
};
/* 注意：HID 报告描述符本体不在此表内，通过 GET_DESCRIPTOR(0x22) 单独返回，
   见 ../20-枝干-设备类协议/HID-人机接口设备/00-HID概述与定位.md */
```

组装自检清单：每个描述符首字节 `bLength` == 该描述符实际字节数；`wTotalLength` == 数组长度；`bNumInterfaces`/`bNumEndpoints` 与实体逐一对应；端点地址不冲突。

### 四、端点缓冲与双缓冲（乒乓）

| 机制 | 原理 | 适用 |
|---|---|---|
| 单缓冲 | 一个 EP 寄存器/一块 RAM，CPU 取走前硬件 NAK | 低速率、低速轮询场景 |
| **双缓冲/乒乓** | 两块缓冲交替：硬件写 B 时 CPU 处理 A | 同步传输（必须，防丢帧）、高轮询率中断/bulk OUT |
| FIFO 分块 | 端点共享大 FIFO，按包动态分配（DWC 类 IP 常见） | 端点数量多、包长可变 |

陷阱：中断端点声明 `bInterval=1ms` 但 CPU 处理超过 1ms → 上一次数据还没取走，新数据只能 NAK，主机侧表现为**周期性丢样**。用乒乓缓冲 + 高优先级（或 DMA）搬运可解。

端点资源分配的两类典型 IP 风格：

| 风格 | 代表 IP | 缓冲组织 | 软件含义 |
|---|---|---|---|
| 静态 Buffer 描述表 | STM32 USB FS（btable）、CH32 | 每端点固定 TX/RX 缓冲地址+计数 | 包长固定，改配置需重排 btable |
| 共享动态 FIFO | DWC/OTG 类、ESP32-S2/S3 | 全局 RAM 池按端点分 FIFO 深度 | 端点数与包长可折中，需预算 GRXFSIZ/GNPTXFSIZ |

### 五、零长度包(ZLP)语义与粘包问题

短包(Short Packet, 长度 < `wMaxPacketSize`)隐含"传输结束"语义，由此推出 bulk/控制传输的边界规则：

**IN 方向（设备→主机）**

| 设备实际数据 M | 主机预期 wLength/长度 | 设备应做 |
|---|---|---|
| M < MPS | — | 正常发完即结束（短包天然终结） |
| M = k×MPS 且 M < 预期 | 预期 > M | **必须补发 ZLP**，否则主机继续等待 |
| M = 预期（恰为整数倍） | M == 预期 | 不补 ZLP |

典型 bug：CDC 数据恰好 64 字节（FS MPS 整数倍）→ 主机驱动缓冲等待 → 看起来"少收一帧"。类协议自带长度字段的（如 MSC 的 `dCBWDataTransferLength`）不需要 ZLP。

**OUT 方向（主机→设备）**

- 协议自带长度字段（BOT 的 CBW）→ 无粘包问题；
- 裸流协议（自定义 bulk）→ 必须约定边界：要么主机端逢整包补 ZLP，要么应用层加分隔符。否则主机一次提交携带两帧数据时，设备端"分包"逻辑无法还原消息边界，即**粘包**。

### 六、枚举时序的关键点

1. **上电稳定优先**：复位后先完成时钟初始化、内核/PLL 稳定，再进入 USB 逻辑。主机检测到插入后有 ≥100ms 的稳定等待窗口，固件可以晚一点"上线"，但**一旦上拉就不能装死**。
2. **D+ 上拉时机由固件控制**：`pull-up` 使能就是设备的"自报家门"开关。正确顺序：EP0 缓冲与中断就绪 → 描述符缓存可读 → 再使能上拉。若上电即上拉而描述符没准备好，`GET_DESCRIPTOR` 只能返回 NAK 或垃圾 → 主机报"无法识别的设备"。这也是"软重枚举"（拔插模拟）的实现方式：断开上拉等数百 ms 再连接。
3. **端点 0 随时待命**：复位结束后 `GET_DESCRIPTOR(Device, 前 8 字节)` 会立刻到来；setup→data→status 全路径的中断处理要快于 8 字节@1.5MB/s 的耗尽时间。FS 时钟误差需满足 ±0.25%（2500ppm）级——**用内部 HSI 跑 USB 是常见枚举失败根源**（见 [../70-枝干-调试测试与安全/02-枚举失败排查手册.md](50-debug-troubleshooting.md)）。
4. **SET_ADDRESS 的生效时机**：地址在 **status 阶段完成后**生效，固件若在 data/status 期间就切地址，主机后续请求将石沉大海（规范行为，硬件 IP 通常已处理，自研栈易踩）。

### 七、低功耗与远程唤醒固件要点

- **挂起检测**：总线上 3ms 无任何事务（含 SOF）→ 硬件产生 SUSPEND 中断 → 固件降频、停无关外设，但必须保持对差分线唤醒信号（K 状态，FS）的检测能力。
- **恢复**：检测到主机 resume（20ms+ K）或本地需要唤醒；本地唤醒（**远程唤醒 Remote Wakeup**）流程：
  1. 配置描述符 `bmAttributes` bit5=1 声明能力；
  2. 主机 `SET_FEATURE(DEVICE_REMOTE_WAKEUP)` 显式使能后**才允许**发起；
  3. 设备驱动 RESUME 信号（K 状态保持 20ms 以上），随后主机恢复 SOF。
- **电流承诺**：挂起未配置状态 ≤0.5mA、配置后挂起 ≤2.5mA 是硬指标（合规项，见 [../70-枝干-调试测试与安全/03-USB-IF合规认证.md](51-compliance-security.md)），固件须真正关闭 LED/外设才达得到。
- 调试提示：量功耗时注意"枚举期间 vs 挂起期间"分开测；远程唤醒失效多因固件在挂起态把唤醒检测的外设时钟也关了。

## 原文：05-实战-TinyUSB设备固件

> Source: [60-枝干-主机侧与实现/05-实战-TinyUSB设备固件.md](https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/05-实战-TinyUSB设备固件.md)

> 工具与官方文档缓存索引: [../80-参考资料/README.md](92-spec-references.md)

本文从零到跑通一个 TinyUSB（Tiny USB Stack）复合设备：**HID 键盘 + CDC-ACM 虚拟串口**。主叙述平台选用 **RP2040（Raspberry Pi Pico，Pico SDK 集成 TinyUSB）**，移植到 STM32 / ESP32-S3 的差异点单独标注。全部代码成体系，可直接照抄建立工程。固件栈版本 TinyUSB 0.17.0（Pico SDK 2.x 内置；更新版本 API 以官方仓库 github.com/hathach/tinyusb 为准）。描述符原理见 [../10-树干-USB核心/07-描述符详解.md](06-descriptors.md)；键盘报告见 [../20-枝干-设备类协议/HID-人机接口设备/05-键盘详解.md](12-hid-devices.md)；CDC 见 [../20-枝干-设备类协议/CDC-通信设备类/01-虚拟串口ACM.md](14-cdc.md)。

### 一、目标与工程结构

最终效果：板子插上 USB 后，主机同时出现一个键盘（按板上按键自动敲出 `hello`）和一个虚拟串口（回环透传）。工程结构：

```
cdc_hid_kbd/
├── CMakeLists.txt          # 构建脚本
├── pico_sdk_import.cmake   # 从 pico-sdk 仓库/external 目录复制
├── tusb_config.h           # TinyUSB 配置（栈裁剪、缓冲）
├── usb_descriptors.c       # 全部描述符 + TinyUSB 描述符回调
└── main.c                  # 应用逻辑 + 类回调（HID get/set report）
```

> 说明：TinyUSB 官方示例把描述符与回调统一放在 `usb_descriptors.c`；部分教程拆成 `usb_desc.c`（纯描述符数据）+ `usb_descriptors.c`（回调），内容等价。

复合设备（Composite Device）关键设计：

| 项目 | 取值 | 原因 |
|---|---|---|
| 设备类 bDeviceClass | `0xEF / 0x02 / 0x01`（Miscellaneous/Common/IAD） | 使用 IAD（Interface Association Descriptor，接口关联描述符）聚合 CDC 双接口，必须用这个三元组 |
| 接口布局 | ITF0 CDC 控制 + ITF1 CDC 数据 + ITF2 HID | CDC 固定占两个接口；HID 单接口 |
| 端点 | EP0x81 中断(通知)、0x02/0x82 批量(CDC 数据)、0x83 中断(HID 输入) | 5 个非 0 端点地址，远低于 RP2040 上限（每方向 16 个） |

### 二、tusb_config.h：栈配置

```c
/* tusb_config.h —— TinyUSB 裁剪与缓冲配置
 * 依赖：TinyUSB 0.17.x；RP2040 + Pico SDK（其他 MCU 只需改 CFG_TUSB_MCU/CFG_TUSB_OS） */
#ifndef _TUSB_CONFIG_H_
#define _TUSB_CONFIG_H_

//---- MCU 与 OS：Pico SDK 集成下也可由构建系统注入 ----
#define CFG_TUSB_MCU               OPT_MCU_RP2040
#define CFG_TUSB_OS                OPT_OS_PICO

//---- 设备栈总开关：本例只做设备（device），不开主机（host）----
#define CFG_TUD_ENABLED            1
#define CFG_TUD_MAX_SPEED          OPT_MODE_FULL_SPEED  // RP2040 仅全速（Full Speed, 12 Mbps）

//---- 端点 ----
#define CFG_TUD_ENDPOINT0_SIZE     64   // EP0 最大包：全速设备 64
// 可用端点地址数上限；老版本该宏拼写为 CFG_TUD_ENDPPOINT_MAX（以所用版本头文件为准）
#define CFG_TUD_ENDPPOINT_MAX      8    // 注意官方拼写就是双 P（ENDPPOINT），见 tusb_option.h

//---- 内存对齐（DMA 需按字对齐）----
#ifndef CFG_TUSB_MEM_SECTION
#define CFG_TUSB_MEM_SECTION
#endif
#ifndef CFG_TUSB_MEM_ALIGN
#define CFG_TUSB_MEM_ALIGN         TU_ATTR_ALIGNED(4)
#endif

//---- 类使能：只用 HID 与 CDC，其余关掉省 ROM/RAM ----
#define CFG_TUD_CDC                1
#define CFG_TUD_MSC                0
#define CFG_TUD_HID                1
#define CFG_TUD_MIDI               0
#define CFG_TUD_VENDOR             0

//---- CDC 缓冲：端点包大小与环形缓冲（Ring Buffer）----
#define CFG_TUD_CDC_EP_BUFSIZE     64   // 批量端点包大小
#define CFG_TUD_CDC_RX_BUFSIZE     256  // 设备→主机方向缓冲
#define CFG_TUD_CDC_TX_BUFSIZE     256  // 主机→设备方向缓冲
#define CFG_TUD_CDC_NOTIF_EP_BUFSIZE 8  // 通知端点（中断 IN）

//---- HID 缓冲：Boot 键盘 8 字节足够，给 64 通用 ----
#define CFG_TUD_HID_EP_BUFSIZE     64

#endif
```

要点：`CFG_TUD_ENABLED` 是设备栈总闸；每个类驱动各有一个数量宏（`CFG_TUD_HID`=HID 实例数，支持放多个实例）。缓冲宏直接影响 RAM 占用，按吞吐需求给，不必一律拉大。

### 三、usb_descriptors.c：描述符组装与回调

配置描述符（Configuration Descriptor）整体布局（共 100 字节），这是复合设备的核心：

| 块 | 长度 | 内容 |
|---|---|---|
| 配置描述符 | 9 | wTotalLength=100，bNumInterfaces=3 |
| IAD | 8 | 声明"接口 0~1 属于 CDC 功能" |
| CDC 控制接口 | 9 | 类 0x02，含 4 个功能描述符：Header(5)+Call Mgmt(5)+ACM(4)+Union(5) |
| 通知端点 | 7 | 0x81 中断 IN，bInterval=1ms（实际按 2^(n-1) 换算） |
| CDC 数据接口 | 9 | 类 0x0A，两个批量端点 |
| 批量端点 ×2 | 14 | 0x02 OUT / 0x82 IN，64 字节 |
| HID 接口 | 9 | 类 0x03，Boot 键盘 |
| HID 描述符 | 9 | 报告描述符长度 63，EP0x83 |
| HID 端点 | 7 | 0x83 中断 IN，bInterval=1 |

```c
/* usb_descriptors.c —— 设备/配置/HID 报告/字符串描述符 + TinyUSB 回调
 * 依赖：TinyUSB 0.17.x；与 tusb_config.h 同一工程 */
#include "tusb.h"

/* VID/PID：仅测试用（pid.codes 测试段），量产请换成自己注册的 VID */
#define USB_VID        0xCAFE
#define USB_PID        0x4004
#define USB_BCD        0x0200   // USB 2.0；用 0x0210+ 需要 BOS 描述符配合

// 接口编号（顺序必须与配置描述符一致）
enum {
  ITF_NUM_CDC_CTRL = 0,
  ITF_NUM_CDC_DATA,
  ITF_NUM_HID,
  ITF_NUM_TOTAL
};

// 端点分配
#define EPNUM_CDC_NOTIF  0x81   // CDC 通知（中断 IN）
#define EPNUM_CDC_OUT    0x02   // CDC 数据 OUT
#define EPNUM_CDC_IN     0x82   // CDC 数据 IN
#define EPNUM_HID_IN     0x83   // HID 键盘输入（中断 IN）

// 配置描述符总长 = 各宏展开长度之和，杜绝手算错
#define CONFIG_TOTAL_LEN    (TUD_CONFIG_DESC_LEN + TUD_CDC_DESC_LEN + TUD_HID_DESC_LEN)

// 设备描述符（18 字节）
tusb_desc_device_t const desc_device = {
    .bLength            = sizeof(tusb_desc_device_t),
    .bDescriptorType    = TUSB_DESC_DEVICE,
    .bcdUSB             = USB_BCD,
    // IAD 复合设备的固定三元组，缺了主机不会按 IAD 聚合接口
    .bDeviceClass       = 0xEF,
    .bDeviceSubClass    = 0x02,
    .bDeviceProtocol    = 0x01,
    .bMaxPacketSize0    = CFG_TUD_ENDPOINT0_SIZE,
    .idVendor           = USB_VID,
    .idProduct          = USB_PID,
    .bcdDevice          = 0x0100,
    .iManufacturer      = 0x01,
    .iProduct           = 0x02,
    .iSerialNumber      = 0x03,
    .bNumConfigurations = 0x01
};

// HID 报告描述符：标准 Boot 键盘（Input 8 字节 + Output 1 字节 LED），
// 与《HID 键盘详解》中的 Boot 键盘描述符逐字节一致
uint8_t const desc_hid_report[] = {
    TUD_HID_REPORT_DESC_KEYBOARD()
};

// 配置描述符：9 配置 + [8 IAD + CDC 双接口] + HID 接口 = 100 字节
uint8_t const desc_configuration[] = {
    // 配置描述符: 配置号1, 3个接口, 无字符串, 总长, 属性(总线供电), 100mA
    TUD_CONFIG_DESCRIPTOR(1, ITF_NUM_TOTAL, 0, CONFIG_TOTAL_LEN, 0x00, 100),

    // 接口 0+1: CDC-ACM。宏内部自动展开 IAD(8B) + 控制接口(9B) +
    // Header/CallMgmt/ACM/Union 功能描述符(19B) + 通知端点(7B) + 数据接口(9B) + 2 批量端点(14B)
    TUD_CDC_DESCRIPTOR(ITF_NUM_CDC_CTRL, 4, EPNUM_CDC_NOTIF, 8,
                       EPNUM_CDC_OUT, EPNUM_CDC_IN, 64),

    // 接口 2: HID Boot 键盘。参数: 接口号, 字符串, 子类/协议, 报告描述符长度, 端点, 包大小, 轮询间隔
    TUD_HID_DESCRIPTOR(ITF_NUM_HID, 5, HID_SUBCLASS_BOOT, HID_PROTOCOL_KEYBOARD,
                       sizeof(desc_hid_report), EPNUM_HID_IN,
                       CFG_TUD_HID_EP_BUFSIZE, 1)
};

// 字符串描述符（UTF-16 由回调转换）
char const *string_desc_arr[] = {
    (const char[]) { 0x09, 0x04 },  // 0: 语言 ID = 英语美国 0x0409
    "USBTree",                      // 1: 厂商
    "TinyUSB HID+CDC Composite",    // 2: 产品
    "20260001",                     // 3: 序列号（建议每板唯一）
    "TinyUSB CDC",                  // 4: CDC 接口
    "TinyUSB HID",                  // 5: HID 接口
};

static uint16_t desc_str[32];  // 转换缓冲：UTF-16 最多 31 字符 + 头

//---- TinyUSB 描述符回调：枚举时协议栈调用它们取描述符 ----

// 设备描述符请求（GET_DESCRIPTOR Device）
uint8_t const *tud_descriptor_device_cb(void) {
  return (uint8_t const *) &desc_device;
}

// 配置描述符请求（GET_DESCRIPTOR Configuration，index 从 0 起）
uint8_t const *tud_descriptor_configuration_cb(uint8_t index) {
  (void) index;  // 单配置，忽略
  return desc_configuration;
}

// HID 报告描述符请求（类特定请求 GET_DESCRIPTOR Report）
uint8_t const *tud_hid_report_descriptor_cb(uint8_t instance) {
  (void) instance;
  return desc_hid_report;
}

// 字符串描述符请求
uint16_t const *tud_descriptor_string_cb(uint8_t index, uint16_t langid) {
  (void) langid;
  uint8_t len = 0;

  if (index == 0) {
    desc_str[1] = 0x0409;           // 返回支持的语言
    len = 1;
  } else {
    if (index >= sizeof(string_desc_arr) / sizeof(string_desc_arr[0])) return NULL;
    const char *str = string_desc_arr[index];
    for (; *str && len < 31; str++) {   // ASCII 逐字节升位为 UTF-16
      desc_str[1 + len++] = (uint16_t)(*str);
    }
  }
  desc_str[0] = (uint16_t)((TUSB_DESC_STRING << 8) | (2 * len + 2));  // bLength 含 2 字节头
  return desc_str;
}
```

`TUD_HID_REPORT_DESC_KEYBOARD()` 是 TinyUSB 内置的标准 Boot 键盘报告描述符宏（63 字节：8 修饰键位 + 1 保留 + 6 键码数组 + LED Output 报告）；想逐项理解 Item 编码请对照 [../20-枝干-设备类协议/HID-人机接口设备/02-报告描述符与Item编码.md](11-hid-core.md)。

### 四、main.c：应用层（轮询骨架）

```c
/* main.c —— 应用逻辑：按键敲 "hello" + CDC 回环透传
 * 依赖：Pico SDK 2.x（pico_stdlib / hardware_gpio）+ TinyUSB */
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "tusb.h"

#define BUTTON_GPIO 15   // 按键接 GPIO15 与 GND 之间，内部上拉

// 'a'~'z' → HID 键码 0x04~0x1D；数字键 0x1E~0x27（键码表见《键盘详解》）
static uint8_t char_to_keycode(char c) {
  if (c >= 'a' && c <= 'z') return (uint8_t)(0x04 + (c - 'a'));
  if (c >= '1' && c <= '9') return (uint8_t)(0x1E + (c - '1'));
  if (c == '0') return 0x27;
  return 0;
}

// 敲一段文本：按下-抬起各发一帧 8 字节 Boot 键盘报告
static void send_text(const char *text) {
  for (const char *p = text; *p; p++) {
    uint8_t kc = char_to_keycode(*p);
    if (!kc) continue;

    uint8_t down[6] = { kc, 0, 0, 0, 0, 0 };
    if (!tud_hid_keyboard_report(0, 0, down)) return;   // 参数: 报告ID, 修饰键, 6键码
    while (!tud_hid_ready()) tud_task();                // 等上一帧送达

    uint8_t up[6] = { 0, 0, 0, 0, 0, 0 };
    tud_hid_keyboard_report(0, 0, up);
    while (!tud_hid_ready()) tud_task();
  }
}

static void hid_task(void) {
  static bool last = true;                 // 上拉：松开为高
  static uint32_t t_last = 0;
  bool now = gpio_get(BUTTON_GPIO);
  uint32_t now_ms = to_ms_since_boot(get_absolute_time());

  if (last && !now && (now_ms - t_last) > 200) {   // 下降沿 + 200ms 消抖
    t_last = now_ms;
    send_text("hello");
  }
  last = now;
}

// CDC 透传：主机发什么就回什么。tud_cdc_* 是 0 号实例的便捷宏
static void cdc_task(void) {
  if (tud_cdc_connected()) {               // 主机打开串口并拉起 DTR 才为真
    uint8_t buf[64];
    uint32_t n = tud_cdc_read(buf, sizeof(buf));
    if (n > 0) {
      tud_cdc_write(buf, n);
      tud_cdc_write_flush();               // 不 flush 会滞留在 TX 缓冲
    }
  }
}

int main(void) {
  stdio_init_all();                        // 仅用于 UART 日志，与 USB 无关
  gpio_init(BUTTON_GPIO);
  gpio_set_dir(BUTTON_GPIO, GPIO_IN);
  gpio_pull_up(BUTTON_GPIO);

  tud_init(0);                             // 初始化设备栈，rhport=0

  while (true) {
    tud_task();                            // USB 协议栈心跳，绝不能饿着
    cdc_task();
    hid_task();
    sleep_ms(1);
  }
  return 0;
}

//---- TinyUSB HID 类要求应用实现的两个回调（缺了直接链接失败）----
uint16_t tud_hid_get_report_cb(uint8_t instance, uint8_t report_id,
                               hid_report_type_t report_type,
                               uint8_t *buffer, uint16_t reqlen) {
  (void)instance; (void)report_id; (void)report_type; (void)buffer; (void)reqlen;
  return 0;   // 本例不支持 GET_REPORT
}

void tud_hid_set_report_cb(uint8_t instance, uint8_t report_id,
                           hid_report_type_t report_type,
                           uint8_t const *buffer, uint16_t bufsize) {
  (void)instance; (void)report_id; (void)bufsize;
  if (report_type == HID_REPORT_TYPE_OUTPUT && bufsize >= 1) {
    // 主机写 LED 状态：bit0=NumLock bit1=CapsLock bit2=ScrollLock，可驱动板上 LED
  }
}
```

### 五、构建与烧录

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)          # 从 pico-sdk/external/ 复制
project(cdc_hid_kbd C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

add_executable(cdc_hid_kbd main.c usb_descriptors.c)
target_include_directories(cdc_hid_kbd PRIVATE ${CMAKE_CURRENT_LIST_DIR})  # 提供 tusb_config.h
target_link_libraries(cdc_hid_kbd pico_stdlib hardware_gpio tinyusb_device)

pico_enable_stdio_usb(cdc_hid_kbd 0)    # 关闭 SDK 自带 USB stdio，避免与本设备冲突
pico_enable_stdio_uart(cdc_hid_kbd 1)
pico_add_extra_outputs(cdc_hid_kbd)
```

```bash
export PICO_SDK_PATH=~/pico-sdk
cmake -B build -S . -DPICO_BOARD=pico
cmake --build build
# 烧录：按住 BOOTSEL 插 USB → 出现 U 盘 RPI-RP2 → 拷入 build/cdc_hid_kbd.uf2
# 或使用 picotool: picotool load build/cdc_hid_kbd.uf2 -fx
```

**移植点速查**：

| 平台 | 差异 |
|---|---|
| STM32（如 F072/G071） | `CFG_TUSB_MCU` 改为对应 `OPT_MCU_STM32F0/...`（见 `tusb_option.h` 全表）；需提供 1ms 时基驱动 `tud_task`；官方例程 `examples/device/cdc_msc_hid` 可按 make `BOARD=` 直接编译再裁剪 |
| ESP32-S3 | 走 ESP-IDF 的 `esp_tinyusb` 组件（`idf.py add-dependency "espressif/esp_tinyusb"`），`CFG_TUSB_MCU` 由组件按芯片自动设置，应用只写描述符与回调；S2/S3 共用 DWC2 设备驱动 |
| 换速度 | RP2040 仅 FS；ESP32-S2/S3 也仅 FS；STM32 需 OTG_HS + 外置 ULPI PHY 才有 HS |

### 六、RTOS 骨架（FreeRTOS）

```c
/* RTOS 版骨架：USB 任务独立，应用任务另起。tusb_config.h 需:
 * #define CFG_TUSB_OS OPT_OS_FREERTOS，并保证 FreeRTOSConfig.h 在包含路径中 */
static void usb_device_task(void *arg) {
  (void)arg;
  tud_init(0);
  while (1) {
    tud_task();          // FreeRTOS 下内部阻塞在事件队列，无需额外 delay
  }
}

static void app_task(void *arg) {
  (void)arg;
  while (1) {
    cdc_task();
    hid_task();
    vTaskDelay(pdMS_TO_TICKS(1));
  }
}

int rtos_main(void) {
  xTaskCreate(usb_device_task, "usbd", 2048, NULL, 5, NULL);  // 优先级高于应用
  xTaskCreate(app_task, "app", 2048, NULL, 4, NULL);
  vTaskStartScheduler();
  return 0;
}
```

规则：`tud_task` 全系统只在一个任务里跑；任务栈建议 ≥ 1.5 KB（复合设备取 2 KB 稳妥）；类回调在 `tud_task` 上下文执行，回调里不要长阻塞。

### 七、常见问题

| 现象 | 根因 | 处置 |
|---|---|---|
| 主机报"设备描述符请求失败"，或 `lsusb -v` 里 wTotalLength 与实际不符 | 配置描述符 `wTotalLength` ≠ 各 `bLength` 之和（手写描述符最易错） | 一律用 `TUD_CONFIG_DESC_LEN + TUD_xxx_DESC_LEN` 求和；核对方法见 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](50-debug-troubleshooting.md) |
| 设备枚举到一半卡死 / 枚举成功但收发全无响应 | `tud_task()` 没喂：主循环被 `while(!ready)` 死等或长 `sleep` 卡住 | 所有等待循环里必须继续调 `tud_task()`；主循环单次阻塞别超过 1ms 量级 |
| 编译报端点不足 / 运行时分配端点失败 | `CFG_TUD_ENDPPOINT_MAX`（官方拼写双 P）小于实际用量，或超出芯片端点数（RP2040 每方向 16；STM32 FS 通常 8；ESP32-S2/S3 更少） | 精简功能或调大宏；非 0 端点地址按 IN/OUT 各自计数，以芯片手册为准 |
| 串口打不开、`tud_cdc_connected()` 恒为假 | 主机未拉 DTR（没真正打开串口），或没 `write_flush` | 先 `tud_cdc_write_flush()`；上位机用 pyserial 打开端口再测 |
| 键盘一次都不上报 | 未等 `tud_hid_ready()` 就调 `tud_hid_keyboard_report`，返回 false 被丢弃 | 发送前轮询 ready；上一帧在途时新帧必须等 |
| Windows 出现设备但找不到串口 | CDC 功能描述符/IAD 缺失或 VID/PID 驱动冲突 | 用 `TUD_CDC_DESCRIPTOR` 完整展开；UsbTreeView 检查接口类是否 0x02/0x0A |
