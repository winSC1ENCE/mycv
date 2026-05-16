<template>
  <section class="hero">
    <div class="container cv-skeleton">
      <SkeletonBlock height="2.8rem" width="60%" />
      <SkeletonBlock height="1.4rem" width="40%" />
      <SkeletonBlock height="1rem" width="100%" />
      <SkeletonBlock height="1rem" width="92%" />
      <SkeletonBlock height="1rem" width="85%" />
    </div>
  </section>

  <section v-for="n in 3" :key="n" class="section">
    <div class="container cv-skeleton">
      <SkeletonBlock height="1.6rem" width="28%" />
      <div class="cv-skeleton__card">
        <SkeletonBlock height="1.1rem" width="50%" />
        <SkeletonBlock height="0.9rem" width="32%" />
        <SkeletonBlock height="0.9rem" width="100%" />
        <SkeletonBlock height="0.9rem" width="88%" />
      </div>
      <div class="cv-skeleton__card">
        <SkeletonBlock height="1.1rem" width="44%" />
        <SkeletonBlock height="0.9rem" width="30%" />
        <SkeletonBlock height="0.9rem" width="95%" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import SkeletonBlock from "./SkeletonBlock.vue";
</script>

<style scoped>
.cv-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.cv-skeleton__card {
  padding: var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
