<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("nav.projects") }}</h1>
      <button class="btn btn--primary" @click="openNew">+ {{ $t("admin.add") }}</button>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <div v-else>
      <div v-for="item in items" :key="item.id" class="entity-row">
        <div class="entity-row__info">
          <strong>{{ item.name }}</strong>
          <span class="entity-row__sub">{{ item.slug }}</span>
        </div>
        <span class="entity-row__badge" :class="{ 'entity-row__badge--off': !item.is_published }">
          {{ item.is_published ? "live" : "hidden" }}
        </span>
        <div class="entity-row__actions">
          <button class="btn-icon" @click="openEdit(item)">✏</button>
          <button class="btn-icon btn-icon--danger" @click="remove(item.id)">✕</button>
        </div>
      </div>
    </div>

    <div v-if="editing !== null" class="form-panel">
      <div class="form-panel__inner">
        <h2 class="form-panel__title">{{ editing.id ? $t("admin.edit") : $t("admin.add") }}</h2>
        <form class="entity-form" @submit.prevent="save">
          <label>{{ $t("admin.fields.name") }}<input v-model="editing.name" required /></label>
          <label>{{ $t("admin.fields.name_de") }}<input v-model="editing.name_de" /></label>
          <label>{{ $t("admin.fields.summary") }}<input v-model="editing.summary" /></label>
          <label>{{ $t("admin.fields.summary_de") }}<input v-model="editing.summary_de" /></label>
          <label
            >{{ $t("admin.fields.description")
            }}<textarea v-model="editing.description" rows="3"></textarea>
          </label>
          <label
            >{{ $t("admin.fields.description_de")
            }}<textarea v-model="editing.description_de" rows="3"></textarea>
          </label>
          <label>{{ $t("admin.fields.url") }}<input v-model="editing.url" type="url" /></label>
          <label
            >{{ $t("admin.fields.repo_url") }}<input v-model="editing.repo_url" type="url"
          /></label>
          <label class="label--checkbox">
            <input v-model="editing.is_published" type="checkbox" />
            {{ $t("admin.fields.published") }}
          </label>

          <fieldset class="photos-panel">
            <legend>{{ photos.length }}/6 {{ $t("admin.fields.photos") }}</legend>
            <small class="form-help">{{ $t("admin.fields.photosHelp") }}</small>
            <ul v-if="photos.length" class="photo-list">
              <li v-for="(p, i) in photos" :key="p.id" class="photo-list__item">
                <img :src="p.url" :alt="p.alt_text" class="photo-list__thumb" />
                <div class="photo-list__actions">
                  <button
                    type="button"
                    class="btn-icon"
                    :disabled="i === 0"
                    :aria-label="$t('admin.fields.movePhotoUp')"
                    @click="movePhoto(i, -1)"
                  >
                    ▲
                  </button>
                  <button
                    type="button"
                    class="btn-icon"
                    :disabled="i === photos.length - 1"
                    :aria-label="$t('admin.fields.movePhotoDown')"
                    @click="movePhoto(i, 1)"
                  >
                    ▼
                  </button>
                  <button
                    type="button"
                    class="btn-icon btn-icon--danger"
                    :aria-label="$t('admin.fields.removePhoto')"
                    @click="removePhoto(i)"
                  >
                    ✕
                  </button>
                </div>
              </li>
            </ul>
            <FileUpload v-if="photos.length < 6" accept="image/*" @uploaded="onPhotoUploaded" />
          </fieldset>

          <p v-if="saveError" class="form-error">{{ saveError }}</p>
          <div class="form-panel__footer">
            <button class="btn btn--primary" type="submit">{{ $t("admin.save") }}</button>
            <button class="btn" type="button" @click="editing = null">
              {{ $t("admin.cancel") }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { projectApi } from "@/api/admin";
import { extractApiError } from "@/api/errors";
import { slugify } from "@/utils/slugify";
import FileUpload from "@/components/admin/FileUpload.vue";
import type { MediaAsset, Project, ProjectWrite } from "@/api/types";

type Draft = Partial<ProjectWrite> & { id?: number };

const items = ref<Project[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const editing = ref<Draft | null>(null);
const saveError = ref<string | null>(null);
const photos = ref<MediaAsset[]>([]);

onMounted(load);

async function load(): Promise<void> {
  loading.value = true;
  try {
    const page = await projectApi.list();
    items.value = page.results;
  } catch {
    error.value = "Failed to load.";
  } finally {
    loading.value = false;
  }
}

function openNew(): void {
  editing.value = { name: "", slug: "", is_published: true };
  photos.value = [];
}

function openEdit(item: Project): void {
  const { media, technologies, ...rest } = item;
  editing.value = {
    ...rest,
    technologies: technologies.map((t) => t.id),
    media: media.map((m) => m.id),
  };
  photos.value = [...media];
}

function onPhotoUploaded(asset: MediaAsset): void {
  if (photos.value.length < 6) photos.value.push(asset);
}

function movePhoto(i: number, dir: -1 | 1): void {
  const j = i + dir;
  if (j < 0 || j >= photos.value.length) return;
  const arr = photos.value;
  [arr[i], arr[j]] = [arr[j], arr[i]];
}

function removePhoto(i: number): void {
  photos.value.splice(i, 1);
}

async function save(): Promise<void> {
  saveError.value = null;
  if (!editing.value) return;
  const { id, ...payload } = editing.value;
  payload.media = photos.value.map((p) => p.id);
  if (!id && payload.name && !payload.slug) {
    payload.slug = slugify(payload.name);
  }
  try {
    if (id) {
      await projectApi.update(id, payload);
    } else {
      await projectApi.create(payload);
    }
    editing.value = null;
    await load();
  } catch (err) {
    saveError.value = extractApiError(err);
  }
}

async function remove(id: number): Promise<void> {
  if (!confirm("Delete this project?")) return;
  await projectApi.destroy(id);
  await load();
}
</script>

<style scoped src="./admin-shared.css"></style>
<style scoped>
.photos-panel {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.photos-panel legend {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0 var(--space-2);
}

.form-help {
  display: block;
  color: var(--color-fg-muted);
  font-size: 0.8rem;
}

.photo-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.photo-list__item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
}

.photo-list__thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.photo-list__actions {
  display: flex;
  gap: var(--space-1);
  margin-left: auto;
}

.btn-icon:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
