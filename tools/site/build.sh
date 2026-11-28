#!/usr/bin/env bash
# 构建 USBTree 静态站点到 _site/（可直接部署到 Cloudflare Pages / 任意静态托管）
#   bash tools/site/build.sh            # 构建
#   bash tools/site/build.sh --check    # 构建后跑内链检查（0 断链才返回 0）
# 依赖：python3 + pip install -r tools/site/requirements.txt
set -euo pipefail
export NO_MKDOCS_2_WARNING=1
cd "$(dirname "$0")/../.."
MERMAID_VER=11.17.2   # 自托管 mermaid，不入库；构建时从 npm registry 取一次并缓存
CACHE=.site-cache; mkdir -p "$CACHE"
if [[ ! -s "$CACHE/mermaid-$MERMAID_VER.min.js" ]]; then
  curl -fsSL "https://registry.npmjs.org/mermaid/-/mermaid-$MERMAID_VER.tgz" \
    | tar -xzO package/dist/mermaid.min.js > "$CACHE/mermaid-$MERMAID_VER.min.js.tmp"
  mv "$CACHE/mermaid-$MERMAID_VER.min.js.tmp" "$CACHE/mermaid-$MERMAID_VER.min.js"
fi
python3 tools/site/prepare.py
mkdir -p _site_src/docs/assets/js
cp "$CACHE/mermaid-$MERMAID_VER.min.js" _site_src/docs/assets/js/mermaid.min.js
python3 -m mkdocs build --strict -f _site_src/mkdocs.gen.yml
test -f _site/index.html
# 原样提供的文件（给人看的 HTML + 给 AI 的纯文本）。规范 PDF/ZIP 不发布。
mkdir -p _site/tech-doc _site/ai-kb _site/graph
cp tech-doc/*.html tech-doc/*.md _site/tech-doc/
rm -f _site/tech-doc/README.md
cp ai-kb/*.md _site/ai-kb/
rm -f _site/ai-kb/README.md
cp graph/*.yaml graph/*.mmd _site/graph/
cp LICENSE _site/LICENSE.txt
cp tools/site/static/* _site/
find _site \( -iname '*.pdf' -o -iname '*.zip' \) -delete
echo "built: $(find _site -name '*.html' | wc -l) html files, $(du -sh _site | cut -f1)"
if [[ "${1:-}" == "--check" ]]; then
  python3 tools/site/check_links.py _site
fi
