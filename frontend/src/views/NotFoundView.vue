<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { usePageMeta } from "@/composables/usePageMeta";

const { t } = useI18n();

usePageMeta({
  title: () => t("errors.notFound.title"),
  description: () => t("errors.notFound.message"),
});
</script>

<template>
  <section class="section not-found">
    <div class="container not-found__inner">
      <div class="not-found__art" aria-hidden="true">
        <svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">
          <!-- comic-style "lost dog" silhouette -->
          <ellipse cx="100" cy="105" rx="60" ry="6" fill="currentColor" opacity="0.15" />
          <path
            d="M50 70 q-10 -25 5 -40 q15 -15 35 -10 q5 -20 25 -20 q15 0 22 10 q15 -5 25 5 q10 10 5 25 q5 15 -5 25 q5 15 -10 20 l-10 -5 l-5 10 l-10 -5 l-5 8 l-10 -8 l-12 5 l-8 -8 l-10 5 l-12 -7 z"
            fill="currentColor"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          />
          <circle cx="88" cy="42" r="3" fill="white" />
          <circle cx="110" cy="42" r="3" fill="white" />
          <circle cx="88" cy="42" r="1.5" fill="currentColor" />
          <circle cx="110" cy="42" r="1.5" fill="currentColor" />
          <path d="M93 55 q6 4 12 0" fill="none" stroke="white" stroke-width="1.5" />
        </svg>
      </div>
      <h1 class="not-found__code">404</h1>
      <h2 class="not-found__title">{{ t("errors.notFound.title") }}</h2>
      <p class="not-found__message">{{ t("errors.notFound.message") }}</p>
      <router-link class="button" :to="{ name: 'home' }">
        ← {{ t("errors.notFound.backHome") }}
      </router-link>
    </div>
  </section>
</template>

<style scoped>
.not-found {
  min-height: 70vh;
  display: flex;
  align-items: center;
}

.not-found__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-3);
  padding: var(--space-8) 0;
}

.not-found__art {
  width: 220px;
  color: var(--color-fg);
}

.not-found__art svg {
  width: 100%;
  height: auto;
}

.not-found__code {
  font-size: clamp(4rem, 12vw, 7rem);
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.04em;
  color: var(--color-accent);
  margin: 0;
}

.not-found__title {
  font-size: 1.5rem;
  font-weight: 700;
}

.not-found__message {
  color: var(--color-fg-muted);
  max-width: 36ch;
}

[data-theme="dog"] .not-found__code {
  transform: rotate(-3deg);
  display: inline-block;
}
</style>
