---
title: "网络子类：ECM、NCM、RNDIS"
layer: 枝干/设备类协议
section: CDC-通信设备类
doc-path: 20-枝干-设备类协议/CDC-通信设备类/02-网络子类ECM-NCM-RNDIS.md
---
# 网络子类：ECM、NCM、RNDIS

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[CDC] → 叶
> ⬆️ 父节点: [00-CDC概述](00-CDC概述.md)

## 1. 用 USB 跑以太网的四种姿势

| 模型 | 规范来源 | 接口签名 | 定位 |
|---|---|---|---|
| ECM (Ethernet Control Model) | CDC 1.2 | 0x02/0x06/0x00 | 官方基线，性能最弱 |
| NCM (Network Control Model) | CDC-NCM 1.0 | 0x02/0x0D/0x00 | 官方演进版，一包多帧 |
| EEM (Ethernet Emulation Model) | CDC-EEM | 0x02/0x0C/0x07 | 轻量帧封装，少见 |
| RNDIS | 微软私有 | 0xEF/0x04/0x01（或伪装 0x02/0x06/0xFF） | 事实标准(历史)，Android 老方案 |

对操作系统而言，它们都长成一块 USB 网卡；差别在**一趟批量事务里能塞多少帧、控制面多复杂**。

## 2. ECM：教科书模型

- 数据面：一次批量事务 = 一个以太网帧（前导/FCS 不传，从目的 MAC 到载荷）；
- 控制面：通信接口带 **Ethernet Networking 功能描述符**（0x0F：48 位 MAC 地址、bmEthernetStatistics、wMaxSegmentSize=1514、段过滤器能力位）；
- 类请求：SET_ETHERNET_PACKET_FILTER (0x0E，wValue=过滤位图：广播/组播/单播/全收)；
- 通知：NETWORK_CONNECTION (0x00，链路 up/down)、CONNECTION_SPEED_CHANGE (0x2A，wValue=上行速率，wIndex=下行速率，单位 bps)；
- 性能天花板：**一帧一事务 + 每帧 52 字节协议开销**（令牌+握手+ACK 链），FS 上约 0.5~0.8 MB/s，HS 上约 20~30 MB/s 就难再高——千兆时代不可用，于是有了 NCM。

## 3. NCM：聚合传输（现代标准）

核心思想：**把 N 个以太网帧打包进一个 NTB（NCM Transfer Block）再走批量端点**，摊薄协议开销、减少事务次数。

NTB 结构骨架（16 位 NTB，NTB-16）：

```
| NHHeader (12B): "NCMH" 签名 0x484D434E, wHeaderLength,
|                 wSequence, wBlockLength(整块长度), wNdpIndex |
| 以太网帧 1 | 帧 2 | ... | 帧 N |
| NDP (网络数据指针): "NCDP"? → 项数组: wDatagramIndex(偏移), wDatagramLen |
```

- 设备与主机互发 NTB；`GET_NTB_PARAMETERS` (0x86) 协商最大块长、NDP 对齐等参数；
- 16 位/16 位 DPS（Datagram Pointer Signature）模式与 32 位 NTB-32 面向 HS/SS；
- Linux `cdc_ncm` 是 4G/5G 上网卡的标准驱动；Windows 8+ 内置。实测 HS 下可稳定 40+ MB/s，配合 SSD 时达瓶颈消除；
- 复合形态：MBIM（子类 0x0E）在 NCM 传输层之上跑 IP 会话协议，是现代蜂窝模组的标准（控制面命令复用同一批量通道，规范独立于 CDC 1.2）。

## 4. RNDIS：微软的"先发优势"

Remote NDIS 是微软在 CDC-ECM 成熟前定义的私有协议（2001），特点：

- 消息封装：`REMOTE_NDIS_INITIALIZE_MSG → INITIALIZE_CMPLT`、`REMOTE_NDIS_PACKET_MSG`（一包一帧，头部 44 字节量级）、KEEPALIVE 心跳；
- 控制面走**接口 0 的中断/控制通道**，数据面走批量对——与 CDC 结构貌合神离；
- 接口签名常见两种：`0xEF/0x04/0x01`（厂商自declare + MS OS 描述符声明 RNDIS）或伪装成 `0x02/0x06/0xFF`（假 CDC，靠 Windows 的兼容 ID 认领）；
- 历史：Android 4.x 之前"USB 网络共享"默认 RNDIS；Windows 全系支持（内置 rndis 驱动）；Linux `rndis_host`。**已被 NCM 取代**（Android 13 起默认 NCM），但存量设备与老车机/工控环境仍常见；
- 驱动绑定的黑科技全靠 [Microsoft OS 描述符](../其他设备类/06-WebUSB与厂商自定义类.md)——想理解 RNDIS 设备怎么免驱，去看那篇。

## 5. 对比速查

| | ECM | NCM | RNDIS | EEM |
|---|---|---|---|---|
| 标准化 | USB-IF | USB-IF | 微软私有 | USB-IF |
| 聚合 | 无（1 帧/事务） | NTB 多帧 | 无 | 帧束（bundle） |
| HS 实测吞吐 | ~20 MB/s | 40+ MB/s | ~30 MB/s | ~35 MB/s |
| 驱动覆盖 | 全平台内置 | Win8+/Linux/macOS | 全平台(存量) | Linux 为主 |
| 现状 | 教学/兼容 | **推荐** | 遗留维护 | 少见 |

## 6. 调试叶子

- Wireshark 抓 USB 网卡：Linux 上直接抓对应 usbmon 接口可见 NTB；抓"网卡侧"则看 cdc_ncm/rndis_host 之上的 ethX；
- 手机"USB 网络共享"不识别：先看设备管理器/lsusb 的接口签名，确认主机驱动认哪种模型（很多手机固件可切换 RNDIS/NCM）；
- 吞吐不达预期：检查 NTB 最大块长协商值与固件缓冲（单帧模式=忘了聚合）、ZLP 边界；
- MBIM/QMI 模组：wwan0 出现但无网 → 控制面会话未建立，属于移动宽带协议层问题，与 USB 传输层无关。

## 相关节点

- 上一级: [00-CDC概述](00-CDC概述.md) · 兄弟: [01-虚拟串口ACM](01-虚拟串口ACM.md)
- 树干: [包格式与事务](../../10-树干-USB核心/05-包格式与事务.md)（理解"开销"从哪来）
- 相邻: [MSC 与 BOT](../MSC-大容量存储/00-MSC概述与BOT.md)（同为"批量端点扛大流量"的设计）
