<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("nav.skills") }}</h1>
      <button class="btn btn--primary" @click="openNew">+ {{ $t("admin.add") }}</button>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <div v-else>
      <div v-for="cat in items" :key="cat.id" class="skill-category">
        <div class="entity-row">
          <div class="entity-row__info">
            <strong>{{ cat.name }}</strong>
            <span class="entity-row__sub">{{ cat.skills.length }} skills</span>
          </div>
          <div class="entity-row__actions">
            <button class="btn-icon" @click="openEdit(cat)">✏</button>
            <button class="btn-icon btn-icon--danger" @click="remove(cat.id)">✕</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="editing !== null" class="form-panel">
      <div class="form-panel__inner">
        <h2 class="form-panel__title">{{ editing.id ? $t("admin.edit") : $t("admin.add") }}</h2>
        <form class="entity-form" @submit.prevent="save">
          <label>{{ $t("admin.fields.name") }}<input v-model="editing.name" required /></label>
          <label>{{ $t("admin.fields.name_de") }}<input v-model="editing.name_de" /></label>
          <label>{{ $t("admin.fields.slug") }}<input v-model="editing.slug" required /></label>
          <label class="label--checkbox">
            <input v-model="editing.is_published" type="checkbox" />
            {{ $t("admin.fields.published") }}
          </label>
          <p v-if="saveError" class="form-error">{{ saveError }}</p>
          <div class="form-panel__footer">
            <button class="btn btn--primary" type="submit">{{ $t("admin.save") }}</button>
            <button class="btn" type="button" @click="editing = null">{{ $t("admin.cancel") }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { skillCategoryApi } from "@/api/admin";
import type { SkillCategory, SkillCategoryWrite } from "@/api/types";

type Draft = Partial<SkillCategoryWrite> & { id?: number };

const items = ref<SkillCategory[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const editing = ref<Draft | null>(null);
const saveError = ref<string | null>(null);

onMounted(load);

async function load(): Promise<void> {
  loading.value = true;
  try {
    const page = await skillCategoryApi.list();
    items.value = page.results;
  } catch {
    error.value = "Failed to load.";
  } finally {
    loading.value = false;
  }
}

function openNew(): void {
  editing.value = { name: "", name_de: "", slug: "", is_published: true };
}

function openEdit(item: SkillCategory): void {
  // Exclude the nested skills array — write payload uses only flat fields
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { skills, ...rest } = item;
  editing.value = { ...rest };
}

async function save(): Promise<void> {
  saveError.value = null;
  if (!editing.value) return;
  try {
    const { id, ...payload } = editing.value;
    if (id) {
      await skillCategoryApi.update(id, payload);
    } else {
      await skillCategoryApi.create(payload);
    }
    editing.value = null;
    await load();
  } catch {
    saveError.value = "Save failed.";
  }
}

async function remove(id: number): Promise<void> {
  if (!confirm("Delete this category?")) return;
  await skillCategoryApi.destroy(id);
  await load();
}
</script>

<style scoped src="./admin-shared.css"></style>
