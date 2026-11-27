# 每个 KB 文件：id, title, topic, level, keywords, sources(USBTree 路径), specs, related(其他 KB id), facts(手写核心事实/勘误)
H = "20-枝干-设备类协议/HID-人机接口设备/"
O = "20-枝干-设备类协议/其他设备类/"
B = "50-枝干-无线关联/BLE-低功耗蓝牙/"
TOPICS = [
dict(id="01-overview-versions", title="USB 概述、版本演进与命名", topic="core", level="入门",
 keywords=["USB 1.1","USB 2.0","USB 3.2 Gen 2x2","USB4","USB4 v2","速率 speed","命名 naming","USB-IF","LS/FS/HS/SS"],
 sources=["10-树干-USB核心/01-概述与版本演进.md","40-枝干-高速演进/03-各版本对比速查.md"],
 specs=["USB 2.0 Specification","USB 3.2 Specification","USB4 Specification v2.0"],
 related=["02-architecture-topology","30-usb3-superspeed","31-usb4","90-quick-reference"],
 facts=r"""
| 速率模式 Speed | 标称速率 | 首个规范 | 物理/编码 |
|---|---|---|---|
| Low Speed (LS) | 1.5 Mbit/s | USB 1.0 (1996-01) | D+/D− 半双工, NRZI + bit stuffing |
| Full Speed (FS) | 12 Mbit/s | USB 1.0/1.1 (1998-09) | 同上 |
| High Speed (HS) | 480 Mbit/s | USB 2.0 (2000-04) | 同上, 微帧 125 µs |
| SuperSpeed Gen 1 (SS) | 5 Gbit/s | USB 3.0 (2008-11) | 独立 TX/RX 对, 8b/10b |
| SuperSpeedPlus Gen 2 | 10 Gbit/s | USB 3.1 (2013-07) | 128b/132b |
| Gen 2x2 | 20 Gbit/s | USB 3.2 (2017-09) | 双通道, 仅 Type-C |
| USB4 Gen 3x2 | 40 Gbit/s | USB4 (2019-08) | 隧道架构, 基于 Thunderbolt 3 |
| USB4 Gen 4 | 80 Gbit/s（非对称 120/40） | USB4 v2 (2022-10) | PAM-3 |

- 命名规则：规范版本号 ≠ 速率。现行营销名按速率：SuperSpeed USB 5Gbps / 10Gbps / 20Gbps、USB 40Gbps、USB 80Gbps。USB 3.0 = USB 3.1 Gen 1 = USB 3.2 Gen 1。
- USB 2.0 规范最常查章节：第 7 章 电气、第 8 章 协议层（包/PID/CRC）、第 9 章 USB Device Framework（描述符、标准请求、设备状态）、第 11 章 Hub。
- 设计原则：Host-centric polled bus——所有事务由主机发起；设备唯一主动行为是挂起态下的远程唤醒（Remote Wakeup）。
- USB 2.0（及 1.x）线上是 NRZI + 位填充，有效速率开销来自位填充、包头/握手与微帧调度，不使用 8b/10b。8b/10b 是 USB 3.0 Gen1（5 Gbit/s 线路速率，编码后 4 Gbit/s）；USB 3.1 Gen2 起为 128b/132b。
"""),
dict(id="02-architecture-topology", title="体系架构、拓扑、端点与管道、集线器", topic="core", level="入门",
 keywords=["host","hub","function","tiered star 分层星型","endpoint 端点","pipe 管道","interface 接口","configuration 配置","device state 设备状态","TT 事务转换器","composite device 复合设备"],
 sources=["10-树干-USB核心/02-体系架构与分层模型.md","10-树干-USB核心/09-集线器与连接管理.md"],
 specs=["USB 2.0 Specification ch.4/5/9/11"],
 related=["04-packets-transactions","06-descriptors","07-enumeration-requests"],
 facts=r"""
| 约束 | 值 | 来源 |
|---|---|---|
| 设备地址 Address | 7 bit, 1–127（0 = 默认地址，仅枚举前） | Token ADDR 字段 7 bit |
| 端点号 Endpoint Number | 0–15，每个方向独立；EP0 双向且必有 | Token ENDP 字段 4 bit |
| 层级 Tiers | 最多 7 层（根集线器为第 1 层；链路上最多 5 个非根集线器） | USB 2.0 §4.1.1 |
| 端点地址编码 | bit7 = 方向（1 = IN 设备→主机），bit3:0 = 端点号，如 0x81 = EP1 IN | USB 2.0 §9.6.6 |

- 方向永远以主机为参照：IN = Device→Host，OUT = Host→Device。
- 层次：Configuration ⊃ Interface（+ Alternate Setting）⊃ Endpoint。同一时刻只有一个 Configuration 生效；类驱动按 Interface 绑定。
- 设备状态（USB 2.0 §9.1）：Attached → Powered → Default（总线复位后）→ Address（SET_ADDRESS）→ Configured（SET_CONFIGURATION ≠ 0）；任一状态总线空闲 3 ms → Suspended。
- 集线器 Hub：上行端口 + Repeater + Hub Controller；HS Hub 含 TT（单 TT / 多 TT）为 FS/LS 设备做 Split 事务。USB 3.x Hub = USB 2.0 Hub + SuperSpeed Hub 并联，两套独立拓扑。
- 复合设备 Composite：bDeviceClass=0x00（或 0xEF/0x02/0x01 + IAD），Windows 由 usbccgp.sys 为每个接口/IAD 功能创建子 devnode。
"""),
dict(id="03-physical-signaling", title="物理层、电气特性与信号编码", topic="core", level="进阶",
 keywords=["VBUS","D+/D-","pull-up 上拉 1.5k","speed detection 速度检测","chirp","NRZI","bit stuffing 位填充","SYNC","EOP","SE0","J/K state"],
 sources=["10-树干-USB核心/03-物理层与电气特性.md","10-树干-USB核心/04-信号编码与比特流.md"],
 specs=["USB 2.0 Specification ch.7"],
 related=["02-architecture-topology","04-packets-transactions","20-connectors-typec"],
 facts=r"""
| 项 | 值 |
|---|---|
| USB 2.0 线 | VBUS(5V)、D−、D+、GND |
| FS 设备识别 | 设备 1.5 kΩ 上拉 D+；主机每线 15 kΩ 下拉 |
| LS 设备识别 | 设备 1.5 kΩ 上拉 D− |
| HS 识别 | 以 FS 连接，复位期间设备发 Chirp K，主机回 K-J 序列，成功后切 HS 终端（45 Ω） |
| 编码 | NRZI：数据 0 = 电平翻转，1 = 保持；连续 6 个 1 后插入 0（bit stuffing） |
| 包边界 | SYNC（FS/LS 8 bit，HS 32 bit）开头；EOP = SE0 + J |
| 复位 Reset | 主机驱动 SE0 ≥ 10 ms |
| 单段线长 | FS/HS 约 5 m |

- HS 设备只跑 FS 的首要原因：Chirp 握手失败（信号完整性、线长、经过仅 FS 的 Hub）。
"""),
dict(id="04-packets-transactions", title="包格式、PID、事务、帧与 Data Toggle", topic="core", level="进阶",
 keywords=["PID","token packet","data packet","handshake","ACK","NAK","STALL","NYET","PING","SPLIT","SOF","frame 帧","microframe 微帧","data toggle","CRC5","CRC16"],
 sources=["10-树干-USB核心/05-包格式与事务.md"],
 specs=["USB 2.0 Specification ch.8"],
 related=["05-transfer-types-bandwidth","09-errors-testmode","30-usb3-superspeed"],
 facts=r"""
PID 字节 = PID[3:0] + 反码 ~PID[3:0]（高 4 位），线上 LSB 先发。

| 类型 | PID | 4 bit | PID 字节 | 说明 |
|---|---|---|---|---|
| Token | OUT | 0001 | 0xE1 | 主机→设备数据 |
| Token | IN | 1001 | 0x69 | 设备→主机数据 |
| Token | SOF | 0101 | 0xA5 | 帧起始 + 11 bit 帧号 |
| Token | SETUP | 1101 | 0x2D | 控制传输 Setup 阶段 |
| Data | DATA0 | 0011 | 0xC3 | |
| Data | DATA1 | 1011 | 0x4B | |
| Data | DATA2 | 0111 | 0x87 | HS 高带宽同步 |
| Data | MDATA | 1111 | 0x0F | HS 高带宽同步 / Split |
| Handshake | ACK | 0010 | 0xD2 | |
| Handshake | NAK | 1010 | 0x5A | 暂时无法收/发 |
| Handshake | STALL | 1110 | 0x1E | 端点停止 / 请求不支持 |
| Handshake | NYET | 0110 | 0x96 | HS：已收，下一包未就绪 |
| Special | PRE / ERR | 1100 | 0x3C | LS 前导 / Split 错误 |
| Special | SPLIT | 1000 | 0x78 | HS Hub Split 事务 |
| Special | PING | 0100 | 0xB4 | HS 批量/控制 OUT 流控 |

- Token 包：PID + ADDR(7) + ENDP(4) + CRC5；Data 包：PID + 0–1024 B + CRC16；Handshake：仅 PID。
- 帧 Frame：FS/LS 1 ms，SOF 每帧一个；HS 微帧 Microframe 125 µs，8 个/帧。
- Data Toggle：DATA0/DATA1 交替去重；SETUP 阶段恒 DATA0；Status 阶段恒 DATA1；SET_CONFIGURATION / SET_INTERFACE / CLEAR_FEATURE(ENDPOINT_HALT) 将相关端点 toggle 复位为 DATA0。
- 同步端点不回握手包。
"""),
dict(id="05-transfer-types-bandwidth", title="四种传输类型、bInterval 与带宽调度", topic="core", level="进阶",
 keywords=["control transfer","bulk","interrupt","isochronous","bInterval","wMaxPacketSize","polling rate 回报率","1000 Hz","8000 Hz","high-bandwidth","bandwidth budget 带宽预算"],
 sources=["10-树干-USB核心/06-四种传输类型.md","10-树干-USB核心/13-总线带宽与调度计算.md"],
 specs=["USB 2.0 Specification ch.5, §9.6.6"],
 related=["04-packets-transactions","06-descriptors","12-hid-devices"],
 facts=r"""
| 类型 | 带宽保证 | 时延保证 | 重传 | wMaxPacketSize LS / FS / HS / SS |
|---|---|---|---|---|
| Control | 保留份额 | 无 | 有 | 8 / 8,16,32,64 / 64 / 512 |
| Bulk | 无 | 无 | 有 | — / 8–64 / 512 / 1024（burst ≤16） |
| Interrupt | 每周期 1 次（HS 可 1–3 事务/微帧） | ≤ 周期 | 有 | ≤8 / ≤64 / ≤1024 / ≤1024 |
| Isochronous | 预留 | 每帧/微帧 | 无 | — / ≤1023 / ≤1024×3 / ≤1024 |

bInterval 语义：

| 速率/类型 | 解释 | 范围 | 最高轮询率 |
|---|---|---|---|
| LS 中断 | 帧数（ms），实际主机多按 ≥10 ms 处理 | 10–255 | ~100 Hz |
| FS 中断 | 帧数（ms） | 1–255 | **1000 Hz**（bInterval=1） |
| FS 同步 | 2^(bInterval−1) 帧 | 1–16 | 1000 Hz |
| HS 中断/同步 | 2^(bInterval−1) 微帧 | 1–16（125 µs – 4.096 s） | **8000 Hz**（bInterval=1） |
| SS 中断/同步 | 同 HS | 1–16 | 8000 Hz |

- HS 高带宽：wMaxPacketSize bit12:11 = 每微帧附加事务数（0–2，即 1–3 个事务）。
- 规则：USB 2.0 周期性传输（中断+同步）最多占 FS 帧 90% / HS 微帧 80%。
- 鼠标回报率：全速中断 bInterval=1 即 1 ms = 1000 Hz（全速上限）；高速 bInterval=1 为 125 µs = 8000 Hz，bInterval=4 为 8×125 µs = 1 ms = 1000 Hz。高带宽（每微帧 2~3 个事务）只增加每微帧字节数，且要求 bInterval=1。
"""),
dict(id="06-descriptors", title="标准描述符字段全表", topic="core", level="进阶",
 keywords=["device descriptor 设备描述符","configuration descriptor","interface descriptor","endpoint descriptor","string descriptor","IAD","BOS","device qualifier","bMaxPacketSize0","wTotalLength","bmAttributes","bMaxPower"],
 sources=["10-树干-USB核心/07-描述符详解.md"],
 specs=["USB 2.0 Specification §9.5–9.6","USB 3.2 Specification §9.6","IAD ECN"],
 related=["07-enumeration-requests","11-hid-core","14-cdc"],
 facts=r"""
描述符类型码 bDescriptorType：

| 值 | 描述符 | 长度 |
|---|---|---|
| 0x01 | Device | 18 |
| 0x02 | Configuration | 9（+ wTotalLength 子树） |
| 0x03 | String | 可变，UTF-16LE；索引 0 = LANGID 列表（0x0409 en-US） |
| 0x04 | Interface | 9 |
| 0x05 | Endpoint | 7（SS 后跟 SS Endpoint Companion 0x30，6 B） |
| 0x06 | Device Qualifier | 10 |
| 0x07 | Other Speed Configuration | 9 |
| 0x0B | Interface Association (IAD) | 8 |
| 0x0F | BOS | 5 + 能力描述符 |
| 0x10 | Device Capability | 可变（0x02 USB 2.0 Extension/LPM，0x03 SS USB，0x05 Platform：MS OS 2.0 / WebUSB） |
| 0x21 / 0x22 / 0x23 | HID / Report / Physical（类描述符） | |
| 0x24 / 0x25 | CS_INTERFACE / CS_ENDPOINT（CDC/UAC/UVC 类特定） | |

Device Descriptor（18 B）：bLength(1)=0x12, bDescriptorType(1)=0x01, bcdUSB(2), bDeviceClass(1), bDeviceSubClass(1), bDeviceProtocol(1), bMaxPacketSize0(1), idVendor(2), idProduct(2), bcdDevice(2), iManufacturer(1), iProduct(1), iSerialNumber(1), bNumConfigurations(1)。多字节字段小端。

- bMaxPacketSize0：**USB 2.0 及以下为字节数**（LS 8；FS 8/16/32/64；HS 64）；**USB 3.x SuperSpeed 为 2 的指数**，固定 0x09 表示 2^9 = 512。
- bcdUSB：0x0200 = USB 2.0；0x0201/0x0210 = 支持 BOS（LPM、MS OS 2.0 平台能力需要）；0x0300/0x0320 = USB 3.x。
- Configuration bmAttributes：D7 必须 1，D6 Self-powered，D5 Remote Wakeup；bMaxPower 单位 2 mA（USB 2.0）/ 8 mA（SS）。
- Endpoint bmAttributes bit1:0：00 Control / 01 Isochronous / 10 Bulk / 11 Interrupt；同步端点 bit3:2 同步类型（异步/自适应/同步），bit5:4 用途（数据/反馈/隐式反馈）。
- USB 2.0 spec Table 9-8 / §5.5.3 与 USB 3.2 spec §9.6.1（Table 9-11）对 bMaxPacketSize0 的编码不同，读描述符时必须先看 bcdUSB 与当前速率，不能把 0x09 当成 9 字节。
"""),
dict(id="07-enumeration-requests", title="枚举流程、Setup 包与标准请求", topic="core", level="进阶",
 keywords=["enumeration 枚举","setup packet","bmRequestType","GET_DESCRIPTOR","SET_ADDRESS","SET_CONFIGURATION","SET_INTERFACE","CLEAR_FEATURE","ENDPOINT_HALT","ZLP","composite","class request","vendor request"],
 sources=["10-树干-USB核心/08-枚举流程与标准请求.md"],
 specs=["USB 2.0 Specification §9.3–9.4"],
 related=["06-descriptors","50-debug-troubleshooting","43-device-firmware"],
 facts=r"""
Setup 包（8 B，SETUP + DATA0）：bmRequestType(1) bRequest(1) wValue(2) wIndex(2) wLength(2)。
bmRequestType：D7 方向（0 OUT/1 IN）；D6:5 类型（0 Standard/1 Class/2 Vendor）；D4:0 接收者（0 Device/1 Interface/2 Endpoint/3 Other）。

| bRequest | 名称 | 典型 bmRequestType | wValue | wIndex | wLength |
|---|---|---|---|---|---|
| 0x00 | GET_STATUS | 0x80/0x81/0x82 | 0 | 0/接口/端点 | 2 |
| 0x01 | CLEAR_FEATURE | 0x00/0x01/0x02 | 特征选择子 | 0/接口/端点 | 0 |
| 0x03 | SET_FEATURE | 0x00/0x01/0x02 | 特征选择子 | 0/接口/端点（TEST_MODE 高字节为测试号） | 0 |
| 0x05 | SET_ADDRESS | 0x00 | 地址 1–127 | 0 | 0 |
| 0x06 | GET_DESCRIPTOR | 0x80（类描述符如 HID Report 为 0x81） | 类型<<8 \| 索引 | 0 或 LANGID | 长度 |
| 0x07 | SET_DESCRIPTOR | 0x00 | 类型<<8 \| 索引 | 0 或 LANGID | 长度 |
| 0x08 | GET_CONFIGURATION | 0x80 | 0 | 0 | 1 |
| 0x09 | SET_CONFIGURATION | 0x00 | 配置值 | 0 | 0 |
| 0x0A | GET_INTERFACE | 0x81 | 0 | 接口 | 1 |
| 0x0B | SET_INTERFACE | 0x01 | 备用设置 | 接口 | 0 |
| 0x0C | SYNCH_FRAME | 0x82 | 0 | 端点 | 2 |
| 0x30 / 0x31 | SET_SEL / SET_ISOCH_DELAY | 0x00 | | | USB 3.x |

特征选择子：0 ENDPOINT_HALT（端点）、1 DEVICE_REMOTE_WAKEUP（设备）、2 TEST_MODE（设备）；USB 3.x 另有 U1_ENABLE(48)、U2_ENABLE(49)、FUNCTION_SUSPEND(0，接口)。

枚举顺序（Windows 典型）：端口复位 → [地址 0] GET_DESCRIPTOR(Device, 64) → 再次复位 → SET_ADDRESS(n) → GET_DESCRIPTOR(Device, 18) → GET_DESCRIPTOR(Config, 9) → GET_DESCRIPTOR(Config, wTotalLength) → 字符串（LANGID、序列号、产品名）→ [可选 BOS / MS OS 描述符] → SET_CONFIGURATION(1) → 类驱动加载。Linux 首次读取通常也是 64 字节。

固件规则：复位后 10 ms 内可在地址 0 响应；SET_ADDRESS 在 Status 阶段完成后才生效；GET_DESCRIPTOR 按 min(wLength, 实际长度) 返回；返回长度 < wLength 且为 wMaxPacketSize0 整数倍时补 ZLP；不支持的请求回 STALL（控制端点 STALL 在下一个 SETUP 自动清除）。
"""),
dict(id="08-power-management", title="电源管理：挂起、远程唤醒、LPM、U1/U2/U3", topic="core", level="进阶",
 keywords=["suspend 挂起","resume","remote wakeup 远程唤醒","selective suspend 选择性挂起","LPM","L1","L2","U0","U1","U2","U3","unit load","bMaxPower"],
 sources=["10-树干-USB核心/10-电源管理与挂起唤醒.md"],
 specs=["USB 2.0 Specification §7.1.7.6, §9.2.5","USB 2.0 LPM ECN","USB 3.2 Specification ch.7"],
 related=["06-descriptors","21-charging-bc12-otg","30-usb3-superspeed"],
 facts=r"""
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
"""),
dict(id="09-errors-testmode", title="错误处理、可靠性、Test Mode 与调试模式", topic="core", level="深入",
 keywords=["CRC","retry 三次重试","STALL","babble","timeout","toggle resync","PING/NYET","TEST_MODE","Test_J","Test_K","Test_SE0_NAK","Test_Packet","debug class"],
 sources=["10-树干-USB核心/11-错误处理与可靠性.md","10-树干-USB核心/12-TestMode与调试模式.md"],
 specs=["USB 2.0 Specification §7.1.20, §8.6, §9.4.9"],
 related=["04-packets-transactions","51-compliance-security"],
 facts=r"""
- 主机控制器对同一事务连续 3 次错误（CRC/超时/位填充错误）后向软件报告。
- STALL：功能性停止。控制端点 STALL 在下一个 SETUP 自动清除；批量/中断端点需 CLEAR_FEATURE(ENDPOINT_HALT)，同时 toggle 复位为 DATA0（主机和设备都要复位，否则数据错位）。
- Babble：设备在帧尾（EOF1 之后）仍在发送，Hub 禁用该端口。
- TEST_MODE 选择子（SET_FEATURE(TEST_MODE)，wIndex 高字节）：0x01 Test_J、0x02 Test_K、0x03 Test_SE0_NAK、0x04 Test_Packet、0x05 Test_Force_Enable；进入后需断电/复位退出。
"""),
dict(id="10-class-index", title="设备类代码索引与驱动映射", topic="class", level="入门",
 keywords=["class code 类代码","bDeviceClass","bInterfaceClass","0x03 HID","0x08 MSC","0x0E UVC","0x01 Audio","0x02 CDC","0xEF misc","0xFF vendor","0xE0 wireless"],
 sources=["20-枝干-设备类协议/00-设备类索引.md"],
 specs=["USB-IF Defined Class Codes"],
 related=["11-hid-core","14-cdc","15-msc","16-uvc","17-uac","18-other-classes-a","19-other-classes-b"],
 facts=r"""
| 类代码 | 类 | 使用层级 | Windows 内置驱动 | Linux 驱动 |
|---|---|---|---|---|
| 0x00 | 按接口定义 | Device | — | — |
| 0x01 | Audio (UAC) | Interface | usbaudio.sys / usbaudio2.sys | snd-usb-audio |
| 0x02 | CDC Control | Both | usbser.sys / UsbNcm.sys | cdc_acm / cdc_ether / cdc_ncm |
| 0x03 | HID | Interface | hidusb.sys + hidclass.sys | usbhid (+hidraw) |
| 0x05 | Physical | Interface | — | — |
| 0x06 | Still Image (PTP/MTP) | Interface | WPD (WpdMtp) | 用户态 libmtp/libgphoto2 |
| 0x07 | Printer | Interface | usbprint.sys | usblp |
| 0x08 | Mass Storage | Interface | usbstor.sys / uaspstor.sys | usb-storage / uas |
| 0x09 | Hub | Device | usbhub.sys / usbhub3.sys | hub (usbcore) |
| 0x0A | CDC Data | Interface | (同 CDC) | |
| 0x0B | Smart Card (CCID) | Interface | usbccid / WUDFUsbccidDriver | pcscd + libccid |
| 0x0D | Content Security | Interface | | |
| 0x0E | Video (UVC) | Interface | usbvideo.sys | uvcvideo |
| 0x0F | Personal Healthcare (PHDC) | Interface | | |
| 0x10 | Audio/Video Devices | Interface | | |
| 0x11 | Billboard | Device | | |
| 0x12 | USB Type-C Bridge | Interface | | |
| 0x3C | I3C | Interface | | |
| 0xDC | Diagnostic | Both | | |
| 0xE0 | Wireless Controller（Bluetooth 0xE0/0x01/0x01） | Interface | BthUsb.sys | btusb |
| 0xEF | Miscellaneous（0xEF/0x02/0x01 = IAD 复合） | Both | usbccgp.sys | usbcore |
| 0xFE | Application Specific（0x01 DFU, 0x02 IrDA, 0x03 USBTMC） | Interface | | usbtmc |
| 0xFF | Vendor Specific | Both | WinUSB / 厂商驱动 | libusb / 厂商驱动 |
"""),
dict(id="11-hid-core", title="HID 核心：类描述符、报告描述符 Item、Usage、类请求", topic="class/hid", level="进阶",
 keywords=["HID","report descriptor 报告描述符","item","Usage Page","Usage","Collection","Report ID","Input/Output/Feature report","GET_REPORT","SET_REPORT","SET_IDLE","SET_PROTOCOL","boot protocol","HidD_GetFeature","top-level collection"],
 sources=[H+"00-HID概述与定位.md",H+"01-HID描述符.md",H+"02-报告描述符与Item编码.md",H+"03-Usage体系与集合.md",H+"04-传输与类特定请求.md"],
 specs=["Device Class Definition for HID 1.11","HID Usage Tables (HUT)"],
 related=["12-hid-devices","13-hid-spec-appendix","41-windows-driver","60-usb-wireless-intersection"],
 facts=r"""
接口：bInterfaceClass=0x03；bInterfaceSubClass 0x00 无 Boot / 0x01 Boot；bInterfaceProtocol 0x01 键盘 / 0x02 鼠标（仅 SubClass=1 有意义）。端点：Interrupt IN 必需，Interrupt OUT 可选（无则 Output 报告走 SET_REPORT）。

HID 描述符（0x21，9 B 起）：bLength, bDescriptorType=0x21, bcdHID(2)=0x0111, bCountryCode(1), bNumDescriptors(1), [bDescriptorType(1)=0x22, wDescriptorLength(2)]×N。报告描述符由 GET_DESCRIPTOR（bmRequestType=0x81, wValue=0x2200, wIndex=接口号）读取。

短 Item 前缀字节：bTag[7:4] | bType[3:2]（0 Main/1 Global/2 Local）| bSize[1:0]（0/1/2/4 字节）。长 Item 前缀 0xFE。

| 类型 | Item | 前缀（bSize=1 时） |
|---|---|---|
| Main | Input / Output / Feature | 0x81 / 0x91 / 0xB1 |
| Main | Collection / End Collection | 0xA1 / 0xC0 |
| Global | Usage Page | 0x05 |
| Global | Logical Minimum / Maximum | 0x15 / 0x25 |
| Global | Physical Minimum / Maximum | 0x35 / 0x45 |
| Global | Unit Exponent / Unit | 0x55 / 0x65 |
| Global | Report Size / Report ID / Report Count | 0x75 / 0x85 / 0x95 |
| Global | Push / Pop | 0xA4 / 0xB4 |
| Local | Usage / Usage Minimum / Usage Maximum | 0x09 / 0x19 / 0x29 |
| Local | Designator / String Index / Delimiter | 0x39 / 0x79 / 0xA9 |

Main Item 数据位：bit0 Data(0)/Constant(1)，bit1 Array(0)/Variable(1)，bit2 Absolute(0)/Relative(1)，bit3 No Wrap/Wrap，bit4 Linear/Nonlinear，bit5 Preferred State/No Preferred，bit6 No Null/Null State，bit7 Non Volatile/Volatile（Input 保留），bit8 Bit Field/Buffered Bytes。
Collection 类型：0x00 Physical、0x01 Application、0x02 Logical、0x03 Report、0x04 Named Array、0x05 Usage Switch、0x06 Usage Modifier。

常用 Usage Page：0x01 Generic Desktop（0x02 Mouse, 0x04 Joystick, 0x05 Gamepad, 0x06 Keyboard, 0x30 X, 0x31 Y, 0x38 Wheel）、0x07 Keyboard/Keypad、0x08 LED、0x09 Button、0x0C Consumer（0xE9 Vol+, 0xEA Vol−, 0xCD Play/Pause, 0x238 AC Pan）、0x0D Digitizer、0x0F PID（力反馈）、0x20 Sensors、0xFF00–0xFFFF Vendor-defined。

类请求（Setup）：

| bRequest | 名称 | bmRequestType | wValue | wIndex | 数据 |
|---|---|---|---|---|---|
| 0x01 | GET_REPORT | 0xA1 | 报告类型<<8 \| Report ID（1 Input, 2 Output, 3 Feature） | 接口 | 报告 |
| 0x02 | GET_IDLE | 0xA1 | 0<<8 \| Report ID | 接口 | 1 B |
| 0x03 | GET_PROTOCOL | 0xA1 | 0 | 接口 | 1 B（0 Boot, 1 Report） |
| 0x09 | SET_REPORT | 0x21 | 同 GET_REPORT | 接口 | 报告 |
| 0x0A | SET_IDLE | 0x21 | Duration(4 ms 单位)<<8 \| Report ID | 接口 | 无 |
| 0x0B | SET_PROTOCOL | 0x21 | 0 Boot / 1 Report | 接口 | 无 |

- Boot 设备必须支持 GET_REPORT(Input)、GET/SET_PROTOCOL；设备复位后默认 Report 协议。
- 有 Report ID 时每个报告首字节为 ID；无 Report ID 时 Input/Output/Feature 每种类型各只有一个报告（Windows API 缓冲区首字节仍须为 0）。
- Windows：hidclass.sys 按顶层集合（Top-Level Collection, Application Collection）创建 HID 设备接口；kbdhid.sys / mouhid.sys 独占 Keyboard/Mouse TLC（用户态无法读取其 Input 报告），厂商配置通道通常使用 Usage Page 0xFF00+ 的独立 TLC。API：HidD_GetFeature / HidD_SetFeature（EP0 Feature）、HidD_GetInputReport / HidD_SetOutputReport（EP0）、ReadFile（中断 IN 缓冲）/ WriteFile（中断 OUT，若无则 SET_REPORT）、HidP_GetCaps（*ReportByteLength 含 Report ID 字节）、HidD_SetNumInputBuffers（默认 32，可调至 512）。
"""),
dict(id="12-hid-devices", title="HID 典型设备：键盘、鼠标、消费控制、手柄、触控、跨传输、完整描述符", topic="class/hid", level="进阶",
 keywords=["boot keyboard report","NKRO","modifier","boot mouse","polling rate","consumer control","gamepad","digitizer","precision touchpad","HID over I2C","HOGP","report descriptor example"],
 sources=[H+"05-键盘详解.md",H+"06-鼠标详解.md",H+"07-消费控制与多媒体.md",H+"08-游戏手柄与摇杆.md",H+"09-触摸屏触摸板与数字化仪.md",H+"10-HID跨传输I2C与BLE.md",H+"11-实战完整报告描述符.md"],
 specs=["HID 1.11 Appendix B (Boot)","HID Usage Tables","HID over I2C 1.0","HOGP 1.0","Windows Precision Touchpad"],
 related=["11-hid-core","13-hid-spec-appendix","60-usb-wireless-intersection"],
 facts=r"""
- Boot 键盘 Input 报告 8 B：byte0 修饰键位图（bit0 LCtrl, 1 LShift, 2 LAlt, 3 LGUI, 4 RCtrl, 5 RShift, 6 RAlt, 7 RGUI）、byte1 保留、byte2–7 最多 6 个键码（6KRO，Usage Page 0x07；0x01 = ErrorRollOver）。Output 报告 1 B LED：bit0 NumLock, bit1 CapsLock, bit2 ScrollLock, bit3 Compose, bit4 Kana。
- Boot 鼠标 Input 报告 ≥3 B：byte0 按键位（bit0 左, 1 右, 2 中），byte1 X、byte2 Y（int8 相对），可选 byte3 滚轮。
- 回报率：FS 中断端点 bInterval=1 → 1000 Hz（FS 上限）；HS 中断端点 bInterval=1 → 125 µs → 8000 Hz，bInterval=2 → 4000 Hz，bInterval=4 → 1000 Hz。
- NKRO：用位图式报告（Usage Min 0x00–Max 0xE7 的 Variable 字段）替代 6 键数组。
"""),
dict(id="13-hid-spec-appendix", title="HID 规范级附录（全表）", topic="class/hid", level="深入",
 keywords=["HID item table","usage tables","unit encoding","HID spec appendix","PID force feedback","sensor usages"],
 sources=[H+"12-HID规范级附录.md"],
 specs=["Device Class Definition for HID 1.11","HID Usage Tables"],
 related=["11-hid-core","12-hid-devices"], facts=""),
dict(id="14-cdc", title="CDC：ACM 虚拟串口、ECM/NCM/RNDIS 网络、请求与通知全表", topic="class/cdc", level="进阶",
 keywords=["CDC","ACM","virtual COM","SET_LINE_CODING","SET_CONTROL_LINE_STATE","SERIAL_STATE","ECM","NCM","RNDIS","functional descriptor","union descriptor"],
 sources=["20-枝干-设备类协议/CDC-通信设备类/00-CDC概述.md","20-枝干-设备类协议/CDC-通信设备类/01-虚拟串口ACM.md","20-枝干-设备类协议/CDC-通信设备类/02-网络子类ECM-NCM-RNDIS.md","20-枝干-设备类协议/CDC-通信设备类/03-CDC规范级-请求与通知全表.md"],
 specs=["CDC 1.2","PSTN 1.2 (ACM)","ECM 1.2","NCM 1.0"],
 related=["06-descriptors","10-class-index","43-device-firmware"],
 facts=r"""
- 结构：Communication Interface（类 0x02，子类 0x02 ACM / 0x06 ECM / 0x0D NCM，含 Interrupt IN 通知端点）+ Data Interface（类 0x0A，Bulk IN + Bulk OUT）；用 IAD（0xEF/0x02/0x01）或 Union Functional Descriptor 绑定。
- 功能描述符（CS_INTERFACE 0x24）子类型：0x00 Header、0x01 Call Management、0x02 ACM、0x06 Union、0x0F Ethernet Networking、0x1A NCM。
- ACM 请求：SET_LINE_CODING 0x20（bmRequestType 0x21，7 B：dwDTERate(4) bCharFormat(1: 0=1, 1=1.5, 2=2 停止位) bParityType(1: 0 None,1 Odd,2 Even,3 Mark,4 Space) bDataBits(1)）、GET_LINE_CODING 0x21（0xA1）、SET_CONTROL_LINE_STATE 0x22（wValue bit0 DTR, bit1 RTS）、SEND_BREAK 0x23。通知 SERIAL_STATE 0x20（2 B 位图：DCD, DSR, Break, Ring, Framing, Parity, Overrun）。
- 波特率对纯 USB 虚拟串口无物理意义，仅 USB-UART 桥使用。
"""),
dict(id="15-msc", title="MSC：BOT、CBW/CSW、SCSI 命令与 Sense 全表", topic="class/msc", level="进阶",
 keywords=["mass storage","BOT","bulk-only","CBW","CSW","SCSI","UFI","UAS","GET_MAX_LUN","READ(10)","REQUEST SENSE","sense key"],
 sources=["20-枝干-设备类协议/MSC-大容量存储/00-MSC概述与BOT.md","20-枝干-设备类协议/MSC-大容量存储/01-SCSI命令与UFI.md","20-枝干-设备类协议/MSC-大容量存储/02-SCSI操作码与Sense全表.md"],
 specs=["MSC Class Overview 1.4","MSC BOT 1.0","UAS 1.0","SPC/SBC (T10)"],
 related=["10-class-index","30-usb3-superspeed"],
 facts=r"""
- 接口：class 0x08，subclass 0x06 SCSI transparent（0x04 UFI 软驱），protocol 0x50 BOT / 0x62 UAS / 0x00 CBI。
- CBW 31 B：dCBWSignature 0x43425355 ("USBC")、dCBWTag、dCBWDataTransferLength、bmCBWFlags（bit7 1=IN）、bCBWLUN、bCBWCBLength(1–16)、CBWCB[16]。
- CSW 13 B：dCSWSignature 0x53425355 ("USBS")、dCSWTag（回显）、dCSWDataResidue、bCSWStatus（0 Passed, 1 Failed, 2 Phase Error）。
- 类请求：Bulk-Only Mass Storage Reset 0xFF（0x21）、Get Max LUN 0xFE（0xA1，返回最大 LUN 号，0 = 单 LUN）。
- Phase Error 恢复：Reset Recovery = BOMS Reset + 对两个批量端点 CLEAR_FEATURE(HALT)。
"""),
dict(id="16-uvc", title="UVC：视频类控制、格式、Probe/Commit 全表", topic="class/uvc", level="进阶",
 keywords=["UVC","VideoControl","VideoStreaming","Camera Terminal","Processing Unit","Extension Unit","probe commit","payload header","MJPEG","YUY2","H.264"],
 sources=["20-枝干-设备类协议/Video-UVC/00-UVC详解.md","20-枝干-设备类协议/Video-UVC/01-UVC规范级-控制与格式全表.md"],
 specs=["UVC 1.5"], related=["17-uac","05-transfer-types-bandwidth"],
 facts=r"""
- 接口：class 0x0E；subclass 0x01 VideoControl、0x02 VideoStreaming、0x03 Interface Collection（IAD 用）。
- 类请求：SET_CUR 0x01、GET_CUR 0x81、GET_MIN 0x82、GET_MAX 0x83、GET_RES 0x84、GET_LEN 0x85、GET_INFO 0x86、GET_DEF 0x87。
- 开流：VS_PROBE_CONTROL 协商（格式/帧/间隔/dwMaxPayloadTransferSize）→ VS_COMMIT_CONTROL → SET_INTERFACE 到带同步端点且带宽足够的 alt setting（批量流无需切换）。
- 负载头 Payload Header：bHeaderLength、bmHeaderInfo（bit0 FID 帧翻转, bit1 EOF, bit2 PTS, bit3 SCR, bit6 ERR, bit7 EOH）。
"""),
dict(id="17-uac", title="UAC：音频类 1.0/2.0/3.0、实体与请求全表", topic="class/uac", level="进阶",
 keywords=["UAC","UAC1","UAC2","UAC3","AudioControl","AudioStreaming","Feature Unit","Clock Source","feedback endpoint","asynchronous","sample rate"],
 sources=["20-枝干-设备类协议/Audio-UAC/00-UAC概述.md","20-枝干-设备类协议/Audio-UAC/01-UAC1.0详解.md","20-枝干-设备类协议/Audio-UAC/02-UAC2与UAC3.md","20-枝干-设备类协议/Audio-UAC/03-UAC规范级-实体与请求全表.md"],
 specs=["USB Audio 1.0","USB Audio 2.0","USB Audio 3.0"], related=["16-uvc","05-transfer-types-bandwidth"],
 facts=r"""
- 接口：class 0x01；subclass 0x01 AudioControl、0x02 AudioStreaming、0x03 MIDIStreaming；UAC2 bInterfaceProtocol 0x20（IP_VERSION_02_00），UAC3 0x30。
- 同步模式：Asynchronous（设备时钟，需反馈端点）、Adaptive（设备跟随主机数据速率）、Synchronous（同步于 SOF）。反馈值格式：FS 10.14（3 B），HS 16.16（4 B），单位 样本/帧或样本/微帧。
- UAC2 增加 Clock Source/Selector/Multiplier 实体、HS 支持、CUR/RANGE 请求（0x01 CUR, 0x02 RANGE）；Windows 10 1703+ 内置 usbaudio2.sys。
"""),
dict(id="18-other-classes-a", title="其他设备类 A：DFU、CCID、PTP/MTP、Printer", topic="class/other", level="进阶",
 keywords=["DFU","DFU_DNLOAD","dfuIDLE","CCID","APDU","PC_to_RDR","PTP","MTP","printer class","GET_DEVICE_ID","IEEE 1284"],
 sources=[O+"01-DFU固件升级.md",O+"02-CCID智能卡.md",O+"03-PTP与MTP.md",O+"04-Printer打印机类.md"],
 specs=["DFU 1.1","CCID 1.1","PIMA 15740 (PTP)","MTP 1.1","USB Printer 1.1"], related=["10-class-index","19-other-classes-b"],
 facts=r"""
- DFU：接口 0xFE/0x01，protocol 0x01 运行时 / 0x02 DFU 模式。请求：DETACH 0x00、DNLOAD 0x01、UPLOAD 0x02、GETSTATUS 0x03、CLRSTATUS 0x04、GETSTATE 0x05、ABORT 0x06。状态：0 appIDLE、1 appDETACH、2 dfuIDLE、3 dfuDNLOAD-SYNC、4 dfuDNBUSY、5 dfuDNLOAD-IDLE、6 dfuMANIFEST-SYNC、7 dfuMANIFEST、8 dfuMANIFEST-WAIT-RESET、9 dfuUPLOAD-IDLE、10 dfuERROR。
- CCID：class 0x0B；Bulk OUT 发 PC_to_RDR_* 消息，Bulk IN 回 RDR_to_PC_*，Interrupt IN 报插卡/拔卡。
- Printer：class 0x07，protocol 0x01 单向 / 0x02 双向 / 0x03 IEEE 1284.4；请求 GET_DEVICE_ID 0x00、GET_PORT_STATUS 0x01、SOFT_RESET 0x02。
"""),
dict(id="19-other-classes-b", title="其他设备类 B：蓝牙 HCI、WebUSB/厂商类、MIDI、USBTMC、长尾类、AV、PHDC", topic="class/other", level="进阶",
 keywords=["Bluetooth HCI over USB","btusb","WebUSB","MS OS 2.0 descriptor","WinUSB compatible ID","vendor class","MIDI","USB-MIDI event packet","USBTMC","SCPI","Billboard","I3C","PHDC","AV class"],
 sources=[O+"05-蓝牙控制器类-HCIoverUSB.md",O+"06-WebUSB与厂商自定义类.md",O+"07-MIDI类.md",O+"08-USBTMC测试测量类.md",O+"09-长尾设备类-AV-Billboard-Healthcare-I3C.md",O+"10-AV设备类详解.md",O+"11-PHDC健康医疗类.md"],
 specs=["Bluetooth Core Vol 4 Part B (USB Transport)","WebUSB (WICG)","Microsoft OS 2.0 Descriptors","USB MIDI 1.0/2.0","USBTMC 1.0","Billboard 1.2","PHDC 1.0"],
 related=["10-class-index","41-windows-driver","42-linux-macos-libusb","60-usb-wireless-intersection"],
 facts=r"""
- 蓝牙控制器：0xE0/0x01/0x01。HCI Command → 控制端点（bmRequestType 0x20 类请求，bRequest 0x00）；HCI Event → Interrupt IN；ACL → Bulk IN/OUT；SCO/eSCO → Isochronous（接口 1 多个 alt setting）。
- MS OS 2.0：BOS 中 Platform Capability UUID {D8DD60DF-4589-4CC7-9CD2-659D9E648A9F}，给出 vendor code 与描述符集长度；主机发厂商请求（bRequest=vendor code, wIndex=0x07 MS_OS_20_DESCRIPTOR_INDEX）取描述符集；其中 Compatible ID "WINUSB" 让 Windows 自动绑定 winusb.sys（免 INF）；Registry Property 可写 DeviceInterfaceGUIDs。
- WebUSB：BOS Platform Capability UUID {3408B638-09A9-47A0-8BFD-A0768815B665}；GET_URL（wIndex=2）返回 Landing Page。
"""),
dict(id="20-connectors-typec", title="连接器演进与 USB Type-C（含 CC 状态机与时序）", topic="phy/typec", level="进阶",
 keywords=["Type-A","Micro-B","Type-C","CC","Rp","Rd","Ra","VCONN","DRP","orientation 方向","SBU","Try.SRC","tCCDebounce","accessory mode"],
 sources=["30-枝干-接口与供电/01-接口形态演进.md","30-枝干-接口与供电/02-USBType-C详解.md","30-枝干-接口与供电/09-TypeC规范级-状态机与CC时序.md"],
 specs=["USB Type-C Cable and Connector Specification 2.x"],
 related=["21-charging-bc12-otg","22-usb-pd","23-altmode-emarker"],
 facts=r"""
| 项 | 值 |
|---|---|
| 针脚 | 24：A/B 两排各 GND, TX1/2±, VBUS, CC1/CC2(VCONN), D+/D−, SBU1/2, RX±；线缆只连一组 D+/D− |
| Sink 下拉 Rd | 5.1 kΩ |
| 电缆 Ra | 800 Ω–1.2 kΩ（需要 VCONN 的有源线缆/E-marker） |
| Rp 广播电流（上拉到 5 V） | Default USB 56 kΩ；1.5 A 22 kΩ；3.0 A 10 kΩ（也可用电流源 80/180/330 µA） |
| tCCDebounce | 100–200 ms |
| 角色 | DFP/UFP（数据），Source/Sink（电源），DRP/DRD（双角色） |
| 方向检测 | 检测到 Rd 的 CC 引脚决定插头朝向与高速通道复用 |
| 附件模式 | Rd/Rd = Debug Accessory；Ra/Ra = Audio Adapter Accessory |
"""),
dict(id="21-charging-bc12-otg", title="充电：BC 1.2、专有快充；OTG 与角色切换 HNP/SRP", topic="power", level="进阶",
 keywords=["BC1.2","SDP","CDP","DCP","primary detection","secondary detection","QC","快充","OTG","ID pin","HNP","SRP","ADP"],
 sources=["30-枝干-接口与供电/03-BC1.2与专有快充.md","30-枝干-接口与供电/06-OTG与角色切换-HNP-SRP.md"],
 specs=["Battery Charging 1.2","USB OTG and Embedded Host Supplement 2.0"], related=["20-connectors-typec","22-usb-pd","08-power-management"],
 facts=r"""
| 端口 | 识别 | 电流 |
|---|---|---|
| SDP Standard Downstream Port | 主检测无响应 | 未配置 100 mA / 配置后 500 mA（USB 3.x 900 mA） |
| CDP Charging Downstream Port | 主检测有响应，次检测区分 | 1.5 A + 数据 |
| DCP Dedicated Charging Port | D+/D− 短接（≤200 Ω） | 1.5 A，无数据 |
- BC 1.2 主检测：设备在 D+ 加 VDP_SRC(0.6 V)，检测 D− 上是否出现电压。
- OTG（Micro-AB）：ID 引脚接地 = A 设备（默认主机）；HNP 主机角色交换；SRP 会话请求。Type-C 时代由 CC（DRP/DR_Swap）替代。
"""),
dict(id="22-usb-pd", title="USB Power Delivery：协议、状态机与消息全表", topic="power/pd", level="深入",
 keywords=["USB PD","BMC","SOP","GoodCRC","Source_Capabilities","Request","Accept","PS_RDY","PDO","RDO","PPS","AVS","EPR","SPR","VDM","PR_Swap","DR_Swap","Hard Reset","MessageID"],
 sources=["30-枝干-接口与供电/04-USBPD协议.md","30-枝干-接口与供电/07-USBPD深入-状态机与消息全表.md","30-枝干-接口与供电/08-USBPD消息全表.md"],
 specs=["USB Power Delivery Specification Rev 3.2"], related=["20-connectors-typec","23-altmode-emarker","21-charging-bc12-otg"],
 facts=r"""
- 物理层：CC 线 BMC 编码，300 kbit/s ±10%；4b5b 编码；包 = Preamble + SOP* + Header(16 bit) + 0–7 个 32 bit Data Object（扩展消息更长）+ CRC32 + EOP。
- SOP* 目标：SOP（对端端口）、SOP'（线缆近端 E-marker）、SOP''（线缆远端）、SOP'_Debug、SOP''_Debug。
- Message Header：bit15 Extended、14:12 Number of Data Objects、11:9 MessageID、8 Port Power Role / Cable Plug、7:6 Spec Revision（00 1.0, 01 2.0, 10 3.x）、5 Port Data Role、4:0 Message Type。
- 每条消息需在 tReceive（约 1 ms）内收到 GoodCRC，否则重传（nRetryCount=2）。
- 显式合同：Source_Capabilities → Request → Accept → PS_RDY。
- PDO 类型（bit31:30）：00 Fixed、01 Battery、10 Variable、11 APDO（bit29:28：00 SPR PPS、01 EPR AVS、10 SPR AVS）。Fixed PDO：电压 50 mV 单位（bit19:10）、最大电流 10 mA 单位（bit9:0）。
- 功率范围：SPR ≤ 100 W（5/9/15/20 V，>3 A 需 5 A E-marker 线）；EPR 28/36/48 V，≤ 240 W（EPR 模式需 EPR_Mode 进入流程与 EPR 线缆）。PPS 电压步进 20 mV、电流步进 50 mA。
- 缓存状态仍不一致：`80-参考资料/README.md` 与 `skills/usb-spec-lookup/SKILL.md` 已登记 `usb-core/USB-PD-3.2-V1.2.zip`；`08-USBPD消息全表.md` 开篇仍写「PD 规范本体未缓存」，同页文末又写已缓存。`90-附录/03-时序参数全表.md` §4 来源说明同样仍写未缓存。
"""),
dict(id="23-altmode-emarker", title="Alternate Mode、Structured VDM 与 E-marker", topic="power/pd", level="深入",
 keywords=["Alt Mode","DisplayPort Alt Mode","SVID","0xFF01","Discover Identity","Discover SVIDs","Discover Modes","Enter Mode","E-marker","cable VDO","Thunderbolt alt mode","Billboard"],
 sources=["30-枝干-接口与供电/05-AlternateMode与E-marker.md"],
 specs=["USB PD 3.2 §6.4.4","VESA DisplayPort Alt Mode 2.x","USB Type-C 2.x"], related=["22-usb-pd","20-connectors-typec","19-other-classes-b"],
 facts=r"""
- Structured VDM 命令：1 Discover Identity、2 Discover SVIDs、3 Discover Modes、4 Enter Mode、5 Exit Mode、6 Attention；16–31 SVID 专用（DP：16 DP Status Update、17 DP Configure）。
- SVID：0xFF00 = PD SID（标准）；0xFF01 = DisplayPort；0x8087 = Intel Thunderbolt 3。
- Alt Mode 进入失败时设备应枚举 Billboard 类（0x11）向用户报告。
- E-marker：线缆通过 SOP' 回应 Discover Identity，Cable VDO 声明最大电流（3 A/5 A）、最高速率、EPR 能力；5 A 与 EPR 线缆必须有 E-marker。
"""),
dict(id="30-usb3-superspeed", title="USB 3.x SuperSpeed：包格式、LTSSM、定时器", topic="speed/usb3", level="深入",
 keywords=["SuperSpeed","LTSSM","U0","U1","U2","U3","Polling","Recovery","LMP","TP","DP","ITP","ERDY","NRDY","burst","streams","8b/10b","128b/132b","LFPS","SS endpoint companion"],
 sources=["40-枝干-高速演进/01-USB3x与SuperSpeed.md","40-枝干-高速演进/04-USB3x包格式与LTSSM.md","40-枝干-高速演进/06-USB3x规范级-包格式与定时器.md"],
 specs=["USB 3.2 Specification ch.6–8"], related=["31-usb4","08-power-management","15-msc"],
 facts=r"""
- 双单工：SSTX±/SSRX± 独立差分对，与 USB 2.0 D+/D− 并行，两套拓扑同时存在。
- 包类型：LMP（Link Management）、TP（Transaction Packet：ACK, NRDY, ERDY, STATUS, STALL, DEV_NOTIFICATION, PING, PING_RESPONSE）、DP（Data Packet header + payload）、ITP（Isochronous Timestamp）。
- 流控：设备无数据回 NRDY；就绪后主动发 ERDY，主机再调度——消除 USB 2.0 的 NAK 轮询。
- 批量 wMaxPacketSize 固定 1024，SS Endpoint Companion 描述符 bMaxBurst 0–15（1–16 包）；bmAttributes 中 MaxStreams（2^n，UAS 用）。
- LTSSM 状态：SS.Disabled、Rx.Detect、Polling（LFPS/TSEQ/TS1/TS2）、U0、U1、U2、U3、Recovery、Hot Reset、Loopback、Compliance Mode、SS.Inactive。
- LFPS（Low Frequency Periodic Signaling）用于 Polling、U1/U2/U3 退出、Warm Reset。
"""),
dict(id="31-usb4", title="USB4：路由器、隧道、配置空间、DROM、连接管理器", topic="speed/usb4", level="深入",
 keywords=["USB4","router","adapter","tunnel 隧道","path","connection manager","CM","Thunderbolt 3","PCIe tunneling","DP tunneling","USB3 tunneling","DROM","config space","PAM-3","USB4 v2","Gen 4","asymmetric"],
 sources=["40-枝干-高速演进/02-USB4与雷电整合.md","40-枝干-高速演进/05-USB4深入-路由隧道与配置.md","40-枝干-高速演进/07-USB4规范级-配置空间与隧道.md","40-枝干-高速演进/08-USB4-DROM设备ROM规范.md","40-枝干-高速演进/09-USB4-CM指南要点.md"],
 specs=["USB4 Specification v2.0","USB4 Connection Manager Guide","USB4 DROM Specification"], related=["30-usb3-superspeed","22-usb-pd","23-altmode-emarker"],
 facts=r"""
- 基本单元 Router（主机路由器 / 设备路由器），端口称 Adapter：Lane Adapter（物理链路）、Protocol Adapter（USB3 / DP IN/OUT / PCIe Up/Down）、Control Adapter。
- 协议流量封装为 Tunneled Packet，沿 Path 在路由器间转发；USB 2.0 不进隧道，走 Type-C 的 D+/D− 独立线对。
- Connection Manager（软件，Windows 11 内置 USB4 CM；Linux thunderbolt 驱动）通过 Control Packet 读写路由器配置空间，发现拓扑、建立隧道、分配带宽。
- 速率：Gen 2（10 Gbps/lane）、Gen 3（20 Gbps/lane），双 lane 合计 20/40 Gbps；USB4 v2 Gen 4 PAM-3 每 lane 40 Gbps，对称 80 Gbps 或非对称 120/40 Gbps。
- 进入 USB4 经由 Type-C/PD：Discover Identity 后 Enter_USB 消息（PD 3.x）。
- 对普通 USB 外设透明：扩展坞后的设备仍是 USB 2.0/3.x 拓扑。
"""),
dict(id="40-host-controller-os", title="主机控制器栈与操作系统 USB 支持", topic="host", level="进阶",
 keywords=["UHCI","OHCI","EHCI","xHCI","TRB","transfer ring","event ring","doorbell","URB","Windows USB stack","usbxhci","ucx","usbhub3","usbccgp","Linux usbcore","macOS IOUSBHost"],
 sources=["60-枝干-主机侧与实现/01-主机控制器栈全景.md","60-枝干-主机侧与实现/02-操作系统USB支持.md"],
 specs=["xHCI 1.2","EHCI 1.0","OHCI 1.0a","UHCI 1.1"], related=["41-windows-driver","42-linux-macos-libusb"],
 facts=r"""
| 控制器 | 速度 | 说明 |
|---|---|---|
| UHCI（Intel）/ OHCI（Compaq/MS/NS） | LS/FS | USB 1.x |
| EHCI | HS | 需伴随控制器（UHCI/OHCI）处理 FS/LS，或内置 TT 的 rate-matching hub |
| xHCI | LS–SS+ | 所有速度一个控制器；Command Ring / Event Ring / 每端点 Transfer Ring（TRB），Doorbell 寄存器触发；Device Context / Slot |

Windows（8+）USB 3 栈：usbxhci.sys → ucx01000.sys（UCX）→ usbhub3.sys → usbccgp.sys（复合）→ 类驱动（hidusb/usbser/usbstor/uaspstor/usbvideo/usbaudio2/BthUsb）或 winusb.sys。旧 USB 2 栈：usbehci/usbport → usbhub.sys。
Linux：xhci_hcd/ehci_hcd → usbcore（hub 线程、URB）→ 接口驱动；用户态经 usbfs（/dev/bus/usb/BBB/DDD）、hidraw；抓包 usbmon。
macOS：IOUSBHostFamily（IOUSBHostDevice/IOUSBHostInterface），DriverKit USBDriverKit。
"""),
dict(id="41-windows-driver", title="Windows USB 驱动开发：选型、WinUSB、KMDF/UMDF、调试", topic="host/windows", level="深入",
 keywords=["WinUSB","WinUsb_ReadPipe","WinUsb_ControlTransfer","KMDF","UMDF","WDFUSBDEVICE","WDFUSBPIPE","continuous reader","INF","MS OS descriptor","USBView","USBPcap","ETW","code 43","code 10","code 28","HidD_SetFeature","SetupDi"],
 sources=["60-枝干-主机侧与实现/08-WindowsUSB驱动开发.md"],
 specs=["Microsoft Learn: USB driver development","WDF","Microsoft OS 2.0 Descriptors"], related=["40-host-controller-os","11-hid-core","19-other-classes-b","50-debug-troubleshooting"],
 facts=r"""
| 路线 | 层 | 用途 | 限制 |
|---|---|---|---|
| 标准类免驱 | 内置类驱动 | HID / CDC / MSC / UVC / UAC | 受类协议约束 |
| WinUSB | winusb.dll → winusb.sys | 私有批量/中断/控制 | 同一时刻单进程打开；无内核时序保证 |
| UMDF 2.x | WUDFHost.exe | 需安装包/电源策略 | 用户态往返开销 |
| KMDF | 内核 | 低延迟、过滤驱动 | 需签名，崩溃即蓝屏 |

- WinUSB 设备接口 GUID 由 INF 或 MS OS 2.0 Registry Property `DeviceInterfaceGUIDs` 提供；路径用 SetupDiGetClassDevs + SetupDiEnumDeviceInterfaces 获取。
- WinUSB API：WinUsb_Initialize / WinUsb_GetAssociatedInterface / WinUsb_QueryPipe / WinUsb_ReadPipe / WinUsb_WritePipe / WinUsb_ControlTransfer(WINUSB_SETUP_PACKET) / WinUsb_SetPipePolicy（PIPE_TRANSFER_TIMEOUT, RAW_IO, AUTO_CLEAR_STALL）/ WinUsb_ResetPipe / WinUsb_AbortPipe / WinUsb_Free。
- KMDF 对象：WDFUSBDEVICE（WdfUsbTargetDeviceCreateWithParameters）、WDFUSBINTERFACE、WDFUSBPIPE；中断 IN 用 WdfUsbTargetPipeConfigContinuousReader。
- 设备管理器错误码：10 无法启动；28 未安装驱动；43 设备报告问题（常见于枚举/描述符失败，usbhub3 置位）；45 未连接。
- 调试：USBView（拓扑+描述符）、USBPcap + Wireshark（URB 级）、ETW 提供程序 Microsoft-Windows-USB-USBXHCI / USB-UCX / USB-USBHUB3 / USB-USBPORT（用 `logman` 或 WPR 采集）。
"""),
dict(id="42-linux-macos-libusb", title="libusb 用户态访问、Linux Gadget/usbip、macOS 与 Linux 主机开发", topic="host/linux-macos", level="进阶",
 keywords=["libusb","libusb_control_transfer","libusb_bulk_transfer","async transfer","hidapi","Zadig","usbfs","udev","Linux gadget","configfs","FunctionFS","usbip","usbmon","IOKit","DriverKit"],
 sources=["60-枝干-主机侧与实现/04-libusb与用户态访问.md","60-枝干-主机侧与实现/06-实战-libusb主机程序.md","60-枝干-主机侧与实现/07-实战-LinuxGadget与usbip.md","60-枝干-主机侧与实现/09-macOS与Linux主机开发.md"],
 specs=["libusb 1.0 API","Linux kernel USB documentation"], related=["40-host-controller-os","41-windows-driver","43-device-firmware"],
 facts=r"""
- libusb 同步 API：libusb_init → libusb_open_device_with_vid_pid → libusb_detach_kernel_driver（Linux）→ libusb_claim_interface → libusb_control_transfer / libusb_bulk_transfer / libusb_interrupt_transfer → libusb_release_interface → libusb_close → libusb_exit。异步：libusb_alloc_transfer + libusb_submit_transfer + libusb_handle_events。
- Windows 上 libusb 需设备绑定 WinUSB（Zadig、INF 或 MS OS 2.0）；不能访问被 hidclass 占用的 HID 接口——HID 用 hidapi。
- Linux 权限：udev 规则 `SUBSYSTEM=="usb", ATTR{idVendor}=="xxxx", MODE="0666"`；hidraw 节点 `KERNEL=="hidraw*"`。
- Gadget configfs：/sys/kernel/config/usb_gadget/<g>/ 下建 idVendor/idProduct/strings/configs/functions（hid.usb0、acm.usb0、ncm.usb0、mass_storage.usb0、ffs.*），最后把 UDC 名写入 UDC 文件绑定。
"""),
dict(id="43-device-firmware", title="设备端固件栈与 TinyUSB 实战", topic="device/firmware", level="进阶",
 keywords=["TinyUSB","tud_task","tud_descriptor_device_cb","tud_hid_report","tud_hid_set_report_cb","tusb_config.h","DCD","USBD","STM32 USB device library","Zephyr","ZLP","composite firmware"],
 sources=["60-枝干-主机侧与实现/03-设备端固件栈.md","60-枝干-主机侧与实现/05-实战-TinyUSB设备固件.md"],
 specs=["TinyUSB documentation","USB 2.0 ch.9"], related=["07-enumeration-requests","11-hid-core","42-linux-macos-libusb"],
 facts=r"""
- 分层：DCD（设备控制器驱动，ISR）→ USBD 核心（EP0、标准请求、描述符回调）→ 类驱动（HID/CDC/MSC/MIDI/Audio/Vendor/DFU）→ 应用回调。
- TinyUSB 回调：tud_descriptor_device_cb、tud_descriptor_configuration_cb、tud_descriptor_string_cb、tud_hid_descriptor_report_cb、tud_hid_get_report_cb、tud_hid_set_report_cb、tud_mount_cb / tud_umount_cb / tud_suspend_cb / tud_resume_cb；发送 tud_hid_ready() + tud_hid_report(id, buf, len)；主循环 tud_task()；唤醒 tud_remote_wakeup()。
- 配置宏：CFG_TUSB_RHPORT0_MODE / CFG_TUD_ENDPOINT0_SIZE / CFG_TUD_HID / CFG_TUD_HID_EP_BUFSIZE / CFG_TUD_CDC / CFG_TUD_MSC。
- 固件铁律见 [07-enumeration-requests](07-enumeration-requests.md)。
"""),
dict(id="50-debug-troubleshooting", title="协议分析仪、抓包与枚举失败排查", topic="debug", level="进阶",
 keywords=["protocol analyzer","Beagle","Ellisys","USBPcap","usbmon","Wireshark filter usb.","enumeration failure","device descriptor request failed","error -71","EPROTO","code 43","fallback to full speed"],
 sources=["70-枝干-调试测试与安全/01-协议分析仪与抓包.md","70-枝干-调试测试与安全/02-枚举失败排查手册.md"],
 specs=["USB 2.0 ch.9"], related=["07-enumeration-requests","41-windows-driver","42-linux-macos-libusb"],
 facts=r"""
| 工具 | 层级 | 可见 | 不可见 |
|---|---|---|---|
| 硬件分析仪（Total Phase Beagle, Ellisys, Teledyne LeCroy） | 线上包 | 每个包、NAK、Chirp、SOF、时序、速度 | — |
| USBPcap（Windows）/ usbmon（Linux）+ Wireshark | URB | 请求、描述符、完成状态 | NAK 重试、物理层 |
| ETW / dmesg | 栈日志 | 枚举阶段与错误码 | 线上数据 |

症状 → 常见根因：完全无反应 → VBUS、纯充电线、上拉未使能；"设备描述符请求失败"/dmesg `device descriptor read/64, error -71` → 时钟偏差、EP0 未及时响应、bMaxPacketSize0 错；SET_ADDRESS 后失联 → 地址切换时机错；代码 43 / `config 1 has an invalid descriptor` → wTotalLength/bLength/bNumEndpoints 不一致；枚举成功无功能 → 类代码错、端点方向错、缺驱动（代码 28）；时好时坏 → 选择性挂起、供电、线材；HS 降为 FS → Chirp 失败。
Wireshark 过滤：`usb.addr == "1.5.1"`、`usb.transfer_type == 0x01`（中断）、`usb.setup.bRequest == 6`、`usbhid.setup.bRequest == 9`。
"""),
dict(id="51-compliance-security", title="USB-IF 合规认证、合规测试实操与 USB 安全", topic="compliance/security", level="深入",
 keywords=["USB-IF compliance","USBCV","Chapter 9 test","HID test","electrical test","eye diagram","PlugFest","TID","logo","WHQL","HLK","BadUSB","Rubber Ducky","USBGuard","device installation restriction"],
 sources=["70-枝干-调试测试与安全/03-USB-IF合规认证.md","70-枝干-调试测试与安全/04-USB安全与BadUSB.md","70-枝干-调试测试与安全/05-合规测试实操.md"],
 specs=["USB-IF Compliance Program","USB 2.0 Electrical Test Spec","USB4 Compliance"], related=["09-errors-testmode","50-debug-troubleshooting"],
 facts=r"""
- USBCV（USB Command Verifier）：Chapter 9 测试、HID 测试、MSC 测试、Hub 测试；Logo 需 VID（USB-IF 会员或单独购买）与 TID。
- 安全威胁：设备可伪装任意类（HID 注入、BadUSB 固件重编程）；防御：Linux USBGuard 白名单、Windows 组策略"设备安装限制"（按设备 ID/类 GUID）、macOS 配件授权、物理端口管控。
"""),
dict(id="60-usb-wireless-intersection", title="无线与 USB 的交汇：HCI-over-USB、HOGP、Wireless USB/MA-USB 历史", topic="wireless", level="进阶",
 keywords=["HOGP","HID over GATT","HID Service 0x1812","Report Map 0x2A4B","Report 0x2A4D","Protocol Mode 0x2A4E","HCI","btusb","Wireless USB","MA-USB","2.4G dongle"],
 sources=["50-枝干-无线关联/00-无线概览与USB交汇.md","50-枝干-无线关联/99-WirelessUSB与MA-USB历史.md",B+"01-蓝牙体系架构与HCI.md",B+"07-HOGP-HIDoverGATT.md"],
 specs=["HOGP 1.0","HIDS 1.0","Bluetooth Core 6.x Vol 4","MA-USB 1.0"], related=["11-hid-core","19-other-classes-b","61-ble-core"],
 facts=r"""
| USB HID | HOGP（HID Service 0x1812） |
|---|---|
| 报告描述符（GET_DESCRIPTOR 0x22） | Report Map 特征 0x2A4B |
| Input 报告（中断 IN） | Report 特征 0x2A4D Notify + Report Reference 描述符 0x2908（Report ID, 类型 1 Input/2 Output/3 Feature） |
| SET_REPORT / Output | 写 Report 特征（Output/Feature） |
| GET/SET_PROTOCOL | Protocol Mode 0x2A4E（0 Boot, 1 Report） |
| 挂起 | HID Control Point 0x2A4C（0 Suspend, 1 Exit Suspend） |
| HID 描述符 bcdHID 等 | HID Information 0x2A4A |
| Boot 报告 | Boot Keyboard Input 0x2A22 / Output 0x2A32，Boot Mouse Input 0x2A33 |
- 2.4 GHz 私有无线接收器对主机是普通 USB（复合）HID 设备，与蓝牙无关。
- HCI over USB 端点映射见 [19-other-classes-b](19-other-classes-b.md)。
"""),
dict(id="61-ble-core", title="BLE 核心：概述、链路层/物理层、广播与连接、ATT/GATT、GAP、SMP、经典蓝牙对比", topic="wireless/ble", level="进阶",
 keywords=["BLE","link layer","PHY 1M 2M Coded","advertising","connection interval","ATT","GATT","GAP","SMP","pairing","LE Secure Connections","BR/EDR"],
 sources=[B+"00-BLE概述.md",B+"02-链路层与物理层.md",B+"03-广播与连接.md",B+"04-ATT与GATT.md",B+"05-GAP与连接管理.md",B+"06-SMP安全与配对.md",B+"08-经典蓝牙与BLE对比.md"],
 specs=["Bluetooth Core Specification 6.0"], related=["60-usb-wireless-intersection","62-ble-advanced","63-ble-uuid"],
 facts="- 注：USBTree 审计指出 Bluetooth Core 6.1/6.2 尚未覆盖（6.2 新增 HCI USB 等时传输相关内容）。"),
dict(id="62-ble-advanced", title="BLE 进阶：LE Audio/LC3、Mesh、经典 Profile、LLCP、测向与信道探测、RF 参数、A2DP/AVDTP", topic="wireless/ble", level="深入",
 keywords=["LE Audio","LC3","CIS","BIS","Auracast","Mesh","A2DP","AVRCP","HFP","LLCP","AoA","AoD","Channel Sounding","RF parameters","AVDTP","SBC","AAC"],
 sources=[B+"09-LEAudio与LC3.md",B+"10-Mesh网络概述.md",B+"11-经典蓝牙Profile详解.md",B+"12-LLCP控制过程全表.md",B+"13-测向与信道探测.md",B+"14-RF物理层参数全表.md",B+"15-A2DP编解码与AVDTP参数.md"],
 specs=["Bluetooth Core Specification 6.0","LC3 1.0","Mesh Protocol 1.1","A2DP 1.4","AVDTP 1.3"], related=["61-ble-core","63-ble-uuid"], facts=""),
dict(id="63-ble-uuid", title="蓝牙标准 UUID 全表", topic="wireless/ble", level="深入",
 keywords=["UUID","16-bit UUID","service UUID","characteristic UUID","descriptor UUID","assigned numbers"],
 sources=[B+"16-标准UUID全表.md"], specs=["Bluetooth SIG Assigned Numbers"], related=["61-ble-core","60-usb-wireless-intersection"], facts=""),
dict(id="90-quick-reference", title="速查表大全与时序参数全表", topic="reference", level="进阶",
 keywords=["cheat sheet 速查","timing parameters 时序参数","constants","bInterval table","PID table","descriptor types","reset timing","resume timing"],
 sources=["90-附录/02-速查表大全.md","90-附录/03-时序参数全表.md"], specs=["USB 2.0","USB 3.2","Type-C","USB PD"], related=["06-descriptors","07-enumeration-requests","05-transfer-types-bandwidth"],
 facts="- `03-时序参数全表.md` §4 来源说明仍写「未缓存 USB PD 规范原文」，同表 tFirstSourceCap 行又写「PD 3.2 V1.2 已缓存」。以 `80-参考资料/README.md` 的 `usb-core/USB-PD-3.2-V1.2.zip` 为准。"),
dict(id="91-glossary", title="术语表（中英对照）", topic="reference", level="入门",
 keywords=["glossary 术语","terminology","abbreviations 缩写"], sources=["90-附录/01-术语表.md"], specs=[], related=["index"], facts=""),
dict(id="92-spec-references", title="官方规范参考与缓存索引", topic="reference", level="入门",
 keywords=["specifications","usb.org","Bluetooth SIG","spec cache","spec_fetch"], sources=["80-参考资料/README.md","00-知识树总图.md"], specs=[], related=["index"],
 facts="- 注：USBTree `80-参考资料/` 原文 PDF 不随仓库分发（但仍存在于 Git 历史中，见审计报告）；`tools/spec_fetch.sh` 对蓝牙 Core 6.0 勘误表与 HID-Service-1.1 会把登录页/中转页保存为 PDF。"),
]
