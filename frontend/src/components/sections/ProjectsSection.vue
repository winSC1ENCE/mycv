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
        <article v-for="project in projects" :key="project.id" class="card">
          <h3>
            <router-link :to="{ name: 'project', params: { slug: project.slug } }">
              {{ pickLocalized(project, "name", locale) }}
            </router-link>
          </h3>
          <p>
            {{ pickLocalized(project, "summary", locale) }}
          </p>
          <div>
            <span v-for="tech in project.technologies" :key="tech.id" class="tag">{{
              tech.name
            }}</span>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
