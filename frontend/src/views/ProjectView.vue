<script setup lang="ts">
import { computed } from "vue";
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

usePageMeta({
  title: () => (name.value ? `${name.value} — Project` : "Project"),
  description: () => summary.value || description.value || "",
});
</script>

<template>
  <section class="section">
    <div class="container">
      <router-link to="/">← Back</router-link>
      <template v-if="project">
        <h1>{{ name }}</h1>
        <p>{{ description }}</p>
        <p v-if="project.url">
          <a :href="project.url" target="_blank" rel="noopener">{{ project.url }}</a>
        </p>
        <div>
          <span v-for="tech in project.technologies" :key="tech.id" class="tag">{{
            tech.name
          }}</span>
        </div>
      </template>
      <p v-else>Project not found.</p>
    </div>
  </section>
</template>
