---
id: 09-errors-testmode
title: "错误处理、可靠性、Test Mode 与调试模式"
topic: core
level: 深入
keywords: ["CRC", "retry 三次重试", "STALL", "babble", "timeout", "toggle resync", "PING/NYET", "TEST_MODE", "Test_J", "Test_K", "Test_SE0_NAK", "Test_Packet", "debug class"]
sources:
  - path: "10-树干-USB核心/11-错误处理与可靠性.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/10-树干-USB核心/11-错误处理与可靠性.md"
  - path: "10-树干-USB核心/12-TestMode与调试模式.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/10-树干-USB核心/12-TestMode与调试模式.md"
spec_refs: ["USB 2.0 Specification §7.1.20, §8.6, §9.4.9"]
related: ["04-packets-transactions", "51-compliance-security"]
usbtree_commit: 03306ba
generated: 2026-11-28
---

# 错误处理、可靠性、Test Mode 与调试模式

> 层级 深入 · 主题 `core` · 相关：[包格式、PID、事务、帧与 Data Toggle](04-packets-transactions.md)、[USB-IF 合规认证、合规测试实操与 USB 安全](51-compliance-security.md)

## 核心事实 Key Facts

> 由维护者整理并与规范核对；与下方 USBTree 原文冲突时以本节为准。

- 主机控制器对同一事务连续 3 次错误（CRC/超时/位填充错误）后向软件报告。
- STALL：功能性停止。控制端点 STALL 在下一个 SETUP 自动清除；批量/中断端点需 CLEAR_FEATURE(ENDPOINT_HALT)，同时 toggle 复位为 DATA0（主机和设备都要复位，否则数据错位）。
- Babble：设备在帧尾（EOF1 之后）仍在发送，Hub 禁用该端口。
- TEST_MODE 选择子（SET_FEATURE(TEST_MODE)，wIndex 高字节）：0x01 Test_J、0x02 Test_K、0x03 Test_SE0_NAK、0x04 Test_Packet、0x05 Test_Force_Enable；进入后需断电/复位退出。

## 原文：11-错误处理与可靠性

> Source: [10-树干-USB核心/11-错误处理与可靠性.md](https://github.com/tangjianfang/USBTree/blob/main/10-树干-USB核心/11-错误处理与可靠性.md)

### 1. 错误从哪里来

| 层 | 错误类型 | 检测者 | 典型根因 |
|---|---|---|---|
| 电气 | 信号失真、抖动超限 | 接收端采样失败 | 线缆质量、阻抗失配、ESD |
| 编码 | 位填充错误（7 个连续 1） | SIE | 时钟偏差、干扰 |
| 校验 | CRC5/CRC16 不符 | SIE | 位错误、包损坏 |
| 时序 | 超时（无握手返回） | 发送方 | 设备忙/失联、NAK 滥用 |
| 协议 | Babble（包尾之后仍有活动） | 集线器/主机 | 设备固件 bug、包长越界 |
| 语义 | 请求非法 → STALL | 设备 | 驱动与固件状态不一致 |

### 2. 重传机制（控制/批量/中断的护城河）

- 接收方 CRC 或位填充校验失败 → **静默丢弃、不发握手**；
- 发送方等不到握手 → **超时 → 原样重发**（数据内容与 toggle 都不变）；
- 接收方看到 toggle 与期望不符 → 判定为"上次其实已成功收到的重放"→ 丢弃数据**但仍回 ACK**，让发送方推进；
- 结果：三种传输类型最终交付的数据**零丢失、零重复、零乱序**——这是批量传输能扛 U 盘大文件的核心保证。

主机侧重试上限：一般 3 次重传失败即上抛软件层错误（丢设备/复位端口），避免总线被坏设备空转占满。

### 3. 数据触发对齐 (Toggle Resync)

错误恢复后两端 toggle 可能失步，规范给了明确的复位规则：

| 场景 | 处理 |
|---|---|
| ClearFeature(ENDPOINT_HALT) 清除 STALL | **两端 toggle 复位为 DATA0** |
| 控制传输 Setup 阶段 | 数据阶段从 DATA1 开始（自动对齐） |
| SET_CONFIGURATION / SET_INTERFACE 之后 | 端点 toggle 复位为 DATA0 |

驱动/固件不一致的经典症状：设备被"卸载重装"后第一批数据全部被丢弃——多半是某一方没按规则复位 toggle。

### 4. STALL：协议层的"举手喊停"

| 类型 | 触发 | 清除方式 |
|---|---|---|
| 功能 STALL (Function Stall) | 端点自身挂起（如 MSC 介质错误） | 主机 ClearFeature(ENDPOINT_HALT) |
| 协议 STALL (Protocol Stall) | 控制请求不支持/参数非法 | 收到下一个 SETUP 自动清除 |

语义要点：
- STALL 是**状态不是流控**：NAK 才是"稍后再来"，STALL 是"不干了，需要主机介入"；
- 主机收到数据/状态阶段 STALL → 整个控制传输以错误告终，类驱动记录并继续（不卸载驱动）；
- IN 端点 STALL 后主机不该再排队请求；OUT 端点 STALL 后到达的包会被设备丢弃。

### 5. 超时与 Babble

- **超时**：FS/LS 发送方在 816 位时间（约 0.68~8.2 ms 视速率）内未收到握手即判失败；HS 用更严的时序；主机收到 NAK 不算超时（NAK 是正常流控）；
- **Babble**：包尾 EOP 之后总线仍有活动（设备发疯了）→ 集线器检测并**禁用该端口**——防止一个坏设备瘫痪整棵树；这是集线器"中继器"职责的一部分（[集线器](02-architecture-topology.md)）。

### 6. 同步传输的容错哲学

- 无握手、无重传：错误数据照常交付（音频掉一个样本人耳无感，等重传则卡顿人人有感）；
- 接收方仍查 CRC 并统计错误率（反馈给驱动做质量监控）；
- 上层容错策略：音频插值/静音替换、视频丢帧——类协议各自的业务逻辑（[UAC](17-uac.md)、[UVC](16-uvc.md)）。

### 7. HS 批量 OUT 的 PING 优化

问题：HS 批量 OUT 被 NAK 时，512 字节大包白白占了一趟微帧。
方案：设备 NYET（"这次收下了，下次先问"）→ 主机改发 **PING**（令牌+握手两拍）→ ACK 才发真正 OUT。
收益：流控开销从"每趟 512B"降到"每趟 8B"。这是 HS 对 2.0 之前的 OUT 流控浪费的修正（[包格式](04-packets-transactions.md)）。

### 8. 可靠性设计清单（工程叶子）

固件侧：
- [ ] 端点 0 永不挂死：每个请求路径都有 ACK/NAK/STALL 的明确归宿；
- [ ] CRC 硬件使能，别软件手算长包；
- [ ] toggle 状态在 STALL 清除/配置切换时复位；
- [ ] 挂起唤醒后首个事务前完成时钟恢复（[电源管理](08-power-management.md)）。

驱动/主机侧：
- [ ] 处理 -EPIPE/-EPROTO/-EOVERFLOW 等错误码的差异化恢复（清 halt vs 重新枚举）；
- [ ] 对 NAK 风暴设软件超时（设备逻辑死锁时给用户反馈）；
- [ ] 复合设备隔离故障接口，不让一个接口的 STALL 拖垮整机。

验证手段：错误注入（线缆接触不良模拟）、抓包统计 NAK 率与重传率（[抓包](50-debug-troubleshooting.md)）、[合规测试](51-compliance-security.md)的协议一致性项。

## 原文：12-TestMode与调试模式

> Source: [10-树干-USB核心/12-TestMode与调试模式.md](https://github.com/tangjianfang/USBTree/blob/main/10-树干-USB核心/12-TestMode与调试模式.md)

>  兄弟: [11-错误处理与可靠性.md](09-errors-testmode.md) · [10-电源管理与挂起唤醒.md](08-power-management.md) · [09-集线器与连接管理.md](02-architecture-topology.md)
> 规范原文缓存索引: [80-参考资料/README.md](92-spec-references.md)

协议是否正确可以靠抓包验证，但**电气波形是否合格**必须让设备发出"已知、可控、可重复"的信号，示波器/误码仪才有测量基准。USB 2.0 在规范 §7.1.20 定义了 Test Mode（测试模式），USB 3.x 用 LTSSM 的 Compliance/Loopback 状态承担同等职责；另有独立于合规测试的调试通道（Debug Descriptor / Debug Mode），用于系统最底层的固件调试。本叶汇总这三层机制。

### 1. 测试模式的定位

| 维度 | Test Mode (USB 2.0) | Compliance Mode (USB 3.x) | Debug Mode |
|---|---|---|---|
| 服务对象 | 电气合规测量 | 电气合规测量 | 软件调试 |
| 由谁发起 | 主机软件（SET_FEATURE 请求） | 测试夹具/测试仪（LFPS 图样） | 主机调试端口（EHCI/xHCI DbC） |
| 强制范围 | 所有 HS-capable 设备/Hub/主机控制器 | 所有 SuperSpeed 链路 | 可选 |
| 退出方式 | 上行口断电（power cycle） | 复位/断电 | 软件退出 |

### 2. 入口：SET_FEATURE(TEST_MODE)

设备测试模式由标准请求进入。请求字段（对照 [08-枚举流程与标准请求.md](07-enumeration-requests.md) 的 Setup 包格式）：

| 字段 | 取值 | 说明 |
|---|---|---|
| bmRequestType | 0x00 | 接收者=设备（TEST_MODE 仅对设备接收者定义），Host→Device，无数据阶段 |
| bRequest | 0x03 | SET_FEATURE |
| wValue | 0x0002 | 特性选择器 TEST_MODE = 2（Table 9-6） |
| wIndex 高字节 | 测试选择器 | Test_J=01H、Test_K=02H、Test_SE0_NAK=03H、Test_Packet=04H、Test_Force_Enable=05H |
| wIndex 低字节 | 0x00 | 必须为 0 |
| wLength | 0 | 无数据阶段 |

进入条件与行为要点（规范 §9.4.9 / §7.1.20）：

- **状态要求**：高速设备在 Default、Address、Configured 三种设备状态下都必须能接受该请求——不要求必须先完成配置（这一点常被误解为"必须配置态"）；
- 仅高速能力设备强制支持；**非高速设备不支持**（返回 STALL）；
- 无效测试选择器 → 设备以请求错误（STALL）应答；wLength 非 0 时行为未定义；
- 状态阶段完成后设备回 ACK，**测试模式切换必须在状态阶段完成后 3 ms 内完成**，且切换不得早于状态阶段（否则主机误以为请求失败）；
- **退出**：上行口的测试模式只能靠**设备断电（power cycle，含拔插）**退出——没有"软件退出"请求，这是排障时"插回设备才恢复"的原因；
- **集线器下行口**走 Hub 类请求 SetPortFeature(PORT_TEST)（§11.24.2.13），选择器同样放 wIndex 高字节，退出方式为**复位集线器**。

```mermaid
flowchart LR
    A[主机枚举完成<br/>任意设备状态] --> B[SET_FEATURE TEST_MODE<br/>wIndex 高字节=选择器]
    B --> C{选择器有效?}
    C -- 否 --> D[STALL<br/>保持正常工作]
    C -- 是 --> E[状态阶段 ACK]
    E --> F["≤3 ms 内切换<br/>进入测试模式"]
    F --> G[持续输出测试信号]
    G --> H[断电 / 拔插<br/>（Hub 口: 复位 Hub）]
    H --> I[重新枚举<br/>恢复正常]
```

#### 2.1 集线器下行口的入口差异

集线器的下行口不能对"不存在"的设备发标准请求，改走 Hub 类请求 SetPortFeature(PORT_TEST)（规范 §11.24.2.13）：

| 字段 | 取值 | 说明 |
|---|---|---|
| bmRequestType | 0x23 | 接收者=其他（类），接收者=集线器 |
| bRequest | 0x03 | SET_FEATURE |
| wValue | 0x0015 | 端口特性选择器 PORT_TEST = 21（区别于设备级 TEST_MODE=2） |
| wIndex 低字节 | 端口号 | 1 起编的下行端口号 |
| wIndex 高字节 | 测试选择器 | 与设备级同一套取值（01H~05H，含 Test_Force_Enable） |

两类入口的行为差异总结：设备上行口进入测试模式后"断电才退"；集线器下行口则是"复位集线器才退"，且 Test_Force_Enable 只对下行口有意义（它就是为测 Hub 断开检测阈值设计的）。

### 3. 五种测试模式详解

所有模式下，设备的行为就是把上行口收发器置于指定状态并**保持**，直到退出动作：

| 模式 | 选择器 | 上行口行为 | 测量目标 |
|---|---|---|---|
| Test_J | 01H | 持续发送高速 J 状态 | D+ 线高电平驱动电平 |
| Test_K | 02H | 持续发送高速 K 状态 | D− 线高电平驱动电平 |
| Test_SE0_NAK | 03H | 进入高速接收态，持续 SE0；**对收到的任何 CRC 正确的 IN 令牌回 NAK** | 输出阻抗、低电平输出电压、负载特性、设备 Squelch（静默电平检测）灵敏度 |
| Test_Packet | 04H | 无限重复发送规范定义的固定测试包 | 上升/下降时间、眼图、抖动等全部动态波形指标 |
| Test_Force_Enable | 05H | 仅 Hub 下行口：无设备接入也强制使能（高速），上行口收到的包在该口照常转发 | Hub 断开检测阈值（改变端口负载轮询 disconnect detect 位） |

工程要点：

- Test_J/Test_K 是**直流电平**测量（驱动器强度），Test_SE0_NAK 是"静态+ stimulus/response"混合测量，Test_Packet 才是波形动态测量；
- Test_SE0_NAK 中"回 NAK"的设计让测试仪可以顺带验证设备的基本协议响应能力（通用功能测试激励）；
- 测试模式进入后设备对主机"失联"是正常现象：主机软件发完请求后不应再期待任何响应（USBHSET 类工具即按此工作）。

#### 3.1 Test_Packet：眼图与示波器校验的标准信号源

测试包内容由规范以**精确比特串**逐字段定义（规范 §7.1.20 Table 7-9，整包约 53 字节）：SYNC → DATA0 PID → 多段 0/1、交替、最长连 1 等特征序列（含刻意安排的位填充 S 标记）→ CRC-16 → EOP。设计目标是让一条包里同时覆盖：

- 高/低电平保持段（测电平与幅度）；
- 最快翻转段（测上升/下降时间与抖动）；
- 最长连 1 段（测位填充行为与时钟恢复能力）；
- 全 0 段与随机性序列（测眼图张开度）。

发送节奏：重复发送，包间隔不小于最小包间隙（§7.1.18）且**不大于 125 µs**——示波器以无限余辉叠加即可拼出眼图；USB-IF 的 SigTest 软件正是对该波形做模板比对（见第 4 节）。

#### 3.2 电气测量项与模式的对应

规范对各电气参数指定了测法（含测试负载条件），合规测试时逐一对应：

| 测量项 | 用哪个模式 | 负载/条件（规范要点） |
|---|---|---|
| 高电平驱动电压 | Test_J / Test_K | 每根数据线对地接 45 Ω 负载分别测 D+ / D− |
| 眼图、上升/下降时间、抖动 | Test_Packet | 规范图示的标准夹具，示波器余辉 + SigTest 模板 |
| 输出阻抗、低电平输出电压、负载特性 | Test_SE0_NAK | 高速接收态持续 SE0 |
| Squelch（静默检测）灵敏度 | Test_SE0_NAK | 测试仪发幅度渐变的合法包，观察设备是否响应 |
| 收发器寄生电容（芯片级） | Test_SE0_NAK | 断电态测线对地电容（die/封装各 ≤5 pF 量级指导值） |
| Hub 断开检测阈值 | Test_Force_Enable | 空载使能端口，改变负载轮询 disconnect detect 位 |

这份对应表就是 [USB-IF 合规认证](51-compliance-security.md) 电气项的底层剧本；第 6 节的 USB 3.x 机制在高速演进枝干接续同一思路。

### 4. 主机侧工具

| 工具 | 角色 | 典型用法 |
|---|---|---|
| USBHSET | 主机侧高速电气测试工具 | 通过主机控制器向目标端口发 SET_FEATURE(TEST_MODE)，配合测试夹具把端口切到 Test_J/K/SE0_NAK/Packet |
| SigTest (USB-IF) | 信号质量分析软件 | 对示波器采到的 Test_Packet 波形做眼图模板/幅度/抖动自动判定 |
| 测试夹具 (fixture) | 把主板连接器引到同轴口 | 分常规/OTG 等多种夹具，属 [USB-IF 合规认证](51-compliance-security.md) 设备清单 |

嵌入式/裸机场景没有 USBHSET 时，任何能发出上述标准请求的主机（包括另一块开发板、协议分析仪的流量注入功能）都可以进入测试模式；设备固件侧则必须实现"收到请求→状态阶段 ACK→3 ms 内切换收发器"的完整路径。

### 5. 调试描述符 (0x0A) 与 Debug Mode

Test Mode 服务于产线/实验室，真正的"开发期调试"靠独立机制——USB 2.0 Debug Device 规范（含 Debug 描述符与 Debug Mode）：

- **Debug 描述符**：类型码 `bDescriptorType = 0x0A`，声明调试能力，其中给出调试专用 **IN/OUT 端点号**（bDebugInEndpoint / bDebugOutEndpoint）；主机通过 GetDescriptor(Debug) 读取；
- **Debug Mode 进入**：主机发 SetFeature(DEBUG_MODE)（设备特性选择器 DEBUG_MODE = 6）；此后设备进入特殊状态，只有"调试从机 (debug slave)"保持工作；
- **电气概貌**：调试从机是精简收发器，挂接在 **D+ 一线**上工作，允许目标系统其余部分（主 PHY、CPU 电源域以外的大部分逻辑）处于断电或深度挂起——这正是"系统已死、还能救"的价值；两根**批量管道**用于固件日志与调试器消息的双向搬运（消息粒度与包长等细节见 USB 2.0 Debug Device 规范原文）；
- **主机侧对应物**：EHCI 的 Debug Port 能力（配合 Linux earlyprintk/dbgp 等）；xHCI 时代对应 **xHCI Debug Capability (DbC)**，以 USB 3.x 批量端点跑同样的角色（字段级细节见 xHCI 规范，此处不展开）。

对照记忆：Test Mode 是"设备向示波器单说"，Debug Mode 是"设备向另一台计算机说话"。

### 6. USB 3.x 对应机制

USB 3.x 没有 SET_FEATURE(TEST_MODE)——链路训练由 LTSSM（见 [04-USB3x包格式与LTSSM.md](30-usb3-superspeed.md)）接管，合规模式成为状态机的一部分。

#### 6.1 Compliance Mode（合规模式）

- **入口**：Polling 阶段，设备收到测试仪/夹具发出的**合规入口 LFPS 图样**（一组频率/时长与正常 Polling 不同的突发序列）后，LTSSM 转入 Compliance 状态；
- **行为**：链路持续发送合规测试图样（Compliance Pattern, CP），供测试仪做眼图、抖动、回损等测量；Gen2 下还涉及接收端均衡（CTLE 等）参数的训练与验证；
- **Compliance Pattern 概览**：规范定义 CP0～CP16 一族图样，CP0 为加扰数据图样（Gen1 眼图/抖动基础图样），CP1 起覆盖回环 BER 与 Gen2 各专用场景（逐图样的编码与用途见规范原文）；
- 与 2.0 的一致性设计：同样是"可控已知信号 + 测量判定"，只是入口从软件请求换成了 LFPS 握手。

#### 6.2 Loopback 模式

LTSSM 的 Loopback 状态：训练期间收到带 **Loopback 位**的 TS1 有序集即进入，此后把收到的数据原样回环发送。测试仪借此对 DUT 做**误码率 (BER) 测试**——先发均衡/适配图样，再切换已知图样统计误码。这是 Gen2 接收端裕量测试的基础设施之一。

#### 6.3 与 USB 2.0 测试模式对照

| 能力 | USB 2.0 | USB 3.x |
|---|---|---|
| 静态电平（J/K） | Test_J / Test_K | CP 图样中的电平保持段 + Lane Margining |
| 眼图/抖动 | Test_Packet | Compliance Mode + CP0 等 |
| stimulus/response | Test_SE0_NAK（回 NAK） | Loopback（回环 BER） |
| 入口载体 | SET_FEATURE 标准请求 | LTSSM Compliance 入口 LFPS 图样 |

### 7. 在合规认证中的位置

上述模式是 [USB-IF 合规认证](51-compliance-security.md) 中"电气信号质量"大项的全部测量载体：2.0 眼图测 Test_Packet、驱动电平测 Test_J/K、Squelch 测 Test_SE0_NAK；3.x 眼图/抖动/BER 全部经 Compliance/Loopback 完成。协议一致性项则靠抓包（[协议分析仪与抓包](50-debug-troubleshooting.md)）与标准请求序列（[枚举流程](07-enumeration-requests.md)）覆盖。

排障提示：设备"进测试模式出不来"的三个高频根因——固件在 ACK 状态阶段后忘记切换收发器（测试仪读不到图样）、把 TEST_MODE 误实现为接口/端点接收者（应 STALL 却行为怪异）、以及在测试模式中响应了本不该响应的流量。
