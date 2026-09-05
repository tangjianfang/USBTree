---
title: "USB3.x 规范级：包格式与定时器"
layer: 枝干/高速演进
doc-path: 40-枝干-高速演进/06-USB3x规范级-包格式与定时器.md
---
# USB3.x 规范级：包格式与定时器

> 🌿 知识树位置: 树干 → 枝干[高速演进] → 叶
> 前置下钻: [04-USB3x包格式与LTSSM.md](04-USB3x包格式与LTSSM.md) · 下一叶: [07-USB4规范级-配置空间与隧道.md](07-USB4规范级-配置空间与隧道.md)
> 树干基础: [../10-树干-USB核心/05-包格式与事务.md](../10-树干-USB核心/05-包格式与事务.md) · [../10-树干-USB核心/11-错误处理与可靠性.md](../10-树干-USB核心/11-错误处理与可靠性.md)
> 规范原文缓存索引: [../80-参考资料/README.md](../80-参考资料/README.md)

[04 叶](04-USB3x包格式与LTSSM.md)给出了链路层全景，本叶按 USB 3.2 规范（本地缓存 `80-参考资料/usb-core/USB3.2-Specification-2018.zip` 内 `USB 3.2 Revision 1.0.pdf`，下称 USB 3.2 spec）逐字段下钻：Header Packet 的 16 字节排布、TP/LMP 子类型全表、ITP 结构、有序集族、链路命令与信用管理/重传定时。所有数值取自 PDF 解析；解析错位处在文中显式标注，无法核实的值一律不写。

## 1. 四类包与 Header Packet 骨架

| 类型 | 全称 | 寻址/路由 | 职责（USB 3.2 spec §8.2） |
|---|---|---|---|
| LMP | Link Management Packet | 不携带地址，**不可路由**，仅链路两端 | 链路自身管理与测试 |
| TP | Transaction Packet | Route String + Device Address，贯穿全路径 | 流控、停摆、通知，无数据载荷 |
| DP | Data Packet | 同上 | DPH（头）+ DPP（载荷+CRC-32） |
| ITP | Isochronous Timestamp Packet | 无地址，**多播**到所有 U0 且完成端口配置的链路 | 主机广播时间戳 |

线上结构（§7.2.1.1）：

- 协议层 Header Packet = **12 B 头信息 + 2 B CRC-16 + 2 B Link Control Word = 16 B**。
- Gen 1：再加 4 符号帧定界 HPSTART（3×SHP + EPF），共 20 符号。
- Gen 2：非 deferred DPH 改用 DPHSTART（3×DPHP + EPF），并在 LCW 之后附 **Length 字段副本**（24 B），以实现单比特容错；deferred DPH 仍用 HPSTART、不带副本。
- 常见资料"Header Packet 32 字节"的说法是把帧符号/缓冲粒度计入后的粗略口径；规范协议层口径是上表 16 B + 帧符号。

CRC 实现（§7.2.1.1.2）：CRC-16 多项式 **100Bh**、初值 FFFFh、余数取反、接收端恒定残差 **F6AAh**——与 USB 2.0 的 CRC-16 不同。CRC-5（LCW 用）多项式 00101b、初值 11111b、残差 01100b。

## 2. 16 字节逐字段排布（DW0~DW3）

以 TP 为例（USB 3.2 spec 图 8-2、表 8-13；位序以规范表为准）：

| DW | 位域（bit） | 字段 | 说明 |
|---|---|---|---|
| 0 | 4:0 | Type | 表 8-1，5 bit，见 §3 |
| 0 | 24:5 | Route String / Reserved（20 b） | 下行包由 hub 路由；设备上行时置 0（§8.9：每级 hub 4 位端口号，Hub Depth×4 为偏移） |
| 0 | 31:25 | Device Address（7 b） | 1~127，0 为默认地址（§8.8） |
| 1 | 3:0 | SubType | TP 子类型，见 §3 |
| 1 | 5:4 | Rsvd | 0 |
| 1 | 6 | rty（仅 ACK） | 重发数据包请求 |
| 1 | 7 | D（Direction） | 0=Host→Device，1=Device→Host |
| 1 | 11:8 | Ept Num（4 b） | 端点号 |
| 1 | 14:12 | TT（Transfer Type，仅 SSP 有效） | 100b=Control 等；SS 模式保留为 0 |
| 1 | 15 | HE（仅 ACK） | Header Error 指示 |
| 1 | 20:16 | NumP（仅 ACK/ERDY 语义） | 可接收缓冲数 |
| 1 | 25:21 | Seq Num（5 b） | 数据包序号 |
| 1 | 30:26 | Rsvd（TPF 位组） | 0 |
| 1 | 31 | PP（Packet Pending，仅 ACK） | 主机还有数据 |
| 2 | 15:0 | Stream ID（SSP 流） | 流式端点 |
| 2 | 31:29 | NBI / DBI / RWRPA / SSI 标志组 | 依方向/TP 而异（表 8-13；**位段解析有错位，以规范表为准**） |
| 3 | 15:0 | CRC-16 | 覆盖前 12 B |
| 3 | 31:16 | Link Control Word | 见下表 |

> LMP/ITP 不带 Route String 与 Device Address（不可路由），DW0 高位为时间戳等自有字段；DPH 的 DW1/DW2 携带 Data Length 等字段。逐包差异以 §8.3~§8.7 各表为准。

Link Control Word（§7.2.1.1.3、表 8-2，偏移记作 3:bit）：

| 位段（SS） | 位段（SSP） | 字段 | 说明 |
|---|---|---|---|
| 3:16~3:18 | 3:16~3:19 | Header Sequence Number | 0~7（SS）/0~15（SSP） |
| 3:19~3:21 | 3:20~3:21 | Reserved | 0 |
| 3:22~3:24 | 3:22~3:24 | Hub Depth | 仅 Deferred 包有效，0~4 |
| 3:25 | 3:25 | DL（Delayed） | 包被延迟/重发，一路置位不清除 |
| 3:26 | 3:26 | DF（Deferred） | 仅 hub 可置：目标下行口在 U1/U2 |
| 3:27~3:31 | 3:27~3:31 | CRC-5 | 保护前 11 位 |

## 3. Type 字段与 TP 子类型全表

Type（表 8-1）：**LMP=00000b、TP=00100b、DPH=01000b、ITP=01100b**，其余保留。

TP SubType（表 8-12，4 bit）：

| 值 | TP | 用途与关键字段（§8.5 各节） |
|---|---|---|
| 0000b | Reserved | — |
| 0001b | ACK | IN：主机请求并确认；OUT：设备确认并报告 NumP；带 rty/PP（§8.5.1） |
| 0010b | NRDY | 端点未就绪（Not Ready），设备→主机（§8.5.2） |
| 0011b | ERDY | 端点就绪（Endpoint Ready），设备主动上报可收/可发 NumP（§8.5.3） |
| 0100b | STATUS | 控制传输状态阶段（§8.5.4） |
| 0101b | STALL | 端点停摆/请求不支持（§8.5.5） |
| 0110b | DEV_NOTIFICATION | 设备通知：Function Wake、LTM（延迟容忍消息）、Bus Interval Adjustment、Sublink Speed（§8.5.6） |
| 0111b | PING | 主机探测链路/设备在场（§8.5.7） |
| 1000b | PING_RESPONSE | 对 PING 的应答（§8.5.8） |
| 1001b~1111b | Reserved | — |

## 4. LMP 子类型表与端口配置流

LMP SubType（表 8-3，4 bit，偏移 0:5）：

| 值 | LMP | 用途（§8.4 各节） |
|---|---|---|
| 0000b | Reserved | — |
| 0001b | Set Link Function | 含 Force_LinkPM_Accept 位：强制接受 LGO_U1/U2（§8.4.2） |
| 0010b | U2 Inactivity Timeout | 携带 8 bit 超时值（§8.4.3） |
| 0011b | Vendor Device Test | 厂商测试专用（§8.4.4） |
| 0100b | Port Capability | 端口能力宣告（§8.4.5） |
| 0101b | Port Configuration | 端口配置（速度/通道协商的结果下发，§8.4.6） |
| 0110b | Port Configuration Response | 配置应答（§8.4.7） |
| 0111b | Precision Time Management | PTM/LDM（链路延迟测量）相关（§8.4.8） |
| 1000b~1111b | Reserved | — |

**进入 U0 的握手次序**（§7.2.4.2.1 前置条件 4、§8.4.5~8.4.7）：

```mermaid
flowchart LR
  A[链路训练完成 进入 U0] --> B[Header Sequence Number 通告]
  B --> C[Rx Header Buffer Credit 通告]
  C --> D[Port Capability LMP 交换]
  D --> E[Port Configuration LMP 下发]
  E --> F[Port Configuration Response LMP 确认]
  F --> G[端口配置完成 才可转发 TP/DP 并接收 ITP]
```

## 5. ITP 结构

ITP（§8.7、表 8-26）：主机在**每个总线区间**（125 µs）内、且根口链路处于 U0 时才发送；不产生应答；进 U0 后 tIsochronousTimestampStart 内即开始。字段：

| DW | 字段 | 位段 | 说明 |
|---|---|---|---|
| 0 | Type | 4:0 | 01100b |
| 0 | ITS（Isochronous Timestamp） | 31:5 | 低 14 位 = 125 µs 总线区间计数器（0x3FFF 回绕）；高 13 位 = Delta（距上一总线区间边界的时间，单位 tIsochTimestampGranularity，不越过边界取最近值） |
| 1 | Bus Interval Adjustment Control | 7:0 | **本版本已弃用**，置 0 |
| 1 | Correction | 20:8 | 经 PTM hub 累积的负时延修正（同粒度单位），主机置 0 |
| 2 | Reserved | — | 0 |
| 3 | CRC-16 + LCW | — | 同其他头包 |

若收到的 ITP 带有 LCW 的 DL 位，时间戳可能严重失准，设备可忽略。

## 6. 有序集（Ordered Set）与成帧符号

Gen 2 的控制块全集（§6.3.2.2）：**TS1、TS2、TSEQ、SYNC、SKP、SDS**。

| 有序集 | 用途 | 出现时机 |
|---|---|---|
| TSEQ | 均衡训练用的初始训练序列 | Polling.RxEQ；Gen 1 期间不得插入 SKP（§6.4.1.1.1） |
| TS1 / TS2 | 链路参数交换、状态协商 | Polling、Recovery、Hot Reset、Loopback 等所有再训练场合 |
| SYNC | 扰码器重置/块对齐 | Gen 2 每 16,384 个 TSEQ 强制插入一次（§6.3.2.3 规则 10） |
| SKP（+SKPEND） | 时钟补偿 | 周期插入；Gen 2 中以 SDP 结尾界定 |
| SDS | 数据流开始标志 | Gen 2 数据块流前（128b/132b） |

成帧/控制符号（表 6-2，Gen 1 值可靠；Gen 2 值仅列解析确认者）：

| 符号 | Gen 1 | Gen 2 | 含义 |
|---|---|---|---|
| SKP | K28.1 | CCh | 补偿频差 |
| SKPEND | — | 96h | SKP 串结束（不扰码） |
| SDP | K28.2 | 69h | 数据包开始 |
| EDP | K28.3 | （解析错位，见规范） | 数据包结束 |
| EDB | — | 9Ah | 废弃（nullified）包结束 |
| SUB | K28.4 | （见规范） | 解码错误替换符号 |
| COM | K28.5 | （见规范） | 符号对齐 |
| SHP | K27.7 | （65h/4Bh 错位，见规范） | Header Packet 开始 |
| DPHP | — | 同上 | Gen 2 非 deferred DPH 开始 |
| SLC | K30.7 | （见规范） | Link Command 开始 |
| EPF | K23.7 | E1h/36h（错位，见规范） | 包帧结束 |
| SDS | — | （见规范） | 数据流开始 |

> 表 6-2 的 PDF 提取在 Gen 2 列存在行错位，仅 SKP/SKPEND/SDP/EDB 四个值能可靠配对；其余以规范表 6-2 为准。另注：**EIEOS、RESET、FTS、CDRSYNC 属于 USB4 的链路训练有序集**（USB4 规范 §4.2），USB 3.2 规范中并不存在，详见 [07-USB4规范级-配置空间与隧道.md](07-USB4规范级-配置空间与隧道.md)。

## 7. 链路命令（Link Command）

结构（表 7-3）：8 符号 = SLC×3 + EPF + **16 bit 链路命令字 + 其副本**。命令字 = 11 bit 命令信息 + CRC-5（算法同 LCW）。

命令字段（表 7-4）：Class=b10:9，Type=b8:7，SubType=b6:4 与 b3:0。

| Class:Type | 命令 | 语义（表 7-5） |
|---|---|---|
| 00 | LGOOD_n（n=序号） | 确认收到对应序号的 Header Packet（SS：n=0~7；SSP：0~15） |
| 00 | LCRD_x / LCRD1_x / LCRD2_x | Rx Header Buffer 信用（x=A~G；Type1/Type2 两类流量各一组） |
| 00 | LBAD | 收到坏序号 HP，要求重发 |
| 00 | LRTY | 请求对端重发（重发 HP 不改 CRC-16） |
| 01 | LGO_U1 / LGO_U2 / LGO_U3 | 请求进入低功耗链路态 |
| 01 | LAU / LXU / LPMA | 接受/拒绝低功耗请求 / 电源管理确认 |
| 10 | LUP / LDN | 端口在 U0 在场宣告（up/down） |

Gen 2x2 每类信用从 A~D 扩到 **A~G**（多 3 个，§7.2.2.2）。流量分类：Type 1 = 周期 DP、TP、ITP、LMP；Type 2 = 异步 DP。

## 8. 信用管理与 Replay 重传定时

- **信用初始化**：进入 U0 后先做 Header Sequence Number 通告与 Rx Header Buffer Credit 通告（§7.2.4.1；低功耗转移条件 §7.2.4.2.1-4 要求两者完成），信用以 LCRD_x 回收，代表对端"Remote Rx Header Buffer"空位。
- **重传（Replay）机制**：发方等 LGOOD_n；收方校验 CRC-16/CRC-5 失败或序号错即回 LBAD，发方以 LRTY 触发重发；重发的 HP 置 LCW 的 DL 位。
- **定时**（表 7-7/7-8，均为 §7.2.4）：

| 定时器 | 值 | 含义 |
|---|---|---|
| PENDING_HP_TIMER | 10 µs | 等 LGOOD_n/LBAD 回执 |
| CREDIT_HP_TIMER | 5,000 µs | 等对端信用 |
| LGOOD/LBAD 回执期限 | SS 3.0 µs / SSP 1.5 µs | 收到 HP 后必须回执 |
| 链路命令处理时限 | 200 ns | 收到命令后的处理窗口 |
| PM_LC_TIMER / PM_ENTRY_TIMER | 4/8 µs、8/16 µs（x1/x2） | 低功耗入口 |
| Ux_EXIT_TIMER / U1_MIN_RESIDENCY_TIMER | 6,000 µs / 3 µs | 低功耗出口/驻留 |

定时器容差 0~+50%（§7.5）。完整 LTSSM 状态超时表见 [../90-附录/03-时序参数全表.md](../90-附录/03-时序参数全表.md)。

## 9. DFP / UFP 传输方向术语

| 术语 | 全称 | 定位 |
|---|---|---|
| DFP | Downstream Facing Port（下行口） | 主机侧与 hub 的下行方向端口；LTSSM Polling.PortConfig 分 (DFP)/(UFP) 两个变体（§7.5.4.6），负责发起 Hot Reset |
| UFP | Upstream Facing Port（上行口） | 设备侧与 hub 上行方向端口 |
| 主机（Host） | — | 唯一可发起 ITP（§8.7）；控制传输发起方 |
| 设备（Device） | — | 以 ERDY/DEV_NOTIFICATION 主动上报（§8.5.3/8.5.6） |

低功耗请求方向：任一端口可发 LGO_Ux，对端以 LAU/LXU 应答（§7.2.4.2）——与 USB 2.0 "只有主机能发起挂起"不同。

## 10. 与 USB 2.0 包体系的对照

| 维度 | USB 2.0 | USB 3.x |
|---|---|---|
| 广播令牌 | OUT/IN/SETUP 广播 | 无令牌，Route String 点对点路由 |
| 重传单位 | 事务（3 包） | 单个 Header Packet（LGOOD/LBAD/LRTY） |
| 流控 | NAK 握手 | NumP 信用 + LCRD 缓冲信用 |
| 同步头 | SYNC 8/32 位 | HPSTART 4 符号 + 16 B 头 |
| 校验 | CRC5/CRC16 | CRC-16（头）+ CRC-32（DPP）+ HEC 类成帧容错 |

## 相关节点

- [04-USB3x包格式与LTSSM.md](04-USB3x包格式与LTSSM.md)：链路层概览与 LTSSM 状态图
- [05-USB4深入-路由隧道与配置.md](05-USB4深入-路由隧道与配置.md)：USB4 体系语境
- [07-USB4规范级-配置空间与隧道.md](07-USB4规范级-配置空间与隧道.md)：USB4 传输层包与有序集增量
- [../10-树干-USB核心/05-包格式与事务.md](../10-树干-USB核心/05-包格式与事务.md)：USB 2.0 包格式基础
- [../10-树干-USB核心/11-错误处理与可靠性.md](../10-树干-USB核心/11-错误处理与可靠性.md)：重传与错误恢复语义
- [../90-附录/03-时序参数全表.md](../90-附录/03-时序参数全表.md)：LTSSM/LFPS 定时参数总表
