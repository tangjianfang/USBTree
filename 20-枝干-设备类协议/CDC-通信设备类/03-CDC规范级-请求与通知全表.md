---
title: "CDC 规范级附录：请求、通知与功能描述符全表"
layer: 枝干/设备类协议
section: CDC-通信设备类
doc-path: 20-枝干-设备类协议/CDC-通信设备类/03-CDC规范级-请求与通知全表.md
---
# CDC 规范级附录：请求、通知与功能描述符全表

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[CDC] → 附录[规范级速查]
> ⬆️ 父节点: [00-CDC概述.md](00-CDC概述.md)
> 📖 全部数值提取自 **CDC 1.2**（核心规范 Table 4/5/13/19、§6.2/6.3）、**PSTN 1.2**、**ECM 1.2**、**WMC 1.1**（同一 zip 缓存，见 [../../80-参考资料/README.md](../../80-参考资料/README.md)）。模型与驱动实战见 [01-虚拟串口ACM.md](01-虚拟串口ACM.md) / [02-网络子类ECM-NCM-RNDIS.md](02-网络子类ECM-NCM-RNDIS.md)。

## 1. 类代码、子类全表与协议编码

接口类：通信控制接口 `bInterfaceClass=0x02 (COMM)`；数据接口 `0x0A (Data Interface Class)`（其子类未用填 0）。

**通信接口子类全表（CDC 1.2 Table 4，0x00~0x0F）：**

| 代码 | 子类/模型 | 出处 | | 代码 | 子类/模型 | 出处 |
|---|---|---|---|---|---|---|
| 00h | 保留 | — | | 08h | Wireless Handset Control Model (WHCM) | WMC1.1 |
| 01h | Direct Line Control Model（直连） | PSTN1.2 | | 09h | Device Management | WMC1.1 |
| 02h | Abstract Control Model (ACM，虚拟串口) | PSTN1.2 | | 0Ah | Mobile Direct Line Model (MDLM) | WMC1.1 |
| 03h | Telephone Control Model | PSTN1.2 | | 0Bh | OBEX | WMC1.1 |
| 04h | Multi-Channel Control Model | ISDN1.2 | | 0Ch | Ethernet Emulation Model (EEM) | EEM1.0 |
| 05h | CAPI Control Model | ISDN1.2 | | 0Dh | Network Control Model (NCM) | NCM1.0 |
| 06h | Ethernet Networking Control Model (ECM) | ECM1.2 | | 0Eh | Mobile Broadband Interface Model (MBIM)* | MBIM1.0 |
| 07h | ATM Networking Control Model | ATM1.2 | | 0Fh~7Fh 保留 / 80h~FEh 厂商 | | |

\* 0Eh/MBIM 不在 CDC 1.2 表内，取自 MBIM 1.0 规范（zip 未缓存该文档），谨慎引用。

**通信接口协议编码（CDC 1.2 Table 5）：** `00h` 无类协议、`01h` AT 命令 (ITU-T V.250)、`02h` PCCA-101 AT、`03h` PCCA-101 & Annex O、`04h` GSM 07.07 AT、`05h` 3GPP 27.007 AT、`06h` C-S0017-0 (CDMA TIA AT)、`07h` USB EEM、`08h~FDh` 由 Command Set Functional Descriptor 声明的外部协议、`FEh` 保留、`FFh` 厂商自定义。

**数据接口协议（Table 7 摘要）**：`00h` 无、`01h` Network Transfer Block（NCM 的 NTB，数据接口唯一类协议值）；`30h~32h+` ISDN BRI 物理层协议（I.430/HDLC 等）。

## 2. 类特定请求全表（CDC 1.2 Table 19，0x00~0x8A，按子规范归属）

所有类请求 bmRequestType：SET=`00100001b (0x21)`，GET=`10100001b (0xA1)`；接收者为通信接口（wIndex=接口号，wValue 多为 0 或选择子）。

| 代码 | 请求 | 模型/出处 | wValue / 数据载荷 |
|---|---|---|---|
| 00h | SEND_ENCAPSULATED_COMMAND | 核心 §6.2.1 | OUT：wLength=命令长度，Data=协议命令（AT 等） |
| 01h | GET_ENCAPSULATED_RESPONSE | 核心 §6.2.2 | IN：Data=上一命令的响应（可分块读） |
| 02h | SET_COMM_FEATURE | PSTN1.2 | OUT：wValue=Feature Selector（00h ABSTRACT_STATE / 01h COUNTRY_SETTING），Data=2B 状态 |
| 03h | GET_COMM_FEATURE | PSTN1.2 | IN：同上，返回当前特征 |
| 04h | CLEAR_COMM_FEATURE | PSTN1.2 | 恢复默认特征，无 Data |
| 05h~0Fh | 保留 | — | — |
| 10h | SET_AUX_LINE_STATE | PSTN | wValue: 0 断开 / 1 连接副话机 |
| 11h | SET_HOOK_STATE | PSTN | wValue: 0000h ON_HOOK / 0001h OFF_HOOK / 0002h SNOOPING（来电显示） |
| 12h | PULSE_SETUP | PSTN | wValue=FFFFh 结束脉冲拨号保持，其他=准备 |
| 13h | SEND_PULSE | PSTN | wValue=make/break 脉冲周期数 |
| 14h | SET_PULSE_TIME | PSTN | 高字节断开 ms，低字节接通 ms |
| 15h | RING_AUX_JACK | PSTN | wValue=振铃次数 |
| 20h | **SET_LINE_CODING** | PSTN | OUT：7 字节 Line Coding 结构（见下） |
| 21h | **GET_LINE_CODING** | PSTN | IN：同结构 |
| 22h | **SET_CONTROL_LINE_STATE** | PSTN | wValue 位图：D0 RTS（载波，V.24-105），D1 DTR（终端在位，V.24-108/2） |
| 23h | **SEND_BREAK** | PSTN | wValue=break 时长 ms；FFFFh=持续 break 直至收到 0000h |
| 30h | SET_RINGER_PARMS / 31h GET_RINGER_PARMS | PSTN | 振铃参数结构 |
| 32h | SET_OPERATION_PARMS / 33h GET_OPERATION_PARMS | PSTN | 拨号/等待参数 |
| 34h | SET_LINE_PARMS / 35h GET_LINE_PARMS | PSTN | 线路参数结构 |
| 36h | DIAL_DIGITS | PSTN | Data=拨号串结构 |
| 37h | SET_UNIT_PARAMETER / 38h GET_UNIT_PARAMETER / 39h CLEAR_UNIT_PARAMETER | ISDN | 单元参数 |
| 3Ah | GET_PROFILE | ISDN | IN：设备配置档 |
| 40h | SET_ETHERNET_MULTICAST_FILTERS | ECM | OUT：组播 MAC 地址表 |
| 41h | SET_ETHERNET_POWER_MANAGEMENT_PATTERN_FILTER | ECM | OUT：电源管理唤醒模式滤波器 |
| 42h | GET_ETHERNET_POWER_MANAGEMENT_PATTERN_FILTER | ECM | IN：读取滤波器状态 |
| 43h | SET_ETHERNET_PACKET_FILTER | ECM | wValue 位图（广播/组播/单播等，ECM §6.3.x）；**注意网络旧文常误写 0x0E，规范值为 43h** |
| 44h | GET_ETHERNET_STATISTIC | ECM | IN：统计计数器结构 |
| 50h | SET_ATM_DATA_FORMAT / 51h GET_ATM_DEVICE_STATISTICS / 52h SET_ATM_DEFAULT_VC / 53h GET_ATM_VC_STATISTICS | ATM | ATM 数据格式/统计 |
| 60h~7Fh | MDLM 语义模型专用请求（32 个） | WMC1.1 Table 5-4 | 具体值由 MDLM Detail 描述符声明的语义模型定义 |
| 80h | GET_NTB_PARAMETERS | NCM1.0 | IN：NTB 参数结构（NTB 格式、缓冲大小等） |
| 81h | GET_NET_ADDRESS / 82h SET_NET_ADDRESS | NCM1.0 | 6 字节 MAC 地址 |
| 83h | GET_NTB_FORMAT / 84h SET_NTB_FORMAT | NCM1.0 | wValue：0001h=16bit NTB，0002h=32bit NTB |
| 85h | GET_NTB_INPUT_SIZE / 86h SET_NTB_INPUT_SIZE | NCM1.0 | 4 字节 dwNtbInMaxSize |
| 87h | GET_MAX_DATAGRAM_SIZE / 88h SET_MAX_DATAGRAM_SIZE | NCM1.0 | 2 字节最大数据报（NCM1.0 新增） |
| 89h | GET_CRC_MODE / 8Ah SET_CRC_MODE | NCM1.0 | wValue：0000h 无 CRC / 0001h 32bit CRC |
| 8Bh~FFh | 保留 | — | — |

**COMM_FEATURE 选择子（PSTN Table 14，SET/GET/CLEAR_COMM_FEATURE 的 wValue）：**

| 选择子 | 代码 | Data 长度 | 含义 |
|---|---|---|---|
| ABSTRACT_STATE | 01h | 2 | 位图：D0=呼叫管理信息复用到数据类接口；D1=Idle（接口暂停收发）——仅 ACM 模型有效 |
| COUNTRY_SETTING | 02h | 2 | ISO3166 国家码，须与 Country Selection 功能描述符声明一致 |

**Line Coding 结构（PSTN Table 17，虚拟串口核心）**：

| 偏移 | 字段 | 值 |
|---|---|---|
| 0 | dwDTERate (4B) | 波特率 bps（LE） |
| 4 | bCharFormat (1B) | 停止位：0=1 位，1=1.5 位，2=2 位 |
| 5 | bParityType (1B) | 0=None，1=Odd，2=Even，3=Mark，4=Space |
| 6 | bDataBits (1B) | 数据位 5/6/7/8/16 |

### 2.1 ECM 请求载荷细节（ECM 1.2 §6.2）

| 请求 | wValue | wLength / Data |
|---|---|---|
| SET_ETHERNET_MULTICAST_FILTERS (40h) | 过滤器数 N | N×6 字节组播 MAC 列表（网络字节序）；改一个须整表重发 |
| SET_ETHERNET_POWER_MANAGEMENT_PATTERN_FILTER (41h) | 过滤器编号 | 电源管理唤醒模式结构：MaskSize(2B)+Mask+Pattern（模式从以太帧 DA 起匹配）；wLength=0 表示清除该滤波器 |
| GET_ETHERNET_POWER_MANAGEMENT_PATTERN_FILTER (42h) | 过滤器编号 | 返回 2B 布尔：0x0001 生效 / 0x0000 未设置或装不下 |
| SET_ETHERNET_PACKET_FILTER (43h) | 过滤位图 | 无 Data。位图：D0 PACKET_TYPE_PROMISCUOUS、D1 ALL_MULTICAST、D2 DIRECTED、D3 BROADCAST、D4 MULTICAST（列表内组播）；D5~D15 保留 |
| GET_ETHERNET_STATISTIC (44h) | 统计特征选择子 | 返回 4B 无符号计数（上电/复位起累计，回绕） |

统计特征选择子（ECM Table 9）：`01h XMIT_OK`、`02h RCV_OK`、`03h XMIT_ERROR`、`04h RCV_ERROR`、`05h RCV_NO_BUFFER`、`06h~0Bh DIRECTED/MULTICAST/BROADCAST_BYTES/FRAMES_XMIT`、`0Ch~11h …_RCV`（各 4B）。

## 3. 类特定通知全表（CDC 1.2 §6.3 + PSTN Table 30 + ECM Table 11）

通知走通信接口的**中断 IN 端点**，固定 `bmRequestType=10100001b (0xA1)`，wIndex=接口号。

| 代码 | 通知 | 出处 | wValue / wLength / Data |
|---|---|---|---|
| 00h | NETWORK_CONNECTION | 核心/PSTN/ECM | wValue 0=断开 1=连接；wLength=0 |
| 01h | RESPONSE_AVAILABLE | 核心/PSTN | 主机应发 GET_ENCAPSULATED_RESPONSE；wLength=0 |
| 08h | AUX_JACK_HOOK_STATE | PSTN | wValue 0=On hook / 1=Off hook |
| 09h | RING_DETECT | PSTN | POTS 线路振铃；wLength=0 |
| 20h | SERIAL_STATE | PSTN | wLength=2，UART 状态位图（见下） |
| 28h | CALL_STATE_CHANGE | PSTN | wValue 高字节=呼叫索引、低字节=状态变更；Data=变长附信息（来电显示等） |
| 29h | LINE_STATE_CHANGE | PSTN | 线路状态变更 |
| 2Ah | CONNECTION_SPEED_CHANGE | 核心/ECM | wLength=8：DLBitRate(4B)+ULBitRate(4B)，bps；规范要求每次 NETWORK_CONNECTION 后必须紧跟本通知 |
| 40h~5Fh | MDLM 语义模型专用通知（32 个） | WMC1.1 Table 5-5 | 语义模型定义 |
| 0Ah~07h/21h~27h/2Bh~3Fh/60h~FFh | 保留 | — | — |

**SERIAL_STATE UART 位图（PSTN Table 31）**：D0 bRxCarrier（DCD，V.24-109）、D1 bTxCarrier（DSR，V.24-106）、D2 bBreak、D3 bRingSignal、D4 bFraming、D5 bParity、D6 bOverRun；D7~D15 保留。一次性信号（break/ring/overrun）通知后自动清零，等状态再次变化才重发；载波类信号仅在变化时通知。

## 4. 功能描述符子类型全表（CDC 1.2 Table 13，CS_INTERFACE 内）

功能描述符通用格式：`bFunctionLength(1) | bDescriptorType=0x24 CS_INTERFACE(1) | bDescriptorSubtype(1) | 类型专属字段…`，置于接口描述符的类特定附加段，且必须以 Header 开头。

| 子类型 | 功能描述符 | | 子类型 | 功能描述符 |
|---|---|---|---|---|
| 00h | Header（头） | | 0Dh | Multi-Channel Management（ISDN） |
| 01h | Call Management（PSTN） | | 0Eh | CAPI Control Management（ISDN） |
| 02h | Abstract Control Management（PSTN/ACM） | | 0Fh | Ethernet Networking（ECM） |
| 03h | Direct Line Management（PSTN/DLM） | | 10h | ATM Networking |
| 04h | Telephone Ringer（PSTN） | | 11h | Wireless Handset Control Model（WMC） |
| 05h | Telephone Call & Line State Reporting（PSTN） | | 12h | Mobile Direct Line Model（WMC） |
| 06h | Union（核心） | | 13h | MDLM Detail（WMC） |
| 07h | Country Selection（核心） | | 14h | Device Management Model（WMC） |
| 08h | Telephone Operational Modes（PSTN） | | 15h | OBEX（WMC） |
| 09h | USB Terminal（PSTN） | | 16h | Command Set（WMC） |
| 0Ah | Network Channel Terminal（PSTN） | | 17h | Command Set Detail（WMC） |
| 0Bh | Protocol Unit（PSTN） | | 18h | Telephone Control Model（WMC） |
| 0Ch | Extension Unit（PSTN） | | 19h | OBEX Service Identifier（WMC） |
| 1Ah | NCM Functional Descriptor（NCM1.0） | | 1Bh~7Fh 保留 / 80h~FEh 厂商 | |

数据类功能描述符（Table 14）只有 `00h Header`，其余保留/厂商。MBIM 功能描述符子类型 0x1F（MBIM 1.0，zip 未缓存，谨慎引用）。

## 5. 核心功能描述符逐字段

**Header（子类型 00h，核心 Table 15）：**

| 偏移 | 字段 | 值 |
|---|---|---|
| 0 | bFunctionLength | 5 |
| 1 | bDescriptorType | 0x24 (CS_INTERFACE) |
| 2 | bDescriptorSubtype | 0x00 |
| 3 | bcdCDC | 规范版本，1.2 版设备 = 0x0120（BCD，LE） |

**Union（子类型 06h，核心 Table 16）：**

| 偏移 | 字段 | 说明 |
|---|---|---|
| 0 | bFunctionLength | 5+N |
| 1 | bDescriptorType | 0x24 |
| 2 | bDescriptorSubtype | 0x06 |
| 3 | bControlInterface | 主控接口号（通信接口） |
| 4~ | bSubordinateInterface0..N-1 | 被捆绑的下级接口号（数据接口等）；主机靠它把 ECM/ACM 的控制接口与数据接口配对 |

**Call Management（子类型 01h，PSTN Table 3）：**

| 偏移 | 字段 | 说明 |
|---|---|---|
| 0 | bFunctionLength | 5 |
| 1 | bDescriptorType | 0x24 |
| 2 | bDescriptorSubtype | 0x01 |
| 3 | bmCapabilities | D0：1=设备自身处理呼叫管理；D1：1=呼叫管理信息可走数据类接口（D0=0 时 D1 必须为 0） |
| 4 | bDataInterface | 用于呼叫管理的数据接口号（不用填 0） |

**Abstract Control Management（子类型 02h，PSTN Table 4）：**

| 偏移 | 字段 | 说明 |
|---|---|---|
| 0 | bFunctionLength | 4 |
| 1 | bDescriptorType | 0x24 |
| 2 | bDescriptorSubtype | 0x02 |
| 3 | bmCapabilities | D0：支持 SET/GET/CLEAR_COMM_FEATURE；D1：支持 SET_LINE_CODING+SET_CONTROL_LINE_STATE+GET_LINE_CODING+SERIAL_STATE 通知；D2：支持 SEND_BREAK；D3：支持 NETWORK_CONNECTION 通知；D4~D7 保留。虚拟串口设备典型值 **0x02** 或 **0x06** |

**Direct Line Management（子类型 03h，PSTN Table 5）：**

| 偏移 | 字段 | 说明 |
|---|---|---|
| 0 | bFunctionLength | 4 |
| 1 | bDescriptorType | 0x24 |
| 2 | bDescriptorSubtype | 0x03 |
| 3 | bmCapabilities | D0：支持 PULSE_SETUP+SEND_PULSE+SET_PULSE_TIME；D1：支持 SET_AUX_LINE_STATE+RING_AUX_JACK+AUX_JACK_HOOK_STATE 通知；D2：脉冲拨号需额外 PULSE_SETUP 释放保持电路；D3~D7 保留 |

Country Selection（子类型 07h，核心 Table 17）：iCountryCodeRelDate(1，字符串索引，日期格式 ddmmyyyy) + wCountryCode0..N-1(各 2B，ISO3166 十六进制码)。

**Ethernet Networking（子类型 0Fh，ECM §5.3）：**

| 偏移 | 字段 | 说明 |
|---|---|---|
| 0 | bFunctionLength | 13 |
| 1 | bDescriptorType | 0x24 |
| 2 | bDescriptorSubtype | 0x0F |
| 3 | iMACAddress | 字符串索引：MAC 地址字符串（以 UTF-16LE 十六进制文本存于 String Descriptor） |
| 4 | bmEthernetStatistics (4B) | 位图：设备支持哪些 Table 9 统计计数器 |
| 8 | wMaxSegmentSize (2B) | 网段内最大帧段（不含 CRC，以太网通常 1514） |
| 10 | wNumberMCFilters (1B) | 可支持组播地址过滤器个数与能力位 |
| 11 | wNumberPowerFilters (1B) | 电源管理模式滤波器个数 |

NCM 功能描述符（子类型 1Ah，NCM1.0 §5.3）：bMasterInterface/bSlaveInterface0（Union 的 NCM 化重复声明）+ bmNetworkCapabilities（D0=支持 extended statistics? 按位定义——zip 未含 NCM 原文，字段细节以 NCM 1.0 为准）。

## 相关节点

- 父分枝：[00-CDC概述.md](00-CDC概述.md)；实战：[01-虚拟串口ACM.md](01-虚拟串口ACM.md) / [02-网络子类ECM-NCM-RNDIS.md](02-网络子类ECM-NCM-RNDIS.md)
- 原文缓存：[../../80-参考资料/README.md](../../80-参考资料/README.md)（CDC-1.2.zip：核心、PSTN、ECM、ISDN、ATM、WMC 各 PDF）
