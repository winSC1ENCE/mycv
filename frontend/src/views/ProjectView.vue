<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useCvStore } from "@/stores/cv";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";
import { usePageMeta } from "@/composables/usePageMeta";
import ImageLightbox from "@/components/base/ImageLightbox.vue";
import RichText from "@/components/base/RichText.vue";
import Icon from "@/components/base/Icon.vue";

const props = defineProps<{ slug: string }>();

const router = useRouter();

function goBack() {
  if (window.history.state?.back) router.back();
  else router.push({ name: "home" });
}

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

usePageMeta({
  title: () => (name.value ? `${name.value} — Project` : "Project"),
  description: () => summary.value || description.value || "",
});
</script>

<template>
  <section class="section">
    <div class="container project-detail">
      <button type="button" class="project-detail__back" @click="goBack">← Back</button>

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

        <ImageLightbox
          v-model:open="lightboxOpen"
          :images="project.media"
          :initial-index="activeIdx"
          @update:initial-index="activeIdx = $event"
        />

        <RichText v-if="description" :text="description" class="project-detail__desc" />
        <p v-if="project.url">
          <a :href="project.url" target="_blank" rel="noopener">{{ project.url }}</a>
        </p>
        <p v-if="project.repo_url">
          <a :href="project.repo_url" target="_blank" rel="noopener" class="project-detail__repo">
            <Icon name="github" /> {{ $t("projects.source_code") }}
          </a>
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
  padding: 0;
  border: none;
  background: none;
  color: var(--color-fg-muted);
  font-size: 0.9rem;
  font-family: inherit;
  cursor: pointer;
}

.project-detail__title {
  margin: 0 0 var(--space-4);
}

.project-detail__repo {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-accent);
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
</style>
