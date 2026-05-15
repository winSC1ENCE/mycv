import { defineStore } from "pinia";
import { ref, watch } from "vue";

export type Theme = "normal" | "dog";
const STORAGE_KEY = "mycv:theme";

function readInitial(): Theme {
  if (typeof window === "undefined") return "normal";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === "dog" ? "dog" : "normal";
}

export const useThemeStore = defineStore("theme", () => {
  const theme = ref<Theme>(readInitial());

  function apply(value: Theme): void {
    if (typeof document !== "undefined") {
      document.documentElement.dataset.theme = value;
    }
  }

  function toggle(): void {
    theme.value = theme.value === "normal" ? "dog" : "normal";
  }

  watch(
    theme,
    (value) => {
      apply(value);
      if (typeof window !== "undefined") window.localStorage.setItem(STORAGE_KEY, value);
    },
    { immediate: true },
  );

  return { theme, toggle };
});
