<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";
import type { Project } from "@/api/types";

defineProps<{ projects: Project[] }>();
const { locale } = storeToRefs(useLocaleStore());
</script>

<template>
  <section class="section" aria-labelledby="projects-title">
    <div class="container">
      <h2 id="projects-title" class="section__title">{{ $t("nav.projects") }}</h2>
      <div class="grid grid--2">
        <article v-for="project in projects" :key="project.id" class="card project-card">
          <router-link
            v-if="project.media.length"
            :to="{ name: 'project', params: { slug: project.slug } }"
            class="project-card__thumb-link"
          >
            <img
              :src="project.media[0].url"
              :alt="project.media[0].alt_text || pickLocalized(project, 'name', locale)"
              class="project-card__thumb"
            />
          </router-link>
          <div class="project-card__body">
            <h3 class="project-card__title">
              <router-link :to="{ name: 'project', params: { slug: project.slug } }">
                {{ pickLocalized(project, "name", locale) }}
              </router-link>
            </h3>
            <p class="project-card__summary">
              {{ pickLocalized(project, "summary", locale) }}
            </p>
            <div class="project-card__tags">
              <span v-for="tech in project.technologies" :key="tech.id" class="tag">{{
                tech.name
              }}</span>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.project-card {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.project-card__thumb-link {
  display: block;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.project-card__thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 200ms ease;
}

.project-card__thumb-link:hover .project-card__thumb {
  transform: scale(1.04);
}

.project-card__body {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  flex: 1;
}

.project-card__title {
  font-size: 1rem;
  margin: 0;
}

.project-card__summary {
  color: var(--color-fg-muted);
  font-size: 0.9rem;
  margin: 0;
  flex: 1;
}

.project-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

[data-theme="dog"] .project-card {
  border: 3px solid var(--color-fg);
  box-shadow: 4px 4px 0 var(--color-fg);
}

[data-theme="dog"] .project-card__thumb-link:hover .project-card__thumb {
  transform: none;
  filter: grayscale(1) contrast(1.2);
}
</style>
