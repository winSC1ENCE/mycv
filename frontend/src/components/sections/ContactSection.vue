<script setup lang="ts">
import { computed } from "vue";
import type { Cv } from "@/api/types";
import Sensitive from "@/components/base/Sensitive.vue";
import Icon from "@/components/base/Icon.vue";

const props = defineProps<{ cv: Cv }>();

const mapsUrl = computed(
  () => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(props.cv.address)}`,
);
</script>

<template>
  <section class="section" aria-labelledby="contact-title">
    <div class="container">
      <h2 id="contact-title" class="section__title">{{ $t("nav.contact") }}</h2>
      <div class="card contact-card">
        <p class="contact-card__row">
          <Icon name="mail" />
          <span v-if="cv.access_granted">{{ cv.email }}</span>
          <Sensitive v-else :blurred="true">{{ cv.email }}</Sensitive>
        </p>
        <p v-if="cv.phone" class="contact-card__row">
          <Icon name="phone" />
          <Sensitive :blurred="!cv.access_granted">{{ cv.phone }}</Sensitive>
        </p>
        <p v-if="cv.address" class="contact-card__row">
          <Icon name="map-pin" />
          <a v-if="cv.access_granted" :href="mapsUrl" target="_blank" rel="noopener">
            {{ cv.address }}
          </a>
          <Sensitive v-else :blurred="true">{{ cv.address }}</Sensitive>
        </p>
        <p class="contact-card__links">
          <a
            v-for="link in cv.social_links"
            :key="link.id"
            :href="link.url"
            target="_blank"
            rel="noopener"
          >
            {{ link.label || link.platform }}
          </a>
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.contact-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.contact-card__row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.contact-card__row .icon {
  color: var(--color-fg-muted);
}

.contact-card__links {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin: var(--space-2) 0 0;
}
</style>
