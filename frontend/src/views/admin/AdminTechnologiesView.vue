<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("admin.nav.technologies") }}</h1>
      <button class="btn btn--primary" @click="openNew">+ {{ $t("admin.add") }}</button>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <div v-else>
      <div v-for="item in items" :key="item.id" class="entity-row">
        <div class="entity-row__info">
          <strong>{{ item.name }}</strong>
          <span class="entity-row__sub">{{ item.category }}</span>
        </div>
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
          <label>{{ $t("admin.fields.slug") }}<input v-model="editing.slug" required /></label>
          <label>{{ $t("admin.fields.category") }}<input v-model="editing.category" /></label>
          <label>{{ $t("admin.fields.icon") }}<input v-model="editing.icon" /></label>
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
import { ref, onMounted } from "vue";
import { technologyApi } from "@/api/admin";
import type { Technology, TechnologyWrite } from "@/api/types";

type Draft = Partial<TechnologyWrite> & { id?: number };

const items = ref<Technology[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const editing = ref<Draft | null>(null);
const saveError = ref<string | null>(null);

onMounted(load);

async function load(): Promise<void> {
  loading.value = true;
  try {
    const page = await technologyApi.list();
    items.value = page.results;
  } catch {
    error.value = "Failed to load.";
  } finally {
    loading.value = false;
  }
}

function openNew(): void {
  editing.value = { name: "", slug: "", is_published: true };
}

function openEdit(item: Technology): void {
  editing.value = { ...item };
}

async function save(): Promise<void> {
  saveError.value = null;
  if (!editing.value) return;
  try {
    const { id, ...payload } = editing.value;
    if (id) {
      await technologyApi.update(id, payload);
    } else {
      await technologyApi.create(payload);
    }
    editing.value = null;
    await load();
  } catch {
    saveError.value = "Save failed.";
  }
}

async function remove(id: number): Promise<void> {
  if (!confirm("Delete this technology?")) return;
  await technologyApi.destroy(id);
  await load();
}
</script>

<style scoped src="./admin-shared.css"></style>
