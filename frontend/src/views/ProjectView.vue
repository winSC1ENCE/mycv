<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { storeToRefs } from "pinia";
import { useCvStore } from "@/stores/cv";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";
import { usePageMeta } from "@/composables/usePageMeta";

const props = defineProps<{ slug: string }>();

const cvStore = useCvStore();
const { cv } = storeToRefs(cvStore);
const { locale } = storeToRefs(useLocaleStore());

const project = computed(() => cv.value?.projects.find((p) => p.slug === props.slug));
const name = computed(() => pickLocalized(project.value, "name", locale.value));
const description = computed(() => pickLocalized(project.value, "description", locale.value));
const summary = computed(() => pickLocalized(project.value, "summary", locale.value));

const activeIdx = ref(0);
const activeImage = computed(() => project.value?.media[activeIdx.value] ?? null);
const lightboxOpen = ref(false);

function mediaCount(): number {
  return project.value?.media.length ?? 0;
}

function prevPhoto(): void {
  const n = mediaCount();
  if (n === 0) return;
  activeIdx.value = (activeIdx.value - 1 + n) % n;
}

function nextPhoto(): void {
  const n = mediaCount();
  if (n === 0) return;
  activeIdx.value = (activeIdx.value + 1) % n;
}

function onKeydown(e: KeyboardEvent): void {
  if (!lightboxOpen.value) return;
  if (e.key === "Escape") lightboxOpen.value = false;
  else if (e.key === "ArrowLeft") prevPhoto();
  else if (e.key === "ArrowRight") nextPhoto();
}

onMounted(() => window.addEventListener("keydown", onKeydown));
onUnmounted(() => window.removeEventListener("keydown", onKeydown));

usePageMeta({
  title: () => (name.value ? `${name.value} — Project` : "Project"),
  description: () => summary.value || description.value || "",
});
</script>

<template>
  <section class="section">
    <div class="container project-detail">
      <router-link to="/" class="project-detail__back">← Back</router-link>

      <template v-if="project">
        <h1 class="project-detail__title">{{ name }}</h1>

        <!-- Image gallery -->
        <div v-if="project.media.length" class="project-gallery">
          <button
            type="button"
            class="project-gallery__main"
            :aria-label="$t('actions.zoom_image')"
            @click="lightboxOpen = true"
          >
            <img
              :src="activeImage!.url"
              :alt="activeImage!.alt_text || name"
              class="project-gallery__hero"
            />
          </button>
          <div v-if="project.media.length > 1" class="project-gallery__thumbs">
            <button
              v-for="(asset, i) in project.media"
              :key="asset.id"
              type="button"
              class="project-gallery__thumb-btn"
              :class="{ 'project-gallery__thumb-btn--active': i === activeIdx }"
              @click="activeIdx = i"
            >
              <img
                :src="asset.url"
                :alt="asset.alt_text || `${name} ${i + 1}`"
                class="project-gallery__thumb-img"
              />
            </button>
          </div>
        </div>

        <Teleport to="body">
          <div
            v-if="lightboxOpen"
            class="lightbox"
            role="dialog"
            aria-modal="true"
            @click.self="lightboxOpen = false"
          >
            <button
              type="button"
              class="lightbox__close"
              :aria-label="$t('actions.close')"
              @click="lightboxOpen = false"
            >
              ✕
            </button>
            <button
              v-if="project.media.length > 1"
              type="button"
              class="lightbox__nav lightbox__nav--prev"
              :aria-label="$t('actions.previous')"
              @click.stop="prevPhoto"
            >
              ‹
            </button>
            <img
              v-if="activeImage"
              :src="activeImage.url"
              :alt="activeImage.alt_text || name"
              class="lightbox__img"
            />
            <button
              v-if="project.media.length > 1"
              type="button"
              class="lightbox__nav lightbox__nav--next"
              :aria-label="$t('actions.next')"
              @click.stop="nextPhoto"
            >
              ›
            </button>
          </div>
        </Teleport>

        <p v-if="description" class="project-detail__desc">{{ description }}</p>
        <p v-if="project.url">
          <a :href="project.url" target="_blank" rel="noopener">{{ project.url }}</a>
        </p>
        <div class="project-detail__tags">
          <span v-for="tech in project.technologies" :key="tech.id" class="tag">{{
            tech.name
          }}</span>
        </div>
      </template>
      <p v-else>Project not found.</p>
    </div>
  </section>
</template>

<style scoped>
.project-detail {
  max-width: 860px;
}

.project-detail__back {
  display: inline-block;
  margin-bottom: var(--space-4);
  color: var(--color-fg-muted);
  font-size: 0.9rem;
}

.project-detail__title {
  margin: 0 0 var(--space-4);
}

.project-detail__desc {
  line-height: 1.7;
  white-space: pre-line;
}

.project-detail__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: var(--space-3);
}

/* Gallery */
.project-gallery {
  margin-bottom: var(--space-6);
}

.project-gallery__main {
  display: block;
  width: 100%;
  padding: 0;
  border: none;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-surface);
  aspect-ratio: 16 / 10;
  cursor: zoom-in;
}

.project-gallery__hero {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.project-gallery__thumbs {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-2);
  flex-wrap: wrap;
}

.project-gallery__thumb-btn {
  width: 72px;
  height: 54px;
  padding: 0;
  border: 2px solid transparent;
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
  background: none;
  flex-shrink: 0;
  transition: border-color 120ms;
}

.project-gallery__thumb-btn--active {
  border-color: var(--color-accent);
}

.project-gallery__thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* Dog mode */
[data-theme="dog"] .project-gallery__main {
  border: 3px solid var(--color-fg);
  box-shadow: 4px 4px 0 var(--color-fg);
  border-radius: 0;
}

[data-theme="dog"] .project-gallery__thumb-btn {
  border-color: var(--color-fg);
  border-radius: 0;
}

[data-theme="dog"] .project-gallery__thumb-btn--active {
  box-shadow: 2px 2px 0 var(--color-fg);
}

[data-theme="dog"] .project-gallery__hero {
  filter: grayscale(1) contrast(1.1);
}

[data-theme="dog"] .project-gallery__thumb-img {
  filter: grayscale(1) contrast(1.1);
}

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: var(--space-4);
}

.lightbox__img {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  display: block;
  border-radius: var(--radius-md);
}

.lightbox__close,
.lightbox__nav {
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

.lightbox__close:hover,
.lightbox__nav:hover {
  background: rgba(0, 0, 0, 0.9);
}

.lightbox__close {
  top: var(--space-4);
  right: var(--space-4);
}

.lightbox__nav--prev {
  left: var(--space-4);
}

.lightbox__nav--next {
  right: var(--space-4);
}

[data-theme="dog"] .lightbox__close,
[data-theme="dog"] .lightbox__nav {
  border-radius: 0;
  border: 2px solid #fff;
}

[data-theme="dog"] .lightbox__img {
  border-radius: 0;
  filter: grayscale(1) contrast(1.1);
  border: 3px solid #fff;
}
</style>
