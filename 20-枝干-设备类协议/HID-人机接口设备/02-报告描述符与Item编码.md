---
title: "报告描述符与 Item 编码"
layer: 枝干/设备类协议
section: HID-人机接口设备
doc-path: 20-枝干-设备类协议/HID-人机接口设备/02-报告描述符与Item编码.md
---
# 报告描述符与 Item 编码

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[HID] → 叶[报告描述符]
> ⬆️ 父节点: [00-HID概述与定位.md](00-HID概述与定位.md)

## 1. 自描述字节流

报告描述符(Report Descriptor)不是"字段表"，而是一段**紧缩的字节码**：由若干 Item（项）顺序排列组成，主机 HID 解析器按顺序"执行"这些 Item，构建出报告的位级布局。它介于"数据结构声明"与"小型编程语言"之间——类比：报告描述符之于 HID 数据，相当于 DTD/Schema 之于 XML。

特点：

- 长度任意（几十字节到数百字节），由 HID 类描述符的 `wDescriptorLength` 声明；
- 获取方式：`GET_DESCRIPTOR(wValue=0x2200)`（见 [01-HID描述符.md](01-HID描述符.md)）；
- Item 序列末尾约定俗成以 `0xC0`（End Collection）收束，但严格说解析器以"读满 wDescriptorLength"为准。

## 2. Item 的两种形态

### 2.1 短 Item（Short Item）

1 字节头部 + 0/1/2/4 字节数据：

```text
  bit  7 6 5 4 | 3 2 | 1 0
     ┌─────────┼─────┼─────┐
     │  bTag   │bType│bSize│
     └─────────┴─────┴─────┘
  bSize: 00=0字节  01=1字节  10=2字节  11=4字节   （数据部分字节数）
  bType: 00=Main  01=Global  10=Local
  bTag:  Item 功能码（随 bType 分空间）
```

- 头部即编码：`前缀 = bTag<<4 | bType<<2 | bSize`。例如 `Usage Page` 的 bTag=0x0、bType=01、数据 1 字节 → 前缀 `0b0000_01_01 = 0x05`。
- **数据为小端(Little-Endian)**，且按规范解释为**有符号数**：若值为负、而数据只有 1/2 字节，解析器将其**符号扩展(sign-extend)到 32 位**。因此 `Logical Minimum (-127)` 编码为 `15 81`（0x81 即 -127），而 `0x15 0xFF` 表示的是 **-1 而不是 255**——这是最常见的编码事故（见 [11-实战完整报告描述符.md](11-实战完整报告描述符.md) 错误清单）。

多字节编码示例：

| Item 字节序列 | 解读 |
|---|---|
| `05 01` | Usage Page(Generic Desktop)，1 字节数据 |
| `26 FF 0F` | Logical Maximum(4095)，前缀 0x26=bSize 10（2 字节数据，小端） |
| `27 00 00 01 00` | Logical Maximum(65536)，bSize=11 → 4 字节数据 |
| `15 81` | Logical Minimum(-127)，负数符号扩展 |
| `26 FF FF` | Logical Maximum(**-1**)，经典符号扩展错误现场 |
| `85 03` | Report ID(3) |
| `A4` / `B4` | Push / Pop，bSize=0 无数据 |

### 2.2 长 Item（Long Item）

前缀固定 `0xFE`（bTag=0xF, bType=11, bSize=10），随后 1 字节说明：高半字节 `bLongItemTag`、低半字节 `bDataSize`，其后跟 0~255 字节数据。长 Item 是规范预留的扩展通道，HID 1.11 未定义任何具体长 Item，实际描述符中不应出现。

## 3. 三类 Item 总表

### 3.1 Main 类（bType=00）——描述数据与结构

| Item | 前缀（1 字节数据项） | 作用 |
|---|---|---|
| Input | `0x80`+位图 → 实际如 `81 02` | 声明一段"设备→主机"数据字段 |
| Output | `0x90` 基 → 如 `91 02` | "主机→设备"数据字段（LED 等） |
| Feature | `0xB0` 基 → 如 `B1 02` | 双向配置字段，仅走控制通道 |
| Collection | `A1 <type>` | 开启集合（如 `A1 01` = Application） |
| End Collection | `C0` | 关闭集合 |

Input/Output/Feature 的 1 字节数据是**位图标志**：

| 位 | 0 | 1 | 说明 |
|---|---|---|---|
| bit0 | Data | Constant | Constant=填充位/保留位 |
| bit1 | Array | Variable | Array=键码数组；Variable=独立位字段 |
| bit2 | Absolute | Relative | 绝对坐标 vs 相对位移（鼠标 X/Y=Relative） |
| bit3 | No Wrap | Wrap | 数值回绕 |
| bit4 | Linear | Non Linear | 物理映射是否线性 |
| bit5 | Preferred State | No Preferred State | 是否有默认回落状态 |
| bit6 | No Null Position | Null State | Null State=存在"无意义"取值（如帽开关 8~15） |
| bit7 | Non Volatile | Volatile | 仅 Output/Feature 有意义：主机是否可主动改写 |
| bit8 | Bit Field | Buffered Bytes | 按位打包 vs 按字节缓冲 |

常用组合速记：`81 02`=Data,Var,Abs（普通位图）；`81 00`=Data,Array,Abs（键码数组）；`81 06`=Data,Var,Rel（鼠标位移）；`81 03`=Const,Var,Abs（填充字节）；`81 42`=Data,Var,Abs,**Null State**（帽开关）。

### 3.2 Global 类（bType=01）——带状态、跨 Item 生效

| Item | bTag | 典型前缀（1 字节数据） | 作用 |
|---|---|---|---|
| Usage Page | 0x0 | `05 <page>` | 设置当前 Usage Page（高 16 位） |
| Logical Minimum | 0x1 | `15 <n>` | 字段数值下界（报告值域） |
| Logical Maximum | 0x2 | `25 <n>` | 数值上界 |
| Physical Minimum | 0x3 | `35 <n>` | 物理量下界 |
| Physical Maximum | 0x4 | `45 <n>` | 物理量上界 |
| Unit Exponent | 0x5 | `55 <e>` | 物理单位指数 |
| Unit | 0x6 | `65 <u>` | 物理单位编码 |
| Report Size | 0x7 | `75 <n>` | 每个字段的位数 |
| Report ID | 0x8 | `85 <id>` | 为随后的报告定义 1~255 的编号 |
| Report Count | 0x9 | `95 <n>` | 相同 Size 字段的个数 |
| Push | 0xA | `A4`（无数据） | 压栈保存全部 Global 状态 |
| Pop | 0xB | `B4`（无数据） | 出栈恢复 |

### 3.3 Local 类（bType=10）——一次性标签

| Item | bTag | 典型前缀 | 作用 |
|---|---|---|---|
| Usage | 0x0 | `09 <id>` | 给随后的 Main Item 贴 Usage 标签 |
| Usage Minimum | 0x1 | `19 <id>` | Array/位图字段的 Usage 起始 |
| Usage Maximum | 0x2 | `29 <id>` | Usage 结束 |

## 4. Global 持久 vs Local 即弃

理解报告描述符的关键心智模型：**解析器维护一个 Global 状态栈和一个 Local 标签列表**。

```text
Global 状态: { Usage Page, Logical Min/Max, Phys Min/Max,
               Unit/Exponent, Report Size, Report Count, Report ID }
   → 一直保持, 直到被新的 Global Item 覆盖或 Pop 恢复

Local 标签: { Usage, Usage Min/Max 累积列表 }
   → 每遇到一个 Main Item(Input/Output/Feature/Collection)
     即"贴"到该 Main Item 上, 然后【清空】
```

因此描述符写作顺序通常是："Global 定参（Page/Logical/Size/Count）→ Local 贴标签 → Main 产出字段"。同一个 `95 08`（Report Count=8）可以连续服务多个 Input Item，直到被改写；而每个 Input 前都要重新贴 Usage。

## 5. 报告字段的位填充与对齐

- 字段从每个字节的**最低位(LSB)开始连续打包**；一个字段可以跨越字节边界（如 12 位 X 后接 12 位 Y 共占 3 字节）。
- **位图(Variable)字段不足整字节时必须用 Constant 位补齐到字节边界**，否则整个报告从此错位：
  `Report Size(1), Report Count(3)`（3 个按钮）+ `Report Size(1), Report Count(5)`（Constant 填充）= 1 字节。
- Array 字段以"取值"表意（值=Usage 编号），单位是 Report Size 位；Boot 键盘的 6 键数组即 6 个 8 位 Array 字段。
- 报告总长 = Σ(Report Size × Report Count) 按字节向上取整，且不得超过端点 `wMaxPacketSize`。

## 6. Report ID 规则

- `85 <id>` 给"随后定义的报告"赋予 1~255 的编号；**Report ID 0 不可用**（0 表示"无 Report ID"的保留语义）。
- 使用 Report ID 后，**该报告在线上传输时第一个字节恒为 Report ID**，数据紧随其后；主机按 ID 分发到不同解析分支。
- 同一接口内 Input/Output/Feature **共用同一套 ID 编号空间**，每个 ID 唯一。
- 一旦接口中任何报告使用了 Report ID，则**所有报告都必须带 ID**（不存在"部分带"的混合状态）。
- 未使用 Report ID 的设备，报告中**没有 ID 字节**，第一个字节就是数据。
- Boot 协议报告是固定格式，永远不含 Report ID 字节（详见 [04-传输与类特定请求.md](04-传输与类特定请求.md)）。

## 7. 实例：8 字节 Boot 键盘报告的描述符（逐行注释）

这是 HID 1.11 附录 Boot 键盘描述符的等价形态，共 **63 字节（0x3F）**，与 [01-HID描述符.md](01-HID描述符.md) 示例中 `wDescriptorLength=0x003F` 一致：

```text
05 01        Usage Page (Generic Desktop)      ; Global: 页=0x01
09 06        Usage    (Keyboard)               ; Local : TLC 用法=键盘
A1 01        Collection (Application)          ; 顶层集合开始
  05 07      Usage Page (Keyboard/Keypad)      ; 切到键码页
  19 E0      Usage Minimum (0xE0)              ; 左Ctrl
  29 E7      Usage Maximum (0xE7)              ; 右GUI
  15 00      Logical Minimum (0)               ; 位值域 0..1
  25 01      Logical Maximum (1)
  75 01      Report Size (1)                   ; 每字段 1 位
  95 08      Report Count (8)                  ; 8 个 → 第 1 字节
  81 02      Input (Data,Var,Abs)              ; [字节0] 修饰键位图
  95 01      Report Count (1)
  75 08      Report Size (8)
  81 03      Input (Const,Var,Abs)             ; [字节1] 保留, 恒 0
  95 06      Report Count (6)                  ; 6 个 8 位 Array 字段
  75 08      Report Size (8)
  15 00      Logical Minimum (0)               ; 0 = 无事件
  25 65      Logical Maximum (101)             ; 0x65 = 键码上限
  19 00      Usage Minimum (0)                 ; Array 值域映射 Usage 0x00..0x65
  29 65      Usage Maximum (101)
  81 00      Input (Data,Array,Abs)            ; [字节2..7] 6 键数组
  05 08      Usage Page (LEDs)                 ; 以下为 LED Output 报告
  19 01      Usage Minimum (Num Lock)
  29 05      Usage Maximum (Kana)
  15 00      Logical Minimum (0)
  25 01      Logical Maximum (1)
  75 01      Report Size (1)
  95 05      Report Count (5)
  91 02      Output (Data,Var,Abs)             ; 5 个 LED 位
  95 03      Report Count (3)
  91 03      Output (Const,Var,Abs)            ; [bit5..7] 填充补齐 1 字节
C0           End Collection                    ; 顶层集合结束
```

对应报告字节流（无 Report ID）：

| 字节 | bit7 | bit6 | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
|---|---|---|---|---|---|---|---|---|
| 0 | 右GUI | 右Alt | 右Shift | 右Ctrl | 左GUI | 左Alt | 左Shift | 左Ctrl |
| 1 | 保留（恒 0） | | | | | | | |
| 2~7 | 键码数组（0=无按键，值域 0x00~0x65） | | | | | | | |

## 相关节点

- 父节点：[00-HID概述与定位.md](00-HID概述与定位.md)
- 描述符获取：[01-HID描述符.md](01-HID描述符.md)
- Usage 语义：[03-Usage体系与集合.md](03-Usage体系与集合.md)
- 综合实战与错误清单：[11-实战完整报告描述符.md](11-实战完整报告描述符.md)
- 树干基础：[07-描述符详解.md](../../10-树干-USB核心/07-描述符详解.md)
