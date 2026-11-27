---
id: 21-charging-bc12-otg
title: "充电：BC 1.2、专有快充；OTG 与角色切换 HNP/SRP"
topic: power
level: 进阶
keywords: ["BC1.2", "SDP", "CDP", "DCP", "primary detection", "secondary detection", "QC", "快充", "OTG", "ID pin", "HNP", "SRP", "ADP"]
sources:
  - path: "30-枝干-接口与供电/03-BC1.2与专有快充.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/30-枝干-接口与供电/03-BC1.2与专有快充.md"
  - path: "30-枝干-接口与供电/06-OTG与角色切换-HNP-SRP.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/30-枝干-接口与供电/06-OTG与角色切换-HNP-SRP.md"
spec_refs: ["Battery Charging 1.2", "USB OTG and Embedded Host Supplement 2.0"]
related: ["20-connectors-typec", "22-usb-pd", "08-power-management"]
usbtree_commit: c987a96
generated: 2026-11-27
---

# 充电：BC 1.2、专有快充；OTG 与角色切换 HNP/SRP

> 层级 进阶 · 主题 `power` · 相关：[连接器演进与 USB Type-C（含 CC 状态机与时序）](20-connectors-typec.md)、[USB Power Delivery：协议、状态机与消息全表](22-usb-pd.md)、[电源管理：挂起、远程唤醒、LPM、U1/U2/U3](08-power-management.md)

## 核心事实 Key Facts

> 由维护者整理并与规范核对；与下方 USBTree 原文冲突时以本节为准。

| 端口 | 识别 | 电流 |
|---|---|---|
| SDP Standard Downstream Port | 主检测无响应 | 未配置 100 mA / 配置后 500 mA（USB 3.x 900 mA） |
| CDP Charging Downstream Port | 主检测有响应，次检测区分 | 1.5 A + 数据 |
| DCP Dedicated Charging Port | D+/D− 短接（≤200 Ω） | 1.5 A，无数据 |
- BC 1.2 主检测：设备在 D+ 加 VDP_SRC(0.6 V)，检测 D− 上是否出现电压。
- OTG（Micro-AB）：ID 引脚接地 = A 设备（默认主机）；HNP 主机角色交换；SRP 会话请求。Type-C 时代由 CC（DRP/DR_Swap）替代。

## 原文：03-BC1.2与专有快充

> Source: [30-枝干-接口与供电/03-BC1.2与专有快充.md](https://github.com/tangjianfang/USBTree/blob/main/30-枝干-接口与供电/03-BC1.2与专有快充.md)

在 Type-C 普及前，USB 充电的主要规范是 USB-IF 的 **Battery Charging Specification 1.2 (BC 1.2)**；各芯片厂则在 D+/D− 上发明了各自的快充协议。理解这一层，才能看懂充电宝、车充、老充电器的行为，以及"假快充"的成因。

### 一、BC 1.2 的三种端口

| 端口类型 | 全称 | 数据 | 最大电流 | 识别特征 |
| --- | --- | --- | --- | --- |
| SDP | Standard Downstream Port（标准下行口） | 有（传统 USB） | 500 mA（USB 2.0 配置后；3.0 口为 900 mA） | 行为等同普通 USB 口，需枚举 |
| CDP | Charging Downstream Port（充电下行口） | 有 | 1.5 A | 内部 D+/D− 经开关短接，但保留与主机数据通路；通过**检测握手**与 DCP 区分 |
| DCP | Dedicated Charging Port（专用充电口） | 无 | 1.5 A | **D+ 与 D− 短接**（短路阻抗不超过 200 Ω），墙上充电器典型形态 |

设计动机：墙上充电器没有主机，若沿用 SDP 规则（必须枚举才能取 500 mA），手机永远只能慢充。DCP 用"D+/D− 短接"这一物理特征让设备**无需枚举**即可判定"可安全取 1.5 A"。

### 二、检测流程

设备侧（PD/充电管理芯片）上电后执行如下序列，避免枚举也能识别端口类型：

```mermaid
sequenceDiagram
    participant P as 外设/手机
    participant S as 端口（充电器或主机）
    P->>S: 1. 数据触点检测 DCD：D+ 施加检测电平，观察 D− 是否跟随
    Note over P,S: 窗口约 900 ms（TDCD）；超时按无数据触点继续
    P->>S: 2. 主检测 Primary：确认 D+/D− 是否短接
    alt D− 跟随（短接）
        P->>P: 判定 DCP（或 CDP 候选）→ 可取 1.5 A
        opt 端口宣称支持 CDP
            P->>S: 3. CDP 握手：D+ 注入检测信号，观察 D− 响应
            S->>P: CDP 应答 → 判定 CDP（1.5 A + 数据）
        end
    else 未短接
        P->>S: 4. 次检测 Secondary：判别 Apple 等分压编码
        S->>P: D+/D− 固定分压电平
        P->>P: 按 Apple 档位取电（非官方）或按 SDP 处理
    end
```

要点：

- **DCD (Data Contact Detect)** 解决"充电器可能没接数据线"导致的检测挂起；时序细节（各阶段电平、阈值、定时器）见 BC 1.2 规范原文。
- 主检测在未检测到短接时进入次检测，识别"不短接 D+/D− 但有固定分压"的专有充电器（Apple 模式）。
- 主机侧 hub/芯片（如 CDP 实现）同样要实现对应的检测与握手逻辑，两端时序不匹配是"充电慢且无数据"类故障的常见根因。

### 三、Apple 分压编码（非官方，业界通行）

Apple 从未公开该规范，但手机/充电器产业广泛实现。充电器在 D+/D− 上接精密电阻分压，输出两档固定电压（约 2.0 V 与 2.7 V），设备测量组合决定可吸取电流：

| D+ 电压 | D− 电压 | 设备可取电流（业界通行值） |
| --- | --- | --- |
| 2.0 V | 2.0 V | 0.5 A |
| 2.0 V | 2.7 V | 1.0 A（iPhone 类） |
| 2.7 V | 2.0 V | 2.1 A（iPad 10 W 类） |
| 2.7 V | 2.7 V | 2.4 A（iPad 12 W 类） |

> **注意**：此表来自产业界与第三方充电芯片数据手册的逆向一致结果，非 USB-IF 或 Apple 官方规范；不同资料对个别档位（如 2.1 A 与 2.4 A 的边界）表述略有出入。BC 1.2 的次检测正是为了兼容这类分压器而设计。

两个工程细节：

- 分压由充电器内**精密电阻到 5 V** 实现，因此 D+/D− 上会有持续的静态漏电流——这也是部分老充电器空载功耗偏高的原因之一；
- 设备端判定只需比较两路电压落在哪一档窗口，故任何"能输出这两个电压"的第三方芯片都可伪装成 Apple 充电器（众多多协议识别芯片的必备功能）。

### 四、高通 Quick Charge 2.0 / 3.0

QC 走另一条路：**用 D+/D− 电平组合命令充电器改变输出电压**，从"5 V 定压大电流"转向"高电压小电流"（线损更小，但机内需二次降压）。

#### 4.1 进入握手

设备将 D+ 拉至约 0.327 V 并保持 ≥1.25 s（此数值来自业界逆向资料与充电芯片手册），充电器（HVDCP）检测到后断开 D+/D− 短接，进入命令模式，随后接受电平组合指令。

#### 4.2 QC 2.0 电压档位电平表

| D+ | D− | 输出电压 |
| --- | --- | --- |
| 0.6 V | 0 V | 5 V（默认） |
| 3.3 V | 0.6 V | 9 V |
| 0.6 V | 0.6 V | 12 V |
| 3.3 V | 3.3 V | 20 V（仅 Class B） |
| 0.6 V | 3.3 V | 进入 QC 3.0 连续调压模式 |

- **Class A**：最高 12 V（手机/平板生态）；
- **Class B**：最高 20 V（笔记本等，市面少见）。

#### 4.3 QC 3.0

在 2.0 基础上改为**连续调压**：3.6 V~20 V、**200 mV 步进**，设备通过 INCREMENT/DECREMENT 电平脉冲逐级升降电压，可寻最优效率点。QC 3.0 兼容 2.0 档位。

### 五、其他专有快充（一句话档案）

| 协议 | 厂商 | 特征 |
| --- | --- | --- |
| AFC (Adaptive Fast Charging) | 三星 | 9 V/1.67 A（15 W）量级，信令与 QC 2.0 同源 |
| FCP (Fast Charge Protocol) | 华为 | 9 V/2 A（18 W）高压方案，类 QC |
| SCP (Super Charge Protocol) | 华为 | 低压大电流直充（4.5 V/5 A、5 V/4.5 A，22.5 W 起步），需专用线缆与芯片 |

另注意：**充电宝/车充里的多协议识别芯片**（BC 1.2 + Apple 分压 + QC + AFC/FCP/SCP 全家桶）已成为独立品类，其作用就是"把每种设备的检测逻辑都应答对"，让任意设备都能取到最大电流——这也是同一充电宝不同手机快慢差异的直接解释。

### 六、协议世代总览与对比

| 协议 | 通道 | 档位 | 最高功率 | 数据可并行 |
| --- | --- | --- | --- | --- |
| BC 1.2 SDP | 枚举+总线规则 | 5 V 固定 | 2.5 W（500 mA） | 是 |
| BC 1.2 CDP | D± 握手 | 5 V 固定 | 7.5 W（1.5 A） | 是 |
| BC 1.2 DCP | D± 短接特征 | 5 V 固定 | 7.5 W（1.5 A） | 否 |
| Apple 分压 | D± 固定电平 | 5 V 固定 | 12 W（2.4 A） | 否 |
| QC 2.0 | D± 电平命令 | 5/9/12 V（Class B 加 20 V） | 18~60 W（按档） | 否 |
| QC 3.0 | D± 电平脉冲 | 3.6~20 V 连续，200 mV 步进 | 同上 | 否 |
| AFC / FCP | D±（类 QC） | 9 V 档为主 | 15~18 W | 否 |
| SCP | 专有信令+专用线 | 低压大电流直充 | 22.5 W 起步 | 否 |
| USB PD 2.0/3.0 | CC（BMC） | Fixed + PPS 连续 | 100 W | 是（完整 USB 3.x） |
| USB PD 3.1 | CC（BMC） | + EPR 28/36/48 V | 240 W | 是 |

横向看：只有 BC 1.2 的 SDP/CDP 与 PD 同时满足"大电流 + 完整数据"，其余快充本质都是**牺牲数据换充电**（D± 被快充信令占用或只有 2.0 通路）。

### 七、常见故障与误区

- **CDP 名存实亡**：真正实现 CDP 握手的主机极少，市场把"D± 短接的 1.5 A 口"统称 DCP；设备若坚持等 CDP 握手，反而可能识别异常——成熟设备都做成"检测到短接即按 DCP 取电"。
- **开机变慢**：BC 1.2 检测序列（DCD 窗口 + 主/次检测）发生在每次插入时，实现不佳的充电管理芯片会把开机/唤醒拖慢数百毫秒至秒级。
- **多口充电器降档**：多口 PD 充电器在两个口同时插入时常把单口 100 W 拆成 60 W+30 W；这与线缆无关，是电源预算策略（读 PDO 即可验证）。
- **DCP 判定被滥用**：部分主机口对 2.0 设备按 DCP 短接处理以加速充电，导致该口数据功能失效——诊断时先确认端口宣称的类型。
- **A 口线冒充快充线**：Apple 分压与 QC 信令都在 D± 上，假线只要通断正确就能"握手成功"，但线阻过大导致实际限流——最终解释权在压降测量。

### 八、为何 Type-C + PD 终结了专有快充

1. **专用通道**：PD 在 CC 上通信，不占用也不破坏 D+/D−，与 USB 2.0 数据互不干扰；
2. **标准化档位**：PDO 广播-请求模型可表达任意电压/电流/功率档（含 PPS 连续调压），表达能力全面超过 QC 2.0/3.0；
3. **双向与角色**：支持 PR_Swap、FRS 等专有协议没有的能力（见 04 叶）；
4. **认证体系**：USB-IF 对线缆（E-marker）与电源的认证解决了专有快充"线不对就慢"的碎片化。

专有协议至今仍存在于存量配件与国内厂商生态（私有 PPS 变体），但新设计已收敛到 PD。

### 九、识别"假快充线"的原理

| 检查点 | 原理 |
| --- | --- |
| 测 D+/D− 通断 | 只有 DCP 短接或分压而无数据通路的线，无法完成 PD（Type-C 线）或专有握手（A 口线） |
| 测 Type-C 线内 CC 是否直通、是否带 E-marker | 5 A 档（>60 W）必须有 E-marker；无 marker 而标 5 A 即假标，Source 会限流到 3 A 甚至默认档 |
| 用 PD 诱骗器/触发器读 PDO | 充电器广播的 PDO 列表是硬事实；线缆/协议芯片问题会让 Request 失败或回落 5 V |
| 测线阻压降 | 标 4.5 A/5 A 的 A-to-C 线若线径过细，大电流下压降超标会触发保护降流 |

排查顺序建议：先读 PDO（协议层）→ 再验线缆 CC/E-marker（物理层）→ 最后测压降（线材质量）。

## 原文：06-OTG与角色切换-HNP-SRP

> Source: [30-枝干-接口与供电/06-OTG与角色切换-HNP-SRP.md](https://github.com/tangjianfang/USBTree/blob/main/30-枝干-接口与供电/06-OTG与角色切换-HNP-SRP.md)

>  兄弟链接: [01-接口形态演进](20-connectors-typec.md) ｜ [02-USBType-C详解](20-connectors-typec.md) ｜ [03-BC1.2与专有快充](21-charging-bc12-otg.md) ｜ [04-USBPD协议](22-usb-pd.md) ｜ [05-AlternateMode与E-marker](23-altmode-emarker.md) ｜ 树干: ../10-树干-USB核心/ ｜ 高速演进: ../40-枝干-高速演进/
> 规范原文缓存索引: [80-参考资料/README.md](92-spec-references.md)

USB OTG (On-The-Go) 是 USB 2.0 的补充规范，首次让一个设备在**主机 (Host)** 与**外设 (Peripheral)** 之间动态切换：插上 U 盘时手机是主机，连上 PC 时手机是外设。为此 OTG 定义了三套机制——**SRP** (Session Request Protocol，B 设备请求供电会话)、**HNP** (Host Negotiation Protocol，不重新插拔即交换主机角色) 与 OTG 3.x 的 **ADP** (Attach Detection Protocol，VBUS 断电时探测接入)。Type-C + PD 时代它们大都被 DRP/PR_Swap/DR_Swap 取代，但在无 PD 控制器的嵌入式场景仍是主流方案。

### 一、OTG 版本演进：1.x → 2.0 → 3.0

| 版本 | 基础规范 | 关键内容 |
| --- | --- | --- |
| OTG 1.0（2001 年 12 月） | USB 2.0 | 首次定义 A/B 设备、SRP、HNP、Mini-AB 插座 |
| OTG 1.2 / 1.3（约 2005/2006） | USB 2.0 | 细化时序与错误处理（具体修订点见规范原文） |
| OTG 2.0（2012） | USB 2.0（含 L1 LPM） | 改用 Micro-AB 插座；并入**嵌入式主机** (Embedded Host) 概念与 **TPL** (Targeted Peripheral List)；本文 SRP/HNP 时序以该版为准 |
| OTG 3.x | USB 3.x | 面向 SuperSpeed 设备；引入 **ADP**（VBUS 完全断电时的接入探测），bcdOTG 特性位扩展 |

> 嵌入式主机 (Embedded Host)：不带可换线缆、用固定/标准 A 插座的主机，只声明支持 TPL 列表内的目标外设，不必实现完整的 A/B 双角色逻辑。各版本年份与修订细节以 usb.org 文档页为准。

### 二、A 设备与 B 设备：角色由插头决定

| 属性 | A 设备 (A-Device) | B 设备 (B-Device) |
| --- | --- | --- |
| 默认角色 | **主机** (Host) | **外设** (Peripheral) |
| VBUS | **供电方**（会话开始时施加 VBUS） | 受电方（可经 SRP 请求会话） |
| 插头/插座 | Micro-A 插头 ↔ **Micro-AB** 插座 | Micro-B 插头 ↔ Micro-B 插座 |
| ID 引脚 | 插头内接地 → 识别为 A | 插头内悬空 → 识别为 B |
| 典型形态 | 手机、OTG 适配器的小主机端 | U 盘、键盘、另一部手机 |

要点：

- 角色判定发生在**连接时刻**（看 ID 引脚），会话期间可通过 **HNP** 交换主机角色，但 **VBUS 始终由 A 设备供给**——OTG 2.0 只切换数据角色，不切换电源角色；
- OTG A 设备的 VBUS 供电下限仅 **8 mA**（标准主机为 100/500 mA），这是为电池设备省电与小体积刻意设定的，B 设备需大电流时在枚举后再按描述符协商；
- 双 OTG 设备（如两台手机）互联时，两端的 Micro-AB 插座由线缆两端的插头类型决定初始 A/B，**线缆本身**（Micro-A 转 Micro-B）固化了角色分配。

### 三、Micro-AB 插座与 ID 引脚

Micro-AB 插座可同时接受 Micro-A 与 Micro-B 插头，靠第 5 脚 **ID** 区分：

| 参数 | 取值（按规范，实现见电气表） | 说明 |
| --- | --- | --- |
| Micro-A 插头 | ID 经 **RA_ID（≤10 Ω 量级）接地** | 声明"我是 A 设备" |
| Micro-B 插头 | ID **悬空** | 声明"我是 B 设备" |
| 插座内部上拉 | R_IDP（约 100 kΩ，上拉至 3.3 V 量级） | 无插头时读高 |
| 判定阈值 | VIDL ≈ 0.8 V：**低于为 A，高于为 B** | 需去抖后判定 |

```mermaid
flowchart LR
    ID[ID 引脚电平] -->|低于 VIDL 约0.8V| A[识别为 A 设备: 默认主机 + 开 VBUS]
    ID -->|高于 VIDL 悬空| B[识别为 B 设备: 默认外设 + 等 VBUS]
    ID -->|无插头 持续高| N[无连接: A/AB 座可发起探测 ADP]
```

### 四、SRP：B 设备请求供电会话

会话结束后（A 关闭 VBUS），B 若想工作必须**请求会话**。SRP 由两段独立脉冲组成，A 检测到**任一**脉冲即可响应：

| 阶段 | 动作 | 参数 |
| --- | --- | --- |
| ① 数据线脉冲 (Data Line Pulsing) | B 打开自己的数据线上拉：全速设备拉 **D+**，低速设备拉 **D-**，持续 **5~10 ms** | 脉宽区间为规范规定（一致性测试 E22 即测此区间） |
| ② VBUS 脉冲 (VBUS Pulsing) | B 用微弱电流源给 VBUS 充电，**至少充到约 2.1 V**（A 侧检测阈值，规范记作 VA_SRP_DET 一类参数），但不允许充到 VBUS 有效值以上（避免被误判为已有供电） | 弱充电，拉不动重负载 |
| 前提 | B 发起前须确认会话确已结束：**VBUS 低于会话结束阈值**（约 0.8~2 V 区间的实现值）且数据线保持 SE0 一段时间（规范 b_se0_srp 条件） | 具体定时器名与取值见规范原文 |
| 核心定时器（evolve #26 自 OTG 2.0 v1.1a 定时表提取） | TA_AIDL_BDIS=200 ms（A-Idle→B-Detach，超时 A 可结束会话）；TA_BDIS_ACON≤100 ms（A 检出 SE0 后转主控）；TB_ASE0_BRST≥155 ms；TA_WAIT_BCON≥1.1 s；TA_BCON_SDB_WIN 典型 1.75 s | 取值单位 ms，出处 OTG 2.0 §5.3.1/§5.2.1 |
| 失败处理 | A 无响应时 B 放弃，须**等 VBUS 完全放电**到会话结束阈值以下才能重试 | 防止残余电压导致 A 误判 |

```mermaid
sequenceDiagram
    participant B as B设备(默认外设)
    participant A as A设备(默认主机/供电方)
    Note over A,B: 会话结束态: VBUS 已关闭放电, 数据线 SE0
    B->>B: 等待 VBUS 低于会话结束阈值 且 SE0 满足
    B->>A: ① 数据线脉冲: D+ 上拉 5~10 ms (低速设备用 D-)
    B->>A: ② VBUS 脉冲: 弱充电至 ≥ 约 2.1 V
    A->>A: 检测到任一脉冲, 决定接受会话
    A->>B: ③ 施加 VBUS (a_wait_vrise, 最低 8 mA 供电能力)
    B->>B: VBUS 达有效值 → 进入 b_peripheral
    A->>B: ④ USB 复位 + 枚举 (A=主机, B=外设)
```

实现提示：A 侧常用比较器分别监测 D+ 电平与 VBUS 电平；B 侧 VBUS 脉冲能力受自身电容制约——**VBUS 挂大电容会充不到阈值，电容太小则脉冲维持不住**，PHY（如 ISP1362、TUSB1210 类器件）通常内置专用电流源与检测电路。

### 五、HNP：不重新插拔的主机角色交换

HNP 让"B 外设临时成为主机"（例如手机读 U 盘后反过来被 PC 读取），全程 **VBUS 不断**。前提：

1. B 的 **OTG 描述符**声明支持 HNP（见第六节）；
2. A（主机）枚举 B 时发送 `SET_FEATURE(a_hnp_support)` 告知"A 支持 HNP"；
3. A 愿意让渡时发送 `SET_FEATURE(b_hnp_enable)` **授权** B 发起交换；
4. A 挂起总线（suspend，**VBUS 必须保持**）。

#### 5.1 OTG 相关 Feature Selector（USB 2.0 第 9 章）

| 值 | 名称 | 方向 | 含义 |
| --- | --- | --- | --- |
| 3 | `b_hnp_enable` | A→B | 授权 B 在挂起后可成为主机 |
| 4 | `a_hnp_support` | A→B | 告知 B：本 A 设备支持 HNP |
| 5 | `a_alt_hnp_support` | A→B | 告知 B：A 在**另一个端口**上支持 HNP（B 经集线器连接时的提示） |

#### 5.2 全速 HNP 完整时序（按规范切换上拉位）

全速 (FS) 下外设身份的物理标志是"**谁把上拉电阻接在 D+ 上**"（主机侧是下拉），HNP 本质就是这颗上拉位的两次移交；高速 (HS) 设备挂起后本就回落 FS 信令，流程等同，详见规范 §6.6。

```mermaid
sequenceDiagram
    participant A as A设备(当前主机)
    participant B as B设备(当前外设, 已收 b_hnp_enable)
    A->>B: SET_FEATURE(a_hnp_support) → SET_FEATURE(b_hnp_enable)
    A->>A: 挂起总线 (VBUS 保持)
    B->>B: 想成为主机: 关闭自己的 D+ 上拉
    Note over A,B: 总线 SE0 (A 的下拉仍在场); VBUS 在 → 不是拔出而是 HNP 请求
    A->>A: 检测到挂起态持续 SE0 → 接受交换: 打开自己的 D+ 上拉 (A 变外设, 呈 J 态)
    B->>B: 检测 D+ 为高 (J) → A 已就外设位; B 切主机 (上拉改下拉)
    B->>A: USB 复位 (SE0 ≥ 10 ms) 后枚举 A
    Note over A,B: B=主机, A=外设; VBUS 仍由 A 供电
    B->>B: 用毕 → B 挂起总线
    A->>A: 想回主机: 关闭自己的 D+ 上拉 → 总线 SE0
    B->>B: 检测挂起态 SE0 (VBUS 在) → 打开自己的 D+ 上拉 (变回外设 J 态)
    A->>A: 检测 D+ 为高 → 恢复主机: 发复位/重开 SOF
```

| 步骤 | 判定条件 | 规范依据提示 |
| --- | --- | --- |
| B 关上拉 → SE0 | A 侧 SE0 持续超过普通设备断开判定阈值（约 2.5 µs 量级）**且 VBUS 在** | 仅凭 SE0 会与拔出混淆，VBUS 是区分依据 |
| A 开 D+ 上拉 | A 必须在规定时间内完成角色切换，否则 B 超时放弃（相关超时参数见规范原文） | 各超时定时器见规范 HNP 时序表 |
| B 发复位 | B 已是主机，对新外设 A 走标准复位+枚举 | 复位时长同 USB 2.0（≥10 ms） |

### 六、OTG 描述符与 bcdOTG 特性位

OTG 描述符只存在于**作为外设的 B 设备**，由 A 在枚举时经标准 `GET_DESCRIPTOR`（类型 9）读取：

| 偏移 | 字段 | 大小 | 取值 |
| --- | --- | --- | --- |
| 0 | bLength | 1 | **5** |
| 1 | bDescriptorType | 1 | **9**（OTG） |
| 2 | bcdOTG | 2 | 高字节=版本号（2.0 补充为 02h，3.x 为 03h）；低字节为特性位 |

bcdOTG 低字节特性位（OTG 3.x 起 ADP 位才有意义）：

| 位 | 特性 | 含义 |
| --- | --- | --- |
| bit0 | SRP 支持 | B 设备可发 SRP / A 设备可检测 SRP |
| bit1 | HNP 支持 | 双方可执行 HNP 角色交换 |
| bit2 | ADP 支持 | OTG 3.0 起定义，支持 VBUS 断电接入探测 |

### 七、ADP：VBUS 断电时的接入探测（OTG 3.0）

SRP 依赖 B 能给 VBUS 充电；但在 VBUS 完全断电、双方都休眠的场景（如 OTG 3.x 的 SuperSpeed 设备），需要**反向**探测：

- **A/DRP 侧主动探测**：周期性把 VBUS 放电到 0，然后停止放电观察——若对面有设备挂着 **VBUS 上拉/电流源**，VBUS 会被拉高越过探测阈值（规范 ADP 参数，典型亚伏级，见规范原文），即判定"有接入"；
- 对面若无设备，VBUS 维持 0，继续休眠轮询；
- ADP 之下才轮到开 VBUS、走正常会话；它取代的是 SRP 中"VBUS 脉冲"那一段，代价是 A 侧需周期性唤醒。

| 对比项 | SRP (OTG 2.0) | ADP (OTG 3.x) |
| --- | --- | --- |
| 发起方 | B 设备 | A/DRP 设备（探测方） |
| 物理手段 | B 拉数据线 + 给 VBUS 充电 | 探测方放电后观察 VBUS 是否被对面拉起 |
| VBUS 状态 | VBUS 已断，B 弱充电 | VBUS 完全断，探测方瞬时观测 |

### 八、OTG 状态机概貌（核心状态节选）

以下为 OTG 2.0 状态机的简化节选（完整状态、转移条件与变量 a_bus_req/b_bus_req 等以规范状态机章节为准）：

```mermaid
stateDiagram-v2
    [*] --> a_idle: ID 接地识别为 A
    a_idle --> a_wait_vrise: a_bus_req(如响应 SRP)
    a_wait_vrise --> a_wait_bcon: VBUS 达有效值
    a_wait_vrise --> a_wait_vfall: 上升失败/超时
    a_wait_bcon --> a_host: 检测到 B 连接
    a_wait_bcon --> a_wait_vfall: 超时无连接
    a_host --> a_suspend: 主机挂起总线
    a_suspend --> a_peripheral: HNP: B 接管主机
    a_suspend --> a_host: B 请求恢复/角色回切
    a_host --> a_vbus_err: VBUS 异常
    a_vbus_err --> a_wait_vfall: 错误路径
    a_peripheral --> a_suspend: 再挂起由 B 主机管理
    a_wait_vfall --> a_idle: VBUS 放电完毕
```

```mermaid
stateDiagram-v2
    [*] --> b_idle: ID 悬空识别为 B
    b_idle --> b_srp_init: b_bus_req 且 SE0 条件满足
    b_srp_init --> b_wait_acon: 两段脉冲发完
    b_wait_acon --> b_peripheral: VBUS 有效(会话被接受)
    b_wait_acon --> b_idle: 超时(等放电后才能重试)
    b_idle --> b_peripheral: 直接检测到 VBUS(被动受电)
    b_peripheral --> b_host: HNP: 授权后接管主机
    b_host --> b_peripheral: 角色回切
```

### 九、Type-C 时代的映射：OTG 概念去了哪里

| OTG 2.0 概念 | OTG 机制 | Type-C + PD 对应物 | 备注 |
| --- | --- | --- | --- |
| A 设备（默认主机+供电） | ID 接地 | DFP + Source（Rp 上拉） | CC 电阻即可宣告角色，无需 ID 引脚 |
| B 设备请求供电 | SRP 两段脉冲 | 插入检测 + PD Request | Type-C 下插入即被 Rp/Rd 检测，SRP 消亡 |
| 主机角色让渡 | HNP（挂起+SE0+上拉移交） | PD **DR_Swap**（数据角色交换） | 都不需重新插拔 |
| ——（OTG 无此能力） | — | PD **PR_Swap**（电源角色交换） | OTG 时代 VBUS 永远归 A；PD 才能换 |
| A/B 双方协商偏好 | 应用层约定 | DRP 轮换 (tDRP，约 50~100 ms) + **Try.SRC/Try.SNK** | "谁说了算"的现代解法 |
| 探测接入 | ADP / SRP | CC 线连接检测（Type-C 规范原生能力） | Type-C 恒有 CC 检测，问题天然简化 |

OTG 的剩余价值：

1. **无 PD 控制器的嵌入式主机**：MCU 的 USB OTG 外设（如 STM32 OTG_FS/HS）+ Micro-AB/转接座，零额外芯片实现"手机读 U 盘"式主机；
2. **BC1.2/专有快充共存**的旧式 micro-USB 生态（见 [03-BC1.2与专有快充](21-charging-bc12-otg.md)）；
3. 作为理解 PD 角色交换（PR_Swap/DR_Swap/FR_Swap）的**概念底座**——状态机思想一脉相承。

### 十、调试 OTG 的常见问题

| 症状 | 根因 | 排查/处置 |
| --- | --- | --- |
| B 发了 SRP，A 不上电 | A 侧比较器阈值与 B 脉冲不匹配：VBUS 充不到约 2.1 V（B 侧负载电容过大）或数据脉冲宽度不足 5 ms | 示波器量两段脉冲；核对 PHY 检测寄存器 |
| VBUS 上升缓慢/欠压 | A 仅承诺 8 mA，线缆压降+容性负载导致达不到 VBUS 有效值（约 4.4 V） | 加软启动限流；核对 a_wait_vrise 类超时 |
| A/B 识别颠倒 | ID 上拉缺失、VIDL 阈值配置错、插头接触不良 | 量 ID 电压；加去抖 |
| B 永远成不了主机 | A 协议栈没读 OTG 描述符、没发 `b_hnp_enable`；或挂起时顺手关了 VBUS（HNP 要求 VBUS 保持） | 抓 SET_FEATURE 请求；检查挂起策略 |
| 挂起态 SE0 被判成拔出 | 判定只看了 SE0，未结合 VBUS 在场 | HNP 请求=SE0 持续 + VBUS 有效，二者缺一不可 |
| 双方同时请求角色 | 未实现规范规定的裁决与回退时序 | 严格按状态机实现，注意回切方向 |
| 断开后无法再次 SRP | VBUS 放电不完全，残留高于会话结束阈值 | 检查放电电阻与 a_wait_vfall 类时序 |
