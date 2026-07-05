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
      <label>
        {{ $t("admin.fields.active_funny_theme") }}
        <select v-model="form.active_funny_theme">
          <option value="none">{{ $t("admin.funnyTheme.none") }}</option>
          <option v-for="opt in FUNNY_OPTIONS" :key="opt.id" :value="opt.id">
            {{ opt.label }}
          </option>
        </select>
      </label>

      <div class="entity-form__wide photo-section">
        <span class="photo-section__title">{{ $t("admin.profilePictures") }}</span>
        <div class="photo-section__grid">
          <div class="photo-block">
            <span class="photo-block__label">{{ $t("admin.fields.photo_normal") }}</span>
            <img :src="normalPreview" alt="" class="photo-block__preview" />
            <span v-if="!form.photo" class="photo-block__hint">
              {{ $t("admin.photoDefaultHint") }}
            </span>
            <FileUpload accept="image/*" @uploaded="onPhotoUploaded('photo', $event)" />
            <button
              v-if="form.photo"
              type="button"
              class="btn photo-block__reset"
              @click="resetPhoto('photo')"
            >
              {{ $t("admin.fields.removePhoto") }}
            </button>
          </div>
          <div class="photo-block">
            <span class="photo-block__label">{{ $t("admin.fields.photo_funny") }}</span>
            <img :src="funnyPreview" alt="" class="photo-block__preview" />
            <span v-if="!form.photo_funny" class="photo-block__hint">
              {{ $t("admin.photoDefaultHint") }}
            </span>
            <FileUpload accept="image/*" @uploaded="onPhotoUploaded('photo_funny', $event)" />
            <button
              v-if="form.photo_funny"
              type="button"
              class="btn photo-block__reset"
              @click="resetPhoto('photo_funny')"
            >
              {{ $t("admin.fields.removePhoto") }}
            </button>
          </div>
        </div>
      </div>

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
import { computed, onMounted, ref } from "vue";
import { personApi } from "@/api/admin";
import type { Cv, MediaAsset, PersonWrite } from "@/api/types";
import { FUNNY_OPTIONS, packFor } from "@/themes/registry";
import MarkdownField from "@/components/base/MarkdownField.vue";
import FileUpload from "@/components/admin/FileUpload.vue";

const form = ref<Partial<PersonWrite> | null>(null);
const photoUrls = ref<{ photo: string | null; photo_funny: string | null }>({
  photo: null,
  photo_funny: null,
});
const normalPreview = computed(() => photoUrls.value.photo ?? "/profile-normal.jpg");
const funnyPreview = computed(
  () =>
    photoUrls.value.photo_funny ??
    packFor(form.value?.active_funny_theme)?.profilePhoto ??
    "/profile-dog.png",
);
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
      photo: cv.photo?.id ?? null,
      photo_funny: cv.photo_funny?.id ?? null,
      active_funny_theme: cv.active_funny_theme,
    };
    photoUrls.value = {
      photo: cv.photo?.url ?? null,
      photo_funny: cv.photo_funny?.url ?? null,
    };
  } catch {
    error.value = "Failed to load.";
  } finally {
    loading.value = false;
  }
}

function onPhotoUploaded(field: "photo" | "photo_funny", asset: MediaAsset): void {
  if (!form.value) return;
  form.value[field] = asset.id;
  photoUrls.value[field] = asset.url;
}

function resetPhoto(field: "photo" | "photo_funny"): void {
  if (!form.value) return;
  form.value[field] = null;
  photoUrls.value[field] = null;
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
.photo-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.photo-section__title {
  font-weight: 600;
}
.photo-section__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}
.photo-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-2);
}
.photo-block__label {
  font-size: 0.875rem;
  color: var(--color-fg-muted);
}
.photo-block__preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
.photo-block__hint {
  font-size: 0.75rem;
  color: var(--color-fg-muted);
}
.photo-block__reset {
  font-size: 0.8125rem;
}
</style>
