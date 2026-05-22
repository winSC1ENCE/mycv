<script setup lang="ts">
import { onMounted, computed } from "vue";
import { storeToRefs } from "pinia";
import { useI18n } from "vue-i18n";
import { useCvStore } from "@/stores/cv";
import { useThemeStore } from "@/stores/theme";
import { useLocaleStore } from "@/stores/locale";
import { buildPdfUrl } from "@/api/exports";
import { useAccessKey } from "@/composables/useAccessKey";
import ErrorBoundary from "@/components/base/ErrorBoundary.vue";

const cvStore = useCvStore();
const themeStore = useThemeStore();
const localeStore = useLocaleStore();
const { cv } = storeToRefs(cvStore);
const { theme } = storeToRefs(themeStore);
const { locale } = storeToRefs(localeStore);
const { t, locale: i18nLocale } = useI18n();

const pdfUrl = computed(() => buildPdfUrl(locale.value, theme.value));

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
        <a
          class="button button--ghost"
          :href="pdfUrl"
          target="_blank"
          rel="noopener"
          :title="t('actions.download_pdf')"
        >
          📄 {{ t("actions.download_pdf") }}
        </a>
        <button
          type="button"
          class="button button--ghost"
          :aria-label="t('actions.toggle_language')"
          @click="
            localeStore.toggle();
            i18nLocale = locale;
          "
        >
          {{ locale.toUpperCase() }}
        </button>
        <button
          type="button"
          class="button button--ghost"
          :aria-label="t('actions.toggle_theme')"
          @click="themeStore.toggle()"
        >
          {{ theme === "normal" ? "🐕 Dog" : "🌞 Normal" }}
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
</template>
