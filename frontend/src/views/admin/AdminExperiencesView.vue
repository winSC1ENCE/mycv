<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("nav.experience") }}</h1>
      <button class="btn btn--primary" @click="openNew">+ {{ $t("admin.add") }}</button>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <SortableList v-else :items="items" @reorder="onReorder">
      <template #item="{ item }">
        <div class="entity-row">
          <span class="drag-handle">⠿</span>
          <div class="entity-row__info">
            <strong>{{ item.role }}</strong>
            <span class="entity-row__sub">{{ item.company }}</span>
          </div>
          <span class="entity-row__badge" :class="{ 'entity-row__badge--off': !item.is_published }">
            {{ item.is_published ? "live" : "hidden" }}
          </span>
          <div class="entity-row__actions">
            <button class="btn-icon" @click="openEdit(item)">✏</button>
            <button class="btn-icon btn-icon--danger" @click="remove(item.id)">✕</button>
          </div>
        </div>
      </template>
    </SortableList>

    <!-- Form panel -->
    <div v-if="editing !== null" class="form-panel">
      <div class="form-panel__inner">
        <h2 class="form-panel__title">
          {{ editing.id ? $t("admin.edit") : $t("admin.add") }}
        </h2>

        <form class="entity-form" @submit.prevent="save">
          <label>{{ $t("admin.fields.role") }}<input v-model="editing.role" required /></label>
          <label>{{ $t("admin.fields.role_de") }}<input v-model="editing.role_de" /></label>
          <label
            >{{ $t("admin.fields.company") }}<input v-model="editing.company" required
          /></label>
          <label>{{ $t("admin.fields.location") }}<input v-model="editing.location" /></label>
          <label
            >{{ $t("admin.fields.start_date")
            }}<input v-model="editing.start_date" type="date" required
          /></label>
          <label
            >{{ $t("admin.fields.end_date") }}<input v-model="editing.end_date" type="date"
          /></label>
          <label>
            {{ $t("admin.fields.description") }}
            <textarea v-model="editing.description" rows="3"></textarea>
          </label>
          <label>
            {{ $t("admin.fields.description_de") }}
            <textarea v-model="editing.description_de" rows="3"></textarea>
          </label>
          <div class="field-group">
            <span class="field-group__label">{{ $t("admin.fields.mediaFile") }}</span>
            <FileUpload accept="image/*,application/pdf" @uploaded="onMediaUploaded" />
            <span v-if="editing.media" class="field-group__hint">
              Current: ID {{ editing.media }}
            </span>
          </div>

          <label class="label--checkbox">
            <input v-model="editing.is_published" type="checkbox" />
            {{ $t("admin.fields.published") }}
          </label>

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
import { computed, ref, onMounted } from "vue";
import { experienceApi } from "@/api/admin";
import { useEscClose } from "@/composables/useEscClose";
import type { Experience, ExperienceWrite, MediaAsset } from "@/api/types";
import FileUpload from "@/components/admin/FileUpload.vue";
import SortableList from "@/components/admin/SortableList.vue";

type Draft = Partial<ExperienceWrite> & { id?: number };

const items = ref<Experience[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const editing = ref<Draft | null>(null);
const saveError = ref<string | null>(null);

onMounted(load);

useEscClose(
  () => {
    editing.value = null;
  },
  computed(() => editing.value !== null),
);

async function load(): Promise<void> {
  loading.value = true;
  try {
    const page = await experienceApi.list();
    items.value = page.results;
  } catch {
    error.value = "Failed to load.";
  } finally {
    loading.value = false;
  }
}

function openNew(): void {
  editing.value = {
    role: "",
    role_de: "",
    company: "",
    location: "",
    start_date: "",
    end_date: null,
    description: "",
    description_de: "",
    media: null,
    is_published: true,
  };
}

function openEdit(item: Experience): void {
  const { media, technologies, ...rest } = item;
  editing.value = {
    ...rest,
    technologies: technologies.map((t) => t.id),
    media: media?.id ?? null,
  };
}

function onMediaUploaded(asset: MediaAsset): void {
  if (editing.value) editing.value.media = asset.id;
}

async function save(): Promise<void> {
  saveError.value = null;
  if (!editing.value) return;
  try {
    const { id, ...payload } = editing.value;
    if (id) {
      await experienceApi.update(id, payload);
    } else {
      await experienceApi.create(payload);
    }
    editing.value = null;
    await load();
  } catch {
    saveError.value = "Save failed.";
  }
}

async function remove(id: number): Promise<void> {
  if (!confirm("Delete this experience?")) return;
  await experienceApi.destroy(id);
  await load();
}

async function onReorder(ids: number[]): Promise<void> {
  await experienceApi.reorder(ids);
}
</script>

<style scoped src="./admin-shared.css"></style>
