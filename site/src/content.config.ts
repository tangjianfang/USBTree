import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';
import { topicSchema } from 'starlight-sidebar-topics/schema';

const link = z.object({ title: z.string(), href: z.string() });

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: topicSchema.extend({
        // USBTree 扩展元数据（prepare.mjs 写入）
        level: z.number().int().min(1).max(4).optional(),
        readingMinutes: z.number().optional(),
        source: z.string().optional(),          // 仓库内源文件路径
        sourceUrl: z.string().optional(),
        section: z.string().optional(),         // 所属分枝（显示用）
        prereqs: z.array(link).default([]),
        specs: z.array(link).default([]),
        labs: z.array(link).default([]),
        concepts: z.array(link).default([]),    // 实验室页 → 概念页
        tbv: z.number().default(0),             // 待核实计数
        tbvAnchor: z.boolean().default(false),  // 是否有「待确认项」章节
        verified: z.preprocess((v) => (v instanceof Date ? v.toISOString().slice(0, 10) : v), z.string()).optional(),        // tech-doc「最后核对」
        docType: z.string().optional(),
        wide: z.boolean().default(false),
      }),
    }),
  }),
};
