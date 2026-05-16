<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("admin.nav.timeline") }}</h1>
      <button class="btn btn--primary" @click="openNew">+ {{ $t("admin.add") }}</button>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <SortableList v-else :items="items" @reorder="onReorder">
      <template #item="{ item }">
        <div class="entity-row">
          <span class="drag-handle">⠿</span>
          <div class="entity-row__info">
            <strong>{{ item.title }}</strong>
            <span class="entity-row__sub">{{ item.date }} · {{ item.kind }}</span>
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

    <div v-if="editing !== null" class="form-panel">
      <div class="form-panel__inner">
        <h2 class="form-panel__title">{{ editing.id ? $t("admin.edit") : $t("admin.add") }}</h2>
        <form class="entity-form" @submit.prevent="save">
          <label>{{ $t("admin.fields.title") }}<input v-model="editing.title" required /></label>
          <label>{{ $t("admin.fields.title_de") }}<input v-model="editing.title_de" /></label>
          <label
            >{{ $t("admin.fields.date") }}<input v-model="editing.date" type="date" required
          /></label>
          <label>
            {{ $t("admin.fields.kind") }}
            <select v-model="editing.kind">
              <option value="milestone">Milestone</option>
              <option value="award">Award</option>
              <option value="transition">Transition</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label
            >{{ $t("admin.fields.description")
            }}<textarea v-model="editing.description" rows="3"></textarea>
          </label>
          <label
            >{{ $t("admin.fields.description_de")
            }}<textarea v-model="editing.description_de" rows="3"></textarea>
          </label>
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
import { timelineApi } from "@/api/admin";
import type { TimelineEntry } from "@/api/types";
import SortableList from "@/components/admin/SortableList.vue";

type Draft = Partial<TimelineEntry> & { id?: number };

const items = ref<TimelineEntry[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const editing = ref<Draft | null>(null);
const saveError = ref<string | null>(null);

onMounted(load);

async function load(): Promise<void> {
  loading.value = true;
  try {
    const page = await timelineApi.list();
    items.value = page.results;
  } catch {
    error.value = "Failed to load.";
  } finally {
    loading.value = false;
  }
}

function openNew(): void {
  editing.value = { title: "", date: "", kind: "milestone", is_published: true };
}

function openEdit(item: TimelineEntry): void {
  editing.value = { ...item };
}

async function save(): Promise<void> {
  saveError.value = null;
  if (!editing.value) return;
  try {
    const { id, ...payload } = editing.value;
    if (id) {
      await timelineApi.update(id, payload);
    } else {
      await timelineApi.create(payload);
    }
    editing.value = null;
    await load();
  } catch {
    saveError.value = "Save failed.";
  }
}

async function remove(id: number): Promise<void> {
  if (!confirm("Delete this timeline entry?")) return;
  await timelineApi.destroy(id);
  await load();
}

async function onReorder(ids: number[]): Promise<void> {
  await timelineApi.reorder(ids);
}
</script>

<style scoped src="./admin-shared.css"></style>
