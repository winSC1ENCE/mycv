<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import Icon from "@/components/base/Icon.vue";
import type { MediaAsset } from "@/api/types";

const props = withDefaults(defineProps<{ media: MediaAsset; alt?: string }>(), { alt: "" });
const { t } = useI18n();
const locked = computed(() => !props.media.url);
const pdfSrc = computed(() => `${props.media.url}#view=FitH`);
</script>

<template>
  <div class="media-preview">
    <div
      v-if="locked"
      class="media-preview__locked"
      :data-tooltip="t('sensitive.tooltip')"
      :aria-label="t('timeline.locked_file')"
      tabindex="0"
    >
      <Icon name="lock" :size="32" />
      <span class="media-preview__locked-text">{{ t("timeline.locked_file") }}</span>
    </div>
    <img
      v-else-if="media.kind === 'image'"
      :src="media.url"
      :alt="media.alt_text || alt"
      class="media-preview__img"
    />
    <div v-else-if="media.kind === 'document'" class="media-preview__document">
      <embed
        :src="pdfSrc"
        type="application/pdf"
        class="media-preview__embed"
        :aria-label="media.alt_text || alt || 'Document'"
      />
      <a
        :href="media.url"
        target="_blank"
        rel="noopener"
        class="media-preview__fallback"
      >
        {{ t("actions.openPdf") }}
      </a>
    </div>
    <video
      v-else-if="media.kind === 'video'"
      :src="media.url"
      controls
      class="media-preview__video"
    />
  </div>
</template>

<style scoped>
.media-preview {
  width: 100%;
}

.media-preview__img {
  max-width: 100%;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.media-preview__document {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.media-preview__embed {
  width: 100%;
  min-height: 540px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.media-preview__fallback {
  align-self: flex-start;
  font-size: 0.875rem;
  color: var(--color-accent);
  text-decoration: underline;
}

.media-preview__video {
  max-width: 100%;
  border-radius: var(--radius-md);
}

.media-preview__locked {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  min-height: 200px;
  background:
    radial-gradient(
      ellipse at center,
      var(--color-surface) 0%,
      var(--color-surface-alt, var(--color-bg, #f4f4f5)) 100%
    );
  backdrop-filter: blur(8px);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  color: var(--color-fg-muted);
  cursor: help;
  user-select: none;
}

.media-preview__locked:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.media-preview__locked-text {
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.media-preview__locked::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  background: var(--color-fg, #0f172a);
  color: var(--color-surface, #ffffff);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition:
    opacity 140ms,
    transform 140ms;
  z-index: 10;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
}

.media-preview__locked:hover::after,
.media-preview__locked:focus-visible::after {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

[data-theme="dog"] .media-preview__locked {
  background: repeating-linear-gradient(
    -3deg,
    var(--color-surface) 0 14px,
    var(--color-border) 14px 16px
  );
  border-radius: 0;
  border: 3px solid var(--color-fg);
  box-shadow: 4px 4px 0 var(--color-fg);
}

[data-theme="dog"] .media-preview__embed,
[data-theme="dog"] .media-preview__img,
[data-theme="dog"] .media-preview__video {
  border-radius: 0;
  border: 3px solid var(--color-fg);
}
</style>
