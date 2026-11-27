# AI 参考知识库

本目录是**给 AI 参考的技术文档**：把 USBTree 正文收成按主题切分、带 YAML frontmatter 的检索包，方便代理按关键词、层级和规范出处取事实。人读仍以仓库根目录的知识树为准。数字或字段冲突时的优先级：官方规范 > 各主题里的「核心事实 Key Facts」> 清洗后的 USBTree 原文。

`tools/validate.sh` 不把本目录算进内容篇，也不对这里做链接、围栏、frontmatter 与孤页检查，避免派生文库改动 10~90 的篇数和统计。

## 结构

| 文件 | 作用 |
|---|---|
| [index.md](index.md) | 主题索引、按问题查找、中英术语对照，以及仍未在正文收口的原文勘误 |
| `01-` … `92-*.md` | 38 个主题。frontmatter 含 `level`、`keywords`、`sources`（仓库路径与 GitHub URL）、`spec_refs`、`related`、`usbtree_commit` |
| [llms-full.md](llms-full.md) | 索引和全部主题按顺序拼接的单文件，主题之间用 `<!-- file: … -->` 分开 |

每个主题的正文顺序是：核心事实（手写，放在 `tools/ai-kb/topics.py`）→ `原文：…`（从对应 USBTree 页面清洗：去掉导航和 emoji，站内链接改写成知识库内链或 GitHub URL，保留表格、代码和 Mermaid）。

## 重建

在仓库根目录执行：

```bash
python3 tools/ai-kb/build_kb.py
```

脚本用仓库内相对路径读取当前检出，原地覆盖本目录的 `index.md`、主题文件和 `llms-full.md`，保留本 README。frontmatter 的 `usbtree_commit` 是这些原文路径上最近一次提交的短哈希；原文有未提交改动时加 `-dirty`。只提交 `ai-kb/` 不会让这个字段跟着变，因此在正文未改时重复运行是空操作。

生成器在 [tools/ai-kb/](../tools/ai-kb/build_kb.py)：`topics.py` 定义主题与核心事实，`build_kb.py` 负责清洗和写出文件。
