---
title: "HID 规范级附录：请求、Usage 与 Item 编码速查"
layer: 枝干/设备类协议
section: HID-人机接口设备
doc-path: 20-枝干-设备类协议/HID-人机接口设备/12-HID规范级附录.md
---
# HID 规范级附录：请求、Usage 与 Item 编码速查

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[HID] → 附录[规范级速查]
> ⬆️ 父节点: [00-HID概述与定位.md](00-HID概述与定位.md)
> 📖 本文是 [04-传输与类特定请求.md](04-传输与类特定请求.md)、[02-报告描述符与Item编码.md](02-报告描述符与Item编码.md)、[03-Usage体系与集合.md](03-Usage体系与集合.md) 的数值级附录：所有表格直接提取自 **Device Class Definition for HID 1.11** 与 **HID Usage Tables 1.3**（缓存于 [../../80-参考资料/README.md](../../80-参考资料/README.md)），只给编号与值，叙述见各详解篇。

## 1. 类特定请求全表（HID 1.11 §7.2）

bRequest 有效值（§7.2 主表）：`0x01 GET_REPORT`（所有设备必备）、`0x02 GET_IDLE`、`0x03 GET_PROTOCOL`（Boot 设备必备）、`0x04~0x08 保留`、`0x09 SET_REPORT`、`0x0A SET_IDLE`、`0x0B SET_PROTOCOL`（Boot 设备必备）。

bmRequestType 只允许两个值：`10100001b (0x81)` = Direction:Device-to-Host / Type:Class / Recipient:Interface；`00100001b (0x21)` = Host-to-Device / Class / Interface。

| bRequest | 代码 | bmRequestType | wValue | wIndex | wLength | Data 阶段 |
|---|---|---|---|---|---|---|
| GET_REPORT (§7.2.1) | 0x01 | 0x81 | Report Type（高字节）+ Report ID（低字节） | 接口号 | 报告长度 | IN：报告内容 |
| GET_IDLE (§7.2.3) | 0x02 | 0x81 | 0（高字节）+ Report ID | 接口号 | 1 | IN：1 字节空闲率 |
| GET_PROTOCOL (§7.2.5) | 0x03 | 0x81 | 0 | 接口号 | 1 | IN：0=Boot 协议，1=Report 协议 |
| SET_REPORT (§7.2.2) | 0x09 | 0x21 | Report Type（高）+ Report ID（低） | 接口号 | 报告长度 | OUT：报告内容 |
| SET_IDLE (§7.2.4) | 0x0A | 0x21 | Duration（高字节）+ Report ID（低字节） | 接口号 | 0 | 无 |
| SET_PROTOCOL (§7.2.6) | 0x0B | 0x21 | 0=Boot 协议，1=Report 协议 | 接口号 | 0 | 无 |

要点：

- **Report Type**（wValue 高字节，GET/SET_REPORT 共用）：`01` Input、`02` Output、`03` Feature、`04~FF` 保留（§7.2.1）。
- Report ID 未使用时 wValue 低字节填 0。
- SET_IDLE 的 Duration：高字节 0 = 永久抑制（仅变化时上报）；非 0 时每单位 = 4 ms，范围 0.004~1.020 s，精度 ±(10% + 2 ms)；Report ID=0 时作用于全部输入报告（§7.2.4）。
- 推荐默认空闲率：键盘 500 ms，鼠标/摇杆无穷（§7.2.4）。
- 上电默认 Report 协议；主机切换前不得假设当前协议（§7.2.6）。
- 描述符类请求 `GET_DESCRIPTOR`：bmRequestType `10000001b (0x81)`，wValue 高字节 `0x21`（HID 描述符）/`0x22`（Report）/`0x23`（Physical），wIndex = 接口号（§7.1.1）。

## 2. bCountryCode 全表（HID 1.11 §6.2.1，Table 后附）

| 代码(十进制) | 国家 | 代码(十进制) | 国家 |
|---|---|---|---|
| 00 | 不支持（多数设备填 0） | 18 | 荷兰 |
| 01 | 阿拉伯 | 19 | 挪威 |
| 02 | 比利时 | 20 | 波斯 |
| 03 | 加拿大双语 | 21 | 波兰 |
| 04 | 加拿大法语 | 22 | 葡萄牙 |
| 05 | 捷克 | 23 | 俄罗斯 |
| 06 | 丹麦 | 24 | 斯洛伐克 |
| 07 | 芬兰 | 25 | 西班牙 |
| 08 | 法国 | 26 | 瑞典 |
| 09 | 德国 | 27 | 瑞士/法语 |
| 10 | 希腊 | 28 | 瑞士/德语 |
| 11 | 希伯来 | 29 | 瑞士 |
| 12 | 匈牙利 | 30 | 中国台湾 |
| 13 | 国际 (ISO) | 31 | 土耳其-Q |
| 14 | 意大利 | 32 | 英国 |
| 15 | 日本 (片假名) | 33 | 美国 |
| 16 | 韩国 | 34 | 南斯拉夫 |
| 17 | 拉丁美洲 | 35~255 | 保留 |

字段描述符布局见 [01-HID描述符.md](01-HID描述符.md)；规范原文：键盘可用它声明键帽语言，其余设备不要求填非 0 值（§6.2.1）。

## 3. Usage Page 完整表（HUT 1.3 §3，Table 3.1，0x00~0xFF 已定义页）

| Page ID | 名称 | | Page ID | 名称 |
|---|---|---|---|---|
| 0x00 | Undefined | | 0x42~0x58 | 保留 |
| 0x01 | Generic Desktop（通用桌面） | | 0x59 | Lighting And Illumination |
| 0x02 | Simulation Controls（仿真） | | 0x5A~0x7F | 保留 |
| 0x03 | VR Controls | | 0x80 | Monitor |
| 0x04 | Sport Controls | | 0x81 | Monitor Enumerated |
| 0x05 | Game Controls | | 0x82 | VESA Virtual Controls |
| 0x06 | Generic Device Controls | | 0x83 | 保留 |
| 0x07 | Keyboard/Keypad | | 0x84 | Power |
| 0x08 | LED | | 0x85 | Battery System |
| 0x09 | Button | | 0x86~0x8B | 保留 |
| 0x0A | Ordinal | | 0x8C | Barcode Scanner |
| 0x0B | Telephony Device | | 0x8D | Scales |
| 0x0C | Consumer | | 0x8E | Magnetic Stripe Reader |
| 0x0D | Digitizers | | 0x8F | 保留 |
| 0x0E | Haptics | | 0x90 | Camera Control |
| 0x0F | Physical Input Device | | 0x91 | Arcade |
| 0x10 | Unicode | | 0x92 | Gaming Device |
| 0x11 | 保留 | | 0x93~0xF1CF | 保留 |
| 0x12 | Eye and Head Trackers | | 0xF1D0 | FIDO Alliance |
| 0x13 | 保留 | | 0xF1D1~0xFEFF | 保留 |
| 0x14 | Auxiliary Display | | 0xFF00~0xFFFF | 厂商自定义 |
| 0x15~0x1F | 保留 | | 0x20 Sensors、0x21~0x3F 保留、0x40 Medical Instrument、0x41 Braille Display | |

约定（HUT §3.1）：Usage ID 0 恒保留；0x01~0x1F 保留给顶层集合；Usage = 页(高 16 位) + ID(低 16 位)，页可用 Usage Page Item 声明以省字节。

## 4. Generic Desktop 页 (0x01) 完整 Usage 表（HUT §4，Table 4.1）

| Usage ID | 名称 | 类型 | | Usage ID | 名称 | 类型 |
|---|---|---|---|---|---|---|
| 0x00 | Undefined | — | | 0x81 | System Power Down | OSC |
| 0x01 | Pointer | CP | | 0x82 | System Sleep | OSC |
| 0x02 | Mouse | CA | | 0x83 | System Wake Up | OSC |
| 0x03 | 保留 | — | | 0x84 | System Context Menu | OSC |
| 0x04 | Joystick | CA | | 0x85 | System Main Menu | OSC |
| 0x05 | Gamepad | CA | | 0x86 | System App Menu | OSC |
| 0x06 | Keyboard | CA | | 0x87 | System Menu Help | OSC |
| 0x07 | Keypad | CA | | 0x88 | System Menu Exit | OSC |
| 0x08 | Multi-axis Controller | CA | | 0x89 | System Menu Select | OSC |
| 0x09 | Tablet PC System Controls | CA | | 0x8A~0x8D | System Menu Right/Left/Up/Down | RTC |
| 0x0A | Water Cooling Device | CA | | 0x8E | System Cold Restart | OSC |
| 0x0B | Computer Chassis Device | CA | | 0x8F | System Warm Restart | OSC |
| 0x0C | Wireless Radio Controls | CA | | 0x90~0x93 | D-pad Up/Down/Right/Left | OOC |
| 0x0D | Portable Device Control | CA | | 0x94/0x95 | Index/Palm Trigger | MC/DV |
| 0x0E | System Multi-Axis Controller | CA | | 0x96 | Thumbstick | CP |
| 0x0F | Spatial Controller | CA | | 0x97/0x98 | System Function Shift(+Lock) | MC/OOC |
| 0x10 | Assistive Control | CA | | 0x99 | Function Shift Lock Indicator | DV |
| 0x11 | Device Dock | CA | | 0x9A | System Dismiss Notification | OSC |
| 0x12 | Dockable Device | CA | | 0x9B | System Do Not Disturb | OOC |
| 0x13 | Call State Management Control | CA | | 0x9C~0x9F | 保留 | — |
| 0x14~0x2F | 保留 | — | | 0xA0/0xA1 | System Dock/Undock | OSC |
| 0x30~0x38 | X,Y,Z,Rx,Ry,Rz,Slider,Dial,Wheel | DV | | 0xA2 | System Setup | OSC |
| 0x39 | Hat switch | DV | | 0xA3~0xA6 | (Debugger) Break 类 | OSC |
| 0x3A | Counted Buffer | CL | | 0xA7 | System Speaker Mute | OSC |
| 0x3B | Byte Count | DV | | 0xA8 | System Hibernate | OSC |
| 0x3C | Motion Wakeup | OSC/DF | | 0xA9~0xAF | 保留 | — |
| 0x3D/0x3E | Start/Select | OOC | | 0xB0~0xB7 | System Display Invert/Internal/External/Both/Dual/Toggle Int-Ext/Swap/Toggle LCD Autoscale | OSC |
| 0x3F | 保留 | — | | 0xB8~0xBF | 保留 | — |
| 0x40~0x46 | Vx,Vy,Vz,Vbrx,Vbry,Vbrz,Vno | DV | | 0xC0 | Sensor Zone | CL |
| 0x47 | Feature Notification | DV/DF | | 0xC1/0xC2 | RPM / Coolant Level | DV |
| 0x48 | Resolution Multiplier | DV | | 0xC3 | Coolant Critical Level | SV |
| 0x49~0x4C | Qx,Qy,Qz,Qw | DV | | 0xC4 | Coolant Pump | US |
| 0x4D~0x7F | 保留 | — | | 0xC5 | Chassis Enclosure | CL |
| 0x80 | System Control | CA | | 0xC6~0xC8 | Wireless Radio Button/LED/Slider | OOC |
| 0xC9/0xCA | Display Rotation Lock Button/Slider | OOC | | 0xD6 | Dockable Device Object Type | DV |
| 0xCB | Control Enable | DF | | 0xD7~0xDF | 保留 | — |
| 0xCC~0xCF | 保留 | — | | 0xE0/0xE2 | Call Active LED / Call Mute LED | OOC |
| 0xD0~0xD3 | Dock UDID/Vendor ID/Prim Usage Page/Prim Usage ID | DV | | 0xE1 | Call Mute Toggle | OSC |
| 0xD4/0xD5 | Docking State / Display Occlusion | DF/CL | | 0xE3~0xFFFF | 保留 | — |

鼠标/键盘常用组合：鼠标 = `Pointer(0x01)` + X/Y(0x30/0x31) + Wheel(0x38)（滚轮分辨率扩展用 0x48 Resolution Multiplier，见 [06-鼠标详解.md](06-鼠标详解.md)）。

## 5. Keyboard/Keypad 页 (0x07) 键值表（HUT §10）

所有键码类型为 Sel；修饰键 (0xE0~0xE7) 为 DV。Boot 键盘至少支持标 Boot 列的键（详见 [05-键盘详解.md](05-键盘详解.md)）。

| ID | 键 | | ID | 键 | | ID | 键 |
|---|---|---|---|---|---|---|---|
| 0x00 | 保留（无键按下） | | 0x1E~0x27 | 1 2 3 4 5 6 7 8 9 0 | | 0x54 | Keypad / |
| 0x01 | ErrorRollOver | | 0x28 | Return (ENTER) | | 0x55 | Keypad * |
| 0x02 | POSTFail | | 0x29 | ESC | | 0x56 | Keypad - |
| 0x03 | ErrorUndefined | | 0x2A | DELETE（退格） | | 0x57 | Keypad + |
| 0x04 | a A | | 0x2B | Tab | | 0x58 | Keypad ENTER |
| 0x05 | b B | | 0x2C | Spacebar | | 0x59~0x62 | Keypad 1~9,0（含 End/方向/Insert 复用） |
| 0x06 | c C | | 0x2D | - _ | | 0x63 | Keypad . |
| 0x07 | d D | | 0x2E | = + | | 0x64 | Non-US \ \| |
| 0x08 | e E | | 0x2F | [ { | | 0x65 | Application（菜单键） |
| 0x09 | f F | | 0x30 | ] } | | 0x66 | Power |
| 0x0A | g G | | 0x31 | \ \| | | 0x67 | Keypad = |
| 0x0B | h H | | 0x32 | Non-US # ~ | | 0x68~0x73 | F13~F24（**不是**多媒体键） |
| 0x0C | i I | | 0x33 | ; : | | 0x74 | Execute |
| 0x0D | j J | | 0x34 | ' " | | 0x75 | Help |
| 0x0E | k K | | 0x35 | ` ~ | | 0x76 | Menu |
| 0x0F | l L | | 0x36 | , < | | 0x77 | Select |
| 0x10 | m M | | 0x37 | . > | | 0x78 | Stop |
| 0x11 | n N | | 0x38 | / ? | | 0x79 | Again |
| 0x12 | o O | | 0x39 | Caps Lock | | 0x7A | Undo |
| 0x13 | p P | | 0x3A~0x45 | F1~F12 | | 0x7B | Cut |
| 0x14 | q Q | | 0x46 | PrintScreen | | 0x7C | Copy |
| 0x15 | r R | | 0x47 | Scroll Lock | | 0x7D | Paste |
| 0x16 | s S | | 0x48 | Pause | | 0x7E | Find |
| 0x17 | t T | | 0x49 | Insert | | 0x7F | Mute |
| 0x18 | u U | | 0x4A | Home | | 0x80 | Volume Up |
| 0x19 | v V | | 0x4B | PageUp | | 0x81 | Volume Down |
| 0x1A | w W | | 0x4C | Delete Forward | | 0x82~0x84 | Locking Caps/Num/Scroll（锁定式，遗留） |
| 0x1B | x X | | 0x4D | End | | 0x85 | Keypad Comma |
| 0x1C | y Y | | 0x4E | PageDown | | 0x86 | Keypad Equal Sign |
| 0x1D | z Z | | 0x4F~0x52 | →←↓↑ | | 0x87~0x8F | International1~9 |
| 0x53 | Keypad Num Lock | | 0x9A | SysReq/Attention | | 0x90~0x98 | LANG1~LANG9（日韩 IME 等） |

其余段：`0x99~0xA4` Alternate Erase/SysReq 附近编辑键（见上表）、`0xA5~0xAF` 保留、`0xB0~0xDF` 键盘专用 Keypad 扩展（00/000、千分位、十六进制 Keypad A~F、Memory Store 等，HUT §10 Table 原文）。

**修饰键 0xE0~0xE7**（字节位序 = 报告中第 1 字节 bit0~bit7）：

| ID | 位 | 键 | ID | 位 | 键 |
|---|---|---|---|---|---|
| 0xE0 | bit0 | Left Control | 0xE4 | bit4 | Right Control |
| 0xE1 | bit1 | Left Shift | 0xE5 | bit5 | Right Shift |
| 0xE2 | bit2 | Left Alt | 0xE6 | bit6 | Right Alt |
| 0xE3 | bit3 | Left GUI（Win/⌘） | 0xE7 | bit7 | Right GUI |

> 勘误提示：0x68~0x73 是 **F13~F24** 功能键；"媒体键"（Play/Pause、音量等）在 **Consumer 页 (0x0C)**，见 §8。音量加减在键盘页也有 0x7F~0x81（Mute/Volume Up/Down）与 Consumer 页 0xE2/0xE9/0xEA 两套，固件按产品定位选其一（HUT §10/§15）。

## 6. LED 页 (0x08) 全表（HUT §11）

LED 全部为 OOC（单按钮翻转语义：1 亮 0 灭），例外见 §11 各小节。

| ID | 指示灯 | | ID | 指示灯 | | ID | 指示灯 |
|---|---|---|---|---|---|---|---|
| 0x00 | Undefined | | 0x18 | Recording Format Detect | | 0x30 | Remote |
| 0x01 | Num Lock | | 0x19 | Off-Hook | | 0x31 | Forward |
| 0x02 | Caps Lock | | 0x1A | Ring | | 0x32 | Reverse |
| 0x03 | Scroll Lock | | 0x1B | Message Waiting | | 0x33 | Stop |
| 0x04 | Compose | | 0x1C | Data Mode | | 0x34 | Rewind |
| 0x05 | Kana | | 0x1D | Battery Operation | | 0x35 | Fast Forward |
| 0x06 | Power | | 0x1E | Battery OK | | 0x36 | Play |
| 0x07 | Shift | | 0x1F | Battery Low | | 0x37 | Pause |
| 0x08 | Do Not Disturb | | 0x20 | Speaker | | 0x38 | Record |
| 0x09 | Mute | | 0x21 | Head Set | | 0x39 | Error |
| 0x0A | Tone Enable | | 0x22 | Hold | | 0x3A | Usage Selected Indicator (US) |
| 0x0B | High Cut Filter | | 0x23 | Microphone | | 0x3B | Usage In Use Indicator (US) |
| 0x0C | Low Cut Filter | | 0x24 | Coverage | | 0x3C | Usage Multi Mode Indicator (UM) |
| 0x0D | Equalizer Enable | | 0x25 | Night Mode | | 0x3D~0x41 | Indicator On/Flash/Slow Blink/Fast Blink/Off (Sel) |
| 0x0E | Sound Field On | | 0x26 | Send Calls | | 0x42~0x46 | Flash/慢闪/快闪 On/Off 时间 (DV) |
| 0x0F | Surround On | | 0x27 | Conference | | 0x47 | Usage Indicator Color (UM) |
| 0x10 | Repeat | | 0x28 | Stand-by | | 0x48~0x4A | Indicator Color Red/Green/Amber |
| 0x11 | Stereo | | 0x29 | Camera On | | 0x4B | Reserved |
| 0x12 | Sampling Rate Detect | | 0x2A | Camera Off | | 0x4C | Paper Out |
| 0x13 | Spinning | | 0x2B | On-Line | | 0x4D | Paper Jam |
| 0x14 | CAV | | 0x2C | Off-Line | | 0x4E~0x4F | Embedded/Magnetic Card Indicator |
| 0x15 | CLV | | 0x2D | Busy | | 0x4F+ | Optical Card / …（HUT §11 Table 尾段） |
| 0x16 | Recording Format Detect(重复段) | | 0x2E | Ready | | 0x47 之后段详见 HUT §11 原表 |
| 0x17 | Off-Hook 前 | | 0x2F | Paper-Out | | |

> 注：上表前段 (0x00~0x2F) 与后段 (0x30~0x4x) 均提取自 HUT §11；个别行因 PDF 双栏错位，名称↔ID 以规范原表为准。键盘常用仅 0x01~0x05（Num/Caps/Scroll/Compose/Kana），其余为电话/音视频设备指示灯。

## 7. Button 页 (0x09)（HUT §12）

- **无固定编号上限**：Usage ID = 按钮序号，`0x01` Primary（左键/扳机）、`0x02` Secondary（右键）、`0x03` Tertiary，序号越大选择语义越弱；`0xFFFF` = Button 65535（Table 12.1）。
- `0x00` = "无按钮按下"（作为 Array 选择器时）。
- 类型依声明而定：可作 Sel（Array 数组，键盘滚轮/鼠标键常用）、OOC、MC、OSC（Table 12.1 Note）。
- GUI 惯例：Button 1 = 选择/拖拽/双击（macOS 唯一物理键）；Button 2 = 属性/右键菜单；Button 3+ 少有系统级功能（HUT §12 正文）。

## 8. Consumer 页 (0x0C) 常用段全表（HUT §15，Table 15.1）

Consumer 页控制均为"应用级"（作用于具体设备而非系统全局，页首声明）。多媒体键固件写法见 [07-消费控制与多媒体.md](07-消费控制与多媒体.md)。

| ID | 名称 | 类型 | | ID | 名称 | 类型 |
|---|---|---|---|---|---|---|
| 0x01 | Consumer Control | CA | | 0xB7 | Stop | OSC |
| 0x02 | Numeric Key Pad | NAry | | 0xB8 | Eject | OSC |
| 0x03 | Programmable Buttons | NAry | | 0xB9 | Random Play | OOC |
| 0x04 | Microphone | CA | | 0xBA | Select Disc | NAry |
| 0x05 | Headphone | CA | | 0xBB | Enter Disc | MC |
| 0x06 | Graphic Equalizer | CA | | 0xBC | Repeat | SC |
| 0x20 | +10 | OSC | | 0xBD | Tracking | LC |
| 0x21 | +100 | OSC | | 0xBE | Track Normal | OSC |
| 0x22 | AM/PM | OSC | | 0xBF | Slow Tracking | OSC |
| 0x30 | Power | OOC | | 0xC0 | Frame Forward | RTC |
| 0x31 | Reset | OSC | | 0xC1 | Frame Back | RTC |
| 0x32 | Sleep | OSC | | 0xC2 | Mark | OSC |
| 0x33 | Sleep After | OSC | | 0xC3 | Clear Mark | OSC |
| 0x34 | Sleep Mode | RTC | | 0xC4 | Repeat From Mark | OSC |
| 0x35 | Illumination | OOC | | 0xC5 | Return To Mark | OSC |
| 0x36 | Function Buttons | NAry | | 0xC6 | Search Mark Forward | OSC |
| 0x40 | Menu | OSC | | 0xC7 | Search Mark Backwards | OSC |
| 0x41 | Menu Pick | OSC | | 0xC8 | Counter Reset | OSC |
| 0x42~0x45 | Menu Up/Down/Left/Right | OSC | | 0xC9 | Show Counter | OSC |
| 0x46 | Menu Escape | OSC | | 0xCA | Tracking Increment | RTC |
| 0x47/0x48 | Menu Value Increase/Decrease | OSC | | 0xCB | Tracking Decrement | RTC |
| 0x60 | Data On Screen | OSC | | 0xCC | Stop/Eject | OSC |
| 0x61/0x62 | Closed Caption (+Select) | OSC | | 0xCD | Play/Pause | OSC |
| 0x63 | VCR/TV | OSC | | 0xCE | Play/Skip | OSC |
| 0x64 | Broadcast Mode | OSC | | 0xCF | Voice Command | OSC |
| 0x65 | Snapshot | OSC | | 0xD0~0xD9 | 游戏录制/摄像头采集开关段 [HUTRR35/66/68] | Sel/OOC |
| 0x66 | Still | OOC | | 0xE0 | Volume | LC |
| 0x67~0x6D | PiP Toggle/Swap、红/绿/蓝/黄菜单键、Aspect | OSC/MC | | 0xE1 | Balance | LC |
| 0x6E~0x7F | 3D Mode、亮度/背光/键盘背光段 [HUTRR41/42] | OSC/OOC | | 0xE2 | **Mute** | OOC |
| 0x80~0x8F | Selection/Mode Step/Enter Channel、Media Select Computer/TV/WWW/DVD/Telephone/Guide/Video Phone/Games | OSC/Sel | | 0xE3 | Bass | LC |
| 0x90~0x9E | Media Select Messages/CD/VCR/Tuner…、Channel Increment/Decrement | Sel/OSC | | 0xE4 | Treble | LC |
| 0xA0~0xA4 | VCR Plus/Once/Daily/Weekly/Monthly | OSC | | 0xE5 | Bass Boost | OOC |
| 0xB0 | Play | OOC | | 0xE6 | Surround Mode | OSC |
| 0xB1 | Pause | OOC | | 0xE7 | Loudness | OOC |
| 0xB2 | Record | OOC | | 0xE8 | MPX | OOC |
| 0xB3 | Fast Forward | OOC | | 0xE9 | **Volume Increment**（音量+） | RTC |
| 0xB4 | Rewind | OOC | | 0xEA | **Volume Decrement**（音量-） | RTC |
| 0xB5 | Scan Next Track | OSC | | 0xEB~0xEF | 保留 | — |
| 0xB6 | Scan Previous Track | OSC | | 0xF0~0xF5 | Speed Select/Playback Speed/Standard/Long/Extended Play/Slow | OSC/NAry/Sel |

其他常用段：`0x100~0x10D` 环境控制（风扇/灯光/报警）、`0x150~0x155` Balance/Bass/Treble 增减 (RTC)、`0x160~0x17F` 扬声器声道布局 (CL)、`0x180~0x1C8` AL 应用启动段（AL Calculator 0x192、AL Email Reader 0x18A、AL Internet Browser 0x196 等，Sel）、`0x200+` Generic GUI Application Controls 与 AC 段（AC New 0x206、AC Search 0x221、AC Home 0x223、AC Back 0x224、AC Forward 0x225、AC Refresh 0x227、AC Bookmarks 0x22A，Sel）、`0x2C0~0x2CC` 键盘辅助属性 [HUTRR15]。

## 9. Digitizers 页 (0x0D) 全表（HUT §16）

> 该表 PDF 双栏提取有错位，按"编号+名称+（类型）"重排；个别类型以 HUT §16 原文为准。

| ID | 名称（类型） | | ID | 名称（类型） |
|---|---|---|---|---|
| 0x01 | Digitizer (CA) | | 0x30 | Tip Pressure (DV) |
| 0x02 | Pen (CA) | | 0x31 | Barrel Pressure (DV) |
| 0x03 | Light Pen (CA) | | 0x32 | **In Range (DV)** |
| 0x04 | Touch Screen (CA) | | 0x33 | **Touch (DV)** |
| 0x05 | Touch Pad (CA) | | 0x34 | Untouch (DV) |
| 0x06 | Whiteboard (CA) | | 0x35 | Tap (MC) |
| 0x07 | Coordinate Measuring Machine (CA) | | 0x36 | Quality (MC) |
| 0x08 | 3D Digitizer (CA) | | 0x37 | Data Valid (OSC) |
| 0x09 | Stereo Plotter (CA) | | 0x38 | Transducer Index (DV) |
| 0x0A | Articulated Arm (CA) | | 0x39 | Tablet Function Keys (CL) |
| 0x0B | Armature (CA) | | 0x3A | Program Change Keys (CL) |
| 0x0C | Multiple Point Digitizer (CA) | | 0x3B | Battery Strength (DV) |
| 0x0D | Free Space Wand (CA) | | 0x3C | Invert (MC) |
| 0x0E | Device Configuration (CA) | | 0x3D / 0x3E | **X Tilt / Y Tilt** (DV) |
| 0x0F | Capacitive Heat Map Digitizer (CA) | | 0x3F / 0x40 | Azimuth / Altitude (DV) |
| 0x10~0x1F | 保留 | | 0x41 | **Twist** (DV) |
| 0x20 | Puck (CA) | | 0x42 | **Tip Switch** (MC) |
| 0x21 | Finger (CA) | | 0x43 | Secondary Tip Switch (MC) |
| 0x22 | Device settings (CA) | | 0x44 | **Barrel Switch** (MC) |
| 0x23 | Character Gesture (CA) | | 0x45 | **Eraser** (MC) |
| 0x24~0x2F | 保留 | | 0x46 | Tablet Pick (MC) |
| 0x47 | Touch Valid (MC) | | 0x54 | **Contact Count** (DV) |
| 0x48 / 0x49 | Width / Height (DV) | | 0x55 | **Contact Count Maximum** (SV) |
| 0x4A~0x50 | 保留 | | 0x56 | Scan Time (DV) |
| 0x51 | Contact Identifier (DV) | | 0x57 / 0x58 | Surface Switch / Button Switch (DF) |
| 0x52 | Device Mode (DV) | | 0x59 | Pad Type (SF) |
| 0x53 | Device Identifier (DV/SV) | | 0x5A | Secondary Barrel Switch (MC) |
| 0x5B~0x69 | 笔序列号/偏好颜色/手势字符段（SV/DV/MC/Sel） | | 0x60~0x6D | Latency Mode/手势数据/电容热图段 [HUTRR45/51/54/63] |

Windows 多点触控 PIP 所需最小集合（Touch 触发 + Contact Count + 坐标 + 0x47/0x48/0x49）的实战描述符见 [09-触摸屏触摸板与数字化仪.md](09-触摸屏触摸板与数字化仪.md)。

## 10. Collection 类型全表（HID 1.11 §6.2.2.4 / §6.2.2.6）

Collection Item 数据字段（D7=1 为厂商定义）：

| 值 | 类型 | 含义 |
|---|---|---|
| 0x00 | Physical | 几何分组（如一组轴、Pointer 集合） |
| 0x01 | Application | 顶层应用集合（鼠标/键盘），系统按它加载驱动；每个 TLC 必须有且仅有一个 |
| 0x02 | Logical | 数据结构关联（如缓冲区+字节计数） |
| 0x03 | Report | 内含一个 Report ID，包裹该报告全部字段 |
| 0x04 | Named Array | 给数组选择器命名 |
| 0x05 | Usage Switch | 修饰所含 Usage 语义（如把 LED 页用法转成指示器） |
| 0x06 | Usage Modifier | 扩展控件的运行模式（如让 LED 支持闪烁/变色） |
| 0x07~0x7F | 保留 | — |
| 0x80~0xFF | 厂商定义 | 应用遇到未知厂商集合须忽略其中全部 Main Item |

规则：Collection 可嵌套；除顶层 Application 外都是可选的；Collection 不产生数据，但必须关联一个 Usage（§6.2.2.6）。

## 11. Item 编码完整表（HID 1.11 §5.3、§6.2.2.1~6.2.2.9）

Short Item 前缀 = `bTag(4bit) | bType(2bit) | bSize(2bit)`：bSize 0/1/2/3 = 数据 0/1/2/4 字节；bType 0=Main、1=Global、2=Local、3=保留。Long Item：前缀固定 `0xFE`（bSize=2 表示"长项标记"，bType=3/11b），后跟 bDataSize(数据字节数) 与 bLongItemTag；HID 1.11 未定义任何 Long tag，`0xF0~0xFF` 段为厂商定义（§6.2.2.3）。

### Main（bType=00，数据字段/分组）

| Item | 前缀(不含 nn) | 完整前缀示例 (bSize=1) | 说明 |
|---|---|---|---|
| Input | 1000 00 nn | 0x80 | 定义输入字段；D0 Data/Constant、D1 Array/Variable、D2 Absolute/Relative、D3 NoWrap/Wrap、D4 Linear/NonLinear、D5 Preferred/NoPreferred、D6 NoNull/NullState、D7 保留、D8 BitField/BufferedBytes（§6.2.2.5） |
| Output | 1001 00 nn | 0x90 | 输出字段；D7 = NonVolatile/Volatile，其余位同 Input |
| Feature | 1011 00 nn | 0xB0 | 特征字段；位定义同 Output |
| Collection | 1010 00 nn | 0xA1 | 数据=集合类型（见 §10） |
| End Collection | 1100 00 nn | 0xC0 | 关闭集合 |
| 保留 | 1101~1111 00 nn | — | — |

### Global（bType=01，改写全局状态表，对后续所有 Main 生效）

| Item | 前缀 (bSize=1) | Item | 前缀 (bSize=1) |
|---|---|---|---|
| Usage Page | 0000 01 nn = 0x04 | Report Size | 0111 01 nn = 0x74 |
| Logical Minimum | 0001 01 nn = 0x14 | Report ID | 1000 01 nn = 0x84 |
| Logical Maximum | 0010 01 nn = 0x24 | Report Count | 1001 01 nn = 0x94 |
| Physical Minimum | 0011 01 nn = 0x34 | Push | 1010 01 nn = 0xA4 |
| Physical Maximum | 0100 01 nn = 0x44 | Pop | 1011 01 nn = 0xB4 |
| Unit Exponent | 0101 01 nn = 0x54 | 保留 | 1100 01~1111 01 nn |
| Unit | 0110 01 nn = 0x64 | — | — |

注：Physical Min/Max 未定义时回退为 Logical 值；Unit/Exponent 编码表（Nibble 半字节语义、0=None/1=cm 等）见 [02-报告描述符与Item编码.md](02-报告描述符与Item编码.md) 与 §6.2.2.7。

### Local（bType=10，仅对下一个 Main 生效，之后清空）

| Item | 前缀 (bSize=1) | Item | 前缀 (bSize=1) |
|---|---|---|---|
| Usage | 0000 10 nn = 0x08 | 保留 | 0110 10 nn |
| Usage Minimum | 0001 10 nn = 0x18 | String Index | 0111 10 nn = 0x78 |
| Usage Maximum | 0010 10 nn = 0x28 | String Minimum | 1000 10 nn = 0x88 |
| Designator Index | 0011 10 nn = 0x38 | String Maximum | 1001 10 nn = 0x98 |
| Designator Minimum | 0100 10 nn = 0x48 | Delimiter | 1010 10 nn = 0xA8 |
| Designator Maximum | 0101 10 nn = 0x58 | 保留 | 1011 10~1111 10 nn |

Local item 在遇到 Main item 后自动清空，无全局副作用；Delimiter 为同一控件定义别名组（§6.2.2.8）。

## 相关节点

- 父分枝：[00-HID概述与定位.md](00-HID概述与定位.md)；请求实战：[04-传输与类特定请求.md](04-传输与类特定请求.md)
- 描述符与 Item 推导：[01-HID描述符.md](01-HID描述符.md) / [02-报告描述符与Item编码.md](02-报告描述符与Item编码.md)
- 设备详解：[05-键盘详解.md](05-键盘详解.md) / [06-鼠标详解.md](06-鼠标详解.md) / [07-消费控制与多媒体.md](07-消费控制与多媒体.md) / [09-触摸屏触摸板与数字化仪.md](09-触摸屏触摸板与数字化仪.md)
- 原文缓存：[../../80-参考资料/README.md](../../80-参考资料/README.md)（HID-1.11.pdf、HID-UsageTables-1.3.pdf）
