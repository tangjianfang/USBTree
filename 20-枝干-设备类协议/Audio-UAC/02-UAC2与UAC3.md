---
title: "UAC 2.0 与 UAC 3.0"
layer: 枝干/设备类协议
section: Audio-UAC
doc-path: 20-枝干-设备类协议/Audio-UAC/02-UAC2与UAC3.md
---
# UAC 2.0 与 UAC 3.0

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[UAC] → 叶
> ⬆️ 父节点: [00-UAC概述](00-UAC概述.md)

## 1. UAC 2.0：实体化与高速化 (2009)

UAC2 的两个根本变化：

1. **时钟成为一等实体**——Clock Source/Selector/Multiplier 单独成实体，采样率控制从"端点的附属属性"升级为"时钟实体的属性"；
2. **面向高速带宽**——24bit/192kHz 多通道、多流并行成为可能。

### 1.1 时钟实体三件套

| 实体 | CS_INTERFACE 子类型 | 职责 |
|---|---|---|
| Clock Source | 0x0A | 一个真实时钟源（内部 PLL / SPDIF 输入 / …），带采样率控制与有效性/锁定状态 |
| Clock Selector | 0x0B | 多时钟源选一（如"内部晶振 or 外部字时钟"） |
| Clock Multiplier | 0x0C | 时钟倍频（整数/分数） |

### 1.2 请求体系差异（与 UAC1 对照背）

| | UAC 1.0 | UAC 2.0 |
|---|---|---|
| 读/写当前值 | GET_CUR=**0x81** / SET_CUR=0x01（evolve #37 按 Table A-9 勘误） | CUR：0x01(SET)/0x01(GET, bit7 区分? — 2.0 中请求码 CUR=0x01, RANGE=0x02，方向由 bmRequestType 区分) |
| 范围查询 | GET_MIN/GET_MAX/GET_RES (0x84~0x86) | **RANGE (0x02)** 一次返回 [Min,Max,Res] 列表 |
| 采样率挂在哪 | 同步端点 (SAMPLING_FREQ_CONTROL) | **Clock Source 实体** (CS_SAM_FREQ_CONTROL=0x01) |
| 寻址 | wValue/wIndex 简单 | wValue=(控制选择子<<8)\|通道号, wIndex=(实体ID<<8)\|接口——**一切控制都经实体 ID** |
| 控制位图 | 8 位 | 16 位（支持更多控制类型） |

UAC2 的 GET_INFO 返回能力位（bit0=可读，bit1=可写），驱动先问再调，交互更严谨。

### 1.3 描述符变化

- CS_INTERFACE 子类型新增：CLOCK_SOURCE 0x0A、CLOCK_SELECTOR 0x0B、CLOCK_MULTIPLIER 0x0C、SAMPLE_RATE_CONVERTER 0x0D；
- Terminal 实体多一个 **bCSourceID** 字段——直接声明"我由哪个时钟源驱动"，实体图从此含时钟拓扑；
- AS 接口的 Type I 格式描述符支持高带宽同步端点（HS 微帧 ×2/×3 事务，[传输类型](../../10-树干-USB核心/06-四种传输类型.md)）；
- 反馈端点数值格式从 10.14 改为 **16.16** 定点。

### 1.4 高速带来的能力表

| 指标 | UAC1 (FS) | UAC2 (HS) |
|---|---|---|
| 典型上限 | 16bit/48kHz 立体声舒适 | 24bit/192kHz × 8 通道可行 |
| 多设备同总线 | 2~3 个即挤占 | 数十个无压力 |
| DSD/DoP、专业多轨 | 不可行 | DAC 旗舰标配 |

### 1.5 驱动支持现状

Linux snd-usb-audio 全面支持；macOS 内置；**Windows 10 1703+ 才内置 UAC2**（此前需厂商驱动）——这是 UAC2 普及晚于技术成熟的原因，也是老设备坚持 UAC1 的现实理由。

## 2. UAC 3.0：为移动而生，为省电而改 (2016)

UAC3 的动机：手机/平板 OTG 生态里 USB 音频的**待机功耗**。核心变化：

- **电源优先架构**：挂起时音频路径可近乎断电，唤醒/待机由 BOS + 新协议驱动；
- **实体模型再重构**：引入 Cluster/GPI/GPIO/Interrupt 实体，控制路径与数据路径进一步解耦；
- **BADD**（Basic Audio Device Definition）：预定义几种标准拓扑（如"Type I 头戴式耳机""Type II 转接坞"），设备按模板声明，主机按模板解析——牺牲灵活性换一致性；
- 音频数据仍走同步端点，控制面改用"Interrupt Message"经中断端点上报（控制事件主动化）。

**现实地位**：规范完整、生态冷淡——手机厂商多走自带协议/厂商驱动，PC 生态支持有限。选型建议：**消费级新设备 → UAC2；嵌入式兼容优先 → UAC1；UAC3 暂观望**。

## 3. 三代总对比

| | UAC 1.0 (1998) | UAC 2.0 (2009) | UAC 3.0 (2016) |
|---|---|---|---|
| 目标速率 | 全速 FS | 高速 HS | HS（电源优化） |
| 时钟模型 | 端点属性 | **Clock Source 实体** | Clock Source 实体+电源状态 |
| 范围查询 | MIN/MAX/RES 三请求 | RANGE 一次到位 | RANGE |
| 典型应用 | 嵌入式声卡/麦克风 | DAC/专业音频/会议设备 | 移动配件（少） |
| 主机免驱 | 全平台 | Win10 1703+/Linux/macOS | 部分平台 |
| 固件复杂度 | 低 | 中 | 高 |

## 4. 选型与实现速断

- 做麦克风/廉价声卡/固件资源紧张 → **UAC1**（TinyUSB 等栈支持最成熟，见[固件栈](../../60-枝干-主机侧与实现/03-设备端固件栈.md)）；
- 做高分辨率 DAC/多通道会议音箱 → **UAC2**，认真做 Clock Source 实体（可提供双时钟源：内部+外部 SPDIF）；
- 反馈端点必须真实现（按本地时钟实测速率上报），假反馈 = 抖动杀手；
- 抓包定位音频问题：看同步端点每微帧实际包长波动与反馈值联动是否合理（[抓包](../../70-枝干-调试测试与安全/01-协议分析仪与抓包.md)）。

## 相关节点

- 上一叶: [00-UAC概述](00-UAC概述.md) · [01-UAC1.0详解](01-UAC1.0详解.md)
- 树干: [电源管理与挂起唤醒](../../10-树干-USB核心/10-电源管理与挂起唤醒.md)（UAC3 的背景）
- 相邻: [蓝牙 LE Audio 对比](../../50-枝干-无线关联/BLE-低功耗蓝牙/08-经典蓝牙与BLE对比.md)（音频的另一条无线路线）
