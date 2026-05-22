<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("admin.nav.socialLinks") }}</h1>
      <button class="btn btn--primary" @click="openNew">+ {{ $t("admin.add") }}</button>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <div v-else>
      <div v-for="item in items" :key="item.id" class="entity-row">
        <div class="entity-row__info">
          <strong>{{ item.label || item.platform }}</strong>
          <span class="entity-row__sub">{{ item.url }}</span>
        </div>
        <span class="entity-row__badge" :class="{ 'entity-row__badge--off': !item.is_published }">
          {{ item.is_published === false ? "hidden" : "live" }}
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
          <label>
            {{ $t("admin.fields.platform") }}
            <select v-model="editing.platform" required>
              <option value="github">GitHub</option>
              <option value="linkedin">LinkedIn</option>
              <option value="xing">Xing</option>
              <option value="email">Email</option>
              <option value="website">Website</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label>{{ $t("admin.fields.label") }}<input v-model="editing.label" /></label>
          <label>{{ $t("admin.fields.url") }}<input v-model="editing.url" type="url" required /></label>
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
import { computed, onMounted, ref } from "vue";
import { socialLinkApi } from "@/api/admin";
import { useEscClose } from "@/composables/useEscClose";
import type { SocialLink, SocialLinkWrite } from "@/api/types";

type Draft = Partial<SocialLinkWrite> & { id?: number };

const items = ref<SocialLink[]>([]);
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
    const page = await socialLinkApi.list();
    items.value = page.results;
  } catch {
    error.value = "Failed to load.";
  } finally {
    loading.value = false;
  }
}

function openNew(): void {
  editing.value = { platform: "github", label: "", url: "", is_published: true };
}

function openEdit(item: SocialLink): void {
  editing.value = { ...item, is_published: item.is_published ?? true };
}

async function save(): Promise<void> {
  saveError.value = null;
  if (!editing.value) return;
  try {
    const { id, ...payload } = editing.value;
    if (id) {
      await socialLinkApi.update(id, payload);
    } else {
      await socialLinkApi.create(payload);
    }
    editing.value = null;
    await load();
  } catch {
    saveError.value = "Save failed.";
  }
}

async function remove(id: number): Promise<void> {
  if (!confirm("Delete this social link?")) return;
  await socialLinkApi.destroy(id);
  await load();
}
</script>

<style scoped src="./admin-shared.css"></style>
