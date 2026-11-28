# Type-C CC 检测与 PD 协商 · 旁白与字幕稿

> 视频 `05-typec-pd` · 时长约 1:39 · 场景源码 [../scenes/s05_typec_pd.py](../scenes/s05_typec_pd.py) · 成品 `site/public/videos/05-typec-pd.mp4`
> 字幕由场景运行时自动记录（`USBScene.say()`），改字幕请改场景源码后重新渲染，再运行 `python3 videos/tools/gen_scripts.py`。

## 内容简介

Rp / Rd 分压如何告诉 Sink 默认 / 1.5 A / 3.0 A，tCCDebounce 后输出 VBUS，再用 Source_Capabilities → Request → Accept → PS_RDY 建立 9 V 显式契约，并标出关键定时器。

## 旁白 / 字幕

| 时间 | 字幕 |
|---|---|
| 0:00 | Type-C CC 检测与 PD 协商：一根 CC 线：先靠电阻分压认出彼此，再用 BMC 谈好电压 |
| 0:04 | Source 在 CC 上接上拉电阻 Rp，Sink 接 5.1 kΩ 下拉电阻 Rd |
| 0:11 | Rp 的阻值告诉 Sink 能取多大电流：分压落在哪个区间，就是哪档 |
| 0:17 | 另一根 CC 悬空，因此还能顺便判断插头是正插还是反插 |
| 0:22 | CC 状态稳定 tCCDebounce（100～200 ms）后，Source 才打开 VBUS 输出 5 V |
| 0:32 | VBUS 有了 5 V，双方开始在 CC 上用 BMC 编码（约 300 kbps）交换 PD 消息 |
| 0:40 | 每条消息对方都要回 GoodCRC；Source 每 100～200 ms 重发能力，直到收到 GoodCRC |
| 0:49 | Sink 从列表里挑一档，用 Request 请求：这里选 #2，9 V / 3 A |
| 0:56 | Sink 发出 Request 后最多等 tSenderResponse（27～50 ms），Source 回 Accept |
| 1:06 | 随后 Source 把电压从 5 V 调到 9 V |
| 1:10 | 调好后发 PS_RDY；Sink 等 PS_RDY 的上限是 tPSTransition（450～550 ms） |
| 1:19 | 收到 PS_RDY，显式契约建立，Sink 可以按 9 V / 3 A 取电 |
| 1:27 | 先电阻、后消息：这就是 Type-C 充电器“认出”设备并升压的全过程 |
| 1:34 | 规范出处：USB Type-C R2.5 表 4-27（Rp）、表 4-28（Rd）、表 4-34（tCCDebounce）、表 4-36（vRd 区间）；USB PD R3.3 §5.5.1（BMC fBitRate 270～330 kbps）；USB PD R3.3 表 6.4 / 表 6.5（控制 / 数据消息类型编码）；USB PD R3.3 §7.31 表 7.10（tTypeCSendSourceCap、tSenderResponse、tPSTransition） |

## 规范核对表

画面里出现的每个数字、编码和时序都对到了规范原文；“—”表示教学示例或主机实现习惯（画面中已注明）。

| 画面说法 | 出处 | 原文要点 / 说明 |
|---|---|---|
| Rp 上拉到 5 V：56 k / 22 k / 10 kΩ；Rd = 5.1 kΩ | USB Type-C R2.5 表 4-27、表 4-28 | — |
| vRd 区间（Rd ±10%）：默认 0.277–0.612 V、1.5 A 0.746–1.164 V、3.0 A 1.369–2.042 V | USB Type-C R2.5 表 4-36 | 画面电压值按 5 V × 5.1/(Rp+5.1) 计算：0.42 / 0.94 / 1.69 V |
| tCCDebounce 100–200 ms | USB Type-C R2.5 表 4-34 | — |
| BMC 约 300 kbps | USB PD R3.3 §5.5.1 | fBitRate 270 / 300 / 330 Kbps |
| Source_Capabilities 00001b、Request 00010b（数据消息） | USB PD R3.3 表 6.5 | — |
| GoodCRC 00001b、Accept 00011b、PS_RDY 00110b（控制消息） | USB PD R3.3 表 6.4 | — |
| tTypeCSendSourceCap 100–200 ms | USB PD R3.3 表 7.10 | min 100 / nom 150 / max 200 ms |
| tSenderResponse 27–50 ms | USB PD R3.3 表 7.10 | min 27 / max 50 ms（R3.3 数值） |
| tPSTransition 450–550 ms（SPR） | USB PD R3.3 表 7.10 | SPR Mode 450 / 500 / 550 ms |
| PDO 列表 5/9/15/20 V × 3 A | — | 教学示例，非某款产品 |

规范原文的官方下载地址见站点 [规范索引](https://usbtree.gumuhub.com/reference/specs/)。
