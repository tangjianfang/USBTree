---
title: "虚拟串口 ACM"
layer: 枝干/设备类协议
section: CDC-通信设备类
doc-path: 20-枝干-设备类协议/CDC-通信设备类/01-虚拟串口ACM.md
---
# 虚拟串口 ACM

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[CDC] → 叶
> ⬆️ 父节点: [00-CDC概述](00-CDC概述.md)

## 1. ACM 的定位

ACM（Abstract Control Management，抽象控制模型）是 CDC 中最常用的子类：**把 USB 批量端点伪装成一条 RS-232 串口线路**。操作系统枚举后出现虚拟 COM 口/ttyACM*，应用照旧用串口 API 读写——但底层没有 UART，只有 USB。这是嵌入式设备调试口、Arduino、GPS 模组、LoRa 模组的标准形态。

## 2. 完整描述符组合（背下来）

一个 ACM 功能 = 通信接口 + 数据接口，描述符布局：

```
IAD (0x0B: FirstInterface=0, Count=2, Class=0x02/0x02/0x01)
├── 接口0 (通信): bInterfaceClass=0x02, SubClass=0x02(ACM), Protocol=0x01(AT)
│   ├── CS_INTERFACE Header      (0x24/0x00, bcdCDC=0x0110)
│   ├── CS_INTERFACE ACM         (0x24/0x02, bmCapabilities=0x02)
│   ├── CS_INTERFACE Union       (0x24/0x06, Master=0, Slave=1)
│   ├── CS_INTERFACE CallMgmt    (0x24/0x01, bmCapabilities=0x00, DataIf=1)
│   └── 端点: 中断 IN (wMaxPacketSize=8~16, bInterval=2ms~255ms)
└── 接口1 (数据): bInterfaceClass=0x0A, SubClass=0x00, Protocol=0x00
    └── 端点: 批量 IN + 批量 OUT (FS 64B / HS 512B)
```

逐项要点：

- **ACM bmCapabilities=0x02** 是最常见取值：支持 SET_LINE_CODING/GET_LINE_CODING/SERIAL_STATE，不支持 Send_Break 等高级特性；
- **Union 是灵魂**：没有它，主机不知道接口 0 与接口 1 属于同一功能；
- **中断 IN 端点必须存在**（哪怕从不发通知）——它是 ACM 描述符合法性的组成部分，bInterval 建议不要低于 2 ms；
- 批量端点包长按速率取上限（FS 64 / HS 512），吞吐才够（[带宽账本](../../10-树干-USB核心/06-四种传输类型.md)）。

## 3. 类请求详解

### 3.1 SET/GET_LINE_CODING (0x20/0x21)

7 字节线路编码结构：

| 偏移 | 字段 | 说明 |
|---|---|---|
| 0 | dwDTERate | 4 字节 LE，波特率数值（如 115200） |
| 4 | bCharFormat | 停止位：0=1 位，1=1.5 位，2=2 位 |
| 5 | bParityType | 校验：0=无，1=奇，2=偶，3=标志，4=空格 |
| 6 | bDataBits | 数据位 5~8/16 |

关键语义：**这是"抽象"参数**——设备应当记住它（应用层可能据此适配），但对 USB 传输本身毫无影响（USB 永远全速跑批量端点）。固件实现要点：`GET_LINE_CODING 必须可回读`，只实现 SET 的设备会被部分驱动拒绝。

### 3.2 SET_CONTROL_LINE_STATE (0x22)

wValue 位图：bit0=DTR（数据终端就绪），bit1=RTS（请求发送）。虚拟串口打开/关闭串口时驱动翻转 DTR——固件可用 DTR 下降沿做"主机已断开"事件（如退出命令模式）。

### 3.3 SEND_BREAK (0x23)

wValue = break 持续毫秒数（0xFFFF 特殊含义见规范）。用于线路 break 条件（如 STM32 DFU 的 1200bps touch：先 SET_LINE_CODING 到 1200 再复位进入 bootloader）。

## 4. 通知：SERIAL_STATE

设备经中断 IN 上报（bmRequestType=0xA1, bNotification=0x20, wLength=2）：

| 位 | 含义 |
|---|---|
| bit3 (0x08) | DSR（数传机就绪） |
| bit2 (0x04) | break |
| bit1 (0x02) | Ring |
| bit0 (0x01) | DCD（载波检测） |

发送条件：状态变化时；无变化不滥发。主机侧重：多数终端程序靠 DCD 判断"线路在位"。

## 5. 数据流与吞吐

```
应用 write() → 驱动缓冲 → 批量 OUT → 设备端点缓冲 → 固件业务
```

- 零长度包 (ZLP) 语义：当传输长度恰为 wMaxPacketSize 整数倍时，框架用 ZLP 标记"这次请求结束"——固件必须正确处理，否则短包粘包（[固件栈](../../60-枝干-主机侧与实现/03-设备端固件栈.md)）；
- 实测吞吐：FS 下 300~700 KB/s，HS 下 5~40 MB/s（取决于主机驱动与固件缓冲策略）；
- 流控缺失提醒：ACM 没有硬件流控语义（RTS/CTS 是抽象的），高速数据流靠批量 NAK 天然反压——设备端缓冲满了让端点 NAK 即可，这是批量传输的礼物（[传输类型](../../10-树干-USB核心/06-四种传输类型.md)）。

## 6. 主机侧驱动

| 平台 | 驱动 | 设备出现为 |
|---|---|---|
| Linux | cdc_acm（内核内置） | /dev/ttyACM0 |
| Windows 10+ | usbser.inf 内置 | COM 口（免 INF） |
| Windows 7 | 需 INF 指向 usbser | COM 口 |
| macOS | 内置 IODriverKit | /dev/tty.usbmodem* |

对比厂商串口芯片（FTDI/CH340 需各自驱动）与 WebUSB 方案的选择见[WebUSB 与厂商自定义类](../其他设备类/06-WebUSB与厂商自定义类.md)。

## 7. 固件实现清单（TinyUSB/裸机通用）

- [ ] 描述符：IAD + 双接口 + 四个功能描述符齐全（顺序：Header→ACM→Union→CallMgmt）；
- [ ] 端点 0 响应 0x20/0x21/0x22/0x23 四个类请求，GET 可回读；
- [ ] 批量 OUT/IN 双缓冲，ZLP 边界正确；
- [ ] （可选）DTR 边沿回调、环形缓冲、热插拔后缓冲清空；
- [ ] 复合（HID+CDC）时 IAD 与接口编号连续性检查（[索引](../00-设备类索引.md)）。

## 相关节点

- 上一级: [00-CDC概述](00-CDC概述.md) · 兄弟: [02-网络子类ECM-NCM-RNDIS](02-网络子类ECM-NCM-RNDIS.md)
- 树干: [四种传输类型](../../10-树干-USB核心/06-四种传输类型.md)
- 应用: [枚举失败排查手册](../../70-枝干-调试测试与安全/02-枚举失败排查手册.md)
