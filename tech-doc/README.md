# 规范可追溯知识库（tech-doc）

本目录是**官方规范可追溯的结构化知识库**，并附同名 **HTML 阅读版**。正文用 [tech-doc](https://github.com/tangjianfang/tech-doc) 技能按 Reverse 模式从官方规范与平台文档整理，每条事实尽量标到章节、表号或官方页面。浏览器直接打开同名 `.html` 即可离线阅读（图嵌在页面里，不依赖外链图片）。

人读的学习路径仍以仓库根目录的知识树为准。本目录用来核对「这句话出自哪一节」。

## 和正文、ai-kb 的关系

| | 知识树（`10`–`90`） | [ai-kb/](../ai-kb/README.md) | tech-doc/（本目录） |
|---|---|---|---|
| 给谁 | 按树干/枝干研读 | 代理按主题检索 | 要回溯官方出处、或要 HTML 阅读版 |
| 材料从哪来 | 本仓库正文 | `tools/ai-kb/build_kb.py` 从正文清洗 | tech-doc 技能从规范原文与平台官方文档整理 |
| 数字冲突时 | 学习叙述以正文为主 | 官方规范 > 主题里的核心事实 > 清洗后的原文 | 以本库引用的规范原文为准 |
| `validate.sh` | 内容页与篇数 | 不计入 | 不计入内容页与篇数；站内链接仍检查 |

`00-README.md` 里的 `/workspace/usb-specs`、`/workspace/usb-os-kb-src` 是整理时的规范缓存路径，不在本仓库中。仓库内的阅读入口是本文件和下面的 13 篇。

## 结构

| 路径 | 作用 |
|---|---|
| [00-README.md](00-README.md) · [HTML](00-README.html) | 知识库索引、文档表、原始工作区说明 |
| [01-usb2-ch9-control.md](01-usb2-ch9-control.md) | USB 2.0 / 3.2 第 9 章：标准请求、描述符、枚举 |
| [02-hid-class-hogp.md](02-hid-class-hogp.md) | HID 类请求与 HID over GATT |
| [03-usb-pd-messages-timers.md](03-usb-pd-messages-timers.md) | USB PD R3.3：消息头、消息类型、定时器 |
| [04-bc12-charger-detection.md](04-bc12-charger-detection.md) | BC 1.2：SDP / CDP / DCP |
| [05-ble-llcp-ifs.md](05-ble-llcp-ifs.md) | BLE 链路层控制过程与帧间隔 |
| [06-linux-virtual-usb.md](06-linux-virtual-usb.md) | USB/IP、ConfigFS、FunctionFS、Raw Gadget |
| [07-linux-usb-stack.md](07-linux-usb-stack.md) | Linux 主机栈、HID、gadget、dummy_hcd |
| [08-arm-embedded-usb.md](08-arm-embedded-usb.md) | ARM SoC 控制器、设备树、双角色、TinyUSB |
| [09-macos-usb.md](09-macos-usb.md) | macOS：IOKit、DriverKit、HID |
| [10-ios-ipados-usb.md](10-ios-ipados-usb.md) | iOS / iPadOS：MFi、DriverKit、配件 |
| [11-android-usb.md](11-android-usb.md) | Android：Host API、AOA、Gadget HAL |
| [12-cross-platform-comparison.md](12-cross-platform-comparison.md) | 上述平台与 Windows 的对照 |
| 同名 `.html` | 上表每一篇的阅读版。HTML 里的站内链接指向 `.html`，Markdown 里的站内链接指向 `.md` |
| [llms-full.md](llms-full.md) | `00`–`12` 按顺序拼接的单文件，篇间用 `<!-- FILE: … -->` 分开 |
| [build/](build/README.md) | 重生成 `07`–`12` 的脚本 |

## 重建

`07`–`12` 可以由 [build/all.sh](build/README.md) 从外部源笔记重做。`00`–`06` 与 `llms-full.md` 是随库提交的成稿，该脚本不覆盖它们。

脚本依赖技能仓库 [github.com/tangjianfang/tech-doc](https://github.com/tangjianfang/tech-doc)（`scripts/check_doc.py` 与 `scripts/mermaid-tools/export_html.mjs`）。源笔记和技能检出都不在 USBTree 里。环境变量、路径和可选截图见 [build/README.md](build/README.md)。

在仓库根目录：

```bash
git clone https://github.com/tangjianfang/tech-doc.git
export TECH_DOC_SKILL="$PWD/../tech-doc"   # 或 ~/.claude/skills/tech-doc
export USB_OS_KB=/path/to/os-kb            # 01-linux.md … 06-cross-platform-comparison.md
bash tech-doc/build/all.sh
```

导出 HTML 之后，`all.sh` 会运行 `build/relink_html.py`，把阅读版里的同库链接改回 `.html`。
