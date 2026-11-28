# 静态站点 · https://usbtree.gumuhub.com

用 [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) 把整棵知识树发布成可搜索的网站（中文分词搜索、Mermaid、浅/深色、手机适配）。

```bash
python3 -m pip install -r tools/site/requirements.txt
bash tools/site/build.sh --check     # 产物在 _site/，并检查内链（0 断链才通过）
python3 -m http.server -d _site 8000 # 本地预览
```

| 文件 | 作用 |
|---|---|
| `mkdocs.yml`（仓库根） | 主题、搜索（`lang: zh` + jieba 构建期分词）、Markdown 扩展 |
| `tools/site/prepare.py` | 把正文暂存到 `_site_src/docs/`：README→首页、无 README 的目录自动生成索引页、按仓库树生成侧栏 nav；改写相对链接（目录→索引页，规范 PDF/ZIP→`tools/spec_fetch.sh` 里的官方下载地址，tech-doc `.md`→同名 `.html`，未发布的仓库文件→GitHub） |
| `tools/site/build.sh` | prepare → `mkdocs build --strict` → 原样拷入 `tech-doc/*.html|md`、`ai-kb/*.md`、`graph/*`、`llms.txt`、`_headers`；删除任何 PDF/ZIP |
| `tools/site/check_links.py` | 扫描产物里所有站内 `href/src` 与锚点 |
| `tools/site/overrides/`、`assets/` | 自托管 mermaid（只在有图的页面加载，不依赖 unpkg CDN）、中文系统字体（不加载 Google Fonts） |
| `.github/workflows/site.yml` | PR/push 时构建+查链；配置 `CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_ACCOUNT_ID` secrets 后 push main 自动部署 |

部署目标：Cloudflare Pages 项目 `usbtree`（`usbtree.pages.dev`），自定义域 `usbtree.gumuhub.com`。手动部署：

```bash
npx wrangler@4 pages deploy _site --project-name=usbtree --branch=main
```

AI 友好入口：`/llms.txt`、`/ai-kb/llms-full.md`、`/tech-doc/llms-full.md`、`/graph/*.yaml`（原样 UTF-8 文本）。
