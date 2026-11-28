#!/usr/bin/env node
/**
 * prepare.mjs — 把 USBTree 仓库正文转换成 Starlight 内容（构建期生成，不入库）。
 *
 *   输入：仓库根的 10–90 知识树、00-知识树总图、tech-doc/*.md、skills/、docs/、graph/*.yaml、
 *         tools/spec_fetch.sh（规范官方直链）、site/content/（手写的首页/路线/实验室页）、site/data/*.yaml
 *   输出：site/src/content/docs/**（.md/.mdx）与 site/src/generated/*.json（侧栏 topics、图谱、统计）
 *
 * 做的事：保持旧站 URL（/10-树干-USB核心/07-描述符详解/）；去掉与页头重复的 H1 和「🌳 知识树位置」块；
 * 把 ⚠️/💡/📌 引用块变成提示框；标出「待核实」；改写仓库相对链接到站内页面 / 官方规范直链 / GitHub；
 * 给每页算难度、阅读时长、最近更新时间、前置阅读、规范出处、相关实验室；生成目录落地页、学习路线、
 * 速查卡（按章节原样摘取）、规范索引与知识图谱数据。
 */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import YAML from 'yaml';

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ROOT = path.resolve(SITE, '..');
const OUT = path.join(SITE, 'src/content/docs');
const GEN = path.join(SITE, 'src/generated');
const AUTHORED = path.join(SITE, 'content');
const GH = 'https://github.com/tangjianfang/USBTree';
const posix = (p) => p.split(path.sep).join('/');
const read = (rel) => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const exists = (rel) => fs.existsSync(path.join(ROOT, rel));
const warn = [];

const labsCfg = YAML.parse(fs.readFileSync(path.join(SITE, 'data/labs.yaml'), 'utf8'));
const pathsCfg = YAML.parse(fs.readFileSync(path.join(SITE, 'data/paths.yaml'), 'utf8'));
const sheetsCfg = YAML.parse(fs.readFileSync(path.join(SITE, 'data/cheatsheets.yaml'), 'utf8'));
const LABSRC = (p) => `${labsCfg.repo}/blob/${labsCfg.commit}/${encodeURI(p)}`;
const LABTREE = (p) => `${labsCfg.repo}/tree/${labsCfg.commit}/${encodeURI(p)}`;

// ───────────────────────────── 规范直链（tools/spec_fetch.sh 清单） ─────────────────────────────
const SPECS = {}; const SPEC_LIST = [];
for (const m of read('tools/spec_fetch.sh').matchAll(/"(MANUAL:)?([^"|]+\.(?:pdf|zip|txt))\|(https?:\/\/[^"]+)"/g)) {
  SPECS['80-参考资料/' + m[2]] = m[3];
  SPEC_LIST.push({ manual: !!m[1], file: m[2], url: m[3] });
}

// ───────────────────────────── git 最近修改时间（一次遍历） ─────────────────────────────
const lastMod = {};
try {
  const log = execFileSync('git', ['-c', 'core.quotepath=off', 'log', '--format=@@%cI', '--name-only', '--no-renames', 'HEAD'],
    { cwd: ROOT, encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 });
  let cur = null;
  for (const line of log.split('\n')) {
    if (line.startsWith('@@')) cur = line.slice(2);
    else if (line && cur && !lastMod[line]) lastMod[line] = cur;
  }
} catch { warn.push('git log 不可用：最近更新时间留空'); }

// ───────────────────────────── 主题（侧栏 topics）与分枝 ─────────────────────────────
// 预留的顶层分枝：仓库里出现名字匹配的编号目录（如 70-工具与分析仪/、75-框架与API/）就自动接管该主题；
// 目录尚不存在时用 site/content/<placeholder>/index.md 占位页兜底。
const RESERVED = [
  { id: 'tools', label: '工具与分析仪', icon: 'analytics', re: /^\d\d-[^/]*(工具|分析仪)/, placeholder: 'tools' },
  { id: 'frameworks', label: '框架与 API', icon: 'seti:json', re: /^\d\d-[^/]*(框架|API)/, placeholder: 'frameworks' },
  { id: 'ai', label: 'AI 时代的 USB', icon: 'star', re: /^\d\d-(AI|[^/]*AI时代)/, placeholder: 'ai' },
];
for (const r of RESERVED) r.dir = fs.readdirSync(ROOT).find((d) => r.re.test(d) && fs.statSync(path.join(ROOT, d)).isDirectory());
const RES = Object.fromEntries(RESERVED.map((r) => [r.id, r]));
const resTopic = (id) => ({ id, label: RES[id].label, icon: RES[id].icon, link: RES[id].dir ? `/${RES[id].dir}/` : `/${RES[id].placeholder}/` });
const TOPICS = [
  { id: 'guide', label: '开始', icon: 'rocket', link: '/guide/learning-paths/' },
  { id: 'core', label: '协议核心', icon: 'list-format', link: '/10-树干-USB核心/' },
  { id: 'classes', label: '设备类', icon: 'puzzle', link: '/20-枝干-设备类协议/' },
  { id: 'power', label: '接口与供电', icon: 'sun', link: '/30-枝干-接口与供电/' },
  { id: 'ble', label: '蓝牙 BLE', icon: 'comment-alt', link: '/50-枝干-无线关联/' },
  { id: 'platform', label: '平台与驱动', icon: 'laptop', link: '/60-枝干-主机侧与实现/' },
  { id: 'debug', label: '调试与安全', icon: 'magnifier', link: '/70-枝干-调试测试与安全/' },
  resTopic('tools'),
  resTopic('frameworks'),
  resTopic('ai'),
  { id: 'spec', label: '规范精读', icon: 'approve-check-circle', link: '/tech-doc/' },
  { id: 'labs', label: '实验室', icon: 'code-branch', link: '/labs/' },
  { id: 'reference', label: '速查与参考', icon: 'notes', link: '/reference/' },
];
const DIR_LABEL = {
  '10-树干-USB核心': 'USB 2.0 核心（树干）', '20-枝干-设备类协议': '设备类协议', '30-枝干-接口与供电': '接口与供电',
  '40-枝干-高速演进': 'USB 3.x / USB4 高速演进', '50-枝干-无线关联': '无线关联', '60-枝干-主机侧与实现': '主机侧与实现',
  '70-枝干-调试测试与安全': '调试、测试与安全', '80-参考资料': '参考资料', '90-附录': '附录',
  'HID-人机接口设备': 'HID 人机接口设备', 'CDC-通信设备类': 'CDC 通信设备类', 'MSC-大容量存储': 'MSC 大容量存储',
  'Video-UVC': 'UVC 视频类', 'Audio-UAC': 'UAC 音频类', '其他设备类': '其他设备类', 'BLE-低功耗蓝牙': 'BLE 低功耗蓝牙',
};
const dirLabel = (d) => DIR_LABEL[path.posix.basename(d)] || path.posix.basename(d).replace(/^\d\d-(树干|枝干)?-?/, '');

function topicOf(rel) {
  if (/^(README|00-知识树总图|COVERAGE|CONTRIBUTING)\.md$/.test(rel) || rel.startsWith('docs/')) return 'guide';
  for (const r of RESERVED) if (r.dir && rel.startsWith(r.dir + '/')) return r.id;
  if (/^(10|40)-/.test(rel)) return 'core';
  if (rel.startsWith('20-')) return 'classes';
  if (rel.startsWith('30-')) return 'power';
  if (rel.startsWith('50-')) return 'ble';
  if (rel.startsWith('60-')) return 'platform';
  if (rel.startsWith('70-') || rel.startsWith('skills/')) return 'debug';
  if (rel.startsWith('tech-doc/')) {
    const n = parseInt((rel.match(/tech-doc\/(\d\d)-/) || [])[1] ?? '0', 10);
    return n >= 6 ? 'platform' : 'spec';
  }
  return 'reference';
}

// ───────────────────────────── 收集源页面 ─────────────────────────────
const pages = new Map(); // rel -> page
function addPage(rel, slug) { pages.set(rel, { rel, slug, url: slug === '' ? '/' : `/${slug}/` }); }
for (const [rel, slug] of [['README.md', 'about'], ['00-知识树总图.md', '00-知识树总图'], ['COVERAGE.md', 'COVERAGE'], ['CONTRIBUTING.md', 'CONTRIBUTING']]) addPage(rel, slug);
const walk = (dir) => fs.readdirSync(path.join(ROOT, dir), { withFileTypes: true }).flatMap((e) =>
  e.isDirectory() ? walk(posix(path.join(dir, e.name))) : e.name.endsWith('.md') ? [posix(path.join(dir, e.name))] : []);
const CONTENT_DIRS = fs.readdirSync(ROOT).filter((d) => /^\d\d-/.test(d) && fs.statSync(path.join(ROOT, d)).isDirectory()).sort();
for (const d of CONTENT_DIRS) for (const rel of walk(d).sort()) {
  addPage(rel, rel.endsWith('/README.md') ? path.posix.dirname(rel) : rel.replace(/\.md$/, ''));
}
for (const rel of walk('skills').sort()) addPage(rel, path.posix.dirname(rel));
for (const rel of walk('docs').sort()) addPage(rel, rel.replace(/\.md$/, ''));
for (const f of fs.readdirSync(path.join(ROOT, 'tech-doc')).filter((f) => f.endsWith('.md') && f !== 'llms-full.md').sort()) {
  addPage('tech-doc/' + f, f === 'README.md' ? 'tech-doc' : 'tech-doc/' + f.replace(/\.md$/, ''));
}
addPage('ai-kb/README.md', 'ai-kb');

// 目录落地页（没有 README 的内容目录）
const dirIndex = new Map(); // dir -> url
for (const d of CONTENT_DIRS) {
  const dirs = new Set([d]);
  for (const rel of walk(d)) { let p = path.posix.dirname(rel); while (p.startsWith(d)) { dirs.add(p); p = path.posix.dirname(p); } }
  for (const x of dirs) dirIndex.set(x, `/${x}/`);
}

// ───────────────────────────── 正文工具 ─────────────────────────────
function splitFrontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?/);
  return m ? { fm: YAML.parse(m[1]) || {}, body: text.slice(m[0].length) } : { fm: {}, body: text };
}
const stripMd = (s) => s.replace(/!\[[^\]]*\]\([^)]*\)/g, '').replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
  .replace(/[*_`>#]/g, '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
function firstParagraph(body) {
  let inCode = false;
  for (const block of body.split(/\n\s*\n/)) {
    const t = block.trim();
    if (t.startsWith('```')) { inCode = !inCode; if ((t.match(/```/g) || []).length % 2 === 0) inCode = false; continue; }
    if (inCode || !t || /^(#|\||>|<|:::|-{3,}|```|\*\*?[^*]*\*\*?$)/.test(t) || /^[-*] /.test(t) || /^\d+\. /.test(t)) continue;
    const s = stripMd(t);
    if (s.length >= 16) return s.length > 120 ? s.slice(0, 118) + '…' : s;
  }
  return '';
}
function readingMinutes(body) {
  const txt = body.replace(/```[\s\S]*?```/g, ' ');
  const cjk = (txt.match(/[\u4e00-\u9fff]/g) || []).length;
  const words = (txt.replace(/[\u4e00-\u9fff]/g, ' ').match(/[A-Za-z0-9]+/g) || []).length;
  return Math.max(1, Math.round(cjk / 450 + words / 220));
}
function levelOf(rel, title) {
  if (/^tech-doc\/0[1-5]-/.test(rel)) return 4;
  if (/^tech-doc\/(0[6-9]|1\d)-/.test(rel)) return 3;
  if (/规范级|全表|附录|DROM|CM 指南|CM指南|配置空间|位级|权威编号/.test(title)) return 4;
  if (/索引|概述|概览|总图|演进|体系架构|术语|对比速查|README|定位/.test(title + rel)) return 1;
  if (/深入|状态机|LTSSM|带宽|调度|错误处理|TestMode|Test Mode|驱动开发|Gadget|usbip|LLCP|测向|Mesh|LE Audio|安全|合规|USB4/.test(title)) return 3;
  return 2;
}
const LEVEL_NAME = { 1: '入门', 2: '基础', 3: '进阶', 4: '专家' };

const OFFICIAL = [
  [/usb\.org/, 'USB-IF'], [/bluetooth\.(com|org)/, 'Bluetooth SIG'], [/kernel\.org/, 'kernel.org'],
  [/learn\.microsoft\.com|docs\.microsoft\.com/, 'Microsoft Learn'], [/developer\.apple\.com|support\.apple\.com/, 'Apple'],
  [/source\.android\.com|developer\.android\.com/, 'Android'], [/intel\.com/, 'Intel'],
];
function specLabelFromFile(f) { return path.posix.basename(f).replace(/\.(pdf|zip|txt)$/, '').replace(/[-_]/g, ' '); }

/** 在代码围栏之外逐段处理正文 */
function mapOutsideCode(body, fn) {
  const parts = body.split(/(^```[\s\S]*?^```[^\n]*$)/m);
  return parts.map((p, i) => (i % 2 === 1 ? p : fn(p))).join('');
}

const LINK_RE = /(!?\[(?:[^\[\]]|\[[^\]]*\])*\]\()(<[^>]+>|[^)\s]+)((?:\s+"[^"]*")?\))/g;

function resolveTarget(target, srcRel, ctx) {
  if (target.startsWith('<') && target.endsWith('>')) target = target.slice(1, -1);
  if (/^page:/.test(target)) {
    const [p, frag] = target.slice(5).split('#');
    const pg = pages.get(p) || (dirIndex.has(p) ? { url: dirIndex.get(p) } : null);
    if (!pg && !p.endsWith('.md')) return '/' + p.replace(/^\/|\/$/g, '') + (p ? '/' : '') + (frag ? '#' + frag : '');
    if (!pg) { warn.push(`[${srcRel}] page: 目标不存在 ${p}`); return target; }
    return pg.url + (frag ? '#' + frag : '');
  }
  if (/^labsrc:/.test(target)) { const t = target.slice(7); const [p, frag] = t.split('#'); return LABSRC(p) + (frag ? '#' + frag : ''); }
  if (/^labtree:/.test(target)) return LABTREE(target.slice(8));
  if (/^repo:/.test(target)) return `${GH}/blob/main/${encodeURI(target.slice(5))}`;
  if (/^[a-z][a-z0-9+.-]*:/i.test(target) || target.startsWith('#') || target.startsWith('/')) return target;
  const [rawPath, ...fragParts] = target.split('#');
  const frag = fragParts.length ? '#' + fragParts.join('#') : '';
  let dec; try { dec = decodeURIComponent(rawPath); } catch { dec = rawPath; }
  const rel = path.posix.normalize(path.posix.join(path.posix.dirname(srcRel), dec)).replace(/\/$/, '');
  if (rel.startsWith('..')) return target;
  if (pages.has(rel)) { ctx?.links.push(rel); return pages.get(rel).url + frag; }
  if (dirIndex.has(rel)) return dirIndex.get(rel) + frag;
  if (exists(rel) && fs.statSync(path.join(ROOT, rel)).isDirectory()) {
    if (pages.has(rel + '/README.md')) return pages.get(rel + '/README.md').url + frag;
    return `${GH}/tree/main/${encodeURI(rel)}`;
  }
  if (SPECS[rel]) { ctx?.specs.push({ title: specLabelFromFile(rel), href: SPECS[rel] }); return SPECS[rel]; }
  if (rel.startsWith('80-参考资料/')) return '/reference/specs/';
  const htmlTwin = rel.match(/^tech-doc\/(.+)\.html$/);
  if (htmlTwin && pages.has(`tech-doc/${htmlTwin[1]}.md`)) return pages.get(`tech-doc/${htmlTwin[1]}.md`).url + frag;
  if (rel === 'LICENSE') return '/LICENSE.txt';
  if (/^ai-kb\/.+\.md$/.test(rel) || /^graph\/[^/]+\.(yaml|mmd)$/.test(rel) || rel === 'tech-doc/llms-full.md') return '/' + rel + frag;
  if (exists(rel)) return `${GH}/blob/main/${encodeURI(rel)}${frag}`;
  warn.push(`[${srcRel}] 断链未改写: ${target}`);
  return target;
}
// 链接文字本身就是 .md 路径时（如“详见 ../10-树干-USB核心/07-描述符详解.md”），换成目标页标题
const _titleCache = new Map();
function titleForUrl(url) {
  const u = url.split('#')[0];
  if (_titleCache.has(u)) return _titleCache.get(u);
  let t = null;
  for (const pg of pages.values()) if (pg.url === u) {
    const src = fs.readFileSync(path.join(ROOT, pg.rel), 'utf8');
    t = (src.match(/^title:\s*["']?(.+?)["']?\s*$/m) || src.match(/^# (.+)$/m) || [])[1] || null;
    break;
  }
  _titleCache.set(u, t);
  return t;
}
function rewriteLinks(text, srcRel, ctx) {
  return text.replace(LINK_RE, (m, a, t, b) => {
    const r = resolveTarget(t, srcRel, ctx);
    if (!a.startsWith('!') && /^\[`?[^\]\s]*\.md(#[^\]]*)?`?\]\($/.test(a) && r.startsWith('/')) {
      const title = titleForUrl(r);
      if (title) a = `[${title.replace(/[\[\]]/g, '')}](`;
    }
    if (ctx && /^https?:/.test(r)) for (const [re, org] of OFFICIAL) if (re.test(r)) {
      const label = stripMd(a.slice(a.startsWith('!') ? 2 : 1, -2)).slice(0, 48) || org;
      ctx.specs.push({ title: label, href: r, org }); break;
    }
    return a + (/[\s()]/.test(r) ? `<${r}>` : r) + b;
  });
}

const CALLOUT = [[/^⚠️?/, 'caution'], [/^❗|^🚫|^⛔/, 'danger'], [/^💡/, 'tip'], [/^📌|^📖|^ℹ️?|^🔎|^🧭/, 'note']];
function transformBody(body, srcRel, ctx, { isTechDoc } = {}) {
  // 去掉第一个 H1（Starlight 页头已渲染标题）
  body = body.replace(/^\s*# .*\n/, '');
  // 「🌳 知识树位置」块 → 提取上一叶作为前置阅读
  body = body.replace(/^> 🌳[^\n]*\n(?:>[^\n]*\n)*/m, (blk) => {
    const prev = blk.match(/上一[叶篇][:：]\s*\[[^\]]*\]\(([^)]+)\)/);
    if (prev) ctx.prevLeaf = prev[1];
    return '';
  });
  // tech-doc 元信息行
  if (isTechDoc) body = body.replace(/^> 类型：[^\n]*\n/m, (line) => {
    for (const seg of line.replace(/^> /, '').split('｜')) {
      const [k, ...v] = seg.split('：'); const val = v.join('：').trim().replace(/`/g, '');
      if (k.trim() === '最后核对') ctx.verified = val;
      if (k.trim() === '类型') ctx.docType = val;
      if (k.trim() === '版本') ctx.version = val;
      if (k.trim() === '范围') for (const f of val.split(/,\s*/)) if (/\.(pdf|zip)$/.test(f)) ctx.scope.push(f.trim());
    }
    return '';
  });
  body = mapOutsideCode(body, (seg) => {
    // 引用块 → 提示框
    seg = seg.replace(/(^>[^\n]*\n?)+/gm, (blk) => {
      const lines = blk.replace(/\n$/, '').split('\n').map((l) => l.replace(/^> ?/, ''));
      const first = lines[0].trim();
      for (const [re, kind] of CALLOUT) if (re.test(first)) {
        lines[0] = first.replace(re, '').replace(/^\uFE0F/, '').trim();
        let title = '';
        const t = lines[0].match(/^\*\*([^*]{1,24})\*\*[：:]?\s*/);
        if (t) { title = t[1].replace(/[：:]$/, ''); lines[0] = lines[0].slice(t[0].length); }
        return `:::${kind}${title ? `[${title}]` : ''}\n${lines.join('\n').trim()}\n:::\n`;
      }
      return blk;
    });
    // 待核实 标记（跳过行内代码）
    seg = seg.split(/(`[^`\n]*`)/).map((s, i) => i % 2 ? s : s
      .replace(/\*\*待核实\*\*/g, '<span class="tbv">待核实</span>')
      .replace(/(?<![">])待核实(?![<])/g, '<span class="tbv">待核实</span>')).join('');
    return rewriteLinks(seg, srcRel, ctx);
  });
  // mermaid：去掉写死浅色主题的 init 指令，让图随站点明暗切换
  body = body.replace(/(```mermaid\n)%%\{init:[^\n]*\}%%\n/g, '$1');
  ctx.tbv = (body.match(/class="tbv"/g) || []).length;
  ctx.tbvAnchor = /^#{2,3} 待确认项/m.test(body);
  return body;
}

// ───────────────────────────── 实验室反向映射 ─────────────────────────────
const labByConcept = {};
for (const lab of labsCfg.labs) for (const c of lab.concepts) {
  if (!pages.has(c)) { warn.push(`labs.yaml: 概念页不存在 ${c}`); continue; }
  (labByConcept[c] ||= []).push({ title: lab.title, href: `/labs/${lab.id}/` });
}

// ───────────────────────────── 图谱：实体 → 文档 ─────────────────────────────
const ent = YAML.parse(read('graph/entities.yaml')).entities;
const relsAll = YAML.parse(read('graph/relations.yaml')).relations;
const entById = Object.fromEntries(ent.map((e) => [e.id, e]));
const prereqByDoc = {};
for (const r of relsAll) if (r.type === 'prerequisite') {
  const from = entById[r.from], to = entById[r.to];
  if (from?.docs && to?.docs && from.docs !== to.docs) (prereqByDoc[from.docs] ||= []).push(to.docs);
}

// ───────────────────────────── 写出页面 ─────────────────────────────
fs.rmSync(OUT, { recursive: true, force: true });
fs.rmSync(GEN, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(GEN, { recursive: true });
const writeDoc = (slug, fm, body, ext = 'md') => {
  const file = path.join(OUT, (slug || 'index') + (slug && !slug.includes('/') && false ? '' : '') + '.' + ext);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const clean = Object.fromEntries(Object.entries(fm).filter(([, v]) => v !== undefined && v !== null && !(Array.isArray(v) && !v.length)));
  fs.writeFileSync(file, `---\n${YAML.stringify(clean, { lineWidth: 0 })}---\n\n${body.trim()}\n`);
};

const meta = {}; // rel -> computed meta for listings
for (const pg of pages.values()) {
  const { fm, body: raw } = splitFrontmatter(read(pg.rel));
  let title = fm.title || (raw.match(/^# (.+)$/m) || [])[1]?.trim() || path.posix.basename(pg.rel, '.md');
  if (pg.rel.startsWith('skills/')) title = (raw.match(/^# (.+)$/m) || [])[1]?.trim() || fm.name || title;
  if (pg.rel === 'README.md') title = '关于 USBTree';
  const ctx = { links: [], specs: [], scope: [], prevLeaf: null };
  const isTechDoc = pg.rel.startsWith('tech-doc/');
  const body = transformBody(raw, pg.rel, ctx, { isTechDoc });
  const level = levelOf(pg.rel, title);
  // 前置阅读：上一叶 + 图谱 prerequisite
  const prereqs = [];
  const pushPre = (rel) => { if (rel && pages.has(rel) && rel !== pg.rel && !prereqs.some((p) => p.rel === rel)) prereqs.push({ rel }); };
  if (ctx.prevLeaf) pushPre(path.posix.normalize(path.posix.join(path.posix.dirname(pg.rel), decodeURIComponent(ctx.prevLeaf))));
  for (const d of prereqByDoc[pg.rel] || []) pushPre(d);
  // 规范出处：去重，最多 6 条；tech-doc 的「范围」优先
  const specs = [];
  for (const f of ctx.scope) { const name = path.posix.basename(f); const hit = Object.entries(SPECS).find(([k]) => k.endsWith('/' + name)); specs.push({ title: specLabelFromFile(name), href: hit ? hit[1] : '/reference/specs/' }); }
  for (const s of ctx.specs) if (!specs.some((x) => x.href === s.href)) specs.push({ title: s.title, href: s.href });
  meta[pg.rel] = { title, level, url: pg.url, desc: fm.description || firstParagraph(body), minutes: readingMinutes(body), tbv: ctx.tbv, tbvAnchor: ctx.tbvAnchor,
    lastUpdated: lastMod[pg.rel], topic: topicOf(pg.rel), prereqs, specs: specs.slice(0, 6), verified: ctx.verified, docType: ctx.docType };
  pg.body = body; pg.title = title;
}
for (const pg of pages.values()) {
  const m = meta[pg.rel];
  const section = pg.rel.includes('/') ? dirLabel(path.posix.dirname(pg.rel)) : '';
  writeDoc(pg.slug, {
    title: m.title, description: m.desc || undefined, slug: pg.slug, topic: m.topic,
    lastUpdated: m.lastUpdated ? new Date(m.lastUpdated) : undefined,
    editUrl: `${GH}/edit/main/${encodeURI(pg.rel)}`,
    level: m.level, readingMinutes: m.minutes, source: pg.rel, sourceUrl: `${GH}/blob/main/${encodeURI(pg.rel)}`,
    section: section || undefined,
    prereqs: m.prereqs.slice(0, 3).map((p) => ({ title: meta[p.rel].title, href: meta[p.rel].url })),
    specs: m.specs, labs: labByConcept[pg.rel] || [], tbv: m.tbv || undefined, tbvAnchor: m.tbvAnchor || undefined, verified: m.verified, docType: m.docType,
  }, pg.body);
}

// ───────────────────────────── 目录落地页 ─────────────────────────────
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const levelChip = (l) => `<span class="lvl lvl-${l}">L${l} ${LEVEL_NAME[l]}</span>`;
function card(rel) {
  const m = meta[rel];
  return `<a class="doc-card" href="${m.url}"><span class="doc-card-title">${esc(m.title)}</span>` +
    `<span class="doc-card-desc">${esc(m.desc)}</span><span class="doc-card-meta">${levelChip(m.level)}<span>约 ${m.minutes} 分钟</span>` +
    `${(labByConcept[rel] || []).length ? '<span class="has-lab">🧪 有配套实验</span>' : ''}</span></a>`;
}
const childrenOf = (dir) => {
  const files = [...pages.keys()].filter((r) => path.posix.dirname(r) === dir && !r.endsWith('/README.md'));
  const subdirs = [...dirIndex.keys()].filter((d) => path.posix.dirname(d) === dir && d !== dir).sort();
  return { files, subdirs };
};
for (const [dir, url] of dirIndex) {
  if (pages.has(dir + '/README.md')) continue;
  const { files, subdirs } = childrenOf(dir);
  const idx = files.find((f) => /\/00-[^/]*索引\.md$/.test(f));
  const intro = idx ? meta[idx].desc : '';
  let body = intro ? `${intro}\n\n` : '';
  const total = [...pages.keys()].filter((r) => r.startsWith(dir + '/')).length;
  body += `<div class="dir-stats"><span>${total} 篇</span>${[1, 2, 3, 4].map((l) => {
    const n = [...pages.keys()].filter((r) => r.startsWith(dir + '/') && meta[r].level === l).length; return n ? levelChip(l) + `<b>${n}</b>` : '';
  }).join('')}</div>\n\n`;
  if (files.length) body += `## 本分枝文档\n\n<div class="doc-grid">\n${files.map(card).join('\n')}\n</div>\n\n`;
  for (const sd of subdirs) {
    const sub = [...pages.keys()].filter((r) => r.startsWith(sd + '/'));
    body += `## [${dirLabel(sd)}](${dirIndex.get(sd)})\n\n<div class="doc-grid">\n${sub.map(card).join('\n')}\n</div>\n\n`;
  }
  const lab = labsCfg.labs.filter((l) => l.concepts.some((c) => c.startsWith(dir + '/')));
  if (lab.length) body += `## 配套实验\n\n${lab.map((l) => `- [${l.title}](/labs/${l.id}/)`).join('\n')}\n`;
  writeDoc(dir, { title: dirLabel(dir), description: intro || `${dirLabel(dir)}：${total} 篇文档总览`, slug: dir, topic: topicOf(dir + '/x.md'),
    tableOfContents: false, section: dir.includes('/') ? dirLabel(path.posix.dirname(dir)) : undefined }, body);
}

// ───────────────────────────── 手写内容（site/content） ─────────────────────────────
const authoredLinks = [];
for (const rel of walkAbs(AUTHORED)) {
  const src = fs.readFileSync(path.join(AUTHORED, rel), 'utf8');
  const { fm, body } = splitFrontmatter(src);
  const slug = rel.replace(/\.(md|mdx)$/, '').replace(/(^|\/)index$/, '');
  const ext = rel.endsWith('.mdx') ? 'mdx' : 'md';
  const virtRel = '__site__/' + rel; // 相对链接按仓库根解析时不适用；手写页用 page:/labsrc:/repo: 前缀
  let out = mapOutsideCode(body, (seg) => rewriteLinks(seg, virtRel, null));
  if (RESERVED.some((r) => r.dir && (slug === r.placeholder || slug.startsWith(r.placeholder + '/')))) continue; // 正式目录已存在：占位页让位
  if (slug.startsWith('labs/')) {
    fm.topic ||= 'labs';
    const lab = labsCfg.labs.find((l) => `labs/${l.id}` === slug);
    if (lab) fm.concepts = lab.concepts.map((c) => ({ title: meta[c].title, href: meta[c].url }));
  }
  if (fm.slug === undefined && slug !== '') fm.slug = slug;
  writeDoc(slug, fm, out, ext);
}
function walkAbs(base, sub = '') {
  return fs.readdirSync(path.join(base, sub), { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walkAbs(base, posix(path.join(sub, e.name))) : /\.mdx?$/.test(e.name) ? [posix(path.join(sub, e.name))] : []);
}

// ───────────────────────────── 学习路线 ─────────────────────────────
const labTitle = Object.fromEntries(labsCfg.labs.map((l) => [l.id, l.title]));
const stages = pathsCfg.stages.map((s, i) => ({
  ...s, n: i + 1,
  pages: s.pages.map((r) => { if (!meta[r]) { warn.push(`paths.yaml: 页面不存在 ${r}`); return null; } return { rel: r, title: meta[r].title, url: meta[r].url, level: meta[r].level, minutes: meta[r].minutes, desc: meta[r].desc }; }).filter(Boolean),
  labs: (s.labs || []).map((id) => ({ id, title: labTitle[id], url: `/labs/${id}/` })),
}));
{
  let body = `按“由浅入深”排好的 8 个阶段。每个阶段列出必读文档（难度、预计阅读时长）与可以动手验证的实验。只想查资料，直接用顶部搜索或[速查卡](/reference/cheatsheets/)。\n\n`;
  body += `<ol class="path-timeline">\n`;
  for (const s of stages) {
    const mins = s.pages.reduce((a, p) => a + p.minutes, 0);
    body += `<li class="path-stage" id="${s.id}"><div class="path-stage-head"><span class="path-num">${s.n}</span><div><h2>${esc(s.title)}</h2><p>${esc(s.goal)}</p>` +
      `<p class="path-meta">${s.pages.length} 篇 · 阅读约 ${Math.round(mins / 6) / 10 >= 1 ? (Math.round(mins / 6) / 10) + ' 小时' : mins + ' 分钟'}</p></div></div>\n<ul class="path-pages">\n` +
      s.pages.map((p) => `<li><a href="${p.url}">${esc(p.title)}</a> ${levelChip(p.level)}<span class="muted">${p.minutes} 分钟</span></li>`).join('\n') +
      `\n</ul>${s.labs.length ? `<p class="path-labs">🧪 动手：${s.labs.map((l) => `<a href="${l.url}">${esc(l.title)}</a>`).join(' · ')}</p>` : ''}</li>\n`;
  }
  body += `</ol>\n`;
  writeDoc('guide/learning-paths', { title: '学习路线', description: '从入门到规范精读的 8 个阶段，附每阶段必读文档与配套实验。', slug: 'guide/learning-paths', topic: 'guide', tableOfContents: false }, body);
}

// ───────────────────────────── 速查卡（按章节原样摘取） ─────────────────────────────
function extractSection(rel, matchRe) {
  const { body } = splitFrontmatter(read(rel));
  const lines = body.split('\n');
  let start = -1, lvl = 0, inCode = false;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('```')) inCode = !inCode;
    const h = !inCode && lines[i].match(/^(#{2,4}) (.*)$/);
    if (h && new RegExp(matchRe).test(h[2].trim())) { start = i; lvl = h[1].length; break; }
  }
  if (start < 0) { warn.push(`cheatsheets: ${rel} 未找到 ${matchRe}`); return null; }
  let end = lines.length; inCode = false;
  for (let i = start + 1; i < lines.length; i++) {
    if (lines[i].startsWith('```')) inCode = !inCode;
    const h = !inCode && lines[i].match(/^(#{1,6}) /);
    if (h && h[1].length <= lvl) { end = i; break; }
  }
  const heading = lines[start].replace(/^#+ /, '');
  return { heading, text: lines.slice(start + 1, end).join('\n') };
}
const sheetList = [];
for (const s of sheetsCfg.sheets) {
  let body = `:::note[本页内容从正文原样摘取]\n每一节下方标注了出处；修改请改源文档，速查卡在构建时自动同步。\n:::\n\n`;
  for (const b of s.blocks) {
    const sec = extractSection(b.file, b.match);
    if (!sec) continue;
    const ctx = { links: [], specs: [], scope: [] };
    const text = transformBody(sec.text, b.file, ctx);
    body += `## ${sec.heading}\n\n${text.trim()}\n\n<p class="cheat-src">出处：<a href="${meta[b.file].url}">${esc(meta[b.file].title)}</a></p>\n\n`;
  }
  writeDoc(`reference/cheatsheets/${s.id}`, { title: s.title, description: s.description, slug: `reference/cheatsheets/${s.id}`, topic: 'reference', wide: true, level: 2 }, body);
  sheetList.push({ id: s.id, title: s.title, desc: s.description, url: `/reference/cheatsheets/${s.id}/` });
}
writeDoc('reference/cheatsheets', { title: '速查卡', description: '开发时随手查：协议字段、请求码、类代码、PD 定时器、BLE 操作码。', slug: 'reference/cheatsheets', topic: 'reference', tableOfContents: false },
  `开发时随手查的表格合集。每张卡都从正文按章节原样摘取，与正文保持同步。\n\n<div class="doc-grid">\n${sheetList.map((s) => `<a class="doc-card" href="${s.url}"><span class="doc-card-title">${esc(s.title)}</span><span class="doc-card-desc">${esc(s.desc)}</span></a>`).join('\n')}\n<a class="doc-card" href="${meta['90-附录/02-速查表大全.md'].url}"><span class="doc-card-title">开发者速查表大全（完整版）</span><span class="doc-card-desc">所有速查表在一页，适合打印或 Ctrl+F。</span></a>\n<a class="doc-card" href="${meta['90-附录/03-时序参数全表.md'].url}"><span class="doc-card-title">时序参数全表</span><span class="doc-card-desc">USB 2.0 / Type-C / PD / BLE 的时序参数与出处。</span></a>\n</div>\n`);

// ───────────────────────────── 规范索引 ─────────────────────────────
{
  const groups = {};
  for (const s of SPEC_LIST) (groups[s.file.split('/')[0]] ||= []).push(s);
  const GL = { 'usb-core': 'USB 核心 / Type-C / PD', 'host-controllers': '主机控制器', 'device-classes': '设备类', bluetooth: '蓝牙', 'bluetooth-profiles': '蓝牙 Profile' };
  const pub = (u) => (OFFICIAL.find(([re]) => re.test(u)) || [null, new URL(u).hostname])[1];
  let body = `USBTree 引用的官方规范清单，链接都指向发布方的官方下载地址（与 [tools/spec_fetch.sh](repo:tools/spec_fetch.sh) 同源，共 ${SPEC_LIST.length} 条）。规范原文受 USB-IF / Bluetooth SIG 许可约束，本站不转载 PDF。\n\n`;
  body += `:::tip[怎么用]\n正文里的规范引用会自动改写成这里的官方链接；标“需登录”的条目没有公开直链，要在发布方网站登录后手动下载。\n:::\n\n`;
  for (const [g, list] of Object.entries(groups)) {
    body += `## ${GL[g] || g}\n\n| 规范 | 发布方 | 获取 |\n|---|---|---|\n`;
    for (const s of list) body += `| ${specLabelFromFile(s.file)} | ${pub(s.url)} | ${s.manual ? `[官方页面（需登录）](${s.url})` : `[官方下载](${s.url})`} |\n`;
    body += '\n';
  }
  body += `## 平台官方文档\n\n平台驱动栈相关结论引用的是各厂商官方在线文档（不是标准组织规范），见各篇“规范出处”：\n\n- Microsoft Learn — Windows USB 驱动（WinUSB、KMDF、UCX）\n- docs.kernel.org — Linux USB / Gadget / Raw Gadget / USB/IP\n- developer.apple.com — IOKit、DriverKit、USBDriverKit、HIDDriverKit\n- source.android.com / developer.android.com — USB Host、AOA、Gadget HAL\n`;
  writeDoc('reference/specs', { title: '规范索引', description: `USBTree 引用的 ${SPEC_LIST.length} 份官方规范与下载地址。`, slug: 'reference/specs', topic: 'reference' }, body);
}

// ───────────────────────────── 图谱数据 ─────────────────────────────
const graph = {
  nodes: ent.map((e) => ({ id: e.id, name: e.name, type: e.type, code: e.code || null, doc: e.docs && meta[e.docs] ? { title: meta[e.docs].title, url: meta[e.docs].url } : null })),
  edges: relsAll.map((r) => ({ id: r.id, from: r.from, to: r.to, type: r.type, note: r.note || null, evidence: r.evidence && meta[r.evidence] ? { title: meta[r.evidence].title, url: meta[r.evidence].url } : null })),
};
fs.writeFileSync(path.join(GEN, 'graph.json'), JSON.stringify(graph));

// ───────────────────────────── 侧栏 topics ─────────────────────────────
const sideLabel = (t) => t.replace(/（[^）]*）$/, '').replace(/\s*\([^)]*\)$/, '');
const item = (rel) => ({ label: sideLabel(meta[rel].title), link: meta[rel].url, ...(meta[rel].level === 4 ? { badge: { text: '规范级', variant: 'note' } } : {}) });
const filesIn = (dir) => [...pages.keys()].filter((r) => path.posix.dirname(r) === dir && !r.endsWith('/README.md'));
const group = (label, dir, collapsed = false) => ({ label, collapsed, items: [{ label: '分枝概览', link: dirIndex.get(dir) }, ...filesIn(dir).map(item)] });
const subGroups = (dir, collapsed) => [...dirIndex.keys()].filter((d) => path.posix.dirname(d) === dir).sort().map((d) => group(dirLabel(d), d, collapsed));
const techDoc = (re) => [...pages.keys()].filter((r) => r.startsWith('tech-doc/') && re.test(r)).sort().map(item);
const L = (label, link) => ({ label, link });
const resItems = (id) => { const r = RES[id]; return r.dir
  ? [{ label: dirLabel(r.dir), items: [L('分枝概览', `/${r.dir}/`), ...filesIn(r.dir).map(item)] }, ...subGroups(r.dir, false)]
  : [L(`${r.label}（建设中）`, `/${r.placeholder}/`)]; };
const items = {
  guide: [L('学习路线', '/guide/learning-paths/'), L('研究路线：虚拟 USB · 驱动 · 固件', '/guide/research/'), L('知识树总图', '/00-知识树总图/'), L('关于 USBTree', '/about/'), L('如何阅读本站', '/guide/how-to-read/'),
    { label: '项目记录', collapsed: true, items: [L('覆盖度清单', '/COVERAGE/'), L('贡献指南', '/CONTRIBUTING/'), ...filesIn('docs').map(item)] }],
  core: [group('USB 2.0 核心（树干）', '10-树干-USB核心'), group('USB 3.x / USB4', '40-枝干-高速演进')],
  classes: [{ label: '总览', items: [L('分枝概览', '/20-枝干-设备类协议/'), ...filesIn('20-枝干-设备类协议').map(item)] }, ...subGroups('20-枝干-设备类协议', true)],
  power: [group('接口与供电', '30-枝干-接口与供电')],
  ble: [{ label: '无线关联', items: [L('分枝概览', '/50-枝干-无线关联/'), ...filesIn('50-枝干-无线关联').map(item)] }, ...subGroups('50-枝干-无线关联', false)],
  platform: [group('主机侧与实现', '60-枝干-主机侧与实现'), { label: '各平台 USB 栈', items: techDoc(/\/(0[7-9]|1[0-2])-/) }, { label: '虚拟 USB', items: techDoc(/\/06-/) }],
  debug: [group('调试、测试与安全', '70-枝干-调试测试与安全'), { label: '可执行技能（skills）', items: [...pages.keys()].filter((r) => r.startsWith('skills/')).map((r) => ({ label: meta[r].title, link: meta[r].url })) }],
  tools: [...resItems('tools'),
    { label: '站内相关', items: [L('协议分析仪与抓包', '/70-枝干-调试测试与安全/01-协议分析仪与抓包/'), L('枚举失败排查手册', '/70-枝干-调试测试与安全/02-枚举失败排查手册/'),
      L('抓包教学样本', '/labs/captures/'), L('usbtest 产测框架', '/labs/usbtest/'), L('USB DevStudio', '/labs/devstudio/')] }],
  frameworks: [...resItems('frameworks'),
    { label: '站内相关', items: [L('libusb 与用户态访问', '/60-枝干-主机侧与实现/04-libusb与用户态访问/'), L('实战：libusb 主机程序', '/60-枝干-主机侧与实现/06-实战-libusb主机程序/'),
      L('WebUSB 与厂商自定义类', '/20-枝干-设备类协议/其他设备类/06-WebUSB与厂商自定义类/'), L('macOS 与 Linux 主机开发', '/60-枝干-主机侧与实现/09-macOS与Linux主机开发/'), L('usbtest 产测框架', '/labs/usbtest/')] }],
  ai: [...resItems('ai'),
    { label: '站内相关', items: [L('给 AI 用（llms.txt / ai-kb）', '/reference/for-ai/'), L('ai-kb 主题知识库', '/ai-kb/'), L('可执行技能：抓包分析', '/skills/usb-capture-analysis/'), L('可执行技能：枚举排障', '/skills/usb-enum-troubleshoot/'), L('研究路线：虚拟 USB · 驱动 · 固件', '/guide/research/'), L('usbsim 协议仿真器', '/labs/usbsim/')] }],
  spec: [L('规范可追溯知识库', '/tech-doc/'), ...techDoc(/\/0[0-5]-/)],
  labs: [L('实验室总览', '/labs/'), { label: '七个全栈实验', items: labsCfg.labs.filter((l) => l.id.startsWith('lab')).map((l) => L(l.title, `/labs/${l.id}/`)) },
    { label: '工具链', items: labsCfg.labs.filter((l) => !l.id.startsWith('lab')).map((l) => L(l.title, `/labs/${l.id}/`)) }],
  reference: [L('速查与参考', '/reference/'), { label: '速查卡', items: [L('全部速查卡', '/reference/cheatsheets/'), ...sheetList.map((s) => L(s.title, s.url))] },
    L('知识图谱', '/explore/graph/'), L('术语表', '/90-附录/01-术语表/'), L('规范索引', '/reference/specs/'),
    { label: '附录', items: [L('附录概览', '/90-附录/'), ...filesIn('90-附录').map(item), L('参考资料缓存索引', '/80-参考资料/')] },
    { label: '给 AI 用', items: [L('AI 接入说明', '/reference/for-ai/'), L('ai-kb 主题知识库', '/ai-kb/')] }],
};
const KNOWN_DIR = /^(10|20|30|40|50|60|80|90)-|^70-枝干-/;
for (const d of CONTENT_DIRS.filter((d) => !RESERVED.some((r) => r.dir === d) && !KNOWN_DIR.test(d))) {
  items.reference.splice(1, 0, { label: dirLabel(d), collapsed: true, items: [L('分枝概览', `/${d}/`), ...filesIn(d).map(item)] }, ...subGroups(d, true));
}
fs.writeFileSync(path.join(GEN, 'topics.json'), JSON.stringify({ topics: TOPICS.map((t) => ({ ...t, id: t.id, items: items[t.id] })), exclude: ['/'] }, null, 1));

// ───────────────────────────── 站点统计（首页） ─────────────────────────────
const contentRels = [...pages.keys()].filter((r) => /^\d\d-/.test(r) && !r.startsWith('80-'));
const recent = [...pages.keys()].filter((r) => lastMod[r] && !r.startsWith('docs/')).sort((a, b) => lastMod[b].localeCompare(lastMod[a])).slice(0, 6)
  .map((r) => ({ title: meta[r].title, url: meta[r].url, date: lastMod[r].slice(0, 10), section: path.posix.dirname(r) === '.' ? '项目' : dirLabel(path.posix.dirname(r)) }));
fs.writeFileSync(path.join(GEN, 'site-data.json'), JSON.stringify({
  stats: { pages: contentRels.length, techdoc: [...pages.keys()].filter((r) => /^tech-doc\/\d\d-/.test(r)).length, entities: ent.length, relations: relsAll.length,
    specs: SPEC_LIST.length, labs: labsCfg.labs.length, cheatsheets: sheetList.length },
  stages, recent, cheatsheets: sheetList, labsCommit: labsCfg.commit,
  topics: TOPICS.map((t) => ({ ...t, count: [...pages.keys()].filter((r) => meta[r].topic === t.id).length })),
}, null, 1));

if (warn.length) { console.warn(`prepare: ${warn.length} 条提示`); for (const w of warn) console.warn('  · ' + w); }
console.log(`prepare: ${pages.size} 篇正文 → ${OUT}`);
if (process.argv.includes('--strict') && warn.some((w) => /断链|不存在|未找到/.test(w))) process.exit(1);
