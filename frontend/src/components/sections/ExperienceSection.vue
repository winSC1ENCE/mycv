<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useLocaleStore } from "@/stores/locale";
import { useI18n } from "vue-i18n";
import { pickLocalized } from "@/composables/useLocalized";
import type { Experience } from "@/api/types";

defineProps<{ experiences: Experience[] }>();
const { locale } = storeToRefs(useLocaleStore());
const { t } = useI18n();
</script>

<template>
  <section class="section" aria-labelledby="experience-title">
    <div class="container">
      <h2 id="experience-title" class="section__title">{{ $t("nav.experience") }}</h2>
      <div class="grid grid--2">
        <article v-for="exp in experiences" :key="exp.id" class="card">
          <h3>
            {{ pickLocalized(exp, "role", locale) }}
            <span> — {{ exp.company }}</span>
          </h3>
          <p class="timeline__date">
            {{ exp.start_date }} → {{ exp.end_date ?? t("labels.present") }}
            <span v-if="exp.location"> · {{ exp.location }}</span>
          </p>
          <p>
            {{ pickLocalized(exp, "description", locale) }}
          </p>
          <div>
            <span v-for="tech in exp.technologies" :key="tech.id" class="tag">{{ tech.name }}</span>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
