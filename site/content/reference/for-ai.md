---
title: 给 AI 用
description: 面向大模型与 RAG 的纯文本入口：llms.txt、ai-kb 主题知识库、tech-doc 全文、知识图谱 YAML。
topic: reference
---

站点同时提供一套给机器读的原始文本，全部是 UTF-8 纯文本、允许跨域读取（`Access-Control-Allow-Origin: *`）：

| 地址 | 内容 |
|---|---|
| [`/llms.txt`](/llms.txt) | 入口索引（[llms.txt 约定](https://llmstxt.org/)） |
| [`/ai-kb/llms-full.md`](/ai-kb/llms-full.md) | 38 个主题合并成一个文件，带 Key Facts 表 |
| [`/ai-kb/index.md`](/ai-kb/index.md) | 各主题文件入口，可按需取单个主题 |
| [`/tech-doc/llms-full.md`](/tech-doc/llms-full.md) | 规范精读 13 篇全文（标注章节号） |
| [`/graph/entities.yaml`](/graph/entities.yaml) · [`/graph/relations.yaml`](/graph/relations.yaml) | 知识图谱实体与关系 |
| [`/tech-doc/*.html`](/tech-doc/01-usb2-ch9-control.html) | tech-doc 的离线单文件 HTML 版 |

ai-kb 由 [tools/ai-kb/build_kb.py](repo:tools/ai-kb/build_kb.py) 从正文生成，说明见 [ai-kb 主题知识库](page:ai-kb/README.md)。
