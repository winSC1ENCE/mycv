import { beforeEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";
import { createPinia, setActivePinia } from "pinia";
import { useThemeStore } from "@/stores/theme";
import { useLocaleStore } from "@/stores/locale";

describe("stores", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it("theme toggles between normal and dog", () => {
    const store = useThemeStore();
    expect(store.theme).toBe("normal");
    store.toggle();
    expect(store.theme).toBe("dog");
    store.toggle();
    expect(store.theme).toBe("normal");
  });

  it("theme persists to localStorage and document dataset", async () => {
    const store = useThemeStore();
    store.toggle();
    await nextTick();
    expect(localStorage.getItem("mycv:theme")).toBe("dog");
    expect(document.documentElement.dataset.theme).toBe("dog");
  });

  it("locale toggles between en and de", () => {
    const store = useLocaleStore();
    expect(store.locale).toBe("en");
    store.toggle();
    expect(store.locale).toBe("de");
    store.set("en");
    expect(store.locale).toBe("en");
  });
});
