<script setup lang="ts">
import { computed } from "vue";
import type { Cv } from "@/api/types";
import Sensitive from "@/components/base/Sensitive.vue";

const props = defineProps<{ cv: Cv }>();

const mapsUrl = computed(
  () => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(props.cv.address)}`,
);
</script>

<template>
  <section class="section" aria-labelledby="contact-title">
    <div class="container">
      <h2 id="contact-title" class="section__title">{{ $t("nav.contact") }}</h2>
      <div class="card">
        <p>
          <span v-if="cv.access_granted">{{ cv.email }}</span>
          <Sensitive v-else :blurred="true">{{ cv.email }}</Sensitive>
          <span v-if="cv.phone">
            · <Sensitive :blurred="!cv.access_granted">{{ cv.phone }}</Sensitive>
          </span>
        </p>
        <p v-if="cv.address" class="contact-meta">
          📍
          <a v-if="cv.access_granted" :href="mapsUrl" target="_blank" rel="noopener">
            {{ cv.address }}
          </a>
          <Sensitive v-else :blurred="true">{{ cv.address }}</Sensitive>
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
