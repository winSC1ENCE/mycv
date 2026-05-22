<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import Icon from "@/components/base/Icon.vue";
import ImageLightbox from "@/components/base/ImageLightbox.vue";
import type { MediaAsset } from "@/api/types";

const props = withDefaults(defineProps<{ media: MediaAsset; alt?: string }>(), { alt: "" });
const { t } = useI18n();
const locked = computed(() => !props.media.url);
const lightboxOpen = ref(false);
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
    <template v-else-if="media.kind === 'image'">
      <button
        type="button"
        class="media-preview__img-btn"
        :aria-label="t('actions.zoom_image')"
        @click="lightboxOpen = true"
      >
        <img :src="media.url" :alt="media.alt_text || alt" class="media-preview__img" />
      </button>
      <ImageLightbox v-model:open="lightboxOpen" :images="[media]" />
    </template>
    <div v-else-if="media.kind === 'document'" class="media-preview__pdf-card">
      <Icon name="file-text" :size="40" class="media-preview__pdf-icon" />
      <div class="media-preview__pdf-meta">
        <span class="media-preview__pdf-title">
          {{ media.alt_text || alt || "Document" }}
        </span>
        <span class="media-preview__pdf-hint">PDF</span>
      </div>
      <a :href="media.url" target="_blank" rel="noopener" class="media-preview__pdf-button">
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

.media-preview__img-btn {
  display: block;
  width: 100%;
  padding: 0;
  border: none;
  background: none;
  cursor: zoom-in;
}

.media-preview__img-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.media-preview__img {
  max-width: 100%;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  display: block;
}

.media-preview__pdf-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.media-preview__pdf-icon {
  color: var(--color-accent);
  flex-shrink: 0;
}

.media-preview__pdf-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.media-preview__pdf-title {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.media-preview__pdf-hint {
  font-size: 0.75rem;
  color: var(--color-fg-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.media-preview__pdf-button {
  background: var(--color-accent);
  color: #ffffff;
  padding: 8px 14px;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  flex-shrink: 0;
}

.media-preview__pdf-button:hover {
  filter: brightness(0.92);
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
  background: radial-gradient(
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

[data-theme="dog"] .media-preview__img,
[data-theme="dog"] .media-preview__video {
  border-radius: 0;
  border: 3px solid var(--color-fg);
}

[data-theme="dog"] .media-preview__pdf-card {
  border-radius: 0;
  border: 3px solid var(--color-fg);
  box-shadow: 4px 4px 0 var(--color-fg);
}

[data-theme="dog"] .media-preview__pdf-button {
  border-radius: 0;
}
</style>
