<script setup lang="ts">
import { ref, watch } from "vue";
import {
  renderMermaidSvgs,
  renderReadmeHtml,
  substitutePlaceholders,
  type ReadmeContext,
} from "@/utils/readme";

const props = defineProps<{ name: string; markdown: string; ctx: ReadmeContext }>();

const html = ref("");

async function rerender(): Promise<void> {
  const text = substitutePlaceholders(props.markdown, props.ctx);
  const svgs = await renderMermaidSvgs(text);
  html.value = renderReadmeHtml(text, svgs);
}

watch(
  () => [props.markdown, props.ctx] as const,
  () => {
    void rerender();
  },
  { immediate: true, deep: true },
);
</script>

<template>
  <div class="readme-preview">
    <header class="readme-preview__header">
      <h1 class="readme-preview__name">{{ name }}</h1>
      <div class="readme-preview__badges">
        <span class="readme-badge">
          <span class="readme-badge__key">version</span>
          <span class="readme-badge__val">{{ ctx.version }}</span>
        </span>
        <span class="readme-badge readme-badge--muted">
          <span class="readme-badge__key">updated</span>
          <span class="readme-badge__val">{{ ctx.updated }}</span>
        </span>
      </div>
    </header>
    <!-- eslint-disable-next-line vue/no-v-html -- sanitized in renderReadmeHtml + renderMermaidSvgs (DOMPurify) -->
    <div class="readme-preview__body" v-html="html"></div>
  </div>
</template>

<style scoped>
.readme-preview {
  background: #fff;
  color: #0f172a;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  font-size: 0.9rem;
  line-height: 1.55;
  overflow-x: auto;
}

.readme-preview__header {
  border-bottom: 1.5px solid #0f172a;
  padding-bottom: var(--space-3);
  margin-bottom: var(--space-4);
}

.readme-preview__name {
  font-size: 1.6rem;
  font-weight: 700;
}

.readme-preview__badges {
  display: flex;
  gap: 6px;
  margin-top: var(--space-2);
}

.readme-badge {
  display: inline-flex;
  overflow: hidden;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
}

.readme-badge__key {
  background: #334155;
  color: #fff;
  padding: 2px 7px;
}

.readme-badge__val {
  background: #2563eb;
  color: #fff;
  padding: 2px 7px;
}

.readme-badge--muted .readme-badge__val {
  background: #94a3b8;
}

.readme-preview__body :deep(h1) {
  font-size: 1.4rem;
  font-weight: 700;
  margin: var(--space-4) 0 var(--space-2);
}
.readme-preview__body :deep(h2) {
  font-size: 1.15rem;
  font-weight: 700;
  margin: var(--space-3) 0 var(--space-2);
}
.readme-preview__body :deep(h3) {
  font-size: 1rem;
  font-weight: 700;
  margin: var(--space-3) 0 var(--space-1);
}
.readme-preview__body :deep(p) {
  margin: 0 0 var(--space-2);
}
.readme-preview__body :deep(ul),
.readme-preview__body :deep(ol) {
  margin: 0 0 var(--space-2) var(--space-4);
}
.readme-preview__body :deep(a) {
  color: #2563eb;
  text-decoration: none;
  word-break: break-all;
}
.readme-preview__body :deep(code) {
  font-family: var(--font-mono);
  font-size: 0.85em;
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 3px;
}
.readme-preview__body :deep(pre) {
  background: #f1f5f9;
  border-radius: 5px;
  padding: var(--space-3);
  margin: 0 0 var(--space-3);
  overflow-x: auto;
}
.readme-preview__body :deep(pre code) {
  background: none;
  padding: 0;
}
.readme-preview__body :deep(blockquote) {
  border-left: 3px solid #cbd5e1;
  padding-left: var(--space-3);
  color: #475569;
  margin: 0 0 var(--space-2);
}
.readme-preview__body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0 0 var(--space-3);
}
.readme-preview__body :deep(th),
.readme-preview__body :deep(td) {
  border: 1px solid #e2e8f0;
  padding: var(--space-1) var(--space-2);
  text-align: left;
}
.readme-preview__body :deep(th) {
  background: #f8fafc;
}
.readme-preview__body :deep(hr) {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: var(--space-4) 0;
}
.readme-preview__body :deep(svg) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto var(--space-3);
}
.readme-preview__body :deep(.mermaid-error) {
  color: #dc2626;
  background: #fef2f2;
}
</style>
