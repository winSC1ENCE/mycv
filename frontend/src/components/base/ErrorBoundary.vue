<template>
  <slot v-if="!caughtError" />
  <section v-else class="section">
    <div class="container error-boundary">
      <h2 class="error-boundary__title">{{ $t("errors.somethingWentWrong") }}</h2>
      <p class="error-boundary__detail">{{ caughtError.message }}</p>
      <button class="button" @click="reset">{{ $t("errors.retry") }}</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from "vue";

const caughtError = ref<Error | null>(null);

onErrorCaptured((err) => {
  caughtError.value = err instanceof Error ? err : new Error(String(err));
  // Stop the error from propagating further so the rest of the app stays mounted
  return false;
});

function reset(): void {
  caughtError.value = null;
}
</script>

<style scoped>
.error-boundary {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  text-align: center;
  padding: var(--space-8) 0;
}

.error-boundary__title {
  font-size: 1.5rem;
  font-weight: 700;
}

.error-boundary__detail {
  color: var(--color-fg-muted);
  font-family: var(--font-mono);
  font-size: 0.875rem;
}
</style>
