---
title: "UAC 概述：USB 音频类"
layer: 枝干/设备类协议
section: Audio-UAC
doc-path: 20-枝干-设备类协议/Audio-UAC/00-UAC概述.md
---
# UAC 概述：USB 音频类

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[UAC] → 叶
> ⬆️ 上一级: [00-设备类索引](../00-设备类索引.md) · 树干基础: [四种传输类型](../../10-树干-USB核心/06-四种传输类型.md)

## 1. UAC 在树上解决什么

USB 音频类（USB Audio Class, UAC）把两件事标准化：**音频数据怎么传**（同步端点 + 时钟闭环）与**音量/静音等控制怎么调**（实体图 + 类请求）。代际：UAC 1.0（1998，全速时代，嵌入式声卡事实标准）→ UAC 2.0（2009，高速，实体化时钟）→ UAC 3.0（2016，移动低功耗，采用率低）。

接口签名：bInterfaceClass=0x01；子类 0x01=音频控制 (AC)，0x02=音频流 (AS)，0x03=MIDI 流（见 [MIDI 类](../其他设备类/07-MIDI类.md)）。

## 2. 实体图 (Entity Graph)：UAC 的世界观

UAC 不用固定结构描述设备，而是画一张**信号流图**：每个实体 (Entity) 有唯一 ID，彼此用 ID 引用连接：

```mermaid
graph LR
    MIC[麦克风] --> IT[Input Terminal<br/>ID=1, 类型=0x0201]
    IT --> FU[Feature Unit<br/>ID=2: 静音/音量]
    FU --> OT[Output Terminal<br/>ID=3, 类型=0x0101 USB流]
    OT -->|同步端点| HOST((主机))
    HOST -->|同步端点| OT2[Input Terminal<br/>USB流]
    OT2 --> FU2[Feature Unit 音量]
    FU2 --> OT3[Output Terminal 扬声器]
```

| 实体 | 子类型 | 职责 |
|---|---|---|
| Input/Output Terminal | 0x02/0x03 | 信号进出设备的"端口"（USB 流 / 模拟接口） |
| Mixer Unit | 0x04 | 多路混合（音量矩阵） |
| Selector Unit | 0x05 | 多输入选一（如前后面板切换） |
| **Feature Unit** | 0x06 | 音量/静音/低音高音——90% 设备只有它 |
| Processing Unit | 0x07 | 均衡器、AGC、延迟等 |
| Extension Unit | 0x08 | 厂商私有扩展 |
| Clock Source (仅 UAC2+) | 0x0A | 时钟实体（见 [UAC2](02-UAC2与UAC3.md)） |

主机混音器直接把实体图映射成系统音量控件——**你调节的系统音量就是一条 SET_CUR 请求打在 Feature Unit 上**。

## 3. 接口与端点构成

一个完整音频功能（IAD 捆扎）：

```
IAD
├── 接口0: 音频控制 AC (0x01/0x01/0x00)
│   ├── 类特定 AC 头 + 实体图描述符
│   └── (可选) 中断 IN 端点: 音量变化/静音状态主动上报
├── 接口1: 音频流 AS (0x01/0x02/0x00)
│   ├── Alt0: 零带宽(无端点) ← 挂起/停流用
│   ├── Alt1: 48kHz/16bit 立体声 + 同步端点
│   └── Alt2: 96kHz/24bit ...（带宽换挡）
└── (可选) 同步反馈端点: 挂在 AS 接口上
```

三个关键点：

1. **同步 (Isochronous) 端点**承载音频数据，带宽在配置时预留（[传输类型](../../10-树干-USB核心/06-四种传输类型.md)）；
2. **Alternate Setting 换挡**：停止播放 → 主机切 Alt0（释放带宽），开始播放 → 切 Alt1；采样率/位深切换就是切 Alt Setting 或动态改时钟（UAC2）；
3. **反馈端点**：异步播放的时钟闭环，见下。

## 4. 时钟同步三模式（音频品质的分水岭）

| 模式 | 主时钟在哪 | 机制 | 品质 |
|---|---|---|---|
| 同步 Synchronous | 主机（SOF） | 设备锁 SOF 派生采样时钟 | 差：SOF 抖动直入音频 |
| 自适应 Adaptive | 主机数据流 | 设备锁**数据到达速率**恢复时钟 | 中 |
| **异步 Asynchronous** | **设备**（本地晶振/DAC） | 设备自有高精度时钟，用**反馈端点**告诉主机"我真实消耗速率"，主机微调发送量 | **最佳**（USB 时钟域与音频时钟域隔离） |

反馈端点机制：异步**播放**（主机→设备）设备的同步 OUT 端点旁挂一个同步 IN 端点，周期性上报采样频率比率（10.14 定点，UAC1；16.16，UAC2），48 kHz 时为 48×2¹⁴ = **0x0C0000**（实测围绕该值 ±100 ppm 微调）。主机据此每毫秒增减 1~2 个采样帧——**这就是"异步 USB 解码器"宣传的协议基础**。

## 5. 控制面：类请求的统一格式

所有控制都发往实体：`SET_CUR/GET_CUR`（UAC1: bRequest 0x01/0x02；UAC2: 0x01/0x02 + RANGE 0x02），`wValue = (控制选择子<<8) | 通道号`，`wIndex = (实体ID<<8) | 接口号`：

- Feature Unit 通道 0 = 主音量（全通道联控），通道 1/2 = 左/右；
- 音量选择子：MUTE=0x01，VOLUME=0x02；
- 采样率控制在 UAC1 挂在**同步端点**（SAMPLING_FREQ_CONTROL），在 UAC2 挂在 **Clock Source 实体**——代际分水岭（[UAC2 与 UAC3](02-UAC2与UAC3.md)）。

## 6. 主机驱动

Linux `snd-usb-audio`（UAC1/2/3 全支持）、macOS CoreAudio 内置、Windows usbaudio.sys（UAC1 免驱；UAC2 从 Win10 支持）。**免驱 + 任意采样率自适应**使 UAC 成为最成功的设备类之一；声卡厂商的"驱动盘"装的只是控制面板，不是协议驱动。

## 相关节点

- 下一叶: [01-UAC1.0详解.md](01-UAC1.0详解.md) · [02-UAC2与UAC3.md](02-UAC2与UAC3.md)
- 树干: [同步传输](../../10-树干-USB核心/06-四种传输类型.md) · [错误处理（同步不容错重传）](../../10-树干-USB核心/11-错误处理与可靠性.md)
- 相邻: [MIDI 类](../其他设备类/07-MIDI类.md)（同属 0x01 类的 0x03 子类）
