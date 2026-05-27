<script setup lang="ts">
import { computed } from "vue";
import { renderMarkdown } from "@/utils/markdown";

const props = defineProps<{ text: string }>();

const html = computed(() => renderMarkdown(props.text));
</script>

<template>
  <!-- eslint-disable-next-line vue/no-v-html -- sanitized by renderMarkdown (DOMPurify) -->
  <div class="rich-text" v-html="html"></div>
</template>

<style scoped>
.rich-text :deep(p) {
  margin: 0 0 var(--space-2) 0;
  line-height: 1.65;
}

.rich-text :deep(p:last-child) {
  margin-bottom: 0;
}

.rich-text :deep(ul),
.rich-text :deep(ol) {
  margin: 0 0 var(--space-2) 0;
  padding-left: 1.4em;
}

.rich-text :deep(li) {
  margin: 0 0 var(--space-1) 0;
  line-height: 1.55;
}

.rich-text :deep(strong) {
  font-weight: 700;
}

.rich-text :deep(em) {
  font-style: italic;
}

.rich-text :deep(a) {
  color: var(--color-accent);
  text-decoration: underline;
}

.rich-text :deep(code) {
  font-family: var(--font-mono);
  font-size: 0.9em;
  background: var(--color-accent-soft);
  padding: 0.1em 0.35em;
  border-radius: var(--radius-sm);
}

.rich-text :deep(h3),
.rich-text :deep(h4) {
  margin: var(--space-2) 0 var(--space-1) 0;
}

.rich-text :deep(blockquote) {
  margin: 0 0 var(--space-2) 0;
  padding-left: var(--space-3);
  border-left: 3px solid var(--color-border);
  color: var(--color-muted);
}
</style>
