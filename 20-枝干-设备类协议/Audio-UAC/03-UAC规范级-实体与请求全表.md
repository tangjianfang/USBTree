---
title: "UAC 规范级附录：实体、请求与选择子全表"
layer: 枝干/设备类协议
section: Audio-UAC
doc-path: 20-枝干-设备类协议/Audio-UAC/03-UAC规范级-实体与请求全表.md
---
# UAC 规范级附录：实体、请求与选择子全表

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[UAC] → 附录[规范级速查]
> ⬆️ 父节点: [00-UAC概述.md](00-UAC概述.md)
> 📖 数据提取自 **UAC 1.0**（含 Frmts10 音频数据格式、Termt10 终端类型）与 **UAC 2.0**（Audio20 final），缓存见 [../../80-参考资料/README.md](../../80-参考资料/README.md)。架构叙述见 [01-UAC1.0详解.md](01-UAC1.0详解.md) / [02-UAC2与UAC3.md](02-UAC2与UAC3.md)，本文只放编号与字段。

## 1. 类代码速记

| 层级 | UAC1 | UAC2 |
|---|---|---|
| 接口类 bInterfaceClass | AUDIO=0x01 | AUDIO=0x01 |
| 子类 | AUDIOCONTROL=0x01 / AUDIOSTREAMING=0x02 / MIDISTREAMING=0x03 | 同左（未定义子类=0x00） |
| Audio Function 级（设备描述符） | — | AUDIO_FUNCTION=0xFF，子类 0x00，协议 AF_VERSION_02_00=0x20 |

## 2. UAC1 类特定请求码全表（UAC1 §A.9，Table A-9，共 11 个）

| bRequest | 值 | bmRequestType | 方向 | 作用 |
|---|---|---|---|---|
| SET_CUR | 0x01 | 00100001b/00100010b (0x21/0x22) | OUT | 写控件当前值 |
| SET_MIN | 0x02 | 同上 | OUT | 写最小值（少见可编程） |
| SET_MAX | 0x03 | 同上 | OUT | 写最大值 |
| SET_RES | 0x04 | 同上 | OUT | 写分辨率（步进） |
| SET_MEM | 0x05 | 同上 | OUT | 写实体内存空间 |
| GET_CUR | 0x81 | 10100001b/10100010b (0xA1/0xA2) | IN | 读当前值 |
| GET_MIN | 0x82 | 同上 | IN | 读最小值 |
| GET_MAX | 0x83 | 同上 | IN | 读最大值 |
| GET_RES | 0x84 | 同上 | IN | 读步进 |
| GET_MEM | 0x85 | 同上 | IN | 读实体内存 |
| GET_STAT | 0xFF | 10100001b/10100010b | IN | 读实体状态（中断占位，见 §7） |

寻址规则（§5.2.1）：wValue 高字节 = Control Selector (CS)，低字节 = Channel Number (CN)（Mixer 用输出通道 OCN×16+输入 ICN？实为 MCN，Mixer 控制单列）；wIndex 低字节 = 接口号/端点号，高字节 = 实体 ID（Unit/Terminal ID；寻址接口本身为 0）。接收者 0x01=接口（AudioControl 或 AudioStreaming），0x02=同步端点。

## 3. UAC1 控制选择子（UAC1 §A.10）

**Terminal（A.10.1）**：`0x00 TE_CONTROL_UNDEFINED`、`0x01 COPY_PROTECT_CONTROL`。

**Feature Unit（A.10.2，bmaControls 位图序号 = 控制号）**：

| 控制号 | 名称 | | 控制号 | 名称 |
|---|---|---|---|---|
| 0x00 | FU_CONTROL_UNDEFINED | | 0x06 | GRAPHIC_EQUALIZER_CONTROL |
| 0x01 | **MUTE** | | 0x07 | AUTOMATIC_GAIN |
| 0x02 | **VOLUME** | | 0x08 | DELAY |
| 0x03 | BASS | | 0x09 | BASS_BOOST |
| 0x04 | MID | | 0x0A | LOUDNESS |
| 0x05 | TREBLE | | 0x0B+ | 保留（UAC1 无 0x0B~0x0D） |

FU 描述符中每通道 1 字节位图：D0=MUTE 支持、D1=VOLUME、…（即 bmaControls 的第 n 位对应控制号 n）；通道 0 为主控（master），后接每逻辑通道各一字节（§3.5.5 / Table 4-7）。

**Processing Unit 各类型（A.10.3）**：

| PU 类型 | 选择子（值） |
|---|---|
| Up/Down-mix (UD) | UD_ENABLE 0x01、UD_MODE_SELECT 0x02 |
| Dolby Prologic (DP) | DP_ENABLE 0x01、DP_MODE_SELECT 0x02 |
| 3D Stereo Extender (3D) | 3D_ENABLE 0x01、SPACIOUSNESS 0x03 |
| Reverberation (RV) | RV_ENABLE 0x01、REVERB_LEVEL 0x02、REVERB_TIME 0x03、REVERB_FEEDBACK 0x04 |
| Chorus (CH) | CH_ENABLE 0x01、CHORUS_LEVEL 0x02、CHORUS_RATE 0x03、CHORUS_DEPTH 0x04 |
| Dynamic Range Compressor (DR) | DR_ENABLE 0x01、COMPRESSION_RATE 0x02、MAXAMPL 0x03、THRESHOLD 0x04、ATTACK_TIME 0x05、RELEASE_TIME 0x06 |

（各类型 0x00 均为 *_CONTROL_UNDEFINED。）

**Extension Unit（A.10.4）**：`0x00 XU_CONTROL_UNDEFINED`、`0x01 XU_ENABLE_CONTROL`，其余厂商自定义。
**Endpoint（A.10.5，寻址同步端点）**：`0x00 EP_CONTROL_UNDEFINED`、`0x01 SAMPLING_FREQ_CONTROL`、`0x02 PITCH_CONTROL`。

## 4. UAC1 终端类型完整表（Termt10 §2，wTerminalType）

**USB 终端（0x01xx，Table 2-1）**：0x0100 USB Undefined、0x0101 **USB streaming**（AS 接口 bTerminalLink 指向）、0x01FF USB vendor specific。

**输入终端（0x02xx，Table 2-2）**：0x0200 Undefined、0x0201 Microphone、0x0202 Desktop microphone、0x0203 Personal microphone（头戴/领夹）、0x0204 Omni-directional microphone、0x0205 Microphone array、0x0206 Processing microphone array。

**输出终端（0x03xx，Table 2-3）**：0x0300 Undefined、0x0301 Speaker、0x0302 Headphones、0x0303 Head Mounted Display Audio、0x0304 Desktop speaker、0x0305 Room speaker、0x0306 Communication speaker、0x0307 Low Frequency Effects Speaker（低音炮）。

**双向终端（0x04xx，Table 2-4，成对 IT/OT 用 bAssocTerminal 互链）**：0x0400 Undefined、0x0401 Handset、0x0402 Headset、0x0403 Speakerphone（无回声消除）、0x0404 Echo-suppressing speakerphone、0x0405 Echo-canceling speakerphone。

**电话终端（0x05xx，Table 2-5，双向）**：0x0500 Undefined、0x0501 Phone line（PSTN/ISDN/PBX）、0x0502 Telephone、0x0503 Down Line Phone。

**外部终端（0x06xx，Table 2-6）**：0x0600 Undefined、0x0601 Analog connector、0x0602 Digital audio interface、0x0603 Line connector、0x0604 Legacy audio connector、0x0605 S/PDIF interface、0x0606 1394 DA stream、0x0607 1394 DV stream soundtrack。

**内嵌功能终端（0x07xx，Table 2-7）**：0x0700 Undefined、0x0701 Level Calibration Noise Source (O)、0x0702 Equalization Noise (O)、0x0703 CD player (I)、0x0704~0x07xx Turntable、Tape、Tuner、Satellite 等内嵌源（Termt10 §2.7 余段）。

## 5. UAC1 预置格式类型表（Frmts10 §A.1，wFormatTag）

| Type | wFormatTag | 名称 | Type | wFormatTag | 名称 |
|---|---|---|---|---|---|
| I | 0x0000 | TYPE_I_UNDEFINED | III | 0x2000 | TYPE_III_UNDEFINED |
| I | 0x0001 | **PCM**（Type I 描述符含 bNrChannels/tSubframeSize/bBitResolution/tSamFreq[]） | III | 0x2001 | IEC1937_AC-3（非音频载荷走 IEC 60958 帧） |
| I | 0x0002 | PCM8 | III | 0x2002 | IEC1937_MPEG-1_Layer1 |
| I | 0x0003 | IEEE_FLOAT | III | 0x2003 | IEC1937_MPEG-1_Layer2/3 或 MPEG-2_NOEXT |
| I | 0x0004 | ALAW | III | 0x2004 | IEC1937_MPEG-2_EXT |
| I | 0x0005 | MULAW | III | 0x2005 | IEC1937_MPEG-2_Layer1_LS |
| II | 0x1000 | TYPE_II_UNDEFINED（描述符带 wMaxBitRate/wSamplesPerFrame） | III | 0x2006 | IEC1937_MPEG-2_Layer2/3_LS |
| II | 0x1001 | MPEG | — | — | — |
| II | 0x1002 | AC-3 | — | — | — |

FORMAT_TYPE 码（AS 格式描述符 bFormatType，Frmts10 §A.2）：0x00 未定义、0x01 TYPE_I、0x02 TYPE_II、0x03 TYPE_III。MPEG/AC-3 专用 AS 控制选择子见 Frmts10 §A.3（如 MPEG: MP_MPEG2_LAYER 等，AC-3: AS_MODE 等——需要时查原文，此处从略）。

> 0x8xxx 段无官方预置值；厂商自定义格式走 WAVE_FORMAT_EXTENSIBLE 风格 GUID（UAC1 未定义，勿写 0x8xxx 编号）。Type III 的本质：把非 PCM 压缩流伪装成 16-bit PCM 过 IEC 60958，使老式同步机制可用（Frmts10 §2.3）。

## 6. UAC1 GET_STAT 中断机制（UAC1 §5.2.4.2）

- UAC1 **没有**音频控制中断端点；状态经 `GET_STAT (0xFF)` 轮询：bmRequestType=0xA1（接口）/0xA2（端点），wValue=0，wIndex=实体 ID+接口（或端点），Data = 状态消息（规范留空，当前应返回空包/短包）。

## 7. UAC2 CS_INTERFACE 描述符子类型全表（UAC2 §A.9/A.10）

**AudioControl (AC) 接口（A.9）：**

| 子类型 | 值 | 子类型 | 值 |
|---|---|---|---|
| AC_DESCRIPTOR_UNDEFINED | 0x00 | EXTENSION_UNIT | 0x09 |
| HEADER | 0x01 | CLOCK_SOURCE | 0x0A |
| INPUT_TERMINAL | 0x02 | CLOCK_SELECTOR | 0x0B |
| OUTPUT_TERMINAL | 0x03 | CLOCK_MULTIPLIER | 0x0C |
| MIXER_UNIT | 0x04 | SAMPLE_RATE_CONVERTER | 0x0D |
| SELECTOR_UNIT | 0x05 | — | — |
| FEATURE_UNIT | 0x06 | — | — |
| EFFECT_UNIT | 0x07 | — | — |
| PROCESSING_UNIT | 0x08 | — | — |

**AudioStreaming (AS) 接口（A.10）**：0x00 AS_DESCRIPTOR_UNDEFINED、0x01 AS_GENERAL、0x02 FORMAT_TYPE、0x03 ENCODER、0x04 DECODER。

## 8. UAC2 类特定请求码（A.14）与寻址

| bRequest | 值 | bmRequestType | 说明 |
|---|---|---|---|
| CUR | 0x01 | SET: 0x21/0x22；GET: 0xA1/0xA2 | 当前值（单值）。SET 面向控件/端点；GET 面向全部 |
| RANGE | 0x02 | GET: 0xA1/0xA2 | 代替 UAC1 的 MIN/MAX/RES：返回 wNumSubRanges + 各 {MIN,MAX,RES} 三元组 |
| MEM | 0x03 | SET: 0x21；GET: 0xA1 | 实体内存空间（wValue=零基偏移） |

- wValue = CS（高字节）+ CN（低字节，主控 CN=0）；Mixer 控件低字节为 MCN。
- wIndex = 接口号（低）+ 实体 ID（高）；端点控件时高字节为 0。
- 字节序：UAC2 多字节参数为**小端**（与 UAC1 相同，但 RANGE 布局是 2.0 新增）。
- 实体控制能力经 High Capability 描述符（bBitBitmapPerChannel 等）声明，不做"逐属性探测"。

**RANGE 参数块布局（§5.2.3）**：`wNumSubRanges(2, LE)` 后接每组 `{MIN, MAX, RES}` 三元组，宽度与该控制的 CUR 值一致——CS_SAM_FREQ 每项 4 字节 LE（如 {44100, 44100, 0} 表示单点）、FU_VOLUME 每项 2 字节。单值控制（如 MUTE）RANGE 通常返回 1 组 {0,1,0} 或 STALL；主机据此绘制可选值集合。

**UAC1 → UAC2 请求迁移速记**：SET_CUR/GET_CUR 保留；MIN/MAX/RES 三请求合并为 RANGE；SET_MEM/GET_MEM → MEM；GET_STAT(0xFF) → 中断端点消息（§10）；新增 SET 信息经 High Capability 描述符预声明，不再逐属性 GET 探测。

**值宽度备忘**：UAC1 端点 SAMPLING_FREQ_CONTROL 的 CUR 值为 **3 字节 LE**（0x01 控制），FU_VOLUME CUR 为 2 字节（正值=增益，负值=衰减，步进由 GET_RES 给出）；UAC2 的 CS_SAM_FREQ CUR 为 **4 字节 LE**——混用两代规范时的经典坑。

## 9. UAC2 实体控制选择子全表（A.17）

**Clock Source（A.17.1）**：`0x00 UNDEFINED`、`0x01 CS_SAM_FREQ_CONTROL`（CUR+RANGE）、`0x02 CS_CLOCK_VALID_CONTROL`（只读 CUR：0=无效 1=有效）。

**Clock Selector（A.17.2）**：`0x00 UNDEFINED`、`0x01 CX_CLOCK_SELECTOR_CONTROL`（CUR：当前选中的时钟源 1 基序号）。

**Clock Multiplier（A.17.3）**：`0x00 UNDEFINED`、`0x01 CM_NUMERATOR_CONTROL`、`0x02 CM_DENOMINATOR_CONTROL`。

**Terminal（A.17.4，IT/OT 通用）**：0x00 UNDEFINED、0x01 TE_COPY_PROTECT、0x02 TE_CONNECTOR、0x03 TE_OVERLOAD、0x04 TE_CLUSTER、0x05 TE_UNDERFLOW、0x06 TE_OVERFLOW、0x07 TE_LATENCY。

**Mixer（A.17.5）**：0x00 UNDEFINED、0x01 MU_MIXER、0x02 MU_CLUSTER、0x03 MU_UNDERFLOW、0x04 MU_OVERFLOW、0x05 MU_LATENCY。

**Selector（A.17.6）**：0x00 UNDEFINED、0x01 SU_SELECTOR、0x02 SU_LATENCY。

**Feature Unit（A.17.7，0x00~0x10）**：

| 控制号 | 名称 | | 控制号 | 名称 |
|---|---|---|---|---|
| 0x00 | FU_CONTROL_UNDEFINED | | 0x09 | FU_BASS_BOOST |
| 0x01 | FU_MUTE | | 0x0A | FU_LOUDNESS |
| 0x02 | FU_VOLUME | | 0x0B | FU_INPUT_GAIN |
| 0x03 | FU_BASS | | 0x0C | FU_INPUT_GAIN_PAD |
| 0x04 | FU_MID | | 0x0D | FU_PHASE_INVERTER |
| 0x05 | FU_TREBLE | | 0x0E | FU_UNDERFLOW（只读） |
| 0x06 | FU_GRAPHIC_EQUALIZER | | 0x0F | FU_OVERFLOW（只读） |
| 0x07 | FU_AUTOMATIC_GAIN | | 0x10 | FU_LATENCY（只读） |
| 0x08 | FU_DELAY | | — | — |

**Effect Unit（A.17.8，按效果类型分表）**：参数 EQ (PE)：ENABLE 0x01、CENTERFREQ 0x02、QFACTOR 0x03、GAIN 0x04 (+UNDERFLOW/OVERFLOW/LATENCY 0x05~0x07)；混响 (RV)：TYPE 0x02、LEVEL 0x03、TIME 0x04、FEEDBACK 0x05、PREDELAY 0x06、DENSITY 0x07、HIFREQ_ROLLOFF 0x08 (0x09~0x0B 状态)；调制延迟 (MD)：BALANCE 0x02、RATE 0x03、DEPTH 0x04、TIME 0x05；动态范围压缩 (DR)：COMPRESSION_RATE 0x02、MAXAMPL 0x03、THRESHOLD 0x04、ATTACK 0x05、RELEASE 0x06。效果类型码见 A.11（PARAM_EQ_SECTION 0x01、REVERBERATION 0x02、MOD_DELAY 0x03、DYN_RANGE_COMP 0x04）。

**Processing Unit（A.17.9）**：Up/Down-mix (UD)、Dolby Prologic (DP)、Stereo Extender (ST) 三类，均 ENABLE/MODE_SELECT + 状态位（UNDERFLOW/OVERFLOW/LATENCY），值表见 A.17.9 原文。

**Extension Unit（A.17.10）**：仅 0x00 UNDEFINED，其余厂商自定义。
**AudioStreaming 接口（A.17.11）**：0x00 UNDEFINED、0x01 AS_VALID_ALT_CONTROL、0x02 AS_ACT_ALT_CONTROL（只读：当前 alternate setting）。

## 9b. UAC2 其他类型码（A.11~A.13、A.15、A.16）

**Effect Unit 效果类型 wEffectType（A.11）**：0x00 EFFECT_UNDEFINED、0x01 PARAM_EQ_SECTION_EFFECT、0x02 REVERBERATION_EFFECT、0x03 MOD_DELAY_EFFECT、0x04 DYN_RANGE_COMP_EFFECT（Effect Unit 描述符 wEffectType 字段决定用 A.17.8 的哪张选择子表）。

**Processing Unit 过程类型 wProcessType（A.12）**：0x00 PROCESS_UNDEFINED、0x01 UP/DOWNMIX_PROCESS、0x02 DOLBY_PROLOGIC_PROCESS、0x03 STEREO_EXTENDER_PROCESS。

**端点描述符子类型（A.13）**：0x00 DESCRIPTOR_UNDEFINED、0x01 EP_GENERAL。

**编码器类型（A.15，AS ENCODER 描述符）**：0x00 UNDEFINED、0x01 OTHER、0x02 MPEG、0x03 AC-3、0x04 WMA、0x05 DTS；**解码器类型（A.16，AS DECODER 描述符）**：0x00 UNDEFINED、0x01 OTHER、0x02 MPEG、0x03 AC-3、0x04 WMA、0x05 DTS。

## 10. UAC2 中断数据消息（§6.1，Table 6-1，固定 6 字节）

| 偏移 | 字段 | 值 |
|---|---|---|
| 0 | bInfo | D0：0=类特定 / 1=厂商自定义；D1：0=来自接口内实体 / 1=来自端点；D7..2 保留 |
| 1 | bAttribute | 触发中断的属性：0x01 CUR / 0x02 RANGE / 0x03 MEM |
| 2 | wValue | CS（高）+ CN 或 MCN（低）；MEM 时为零基偏移，偏移 0 表示"多处变化需全查" |
| 4 | wIndex | 实体 ID 或 0（高）+ 接口号/端点号（低） |

要点：边沿触发，无需主机应答清位；中断仅通知，细节靠 GET 请求回查；无 pending 中断时端点 NAK。UAC1 的对应物是 GET_STAT 轮询（§6），两代机制完全不同。

## 相关节点

- 父分枝：[00-UAC概述.md](00-UAC概述.md)；实现：[01-UAC1.0详解.md](01-UAC1.0详解.md) / [02-UAC2与UAC3.md](02-UAC2与UAC3.md)
- 原文缓存：[../../80-参考资料/README.md](../../80-参考资料/README.md)（UAC-1.0.pdf、UAC-1.0-Formats.pdf、UAC-1.0-Terminals.pdf、UAC-2.0-final.zip）
