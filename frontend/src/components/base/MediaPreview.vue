<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import type { MediaAsset } from "@/api/types";

const props = withDefaults(defineProps<{ media: MediaAsset; alt?: string }>(), { alt: "" });
const { t } = useI18n();
const locked = computed(() => !props.media.url);
</script>

<template>
  <div class="media-preview">
    <div
      v-if="locked"
      class="media-preview__locked"
      :title="t('sensitive.tooltip')"
      :aria-label="t('timeline.locked_file')"
    >
      🔒
    </div>
    <img
      v-else-if="media.kind === 'image'"
      :src="media.url"
      :alt="media.alt_text || alt"
      class="media-preview__img"
    />
    <iframe
      v-else-if="media.kind === 'document'"
      :src="media.url"
      class="media-preview__iframe"
      :title="media.alt_text || alt || 'Document'"
    />
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

.media-preview__iframe {
  width: 100%;
  height: 600px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.media-preview__video {
  max-width: 100%;
  border-radius: var(--radius-md);
}

.media-preview__locked {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 200px;
  background: repeating-linear-gradient(
    45deg,
    var(--color-surface),
    var(--color-surface) 8px,
    var(--color-border) 8px,
    var(--color-border) 16px
  );
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  font-size: 2rem;
  cursor: help;
  user-select: none;
}
</style>
