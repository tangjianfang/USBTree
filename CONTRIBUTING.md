# 贡献指南

欢迎为 USBTree 添枝加叶。本库的定位与四层结构见 [README](README.md)，动笔前请先读 [知识树总图](00-知识树总图.md)。

## 提交什么

| 类型 | 去处 | 要求 |
|---|---|---|
| 勘误 | 直接改正文 + 勘误注记 | 必须给出证据（缓存规范页码/章节、官方文档链接、内核源码），参照文中既有 `⚠️ 勘误` 格式 |
| 新知识点（叶） | 归入对应枝干目录 | 文件开头标注知识树位置与父节点链接；文末"相关节点" |
| 新协议/新机制 | 先进 [graph/entities.yaml](graph/entities.yaml) 落实体 → [graph/relations.yaml](graph/relations.yaml) 加边（带 evidence）→ `bash tools/gen_graph.sh` | 关系类型用既有词汇表，新增类型需先登记 |
| 新缓存规范 | `80-参考资料/<子目录>/` + 更新[索引](80-参考资料/README.md) | 只增不改；**不要提交二进制**（gitignore 会拦截，直链写进索引即可） |
| 工具改进 | `tools/` | bash 可移植（Git Bash + Ubuntu CI 均需通过） |

## 硬性门槛（PR 必须满足）

1. `bash tools/validate.sh` **8/8 通过**——包括 frontmatter title≡H1、图谱边端点存在性；
2. 不引入 TODO/占位符；不确定的数值写"见规范原文"，**严禁编造**；
3. 规范数值优先用 `bash tools/spec_extract.sh <缓存文件> [检索词]` 从原文提取并标注章节；
4. 不重新分发官方规范二进制（许可约束，见 [LICENSE](LICENSE) 范围说明）；
5. 单 PR diff 建议 ≤300 行，大改请先开 issue 讨论。

## 知识树新增节点规则

1. 判断层级：核心机制 → 树干；协议族 → 新枝干目录（需先在总图登记）；族内子模块 → 子目录；单点知识 → 文件内小节；
2. 双向链接：新文件必须被至少一处父/兄弟节点引用，且自身链接回树干；
3. 更新 [00-知识树总图](00-知识树总图.md) mindmap 与 [README](README.md) 目录树。

## 提交规范

- 格式：`<类型>: <一句话>`（类型：fix/feat/docs/chore/evolve），一次提交一个完整动作；
- 涉及图谱数据变更时，`graph/export.mmd` 必须同提交重新生成。

## 本地验证

```bash
bash tools/validate.sh        # 8 项检查：链接/围栏/图谱引用/frontmatter/边端点/title≡H1/导出新鲜度/H1 唯一
bash tools/gen_graph.sh       # 图谱数据变更后重新生成 export.mmd
bash tools/spec_extract.sh "80-参考资料/usb-core/USB4-Specification-v2-2025-11.zip" "tunnel"   # 规范检索
```
