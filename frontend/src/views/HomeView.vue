<script setup lang="ts">
import { computed } from "vue";
import { storeToRefs } from "pinia";
import { useCvStore } from "@/stores/cv";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";
import { usePageMeta } from "@/composables/usePageMeta";

import ProfileSection from "@/components/sections/ProfileSection.vue";
import SkillsSection from "@/components/sections/SkillsSection.vue";
import ProjectsSection from "@/components/sections/ProjectsSection.vue";
import TimelineSection from "@/components/timeline/TimelineSection.vue";
import ContactSection from "@/components/sections/ContactSection.vue";
import CvSkeleton from "@/components/base/CvSkeleton.vue";
import RichText from "@/components/base/RichText.vue";

const cvStore = useCvStore();
const { cv, loading, error } = storeToRefs(cvStore);
const { locale } = storeToRefs(useLocaleStore());

const summary = computed(() => pickLocalized(cv.value, "summary", locale.value));
const title = computed(() => pickLocalized(cv.value, "title", locale.value));

usePageMeta({
  title: () => (cv.value ? `${cv.value.full_name} — CV` : "CV"),
  description: () => summary.value || "Interactive CV",
  jsonLd: () => {
    if (!cv.value) return {};
    const ld: Record<string, unknown> = {
      "@context": "https://schema.org",
      "@type": "Person",
      name: cv.value.full_name,
      givenName: cv.value.first_name,
      familyName: cv.value.last_name,
      jobTitle: title.value,
      url: typeof window !== "undefined" ? window.location.origin : "",
      sameAs: cv.value.social_links.map((s) => s.url),
    };
    if (cv.value.access_granted) {
      ld.email = cv.value.email;
    }
    return ld;
  },
});
</script>

<template>
  <CvSkeleton v-if="loading" />
  <section v-else-if="error" class="hero">
    <div class="container">
      <p>{{ $t("labels.error") }}</p>
    </div>
  </section>

  <template v-else-if="cv">
    <section class="hero">
      <div class="container">
        <h1 class="hero__title">{{ cv.full_name }}</h1>
        <p class="hero__subtitle">{{ title }}</p>
        <RichText v-if="summary" :text="summary" class="hero__summary" />
      </div>
    </section>

    <ProfileSection :cv="cv" />
    <TimelineSection />
    <SkillsSection :categories="cv.skill_categories" />
    <ProjectsSection :projects="cv.projects" />
    <ContactSection :cv="cv" />
  </template>
</template>
