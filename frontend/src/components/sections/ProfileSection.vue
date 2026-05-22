<script setup lang="ts">
import { computed } from "vue";
import type { Cv } from "@/api/types";
import { useThemeStore } from "@/stores/theme";
import Sensitive from "@/components/base/Sensitive.vue";
import Icon from "@/components/base/Icon.vue";

defineProps<{ cv: Cv }>();

const themeStore = useThemeStore();
const profilePhoto = computed(() =>
  themeStore.theme === "dog" ? "/profile-dog.png" : "/profile-normal.jpg",
);
const photoAlt = computed(() =>
  themeStore.theme === "dog" ? "Nicolas Mischler — comic portrait" : "Nicolas Mischler",
);
</script>

<template>
  <section class="section" aria-labelledby="profile-title">
    <div class="container">
      <h2 id="profile-title" class="section__title">{{ $t("nav.summary") }}</h2>
      <div class="card profile-card">
        <img
          :src="profilePhoto"
          :alt="photoAlt"
          class="profile-card__photo"
          width="120"
          height="120"
        />
        <div class="profile-card__info">
          <p>
            <strong>{{ cv.full_name }}</strong> · {{ cv.title }}
          </p>
          <p v-if="cv.location" class="profile-card__row">
            <Icon name="map-pin" /> {{ cv.location }}
          </p>
          <p v-if="cv.zivilstand" class="profile-card__row">
            <Icon name="heart" />
            <Sensitive :blurred="!cv.access_granted">{{ cv.zivilstand }}</Sensitive>
          </p>
          <p v-if="cv.date_of_birth" class="profile-card__row">
            <Icon name="cake" />
            <Sensitive :blurred="!cv.access_granted">{{ cv.date_of_birth }}</Sensitive>
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.profile-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.profile-card__photo {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  object-position: center 25%;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

[data-theme="dog"] .profile-card__photo {
  border-radius: 50%;
  object-position: center center;
  border: 3px solid #0a0a0a;
  box-shadow: 4px 4px 0 #0a0a0a;
}

.profile-card__info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.profile-card__row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  color: var(--color-fg);
}

.profile-card__row .icon {
  color: var(--color-fg-muted);
}

@media (max-width: 480px) {
  .profile-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
