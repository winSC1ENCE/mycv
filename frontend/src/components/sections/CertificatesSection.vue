<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useLocaleStore } from "@/stores/locale";
import { pickLocalized } from "@/composables/useLocalized";
import type { Certificate } from "@/api/types";

defineProps<{ certificates: Certificate[] }>();
const { locale } = storeToRefs(useLocaleStore());
</script>

<template>
  <section class="section" aria-labelledby="certificates-title">
    <div class="container">
      <h2 id="certificates-title" class="section__title">{{ $t("nav.certificates") }}</h2>
      <div class="grid grid--2">
        <article v-for="cert in certificates" :key="cert.id" class="card">
          <h3>{{ pickLocalized(cert, "name", locale) }}</h3>
          <p class="timeline__date">{{ cert.issuer }} · {{ cert.issue_date }}</p>
          <p>
            {{ pickLocalized(cert, "description", locale) }}
          </p>
        </article>
      </div>
    </div>
  </section>
</template>
