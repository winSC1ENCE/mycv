import { defineStore } from "pinia";
import { ref, watch } from "vue";

export type Locale = "en" | "de";
const STORAGE_KEY = "mycv:locale";

function readInitial(): Locale {
  if (typeof window === "undefined") return "en";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === "de" ? "de" : "en";
}

export const useLocaleStore = defineStore("locale", () => {
  const locale = ref<Locale>(readInitial());

  function set(value: Locale): void {
    locale.value = value;
  }

  function toggle(): void {
    locale.value = locale.value === "en" ? "de" : "en";
  }

  watch(locale, (value) => {
    if (typeof window !== "undefined") window.localStorage.setItem(STORAGE_KEY, value);
    if (typeof document !== "undefined") document.documentElement.lang = value;
  });

  return { locale, set, toggle };
});
