<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { storeToRefs } from "pinia";
import { useI18n } from "vue-i18n";
import { useCvStore } from "@/stores/cv";
import { useThemeStore } from "@/stores/theme";
import { useLocaleStore } from "@/stores/locale";
import { packFor } from "@/themes/registry";
import { useAccessKey } from "@/composables/useAccessKey";
import ErrorBoundary from "@/components/base/ErrorBoundary.vue";
import FunBubbles from "@/components/timeline/FunBubbles.vue";
import EasterEggButton from "@/components/base/EasterEggButton.vue";

const cvStore = useCvStore();
const themeStore = useThemeStore();
const localeStore = useLocaleStore();
const { cv } = storeToRefs(cvStore);
const { theme, activeFunny, funnyAvailable } = storeToRefs(themeStore);
const { locale } = storeToRefs(localeStore);
const { t, locale: i18nLocale } = useI18n();

// The funny theme the public site exposes is admin-controlled (server value).
watch(
  () => cv.value?.active_funny_theme,
  (value) => themeStore.setAvailableFunny(value),
  { immediate: true },
);

// Toggle button shows the available funny theme when in normal mode, else "Normal".
const toggleLabel = computed(() => {
  if (theme.value !== "normal") return "🌞 Normal";
  const pack = packFor(activeFunny.value);
  return pack ? `${pack.emoji} ${pack.label}` : "";
});

useAccessKey();

onMounted(() => {
  cvStore.load();
});
</script>

<template>
  <header class="header">
    <div class="container header__row">
      <router-link :to="{ name: 'home' }" class="header__brand">
        {{ cv ? cv.full_name : "mycv" }}
      </router-link>
      <div class="header__actions">
        <button
          type="button"
          class="button button--ghost"
          :aria-label="t('actions.toggle_language')"
          @click="
            localeStore.toggle();
            i18nLocale = locale;
          "
        >
          {{ locale === "en" ? "DE" : "EN" }}
        </button>
        <button
          v-if="funnyAvailable || theme !== 'normal'"
          type="button"
          class="button button--ghost"
          :aria-label="t('actions.toggle_theme')"
          @click="themeStore.toggleFunny()"
        >
          {{ toggleLabel }}
        </button>
      </div>
    </div>
  </header>

  <main>
    <ErrorBoundary>
      <router-view />
    </ErrorBoundary>
  </main>

  <footer class="footer">
    <div class="container">
      <p>© {{ new Date().getFullYear() }} {{ cv ? cv.full_name : "" }}</p>
    </div>
  </footer>

  <FunBubbles v-if="theme !== 'normal'" />
  <EasterEggButton v-if="theme !== 'normal'" :theme="theme" />
</template>
