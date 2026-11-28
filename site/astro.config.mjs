// USBTree 阅读站 · Astro Starlight
// 内容不在本目录手写维护：scripts/prepare.mjs 在构建前把仓库正文（10–90、tech-doc、skills…）
// 转换进 src/content/docs/（gitignore），并生成侧栏/图谱/统计数据到 src/generated/。
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightSidebarTopics from 'starlight-sidebar-topics';
import starlightLinksValidator from 'starlight-links-validator';
import mermaid from 'astro-mermaid';
import { readFileSync } from 'node:fs';

const gen = JSON.parse(readFileSync(new URL('./src/generated/topics.json', import.meta.url), 'utf8'));

export default defineConfig({
  site: 'https://usbtree.gumuhub.com',
  trailingSlash: 'always',
  build: { format: 'directory' },
  integrations: [
    mermaid({ theme: 'default', autoTheme: true, enableLog: false,
      mermaidConfig: { fontFamily: 'system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif', flowchart: { htmlLabels: true }, sequence: { mirrorActors: false } } }),
    starlight({
      title: 'USBTree',
      description: '中文 USB / BLE 知识树：协议核心、设备类、Type-C/PD、USB3/USB4、BLE、各平台驱动栈与虚拟 USB 研究，每条事实尽量溯源到官方规范。',
      logo: { src: './src/assets/logo.svg', replacesTitle: false },
      favicon: '/favicon.svg',
      defaultLocale: 'root',
      locales: { root: { label: '简体中文', lang: 'zh-CN' } },
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/tangjianfang/USBTree' }],
      customCss: ['./src/styles/custom.css'],
      lastUpdated: false, // 由 prepare.mjs 按源文件 git 时间写入 frontmatter
      pagination: true,
      tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 3 },
      expressiveCode: {
        themes: ['github-light', 'github-dark'],
        useStarlightDarkModeSwitch: true,
        styleOverrides: { borderRadius: '0.5rem', codeFontSize: '0.85rem' },
        defaultProps: { wrap: false },
      },
      head: [
        { tag: 'meta', attrs: { name: 'theme-color', content: '#0f766e' } },
        { tag: 'link', attrs: { rel: 'alternate', type: 'text/plain', href: '/llms.txt', title: 'llms.txt' } },
      ],
      components: {
        PageTitle: './src/components/PageTitle.astro',
        Sidebar: './src/components/Sidebar.astro',
        SocialIcons: './src/components/HeaderLinks.astro',
        Footer: './src/components/Footer.astro',
        Head: './src/components/Head.astro',
      },
      plugins: [
        starlightSidebarTopics(gen.topics, { exclude: gen.exclude }),
        starlightLinksValidator({
          errorOnRelativeLinks: false,
          errorOnInvalidHashes: true,
          errorOnLocalLinks: true,
          exclude: ['/ai-kb/*.md', '/tech-doc/*.html', '/tech-doc/*.md', '/graph/*', '/llms.txt', '/llms-full.txt', '/LICENSE.txt', '/data/*'],
        }),
      ],
    }),
  ],
});
