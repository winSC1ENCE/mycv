<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import type { MediaAsset } from "@/api/types";

const props = withDefaults(
  defineProps<{ images: MediaAsset[]; open: boolean; initialIndex?: number }>(),
  { initialIndex: 0 },
);
const emit = defineEmits<{
  "update:open": [value: boolean];
  "update:initialIndex": [value: number];
}>();

const { t } = useI18n();
const activeIdx = ref(props.initialIndex);

watch(
  () => [props.open, props.initialIndex] as const,
  ([open, idx]) => {
    if (open) activeIdx.value = idx;
  },
);

const activeImage = computed(() => props.images[activeIdx.value] ?? null);
const multi = computed(() => props.images.length > 1);

function close(): void {
  emit("update:open", false);
}

function prev(): void {
  const n = props.images.length;
  if (n === 0) return;
  activeIdx.value = (activeIdx.value - 1 + n) % n;
  emit("update:initialIndex", activeIdx.value);
}

function next(): void {
  const n = props.images.length;
  if (n === 0) return;
  activeIdx.value = (activeIdx.value + 1) % n;
  emit("update:initialIndex", activeIdx.value);
}

function onKeydown(e: KeyboardEvent): void {
  if (!props.open) return;
  if (e.key === "Escape") close();
  else if (e.key === "ArrowLeft") prev();
  else if (e.key === "ArrowRight") next();
}

onMounted(() => window.addEventListener("keydown", onKeydown));
onUnmounted(() => window.removeEventListener("keydown", onKeydown));
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open && activeImage"
      class="image-lightbox"
      role="dialog"
      aria-modal="true"
      @click.self="close"
    >
      <button
        type="button"
        class="image-lightbox__close"
        :aria-label="t('actions.close')"
        @click="close"
      >
        ✕
      </button>
      <button
        v-if="multi"
        type="button"
        class="image-lightbox__nav image-lightbox__nav--prev"
        :aria-label="t('actions.previous')"
        @click.stop="prev"
      >
        ‹
      </button>
      <img
        :src="activeImage.url"
        :alt="activeImage.alt_text || ''"
        class="image-lightbox__img"
      />
      <button
        v-if="multi"
        type="button"
        class="image-lightbox__nav image-lightbox__nav--next"
        :aria-label="t('actions.next')"
        @click.stop="next"
      >
        ›
      </button>
    </div>
  </Teleport>
</template>

<style scoped>
.image-lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: var(--space-4);
}

.image-lightbox__img {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  display: block;
  border-radius: var(--radius-md);
}

.image-lightbox__close,
.image-lightbox__nav {
  position: absolute;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 1.5rem;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 120ms;
}

.image-lightbox__close:hover,
.image-lightbox__nav:hover {
  background: rgba(0, 0, 0, 0.9);
}

.image-lightbox__close {
  top: var(--space-4);
  right: var(--space-4);
}

.image-lightbox__nav--prev {
  left: var(--space-4);
}

.image-lightbox__nav--next {
  right: var(--space-4);
}

[data-theme="dog"] .image-lightbox__close,
[data-theme="dog"] .image-lightbox__nav {
  border-radius: 0;
  border: 2px solid #fff;
}

[data-theme="dog"] .image-lightbox__img {
  border-radius: 0;
  filter: grayscale(1) contrast(1.1);
  border: 3px solid #fff;
}
</style>
