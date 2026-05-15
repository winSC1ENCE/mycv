<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";
import type { Education } from "@/api/types";

defineProps<{ educations: Education[] }>();
const { locale } = storeToRefs(useLocaleStore());
</script>

<template>
  <section class="section" aria-labelledby="education-title">
    <div class="container">
      <h2 id="education-title" class="section__title">{{ $t("nav.education") }}</h2>
      <div class="grid grid--2">
        <article v-for="edu in educations" :key="edu.id" class="card">
          <h3>{{ pickLocalized(edu, "degree", locale) }}</h3>
          <p class="timeline__date">
            {{ edu.institution }} · {{ edu.start_date }} → {{ edu.end_date ?? "" }}
          </p>
          <p>
            {{ pickLocalized(edu, "description", locale) }}
          </p>
        </article>
      </div>
    </div>
  </section>
</template>
