import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { login as apiLogin, logout as apiLogout, fetchMe } from "@/api/auth";
import type { User } from "@/api/types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const isLoading = ref(false);

  const isAuthenticated = computed(() => user.value !== null);
  const isAdmin = computed(() => user.value?.is_staff === true);

  async function init(): Promise<void> {
    try {
      user.value = await fetchMe();
    } catch {
      user.value = null;
    }
  }

  async function login(username: string, password: string): Promise<void> {
    isLoading.value = true;
    try {
      user.value = await apiLogin(username, password);
    } finally {
      isLoading.value = false;
    }
  }

  async function logout(): Promise<void> {
    await apiLogout();
    user.value = null;
  }

  return { user, isLoading, isAuthenticated, isAdmin, init, login, logout };
});
