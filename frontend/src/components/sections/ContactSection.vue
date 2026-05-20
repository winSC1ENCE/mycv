<script setup lang="ts">
import type { Cv } from "@/api/types";
import Sensitive from "@/components/base/Sensitive.vue";

defineProps<{ cv: Cv }>();
</script>

<template>
  <section class="section" aria-labelledby="contact-title">
    <div class="container">
      <h2 id="contact-title" class="section__title">{{ $t("nav.contact") }}</h2>
      <div class="card">
        <p>
          <a v-if="cv.access_granted" :href="`mailto:${cv.email}`">{{ cv.email }}</a>
          <Sensitive v-else :blurred="true">{{ cv.email }}</Sensitive>
          <span v-if="cv.phone"> · <Sensitive :blurred="!cv.access_granted">{{ cv.phone }}</Sensitive></span>
        </p>
        <p v-if="cv.address || cv.zivilstand || cv.date_of_birth" class="contact-meta">
          <span v-if="cv.address">
            📍 <Sensitive :blurred="!cv.access_granted">{{ cv.address }}</Sensitive>
          </span>
          <span v-if="cv.zivilstand">
            · <Sensitive :blurred="!cv.access_granted">{{ cv.zivilstand }}</Sensitive>
          </span>
          <span v-if="cv.date_of_birth">
            · <Sensitive :blurred="!cv.access_granted">{{ cv.date_of_birth }}</Sensitive>
          </span>
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
