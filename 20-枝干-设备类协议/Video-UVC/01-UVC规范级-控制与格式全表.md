---
title: "UVC 规范级附录：控制选择子、请求码与格式全表"
layer: 枝干/设备类协议
section: Video-UVC
doc-path: 20-枝干-设备类协议/Video-UVC/01-UVC规范级-控制与格式全表.md
---
# UVC 规范级附录：控制选择子、请求码与格式全表

> 🌿 知识树位置: 树干 → 枝干[设备类] → 分枝[UVC] → 附录[规范级速查]
> ⬆️ 父节点: [00-UVC详解.md](00-UVC详解.md)
> 📖 全部数值提取自 **UVC 1.5 Class specification**（附录 A 代码表、§2.4.2 状态中断、§4 控制请求）与 **UVC 1.5 各 Payload 白皮书**（Uncompressed/MJPEG/H.264/Frame-Based），缓存见 [../../80-参考资料/README.md](../../80-参考资料/README.md)。设备模型与枚举叙述见详解篇，本文只放编号。

## 1. 类代码、子类与描述符子类型（UVC 1.5 附录 A.1~A.7）
> 🔍 对抗抽查（evolve #20）：VS_PROBE_CONTROL=0x01、VS_COMMIT_CONTROL=0x02（Table A-16）与 UVC 1.5 原文比对一致。


| 代码名 | 值 | 用途 |
|---|---|---|
| CC_VIDEO | 0x0E | 接口类代码 (bInterfaceClass) |
| SC_UNDEFINED / SC_VIDEOCONTROL / SC_VIDEOSTREAMING / SC_VIDEO_INTERFACE_COLLECTION | 0x00 / 0x01 / 0x02 / 0x03 | 子类代码 (A.2) |
| PC_PROTOCOL_UNDEFINED / PC_PROTOCOL_15 | 0x00 / 0x01 | bInterfaceProtocol（1.5 设备应为 0x01）(A.3) |
| CS_UNDEFINED / CS_DEVICE / CS_CONFIGURATION / CS_STRING / CS_INTERFACE / CS_ENDPOINT | 0x20 / 0x21 / 0x22 / 0x23 / 0x24 / 0x25 | 类特定描述符类型 (A.4) |

**VC 接口描述符子类型（A.5）：** `0x00 VC_DESCRIPTOR_UNDEFINED`、`0x01 VC_HEADER`、`0x02 VC_INPUT_TERMINAL`、`0x03 VC_OUTPUT_TERMINAL`、`0x04 VC_SELECTOR_UNIT`、`0x05 VC_PROCESSING_UNIT`、`0x06 VC_EXTENSION_UNIT`、`0x07 VC_ENCODING_UNIT`。

**VS 接口描述符子类型（A.6）：**

| 子类型 | 值 | 子类型 | 值 |
|---|---|---|---|
| VS_UNDEFINED | 0x00 | VS_FORMAT_DV | 0x0C |
| VS_INPUT_HEADER | 0x01 | VS_COLORFORMAT | 0x0D |
| VS_OUTPUT_HEADER | 0x02 | 保留 | 0x0E / 0x0F |
| VS_STILL_IMAGE_FRAME | 0x03 | VS_FORMAT_FRAME_BASED | 0x10 |
| VS_FORMAT_UNCOMPRESSED | 0x04 | VS_FRAME_FRAME_BASED | 0x11 |
| VS_FRAME_UNCOMPRESSED | 0x05 | VS_FORMAT_STREAM_BASED | 0x12 |
| VS_FORMAT_MJPEG | 0x06 | VS_FORMAT_H264 | 0x13 |
| VS_FRAME_MJPEG | 0x07 | VS_FRAME_H264 | 0x14 |
| 保留 | 0x08 / 0x09 | VS_FORMAT_H264_SIMULCAST | 0x15 |
| VS_FORMAT_MPEG2TS | 0x0A | VS_FORMAT_VP8 / VS_FRAME_VP8 / VS_FORMAT_VP8_SIMULCAST | 0x16 / 0x17 / 0x18 |
| 保留 | 0x0B | — | — |

**VS 端点描述符子类型（A.7）：** `0x00 EP_UNDEFINED`、`0x01 EP_GENERAL`、`0x02 EP_ENDPOINT`、`0x03 EP_INTERRUPT`。

## 2. 类特定请求码（A.8，bmRequestType：SET=0x21/0x22，GET=0xA1/0xA2）

| 请求码 | 值 | 请求码 | 值 |
|---|---|---|---|
| RC_UNDEFINED | 0x00 | GET_CUR | 0x81 |
| SET_CUR | 0x01 | GET_MIN | 0x82 |
| SET_CUR_ALL | 0x11 | GET_MAX | 0x83 |
| — | — | GET_RES | 0x84 |
| — | — | GET_LEN | 0x85 |
| — | — | GET_INFO | 0x86 |
| — | — | GET_DEF | 0x87 |
| — | — | GET_CUR_ALL / GET_MIN_ALL / GET_MAX_ALL / GET_RES_ALL / GET_DEF_ALL | 0x91 / 0x92 / 0x93 / 0x94 / 0x97 |

寻址规则（§4.1）：

- wValue 高字节 = Control Selector（CS），低字节 = Unit/Terminal 内通道号（通常 0）。
- wIndex 低字节 = 接口号或端点号，高字节 = **实体 ID**（bUnitID/bTerminalID；寻址接口本身时填 0）。
- SET 只支持 CUR 属性；GET 可取 CUR/MIN/MAX/RES/LEN/INFO/DEF。
- bmRequestType：控制接口 `0x21/0xA1`；VS 接口 `0x21/0xA1`；VS 数据端点 `0x22/0xA2`。

**GET_INFO 能力位（Table 4-3）**：D0=支持 GET、D1=支持 SET（能力位）；D2=因自动模式禁用、D5=与 Commit 状态不兼容而禁用（状态位）；D3=Autoupdate 控件、D4=异步控件（能力位）；D6~D7 保留。支持 D2/D5 的设备必须具备状态中断能力（D3=1）。

## 3. VC 接口控制选择子（A.9.1）

| 选择子 | 值 |
|---|---|
| VC_CONTROL_UNDEFINED | 0x00 |
| VC_VIDEO_POWER_MODE_CONTROL | 0x01 |
| VC_REQUEST_ERROR_CODE_CONTROL | 0x02 |
| 保留 | 0x03 |

`VC_REQUEST_ERROR_CODE_CONTROL`（GET_CUR，1 字节）返回上一次出错请求的 originating unit/terminal ID；无错时为 0（§4.2.1）。VC_VIDEO_POWER_MODE 仅 SET_CUR/GET_CUR（0=暂停，1=运行）。

## 4. Camera Terminal 控制选择子全表（A.9.4，wValue 高字节 = CS，实体 = 输入终端）

| 选择子 | 值 | 典型请求集 |
|---|---|---|
| CT_CONTROL_UNDEFINED | 0x00 | — |
| CT_SCANNING_MODE_CONTROL | 0x01 | GET_CUR/MIN/MAX/RES/DEF/INFO, SET_CUR |
| CT_AE_MODE_CONTROL | 0x02 | 同上（位图：D0 手动，D1 光圈优先，D2 快门优先，D3 自动） |
| CT_AE_PRIORITY_CONTROL | 0x03 | 同上 |
| CT_EXPOSURE_TIME_ABSOLUTE_CONTROL | 0x04 | 同上（单位 100 µs） |
| CT_EXPOSURE_TIME_RELATIVE_CONTROL | 0x05 | 同上 |
| CT_FOCUS_ABSOLUTE_CONTROL | 0x06 | 同上 |
| CT_FOCUS_RELATIVE_CONTROL | 0x07 | 同上（+ GET_SPEED 类扩展，D0~D2 方向位） |
| CT_FOCUS_AUTO_CONTROL | 0x08 | 同上（0/1 开关） |
| CT_IRIS_ABSOLUTE_CONTROL | 0x09 | 同上（f 数 ×100） |
| CT_IRIS_RELATIVE_CONTROL | 0x0A | 同上 |
| CT_ZOOM_ABSOLUTE_CONTROL | 0x0B | 同上（焦距 ×100 mm） |
| CT_ZOOM_RELATIVE_CONTROL | 0x0C | 同上 |
| CT_PANTILT_ABSOLUTE_CONTROL | 0x0D | 同上（8 字节：Pan 4B + Tilt 4B，角度 ×0.1°） |
| CT_PANTILT_RELATIVE_CONTROL | 0x0E | 同上 |
| CT_ROLL_ABSOLUTE_CONTROL | 0x0F | 同上 |
| CT_ROLL_RELATIVE_CONTROL | 0x10 | 同上 |
| CT_PRIVACY_CONTROL | 0x11 | 同上（0/1 遮蔽） |
| CT_FOCUS_SIMPLE_CONTROL | 0x12 | 同上 |
| CT_WINDOW_CONTROL | 0x13 | 同上（32 字节窗口结构） |
| CT_REGION_OF_INTEREST_CONTROL | 0x14 | 同上（ROI 设置） |

> 请求集"同上"为 §4.2.2.1 各控制通用框架：SET_CUR + GET_CUR/MIN/MAX/RES/DEF/INFO；个别控制有附加字段（如相对控制的 SPEED），以 §4.2.2.1 原文为准。

## 5. Processing Unit 控制选择子全表（A.9.5，PU_* 0x00~0x13）

| 选择子 | 值 | 选择子 | 值 |
|---|---|---|---|
| PU_CONTROL_UNDEFINED | 0x00 | PU_WHITE_BALANCE_COMPONENT_CONTROL | 0x0C |
| PU_BACKLIGHT_COMPENSATION_CONTROL | 0x01 | PU_WHITE_BALANCE_COMPONENT_AUTO_CONTROL | 0x0D |
| PU_BRIGHTNESS_CONTROL | 0x02 | PU_DIGITAL_MULTIPLIER_CONTROL | 0x0E |
| PU_CONTRAST_CONTROL | 0x03 | PU_DIGITAL_MULTIPLIER_LIMIT_CONTROL | 0x0F |
| PU_GAIN_CONTROL | 0x04 | PU_HUE_AUTO_CONTROL | 0x10 |
| PU_POWER_LINE_FREQUENCY_CONTROL | 0x05 | PU_ANALOG_VIDEO_STANDARD_CONTROL | 0x11 |
| PU_HUE_CONTROL | 0x06 | PU_ANALOG_LOCK_STATUS_CONTROL | 0x12 |
| PU_SATURATION_CONTROL | 0x07 | PU_CONTRAST_AUTO_CONTROL | 0x13 |
| PU_SHARPNESS_CONTROL | 0x08 | —（UVC 1.5 止于 0x13；网络上常见的 0x14+ 为未定值，勿引用） | — |
| PU_GAMMA_CONTROL | 0x09 | — | — |
| PU_WHITE_BALANCE_TEMPERATURE_CONTROL | 0x0A | — | — |
| PU_WHITE_BALANCE_TEMPERATURE_AUTO_CONTROL | 0x0B | — | — |

请求框架同 §4：无符号量（亮度等）可带 MIN/MAX/RES/DEF；POWER_LINE_FREQUENCY 取 0=禁用/1=50Hz/2=60Hz；ANALOG_VIDEO_STANDARD 取 0~6（None/NTSC/PAL/SECAM/NTSC-M/PAL-M/PAL-N 组合，§4.2.2.2）。

## 6. Encoding Unit 控制选择子全表（A.9.6，EU_*，H.264 编码器用）

| 选择子 | 值 | 选择子 | 值 |
|---|---|---|---|
| EU_CONTROL_UNDEFINED | 0x00 | EU_AVERAGE_BITRATE_CONTROL | 0x07 |
| EU_SELECT_LAYER_CONTROL | 0x01 | EU_CPB_SIZE_CONTROL | 0x08 |
| EU_PROFILE_TOOLSET_CONTROL | 0x02 | EU_PEAK_BIT_RATE_CONTROL | 0x09 |
| EU_VIDEO_RESOLUTION_CONTROL | 0x03 | EU_QUANTIZATION_PARAMS_CONTROL | 0x0A |
| EU_MIN_FRAME_INTERVAL_CONTROL | 0x04 | EU_SYNC_REF_FRAME_CONTROL | 0x0B |
| EU_SLICE_MODE_CONTROL | 0x05 | EU_LTR_BUFFER_CONTROL / EU_LTR_PICTURE_CONTROL / EU_LTR_VALIDATION_CONTROL | 0x0C / 0x0D / 0x0E |
| EU_RATE_CONTROL_MODE_CONTROL | 0x06 | EU_LEVEL_IDC_LIMIT_CONTROL 0x0F、EU_SEI_PAYLOADTYPE_CONTROL 0x10、EU_QP_RANGE_CONTROL 0x11、EU_PRIORITY_CONTROL 0x12、EU_START_OR_STOP_LAYER_CONTROL 0x13、EU_ERROR_RESILIENCY_CONTROL 0x14 | 0x0F~0x14 |

EU 控制多为编码器配置型（SET_CUR + GET_*）；`EU_SELECT_LAYER`/`EU_START_OR_STOP_LAYER` 是 SVC 分层流控键（§4.2.2.4）。

## 7. Selector / Extension Unit 控制框架（§2.3.4 / §2.3.7 / §4.2.2.2 / §4.2.2.5）

- **Selector Unit (SU)**：仅一个控制 `SU_INPUT_SELECT_CONTROL`（CS=0x01），SET_CUR/GET_CUR 选择上游输入引脚（1 基编号）；无 MIN/MAX/RES/DEF 语义。
- **Extension Unit (XU)**：厂商自定义控制，选择子由厂商在 XU 描述符的 bControlSize/bmControls 位图中声明（A.9.7 仅定义 `XU_CONTROL_UNDEFINED=0x00`，其余全为厂商值）；主机用 `bUnitID + CS` 寻址，GUID 标识扩展功能集。帧计数/厂商开关等均走此通道。

## 8. VS 接口控制选择子全表（A.9.8，寻址 VS 接口，无实体 ID）

| 选择子 | 值 | 请求集 | wLength |
|---|---|---|---|
| VS_CONTROL_UNDEFINED | 0x00 | — | — |
| VS_PROBE_CONTROL | 0x01 | SET_CUR、GET_CUR/DEF/MIN/MAX(部分)/LEN/INFO | 26（1.5 设备 34/48，见下） |
| VS_COMMIT_CONTROL | 0x02 | SET_CUR、GET_CUR/INFO | 26/34/48 |
| VS_STILL_PROBE_CONTROL | 0x03 | 同 PROBE | 26/34 |
| VS_STILL_COMMIT_CONTROL | 0x04 | SET_CUR、GET_CUR/INFO | 26/34 |
| VS_STILL_IMAGE_TRIGGER_CONTROL | 0x05 | SET_CUR（0=普通，1=待触发，2=Abort…§4.2.3.5）、GET_CUR | 1 |
| VS_STREAM_ERROR_CODE_CONTROL | 0x06 | GET_CUR、GET_INFO | 1 |
| VS_GENERATE_KEY_FRAME_CONTROL | 0x07 | SET_CUR、GET_CUR/INFO（H.264 用） | 1 |
| VS_UPDATE_FRAME_SEGMENT_CONTROL | 0x08 | SET_CUR、GET_CUR/INFO（H.264 用） | 变长 |
| VS_SYNCH_DELAY_CONTROL | 0x09 | SET_CUR、GET_CUR/INFO（单位 ms） | 2 |

> Probe/Commit 参数块：26 字节（基础）→ UVC 1.5 扩展至 34（+bmHint 扩展/delay/frame 计数）→ 48（H.264/VP8 加 dwClockFrequency 等字段）；wLength 随设备声明。dwFrameInterval 单位 **100 ns**（如 30fps=333333）。完整字段布局见详解篇与 §4.3.1.1。

## 9. 状态中断包结构（§2.4.2.2，Table 2-1/2-2/2-3）

**公共头：**

| 偏移 | 字段 | 值 |
|---|---|---|
| 0 | bStatusType | D3..0 Originator：0=保留，1=VideoControl 接口，2=VideoStreaming 接口；D7..4 保留 |
| 1 | bOriginator | 报告中断的 Terminal/Unit/接口 ID |

**Originator = VC 接口时（Table 2-2）：**

| 偏移 | 字段 | 值 |
|---|---|---|
| 2 | bEvent | 0x00=Control Change；0x01~0xFF 保留 |
| 3 | bSelector | 触发中断的 Control Selector |
| 4 | bAttribute | 0x00=值变更(GET_CUR)、0x01=信息变更(GET_INFO)、0x02=失败变更(错误码)、0x03=MIN 变更、0x04=MAX 变更、0x05~0xFF 保留 |
| 5 | bValue[n] | 变更后的属性值（长度同该控制 GET 请求） |

**Originator = VS 接口时（Table 2-3）：**

| 偏移 | 字段 | 值 |
|---|---|---|
| 2 | bEvent | 0x00=Button Press（拍照硬按键）；0x01~0xFF=Stream Error |
| 3 | bValue[n] | Button：n=1，0x00=释放 / 0x01=按下。Stream Error：n=1，bValue=bStreamErrorCode（见 §10） |

要点：异步控件（Async）或 Autoupdate 控件完成 SET_CUR 后 ≤10 ms 内必须发 Control Change 中断；硬件快门按钮经 VS 中断上报（§2.4.2.3）。

## 10. VS_STREAM_ERROR_CODE 值表（§4.2.3.5，Table 4-85）

| bStreamErrorCode | 含义 |
|---|---|
| 0 | 无错误 |
| 1 | 受保护内容（只发空包头） |
| 2 | 输入缓冲欠载（源端供数不足，发空包头） |
| 3 | 数据不连续（坏介质/编码器错误） |
| 4 | 输出缓冲欠载（汇端供数不足） |
| 5 | 输出缓冲过载 |
| 6 | 格式变更（动态换格式事件） |
| 7 | 静帧捕获错误 |

载荷头里的 error bit（bit6）只能报"有错"，具体原因须靠本控制或中断包获得。

## 11. 未压缩格式 GUID 常用表（Uncompressed Payload 1.5，Table 2-1）

| 格式 | GUID | 说明 |
|---|---|---|
| YUY2 | `32595559-0000-0010-8000-00AA00389B71` | 打包 4:2:2 |
| NV12 | `3231564E-0000-0010-8000-00AA00389B71` | 平面 4:2:0 |
| M420 | `3032344D-0000-0010-8000-00AA00389B71` | 打包 4:2:0 |
| I420 | `30323449-0000-0010-8000-00AA00389B71` | 平面 4:2:0 |
> 🔍 对抗抽查（evolve #36）：四个官方 GUID（YUY2/NV12/M420/I420）与 Uncompressed Payload 1.5 白皮书逐字符比对一致。


规则：GUID 前 4 字节 = 格式 FourCC 的 ASCII 小端序，余 12 字节固定 `0000-0010-8000-00AA00389B71`（该尾缀为 DirectShow/MediaFoundation 基底模板，1.5 白皮书 Table 2-1 仅官方列出上述四种 YUV；其他如 YV12/RGB 变体 GUID 不在 1.5 白皮书中，勿在合规描述符里臆造）。

## 12. 格式/帧描述符差异对比（Uncompressed vs MJPEG vs Frame-Based vs H.264）

| 维度 | Uncompressed (0x04/0x05) | MJPEG (0x06/0x07) | Frame-Based (0x10/0x11) | H.264 (0x13/0x14, Simulcast 0x15) |
|---|---|---|---|---|
| 格式标识 | guidFormat（16B GUID，§11 表） | 无 GUID（隐含 JPEG）；描述符含 bmFlags（D0=FixedSizeSamples） | guidFormat（16B GUID，厂商/标准 FourCC 均可） | 无 GUID；bLength 固定 **52** |
| 特有字段 | bBitsPerPixel；可选 VS_COLORFORMAT(0x0D) 声明色彩空间 | bmFlags、bDefaultFrameIndex | bBitsPerPixel、bDefaultFrameIndex | bMaxCodecConfigDelay、bmSupportedSliceModes、bmSupportedSyncFrameTypes、bScalingListFlag、bSkipPictureFlag、bSupportedMaxMBpersc、bmSupportedSliceSizes…（编码器能力声明） |
| 公共字段 | bFormatIndex、bNumFrameDescriptors、bAspectRatioX/Y、bmInterlaceFlags、bCopyProtect、bVariableSize(H.264 无；Frame-Based 有) 同左 同左 | 同左 | 同左 | 同左（另含 bNumClockFreq/bClockFrequency 段与 bNumFrameDurationTypes 变长帧率表） |
| 帧描述符 | VS_FRAME_*：dwFrameInterval 表（100ns），D0~D3 位型索引 | 同左 | 同左 | 同左 + simulcast 需独立 FORMAT_H264_SIMULCAST 组 |
| 典型载荷头 | 12B 头：EoH/ERR/FID/IPSR/Presentation 位 + dwPresentationTime + dwSourceClock | 同 Uncompressed 头 + Q 位（Q=0 绝对/1 相对 JPEG 质量）+ bQuality | 同 Uncompressed 头 | 同 Frame-Based 头语义，SOF/EOF + PTS/SCR |
| 白皮书章节 | Uncompressed 1.5 §3 | MJPEG 1.5 §3 | Frame-Based 1.5 §3 | H.264 1.5 §3 |

其余载荷（DV 0x0C、MPEG2-TS 0x0A、Stream-Based 0x12、VP8 0x16）各自有独立白皮书，格式细节超出本表范围。

## 相关节点

- 父分枝：[00-UVC详解.md](00-UVC详解.md)（设备模型、Probe/Commit 状态机、枚举流程）
- 原文缓存：[../../80-参考资料/README.md](../../80-参考资料/README.md)（UVC-1.5.zip 含主规范 + 8 份 Payload 白皮书）
- 同级附录：HID/UAC/CDC/MSC 规范级速查见各分枝 `*规范级*` 文件
