<script setup lang="ts">
import { computed } from "vue";
import { storeToRefs } from "pinia";
import { useCvStore } from "@/stores/cv";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";

import ProfileSection from "@/components/sections/ProfileSection.vue";
import ExperienceSection from "@/components/sections/ExperienceSection.vue";
import EducationSection from "@/components/sections/EducationSection.vue";
import SkillsSection from "@/components/sections/SkillsSection.vue";
import CertificatesSection from "@/components/sections/CertificatesSection.vue";
import ProjectsSection from "@/components/sections/ProjectsSection.vue";
import TimelineSection from "@/components/timeline/TimelineSection.vue";
import ContactSection from "@/components/sections/ContactSection.vue";

const cvStore = useCvStore();
const { cv, loading, error } = storeToRefs(cvStore);
const { locale } = storeToRefs(useLocaleStore());

const summary = computed(() => pickLocalized(cv.value, "summary", locale.value));
const title = computed(() => pickLocalized(cv.value, "title", locale.value));
</script>

<template>
  <section class="hero">
    <div class="container">
      <p v-if="loading">{{ $t("labels.loading") }}</p>
      <p v-else-if="error">{{ $t("labels.error") }}</p>
      <template v-else-if="cv">
        <h1 class="hero__title">{{ cv.full_name }}</h1>
        <p class="hero__subtitle">{{ title }}</p>
        <p>{{ summary }}</p>
      </template>
    </div>
  </section>

  <template v-if="cv">
    <ProfileSection :cv="cv" />
    <TimelineSection :cv="cv" />
    <ExperienceSection :experiences="cv.experiences" />
    <EducationSection :educations="cv.educations" />
    <SkillsSection :categories="cv.skill_categories" />
    <CertificatesSection :certificates="cv.certificates" />
    <ProjectsSection :projects="cv.projects" />
    <ContactSection :cv="cv" />
  </template>
</template>
