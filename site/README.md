# site/ · USBTree 阅读站

线上地址：<https://usbtree.gumuhub.com>（Cloudflare Pages 项目 `usbtree`）

基于 [Astro Starlight](https://starlight.astro.build) 的静态站点。**正文不在这里维护**：构建时 `scripts/prepare.mjs` 从仓库根目录的 Markdown 生成页面，所以只需改仓库里的 `.md`，站点自动跟随。

## 为什么是 Starlight

| 需求 | 做法 |
|---|---|
| 中文搜索 | Pagefind 1.6：索引时按中文分词，查询时用 `Intl.Segmenter`，纯静态、无服务端 |
| 国内访问 | 不用 Google Fonts / CDN，字体走系统中文字体栈，脚本与样式全部自托管 |
| Mermaid | `astro-mermaid` 打包进站点（不走 CDN），跟随深浅色；每张图带“⤢ 放大”（滚轮/双指缩放、拖动平移） |
| 深色模式 / 手机 | Starlight 原生支持 |
| 断链 | `starlight-links-validator`（构建期）+ `scripts/check_links.py`（产物级）双重检查 |

## 本地构建

```bash
cd site
npm ci
npm run dev      # 生成正文 + 本地预览 http://localhost:4321
npm run build    # 生成正文 → astro build → postbuild，产物在 site/dist
npm run check    # 产物内链检查（0 断链）
```

需要 Node 22+、Python 3（只用于链接检查），并且在完整 git 克隆里构建（“更新于”取自 `git log`）。

## 目录

```
site/
├── astro.config.mjs        Starlight 配置、插件、组件覆盖
├── content/                手写页面：首页、学习/研究路线、实验室（usb-labs 摘要）、图谱、参考、预留分枝占位页
├── data/
│   ├── labs.yaml           usb-labs 固定提交 + 每个实验对应的知识树页面
│   ├── paths.yaml          学习路线 8 个阶段
│   └── cheatsheets.yaml    速查卡：从正文按标题摘取的段落
├── scripts/
│   ├── prepare.mjs         仓库 Markdown → src/content/docs（链接改写、元信息、标注、目录页、侧栏主题、图谱 JSON）
│   ├── postbuild.mjs       复制原始文本（ai-kb、tech-doc、graph、llms）到 dist
│   └── check_links.py      产物级内链检查
├── src/components/         页头元信息、主题切换侧栏、顶栏、首页、知识图谱、Mermaid 放大
├── src/styles/custom.css   主题色与版式
└── public/                 favicon、_headers、llms.txt
```

生成目录 `src/content/docs/`、`src/generated/` 与 `dist/` 不入库。

## 内容约定

- **新顶层分枝自动接入**：仓库根目录下任何 `NN-名称/` 目录都会被收进站点。名字含“工具/分析仪”、“框架/API”、“AI 时代”的目录会分别接管预留的“工具与分析仪”、“框架与 API”、“AI 时代的 USB”主题（占位页 `content/{tools,frameworks,ai}/` 自动让位）；其他新目录挂到“速查与参考”侧栏。
- **每页元信息**：难度（L1–L4，按目录和篇幅估算，可在 frontmatter 用 `level` 覆盖）、阅读时长、git 最近修改日期、规范出处（正文里链接到的官方规范）、前置阅读（🌳 块里的“上一叶”加上图谱 `prerequisite` 边）、对应实验（`data/labs.yaml`）。
- **标注**：以 ⚠️ / 💡 / 📌 开头的引用块渲染为提示框，正文里的“待核实”会高亮，页头会显示条数。
- **实验室页**：`content/labs/*.md` 用 `labsrc:路径#Lx-Ly` 链接 usb-labs 源码，固定在 `data/labs.yaml` 的 `commit`。升级 usb-labs 版本时改 `commit` 并复核行号。
- 手写页链接写法：`page:仓库相对路径.md`（知识树页面）、`page:站点路径`（手写页）、`repo:路径`（GitHub 源文件）。

## 代码视频

`/videos/` 页面和嵌在正文里的讲解视频来自仓库根目录的 [`videos/`](../videos/README.md)（Manim 源码）。成品 `public/videos/<id>.{mp4,png,thumb.jpg,vtt}` 与 `manifest.json` **随仓库提交**，构建时原样发布，CI 不渲染视频。`prepare.mjs` 读取 `videos/videos.yaml`：把 `<video controls preload="none">` 插到 `pages` 所列正文的第一个二级标题之前，生成 `/videos/` 索引页（含字幕全文），首页显示缩略图卡片。改了场景源码就运行 `videos/render.sh <id>` 重新渲染并提交产物。

## 部署

`.github/workflows/site.yml`：PR 上构建 + 检查；`main` 上若配置了 `CLOUDFLARE_API_TOKEN` 与 `CLOUDFLARE_ACCOUNT_ID` 就部署到 Pages 项目 `usbtree`。手动部署：

```bash
npx wrangler@4 pages deploy dist --project-name=usbtree --branch=main
```
