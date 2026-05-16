<template>
  <div class="skeleton" :style="{ height, width }" aria-hidden="true" />
</template>

<script setup lang="ts">
withDefaults(defineProps<{ height?: string; width?: string }>(), {
  height: "1em",
  width: "100%",
});
</script>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-surface) 25%,
    var(--color-border) 50%,
    var(--color-surface) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
  border-radius: var(--radius-sm);
  display: block;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton {
    animation: none;
  }
}
</style>
