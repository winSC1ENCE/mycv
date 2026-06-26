import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";
import { isFunnyTheme, type ThemeId } from "@/themes/registry";

export type Theme = ThemeId;
const STORAGE_KEY = "mycv:theme";

function readInitial(): Theme {
  if (typeof window === "undefined") return "normal";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return isFunnyTheme(stored) ? stored : "normal";
}

export const useThemeStore = defineStore("theme", () => {
  const theme = ref<Theme>(readInitial());

  // Which single funny theme the admin has made available on the public site.
  // Gated server-side via `Person.active_funny_theme`; "none" disables funny mode.
  const activeFunny = ref<string>("dog");

  /** True when a funny theme is currently available to switch to. */
  const funnyAvailable = computed(() => isFunnyTheme(activeFunny.value));

  function apply(value: Theme): void {
    if (typeof document !== "undefined") {
      document.documentElement.dataset.theme = value;
    }
  }

  /** Set the active theme, ignoring funny ids that aren't the available one. */
  function setTheme(value: Theme): void {
    if (value === "normal") {
      theme.value = "normal";
      return;
    }
    if (value === activeFunny.value && isFunnyTheme(value)) {
      theme.value = value;
    }
  }

  /** Flip between Normal and the admin-selected funny theme. */
  function toggleFunny(): void {
    if (theme.value === "normal") {
      if (isFunnyTheme(activeFunny.value)) theme.value = activeFunny.value;
    } else {
      theme.value = "normal";
    }
  }

  /** Tell the store which funny theme the server allows; re-validate current. */
  function setAvailableFunny(value: string | null | undefined): void {
    activeFunny.value = value ?? "none";
    // If the current theme is a funny one that's no longer allowed, drop to normal.
    if (theme.value !== "normal" && theme.value !== activeFunny.value) {
      theme.value = "normal";
    }
  }

  watch(
    theme,
    (value) => {
      apply(value);
      if (typeof window !== "undefined") window.localStorage.setItem(STORAGE_KEY, value);
    },
    { immediate: true },
  );

  return { theme, activeFunny, funnyAvailable, setTheme, toggleFunny, setAvailableFunny };
});
