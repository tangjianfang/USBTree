#!/usr/bin/env node
// 构建后：把给 AI / 离线阅读的原始文件原样放进 dist（Pagefind 不索引它们）。规范 PDF/ZIP 一律不发布。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ROOT = path.resolve(SITE, '..');
const DIST = path.join(SITE, 'dist');
const copy = (from, to) => { fs.mkdirSync(path.dirname(to), { recursive: true }); fs.copyFileSync(from, to); };
let n = 0;
for (const [dir, re] of [['tech-doc', /\.(html|md)$/], ['ai-kb', /\.md$/], ['graph', /\.(yaml|mmd)$/]]) {
  for (const f of fs.readdirSync(path.join(ROOT, dir))) {
    if (!re.test(f) || f === 'README.md') continue;
    copy(path.join(ROOT, dir, f), path.join(DIST, dir, f)); n++;
  }
}
copy(path.join(ROOT, 'LICENSE'), path.join(DIST, 'LICENSE.txt'));
copy(path.join(SITE, 'src/generated/graph.json'), path.join(DIST, 'data/graph.json'));
const purge = (d) => { for (const e of fs.readdirSync(d, { withFileTypes: true })) {
  const p = path.join(d, e.name);
  if (e.isDirectory()) purge(p); else if (/\.(pdf|zip)$/i.test(e.name)) fs.rmSync(p);
} };
purge(DIST);
const html = (d) => fs.readdirSync(d, { withFileTypes: true }).reduce((a, e) => a + (e.isDirectory() ? html(path.join(d, e.name)) : e.name.endsWith('.html') ? 1 : 0), 0);
console.log(`postbuild: 原样文件 ${n} 个；HTML ${html(DIST)} 个`);
