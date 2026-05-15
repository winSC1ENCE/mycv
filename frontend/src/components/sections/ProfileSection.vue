<script setup lang="ts">
import type { Cv } from "@/api/types";

defineProps<{ cv: Cv }>();
</script>

<template>
  <section class="section" aria-labelledby="profile-title">
    <div class="container">
      <h2 id="profile-title" class="section__title">{{ $t("nav.summary") }}</h2>
      <div class="card">
        <p>
          <strong>{{ cv.full_name }}</strong> · {{ cv.title }}
        </p>
        <p v-if="cv.location">📍 {{ cv.location }}</p>
        <p v-if="cv.email">
          <a :href="`mailto:${cv.email}`">{{ cv.email }}</a>
        </p>
      </div>
    </div>
  </section>
</template>
