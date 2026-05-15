<script setup lang="ts">
import type { Cv } from "@/api/types";

defineProps<{ cv: Cv }>();
</script>

<template>
  <section class="section" aria-labelledby="contact-title">
    <div class="container">
      <h2 id="contact-title" class="section__title">{{ $t("nav.contact") }}</h2>
      <div class="card">
        <p>
          <a :href="`mailto:${cv.email}`">{{ cv.email }}</a>
          <span v-if="cv.phone"> · {{ cv.phone }}</span>
        </p>
        <p>
          <a
            v-for="link in cv.social_links"
            :key="link.id"
            :href="link.url"
            target="_blank"
            rel="noopener"
            style="margin-right: var(--space-3)"
          >
            {{ link.label || link.platform }}
          </a>
        </p>
      </div>
    </div>
  </section>
</template>
