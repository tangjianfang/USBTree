---
title: 如何阅读本站
description: 页头标记、难度分级、待核实标注、速查卡与图谱的用法，以及本站内容从哪里来。
topic: guide
level: 1
---

## 页头的信息

每篇文档标题下方有一行元信息和一个关系框：

| 标记 | 含义 |
|---|---|
| <span class="lvl lvl-1">L1 入门</span> <span class="lvl lvl-2">L2 基础</span> <span class="lvl lvl-3">L3 进阶</span> <span class="lvl lvl-4">L4 专家</span> | 难度分级。L4 多为“规范级 / 全表 / 附录”，适合查而不是通读 |
| ⏱ 约 N 分钟 | 按正文字数估算的阅读时长（不含代码块） |
| 更新于 | 源文件在仓库里最近一次提交的日期 |
| ✔ 规范核对 | tech-doc 文档对照官方规范最后核对的日期 |
| <span class="tbv">待核实</span> | 官方资料里没找到原文依据的说法，不要当定论引用 |
| ↩ 前置阅读 | 建议先读的文档（来自知识树“上一叶”与图谱的前置关系） |
| 🧪 动手实验 | 这篇讲的概念在 [usb-labs](page:labs) 里有对应实现 |
| § 规范出处 | 本篇引用的官方规范或平台文档，链接都指向发布方官网 |

## 搜索

顶部搜索（快捷键 <kbd>/</kbd> 或 <kbd>Ctrl</kbd>+<kbd>K</kbd>）是全站离线索引，中文按词切分，字段名（`bInterval`、`bMaxPacketSize0`）、缩写（`LLCP`、`HOGP`）和中文术语（描述符、枚举）都能搜。

## 图表

Mermaid 图右上角有 **⤢ 放大**：可以全屏查看，滚轮或双指缩放、拖动平移。

## 内容从哪来

- **知识树正文**（10–90 目录）与 **规范精读**（tech-doc）都来自 [USBTree 仓库](https://github.com/tangjianfang/USBTree)，网站在构建时直接从仓库 Markdown 生成，不另外维护一份。每页右上的“源文件”可以跳到 GitHub。
- **实验室**页是对 [usb-labs](https://github.com/tangjianfang/usb-labs) 代码的摘要，源码链接固定在某个提交上，行号不会漂移。
- **速查卡**按章节从正文原样摘取；**知识图谱**来自 `graph/*.yaml`。
- 规范原文（PDF/ZIP）受 USB-IF / Bluetooth SIG 许可约束，不随本站分发，[规范索引](page:reference/specs)里是官方下载地址。
