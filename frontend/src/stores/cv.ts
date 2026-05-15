import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { fetchCv } from "@/api/client";
import type { Cv } from "@/api/types";

export const useCvStore = defineStore("cv", () => {
  const cv = ref<Cv | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isLoaded = computed(() => cv.value !== null);

  async function load(): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      cv.value = await fetchCv();
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to load CV";
    } finally {
      loading.value = false;
    }
  }

  return { cv, loading, error, isLoaded, load };
});
