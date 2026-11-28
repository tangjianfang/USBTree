# HID 报告描述符解析 · 旁白与字幕稿

> 视频 `04-hid-report` · 时长约 1:40 · 场景源码 [../scenes/s04_hid_report.py](../scenes/s04_hid_report.py) · 成品 `site/public/videos/04-hid-report.mp4`
> 字幕由场景运行时自动记录（`USBScene.say()`），改字幕请改场景源码后重新渲染，再运行 `python3 videos/tools/gen_scripts.py`。

## 内容简介

用 HID 1.11 附录 E.10 的启动鼠标描述符，逐个字节拆出前缀（bTag/bType/bSize），演示解析器状态如何变化、3 字节输入报告如何排布，并解读一条真实报告。

## 旁白 / 字幕

| 时间 | 字幕 |
|---|---|
| 0:00 | HID 报告描述符解析：以规范附录里的启动鼠标为例：50 个字节如何变成 3 字节报告 |
| 0:04 | 这是 HID 1.11 附录 E.10 给出的鼠标报告描述符，一共 50 个字节 |
| 0:11 | 每个短 Item 的第一个字节是前缀：bTag 4 位、bType 2 位、bSize 2 位 |
| 0:19 | bType 区分 Main、Global、Local 三类；bSize 说明后面跟几个数据字节 |
| 0:28 | 解析器自上而下读 Item：Global 更新全局状态，Local 只对下一个 Main 有效 |
| 0:35 | 先声明用途：Generic Desktop 页里的 Mouse，再开 Application 和 Physical 两层集合 |
| 0:45 | 三个按键：每个 1 位、取值 0/1，Report Count 3 × Report Size 1 |
| 0:53 | 再补 5 个常量位，把按键凑成完整的 1 个字节 |
| 0:57 | X、Y 各 8 位，取值 −127～127，Input 标记为相对量 |
| 1:05 | 两个 End Collection 收尾，描述符结束 |
| 1:09 | 每个 Main Item 之后 Local 状态清空，Global 状态一直保留到被改写 |
| 1:18 | 设备发来 3 个字节：01 05 FB |
| 1:22 | HUT 规定 Y 值随“由远及近”增大（屏幕上向下），所以 −5 是向上 |
| 1:29 | 掌握这四条，就能手工读懂任何 HID 报告描述符 |
| 1:35 | 规范出处：HID 1.11 §6.2.2.2（短 Item：bSize / bType / bTag）；HID 1.11 §6.2.2.4–§6.2.2.8（Main / Global / Local Item 与 Input 标志位）；HID 1.11 附录 B.2（启动鼠标报告格式）、附录 E.10（鼠标报告描述符字节）；HID Usage Tables 1.7 §4.2（X 由左到右增大、Y 由远及近增大） |

## 规范核对表

画面里出现的每个数字、编码和时序都对到了规范原文；“—”表示教学示例或主机实现习惯（画面中已注明）。

| 画面说法 | 出处 | 原文要点 / 说明 |
|---|---|---|
| 前缀字节 bTag 4 位 · bType 2 位 · bSize 2 位；bSize 3 表示 4 字节 | HID 1.11 §6.2.2.2 | 0 = 0 bytes … 3 = 4 bytes |
| bType 0 Main / 1 Global / 2 Local | HID 1.11 §6.2.2.2 | — |
| 50 字节描述符逐字节 | HID 1.11 附录 E.10 | 05 01 09 02 A1 01 … C0 C0 |
| Input 标志位：bit0 Data/Constant、bit1 Array/Variable、bit2 Absolute/Relative | HID 1.11 §6.2.2.4 | 81 02 / 81 01 / 81 06 |
| Main Item 之后 Local 状态清空，Global 保留 | HID 1.11 §6.2.2.8 | Local items only describe the data fields defined by the next Main item |
| 报告格式：字节 0 按键 1–3、字节 1 X、字节 2 Y | HID 1.11 附录 B.2 | — |
| X 由左到右增大、Y 由远及近增大 | HID Usage Tables 1.7 §4.2 | Report values should increase as the control's position is moved from far to near |
| 示例报告 01 05 FB | — | 教学示例，非规范数据 |

规范原文的官方下载地址见站点 [规范索引](https://usbtree.gumuhub.com/reference/specs/)。
