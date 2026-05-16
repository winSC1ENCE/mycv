<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">{{ $t("admin.login") }}</h1>

      <form class="login-form" @submit.prevent="submit">
        <div class="field">
          <label class="field__label" for="username">{{ $t("admin.username") }}</label>
          <input
            id="username"
            v-model="username"
            class="field__input"
            type="text"
            autocomplete="username"
            :class="{ 'field__input--error': errors.username }"
          />
          <span v-if="errors.username" class="field__error">{{ errors.username }}</span>
        </div>

        <div class="field">
          <label class="field__label" for="password">{{ $t("admin.password") }}</label>
          <input
            id="password"
            v-model="password"
            class="field__input"
            type="password"
            autocomplete="current-password"
            :class="{ 'field__input--error': errors.password }"
          />
          <span v-if="errors.password" class="field__error">{{ errors.password }}</span>
        </div>

        <p v-if="apiError" class="login-form__api-error">{{ apiError }}</p>

        <button class="btn btn--primary" type="submit" :disabled="auth.isLoading">
          {{ auth.isLoading ? $t("common.loading") : $t("admin.login") }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useForm, useField } from "vee-validate";
import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";
import { useAuthStore } from "@/stores/auth";

const schema = toTypedSchema(
  z.object({
    username: z.string().min(1, "Username is required"),
    password: z.string().min(1, "Password is required"),
  }),
);

const { handleSubmit, errors } = useForm({ validationSchema: schema });
const { value: username } = useField<string>("username");
const { value: password } = useField<string>("password");

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const apiError = ref<string | null>(null);

const submit = handleSubmit(async (values) => {
  apiError.value = null;
  try {
    await auth.login(values.username, values.password);
    const next = typeof route.query.next === "string" ? route.query.next : "/admin";
    router.push(next);
  } catch (err: unknown) {
    if (err && typeof err === "object" && "response" in err) {
      const resp = (
        err as { response?: { status?: number; data?: { non_field_errors?: string[] } } }
      ).response;
      if (resp?.status === 429) {
        apiError.value = "Too many attempts. Please wait a minute.";
      } else {
        const msgs = resp?.data?.non_field_errors;
        apiError.value = msgs?.[0] ?? "Invalid username or password.";
      }
    } else {
      apiError.value = "Login failed. Please try again.";
    }
  }
});
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: var(--space-8);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.login-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: var(--space-6);
  color: var(--color-fg);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.login-form__api-error {
  color: var(--color-error, #dc2626);
  font-size: 0.875rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.field__label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-fg-muted);
}

.field__input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  color: var(--color-fg);
  font-size: 1rem;
}

.field__input--error {
  border-color: var(--color-error, #dc2626);
}

.field__error {
  font-size: 0.75rem;
  color: var(--color-error, #dc2626);
}

.btn {
  padding: var(--space-3) var(--space-6);
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--primary {
  background: var(--color-accent);
  color: #fff;
}
</style>
