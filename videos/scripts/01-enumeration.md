# USB 枚举全过程 · 旁白与字幕稿

> 视频 `01-enumeration` · 时长约 1:34 · 场景源码 [../scenes/s01_enumeration.py](../scenes/s01_enumeration.py) · 成品 `site/public/videos/01-enumeration.mp4`
> 字幕由场景运行时自动记录（`USBScene.say()`），改字幕请改场景源码后重新渲染，再运行 `python3 videos/tools/gen_scripts.py`。

## 内容简介

从插入、去抖、复位，到读设备描述符、SET_ADDRESS、读配置描述符、SET_CONFIGURATION，主机与设备两条时间线逐步对照，附各步骤的规范时限。

## 旁白 / 字幕

| 时间 | 字幕 |
|---|---|
| 0:00 | USB 枚举全过程：从插入到 SET_CONFIGURATION，主机和设备各做了什么 |
| 0:06 | 设备插入：全速设备把 D+ 上拉，集线器检测到连接 |
| 0:11 | 主机至少去抖 100 ms，确认连接稳定、电源就绪 |
| 0:16 | 主机让集线器复位端口：总线保持 SE0 至少 10 ms |
| 0:21 | 复位结束后进入 Default 状态，地址为 0；主机再留 10 ms 恢复时间 |
| 0:28 | 在地址 0 上读设备描述符，目的是拿到端点 0 的最大包长 |
| 0:33 | 关键是偏移 7 的 bMaxPacketSize0；先要 64 字节是主机实现习惯，并非规范要求 |
| 0:42 | 主机发 SET_ADDRESS，给设备一个 1 到 127 的唯一地址 |
| 0:48 | 状态阶段完成后设备才切换地址：50 ms 内完成，再留 2 ms 恢复 |
| 0:54 | 之后所有请求都发往新地址：先读完整的 18 字节设备描述符 |
| 1:02 | 配置描述符分两次读：先读 9 字节拿总长，再一次读完整棵描述符树 |
| 1:08 | 最后 SET_CONFIGURATION(1)：端点就绪，设备进入 Configured 状态 |
| 1:16 | 此后设备可按 bMaxPower 取电，类驱动接管各个接口 |
| 1:22 | 一句话记住：去抖、复位、读包长、给地址、读描述符、选配置 |
| 1:29 | 规范出处：USB 2.0 规范 §9.1.1 图 9-1（设备状态）、§9.1.2（总线枚举步骤）；USB 2.0 §7.1.7.3 图 7-29（TATTDB 100 ms）、§7.1.7.5（TDRST ≥10 ms、TRSTRCY 10 ms）；USB 2.0 §9.2.6.2–9.2.6.3（复位恢复 10 ms；SET_ADDRESS 50 ms + 2 ms）；USB 2.0 §9.3 表 9-2、§9.4 表 9-4/9-5、§9.6.1 表 9-8 |

## 规范核对表

画面里出现的每个数字、编码和时序都对到了规范原文；“—”表示教学示例或主机实现习惯（画面中已注明）。

| 画面说法 | 出处 | 原文要点 / 说明 |
|---|---|---|
| 主机去抖 ≥ 100 ms（TATTDB） | USB 2.0 §7.1.7.3 图 7-29 Δt3 | debounce interval with a minimum duration of 100 ms |
| 复位 SE0 ≥ 10 ms（TDRST） | USB 2.0 §7.1.7.5 | the duration of each SE0 assertion must be at least 10 ms (TDRST) |
| 复位恢复 10 ms（TRSTRCY） | USB 2.0 §7.1.7.5、§9.2.6.2 | reset recovery time 10 ms (TRSTRCY) |
| Default 状态：地址 0、≤ 100 mA | USB 2.0 §9.1.2 第 4 步 | can draw no more than 100 mA from VBUS … answers to the default address |
| 先读设备描述符获知端点 0 最大包长 | USB 2.0 §9.1.2 第 6 步 | reads the device descriptor to determine what actual maximum data payload size |
| bMaxPacketSize0 在偏移 7；全速 8/16/32/64、高速 64、低速 8 | USB 2.0 §9.6.1 表 9-8、§5.5.3 | only 8, 16, 32, or 64 are valid |
| 首读 64 字节、再复位一次 | — | 主机实现习惯（Windows 等），规范未要求；画面已注明 |
| SET_ADDRESS 状态阶段 50 ms 内完成，之后 2 ms 恢复 | USB 2.0 §9.2.6.3 | within 50 ms … SetAddress() recovery interval of 2 ms |
| SETUP 字节 80 06 00 01 00 00 40 00 / 00 05 05 00… / 00 09 01 00… | USB 2.0 §9.3 表 9-2、表 9-4、表 9-5 | GET_DESCRIPTOR=6、SET_ADDRESS=5、SET_CONFIGURATION=9；DEVICE=1、CONFIGURATION=2 |
| 配置后按 bMaxPower 取电，切换位复位为 DATA0 | USB 2.0 §9.1.2 第 8 步、§8.5.2 | toggle sequence is initialized to DATA0 when the endpoint experiences any configuration event |

规范原文的官方下载地址见站点 [规范索引](https://usbtree.gumuhub.com/reference/specs/)。
