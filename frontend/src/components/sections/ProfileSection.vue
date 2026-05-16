<script setup lang="ts">
import { computed } from "vue";
import type { Cv } from "@/api/types";
import { useThemeStore } from "@/stores/theme";

defineProps<{ cv: Cv }>();

const themeStore = useThemeStore();
const profilePhoto = computed(() =>
  themeStore.theme === "dog" ? "/profile-dog.png" : "/profile-normal.png",
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
          <p v-if="cv.location">📍 {{ cv.location }}</p>
          <p v-if="cv.email">
            <a :href="`mailto:${cv.email}`">{{ cv.email }}</a>
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
  flex-shrink: 0;
}

[data-theme="dog"] .profile-card__photo {
  border-radius: var(--radius-sm);
  border: 3px solid var(--color-ink);
  box-shadow: 4px 4px 0 var(--color-ink);
}

.profile-card__info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

@media (max-width: 480px) {
  .profile-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
