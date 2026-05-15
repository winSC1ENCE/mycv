<script setup lang="ts">
import { onMounted } from "vue";
import { storeToRefs } from "pinia";
import { useI18n } from "vue-i18n";
import { useCvStore } from "@/stores/cv";
import { useThemeStore } from "@/stores/theme";
import { useLocaleStore } from "@/stores/locale";

const cvStore = useCvStore();
const themeStore = useThemeStore();
const localeStore = useLocaleStore();
const { cv } = storeToRefs(cvStore);
const { theme } = storeToRefs(themeStore);
const { locale } = storeToRefs(localeStore);
const { t, locale: i18nLocale } = useI18n();

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
    <router-view />
  </main>

  <footer class="footer">
    <div class="container">
      <p>© {{ new Date().getFullYear() }} {{ cv ? cv.full_name : "" }} · cv.chlous.top</p>
    </div>
  </footer>
</template>
