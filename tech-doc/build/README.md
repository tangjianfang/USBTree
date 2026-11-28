# 重建 07–12

这些脚本只重写 `tech-doc/` 里的 `07`–`12`（Markdown，再用技能导出 HTML）。`00`–`06` 与 `llms-full.md` 不在此列。说明见 [上一级 README](../README.md)。

## 依赖

必须有 [tech-doc 技能](https://github.com/tangjianfang/tech-doc) 的检出。USBTree 不内嵌该技能。

```bash
git clone https://github.com/tangjianfang/tech-doc.git
export TECH_DOC_SKILL=/path/to/tech-doc
```

`TECH_DOC_SKILL` 指向仓库根目录，下面要有：

- `scripts/check_doc.py`
- `scripts/mermaid-tools/export_html.mjs`

装进 Claude Code 时，这个目录通常是 `~/.claude/skills/tech-doc`。另外需要本机的 `python3` 与 `node`。

`07`–`12` 的源笔记也不在本仓库（原先在 `/workspace/usb-os-kb`）。设置：

```bash
export USB_OS_KB=/path/to/os-kb
```

该目录需包含 `01-linux.md`、`02-arm-embedded.md`、`03-macos.md`、`04-ios-ipados.md`、`05-android.md`、`06-cross-platform-comparison.md`。未设置时，脚本会找 `tech-doc/build/os-kb/`（该目录已 gitignore，不要提交）。

## 路径

能放进仓库的路径都相对本文件解析，不再写 `/workspace/usb-techdoc` 或 `/home/box/.claude/skills/tech-doc`：

| 变量 | 默认 | 含义 |
|---|---|---|
| （脚本位置） | `tech-doc/build/` | `all.sh`、`run.py`、`build.py` 用自己的目录定位仓库 |
| `TECH_DOC_OUT` | `tech-doc/` | `07`–`12` 的写出目录 |
| `USB_OS_KB` | `tech-doc/build/os-kb` | 源笔记。材料不在仓库里，所以默认只是一个本地约定路径 |
| `TECH_DOC_SKILL` | 无默认，必须设置 | 技能检出 |
| `TECH_DOC_SHOTS` | `/tmp/tech-doc-shots` | 仅 `shots.py`。PNG 不入库 |

## 运行

在仓库根目录：

```bash
bash tech-doc/build/all.sh
```

顺序：`run.py` 根据源笔记写 `07`–`12` 的 Markdown → 技能 `check_doc.py --fix-style` → `export_html.mjs` 导出同名 HTML → `relink_html.py` 把 HTML 站内链接从 `.md` 改到 `.html`。Markdown 源里的链接保持指向 `.md`。

`shots.py` 不在 `all.sh` 里。它用本机的 `google-chrome` 把每篇 HTML 的主图截到 `/tmp`，需要时单独执行：`python3 tech-doc/build/shots.py`。
