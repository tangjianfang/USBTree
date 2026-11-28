---
id: 08-power-management
title: "电源管理：挂起、远程唤醒、LPM、U1/U2/U3"
topic: core
level: 进阶
keywords: ["suspend 挂起", "resume", "remote wakeup 远程唤醒", "selective suspend 选择性挂起", "LPM", "L1", "L2", "U0", "U1", "U2", "U3", "unit load", "bMaxPower"]
sources:
  - path: "10-树干-USB核心/10-电源管理与挂起唤醒.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/10-树干-USB核心/10-电源管理与挂起唤醒.md"
spec_refs: ["USB 2.0 Specification §7.1.7.6, §9.2.5", "USB 2.0 LPM ECN", "USB 3.2 Specification ch.7"]
related: ["06-descriptors", "21-charging-bc12-otg", "30-usb3-superspeed"]
usbtree_commit: d8dc27d
generated: 2026-11-29
---

# 电源管理：挂起、远程唤醒、LPM、U1/U2/U3

> 层级 进阶 · 主题 `core` · 相关：[标准描述符字段全表](06-descriptors.md)、[充电：BC 1.2、专有快充；OTG 与角色切换 HNP/SRP](21-charging-bc12-otg.md)、[USB 3.x SuperSpeed：包格式、LTSSM、定时器](30-usb3-superspeed.md)

## 核心事实 Key Facts

> 由维护者整理并与规范核对；与下方 USBTree 原文冲突时以本节为准。

| 项 | 值 |
|---|---|
| 进入挂起 | 总线空闲（无 SOF/流量）3 ms |
| 挂起电流 | ≤ 2.5 mA（USB 2.0 ECN 后；早期 500 µA） |
| 主机恢复 Resume | 主机驱动 K ≥ 20 ms，随后 LS EOP |
| 远程唤醒 | 设备挂起 ≥ 5 ms 后才可发起，驱动 K 1–15 ms；需主机先 SET_FEATURE(DEVICE_REMOTE_WAKEUP)，配置描述符 bmAttributes D5=1 |
| 单位负载 Unit Load | USB 2.0 100 mA（配置后最多 500 mA）；USB 3.x 150 mA（最多 900 mA） |
| LPM（L1） | 需 bcdUSB ≥ 0x0201 + BOS USB 2.0 Extension（bmAttributes bit1 LPM）；进出为微秒级 |
| USB 3.x 链路态 | U0 工作、U1/U2 低功耗（由 U1_ENABLE/U2_ENABLE 及超时控制）、U3 挂起 |

- Windows "USB 选择性暂停"（Selective Suspend）：HID 类驱动在空闲时请求挂起；外设"唤醒后丢首个报告/无法唤醒"多与固件 Suspend/Resume 处理或远程唤醒未授权有关。

## 原文：10-电源管理与挂起唤醒

> Source: [10-树干-USB核心/10-电源管理与挂起唤醒.md](https://github.com/tangjianfang/USBTree/blob/main/10-树干-USB核心/10-电源管理与挂起唤醒.md)

### 1. 为什么 USB 2.0 的电源管理这么"粗"

USB 2.0 把整条总线当一个整体对待：主机停发 SOF（帧起始包）就是挂起的唯一开关。设备端识别挂起的方式是**被动计时**：总线空闲 ≥ 3 ms 即进入挂起。

| 参数 | 数值 | 说明 |
|---|---|---|
| 挂起判定 | 空闲 ≥ 3 ms | 设备必须在收到最后一个包后 7 ms 内进入挂起（3ms 判定 + 裕量） |
| 挂起电流上限 | **2.5 mA**（总线供电设备） | 含远程唤醒电路 |
| 主机恢复信号 | K 态 ≥ 20 ms，随后低速 EOP | 集线器逐级转发 |
| 恢复后恢复时间 | 设备须在恢复结束后 ~10 ms 内可通信 | 固件时钟恢复要快 |
| 远程唤醒 | 设备挂起 ≥ 5 ms 后可发 1~15 ms 的 K | 且必须先获授权（见下） |

**远程唤醒授权流程**：主机在挂起前 `SET_FEATURE(DEVICE_REMOTE_WAKEUP)`（[标准请求](07-enumeration-requests.md)表）→ 设备挂起后检测到本地事件（如键盘按键）→ 驱动 K ≥ 若干 ms → 集线器逐级向上中继 → 主机回发完整恢复序列。没拿到授权就发唤醒是固件 bug。

### 2. 选择性挂起

主机可对树上任一子树单独挂起（SET_FEATURE(PORT_SUSPEND)），其余照常工作——鼠标闲置挂起、U 盘继续读写。这是操作系统"USB 选择性挂起"开关背后的机制，也是很多设备兼容性问题（挂起后唤不醒）的来源。

### 3. LPM：链路电源管理 (L1 Sleep)

USB 2.0 补充规范引入，BOS 描述符声明（USB 2.0 Extension capability）：

- 主机发 **LPM 事务**（扩展令牌包）让设备进入 **L1 Sleep**，几十微秒级进出，远快于 L2 挂起（毫秒级）；
- 设备在 L1 中仍可被快速唤醒，电流限值比 2.5 mA 宽（支持更高的 L1 电流档位，需描述符声明）；
- 意义：SS 集线器时代主机频繁进出低功耗，L1 让"挂起"从秒级事件变成微秒级动作。

### 4. USB 3.x 的链路电源状态 U0~U3

3.x 链路是两条独立实体（各方向），低功耗在**链路对之间协商**：

| 状态 | 名称 | 特征 | 进出延迟 |
|---|---|---|---|
| U0 | 正常活动 | 全速传输 | — |
| U1 | 快速待机 | 空闲短憩 | 微秒级 |
| U2 | 深度待机 | 更省电 | 几十微秒~毫秒 |
| U3 | 挂起 | 对应 2.0 挂起 | 毫秒级（LFPS 唤醒） |

- 进出 U1/U2/U3 通过 **LFPS（Low Frequency Periodic Signaling）** 脉冲握手（与链路训练共用信令通道，见[USB3x](30-usb3-superspeed.md)）；
- **Function Remote Wake**：3.x 精确到**接口级**唤醒——键盘接口唤醒，同设备的鼠标接口继续睡；实现依赖 BOS 的 SuperSpeed capability + 主机下发 FUNCTION_SUSPEND 控制请求 + **Device Notification**（"Function Wake"通知包）通知主机；
- 固件注意点：3.x 下端点挂起/恢复由链路层处理，但接口级功能挂起仍需类协议配合。

### 5. 设备端实现要点（固件叶子）

1. **时钟策略**：挂起时停 PLL/主时钟，仅留低速唤醒检测（D+/D- 边沿或 VBUS 检测）；唤醒后必须在恢复序列结束前恢复时钟（xHCI 主机恢复后立刻发令牌，时钟没起来就丢第一个包）；
2. **VBUS 检测**：自供电设备也要能感知 VBUS 掉电（总线掉电时主动进入未连接态，停止驱动上拉）；
3. **挂起电流核算**：MCU 睡眠电流 + 上拉电阻电流 + 分压网络 ≤ 2.5 mA（或声明 LPM 档位）；
4. **远程唤醒三条件**：配置了远程唤醒能力（bmAttributes bit5）+ 主机 SET_FEATURE 授权 + 挂起满 5 ms；
5. 调试技巧：挂起问题的抓包特征是"恢复序列后第一个 IN 事务无应答/超时重试"（[抓包](50-debug-troubleshooting.md)）。

### 6. 供电侧的演进（指向枝干）

| 主题 | 去处 |
|---|---|
| Type-C CC 电阻协商电流 (1.5A/3A) | [Type-C 详解](20-connectors-typec.md) |
| PD 协商 (PDO/RDO, 最高 240W) | [USB PD 协议](22-usb-pd.md) |
| BC 1.2 / 专有快充 | [BC1.2 与专有快充](21-charging-bc12-otg.md) |
| OTG / DRP 角色切换（设备变主机） | [接口形态演进](20-connectors-typec.md) |
