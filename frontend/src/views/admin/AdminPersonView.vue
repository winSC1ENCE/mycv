<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("admin.nav.person") }}</h1>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <form v-else-if="form" class="entity-form entity-form--inline" @submit.prevent="save">
      <label>{{ $t("admin.fields.first_name") }}<input v-model="form.first_name" required /></label>
      <label>{{ $t("admin.fields.last_name") }}<input v-model="form.last_name" required /></label>
      <label>{{ $t("admin.fields.slug") }}<input v-model="form.slug" required /></label>
      <label>{{ $t("admin.fields.title") }}<input v-model="form.title" required /></label>
      <label>{{ $t("admin.fields.title_de") }}<input v-model="form.title_de" /></label>
      <label>{{ $t("admin.fields.email") }}<input v-model="form.email" type="email" /></label>
      <label>{{ $t("admin.fields.phone") }}<input v-model="form.phone" type="tel" /></label>
      <label>{{ $t("admin.fields.location") }}<input v-model="form.location" /></label>
      <label>{{ $t("admin.fields.zivilstand") }}<input v-model="form.zivilstand" /></label>
      <label>{{ $t("admin.fields.zivilstand_de") }}<input v-model="form.zivilstand_de" /></label>
      <label>{{ $t("admin.fields.address") }}<input v-model="form.address" /></label>
      <label
        >{{ $t("admin.fields.date_of_birth") }}<input v-model="form.date_of_birth" type="date"
      /></label>
      <label class="entity-form__wide">
        {{ $t("admin.fields.summary") }}
        <MarkdownField v-model="form.summary" :rows="4" />
      </label>
      <label class="entity-form__wide">
        {{ $t("admin.fields.summary_de") }}
        <MarkdownField v-model="form.summary_de" :rows="4" />
      </label>

      <p v-if="saveError" class="form-error">{{ saveError }}</p>
      <p v-if="saved" class="form-success">{{ $t("admin.saved") }}</p>

      <div class="form-panel__footer">
        <button class="btn btn--primary" type="submit" :disabled="saving">
          {{ saving ? $t("common.loading") : $t("admin.save") }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { personApi } from "@/api/admin";
import type { Cv, PersonWrite } from "@/api/types";
import MarkdownField from "@/components/base/MarkdownField.vue";

const form = ref<Partial<PersonWrite> | null>(null);
const originalSlug = ref<string>("");
const loading = ref(false);
const error = ref<string | null>(null);
const saving = ref(false);
const saveError = ref<string | null>(null);
const saved = ref(false);

onMounted(load);

async function load(): Promise<void> {
  loading.value = true;
  try {
    const cv: Cv = await personApi.retrieve();
    originalSlug.value = cv.slug;
    form.value = {
      slug: cv.slug,
      first_name: cv.first_name,
      last_name: cv.last_name,
      title: cv.title,
      title_de: cv.title_de,
      email: cv.email,
      phone: cv.phone,
      location: cv.location,
      address: cv.address,
      zivilstand: cv.zivilstand,
      zivilstand_de: cv.zivilstand_de,
      date_of_birth: cv.date_of_birth ?? undefined,
      summary: cv.summary,
      summary_de: cv.summary_de,
    };
  } catch {
    error.value = "Failed to load.";
  } finally {
    loading.value = false;
  }
}

async function save(): Promise<void> {
  if (!form.value) return;
  saveError.value = null;
  saved.value = false;
  saving.value = true;
  try {
    await personApi.update(originalSlug.value, form.value);
    saved.value = true;
    if (form.value.slug) originalSlug.value = form.value.slug;
    setTimeout(() => (saved.value = false), 2000);
  } catch {
    saveError.value = "Save failed.";
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped src="./admin-shared.css"></style>
<style scoped>
.entity-form--inline {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3) var(--space-4);
  max-width: 900px;
}
.entity-form__wide {
  grid-column: 1 / -1;
}
.form-success {
  color: var(--color-success, #16a34a);
  font-size: 0.875rem;
}
</style>
