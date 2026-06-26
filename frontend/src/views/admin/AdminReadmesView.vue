<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("admin.nav.readmes") }}</h1>
      <button class="btn btn--primary" @click="openNew">+ {{ $t("admin.add") }}</button>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <table v-else class="readme-table">
      <thead>
        <tr>
          <th class="readme-table__sortable" @click="setSort('name')">
            {{ $t("admin.fields.name") }}{{ sortIndicator("name") }}
          </th>
          <th>{{ $t("admin.readme.version") }}</th>
          <th class="readme-table__sortable" @click="setSort('created_at')">
            {{ $t("admin.fields.created") }}{{ sortIndicator("created_at") }}
          </th>
          <th>{{ $t("admin.fields.status") }}</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in sortedItems" :key="item.id">
          <td>
            <strong>{{ item.name }}</strong>
          </td>
          <td>{{ item.version }}</td>
          <td>{{ formatDate(item.created_at) }}</td>
          <td>
            <span
              class="entity-row__badge"
              :class="{ 'entity-row__badge--off': !item.is_published }"
            >
              {{ item.is_published ? "live" : "hidden" }}
            </span>
          </td>
          <td class="readme-table__actions">
            <button class="btn-icon" @click="openEdit(item)">✏</button>
            <button class="btn-icon btn-icon--danger" @click="remove(item.id)">✕</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Editor -->
    <div v-if="editing !== null" class="readme-editor">
      <div class="readme-editor__pane">
        <div class="readme-editor__toolbar">
          <h2 class="form-panel__title">{{ editing.id ? $t("admin.edit") : $t("admin.add") }}</h2>
          <button class="btn btn--ghost btn--sm" type="button" @click="applyTemplate">
            {{ $t("admin.readme.newFromTemplate") }}
          </button>
        </div>

        <form class="entity-form" @submit.prevent="save">
          <label>{{ $t("admin.fields.name") }}<input v-model="editing.name" required /></label>
          <label
            >{{ $t("admin.readme.version") }}<input v-model="editing.version" placeholder="v1.0.0"
          /></label>
          <label>
            {{ $t("admin.readme.accessKey") }}
            <select v-model="editing.access_key">
              <option :value="null">{{ $t("admin.readme.noKey") }}</option>
              <option v-for="k in keys" :key="k.id" :value="k.id">
                {{ k.label || k.token.slice(0, 8) }} — {{ formatDateTime(k.expires_at) }}
              </option>
            </select>
          </label>

          <div class="readme-editor__lang">
            <button
              type="button"
              class="btn btn--sm"
              :class="{ 'btn--primary': lang === 'en' }"
              @click="lang = 'en'"
            >
              EN
            </button>
            <button
              type="button"
              class="btn btn--sm"
              :class="{ 'btn--primary': lang === 'de' }"
              @click="lang = 'de'"
            >
              DE
            </button>
          </div>

          <label>
            {{ lang === "de" ? $t("admin.fields.content_de") : $t("admin.fields.content") }}
            <MarkdownField v-model="bodyModel" :rows="20" hide-preview />
          </label>

          <label class="label--checkbox">
            <input v-model="editing.is_published" type="checkbox" />
            {{ $t("admin.fields.published") }}
          </label>

          <p v-if="saveError" class="form-error">{{ saveError }}</p>
          <div class="form-panel__footer">
            <button class="btn btn--primary" type="submit" :disabled="busy">
              {{ $t("admin.save") }}
            </button>
            <button class="btn" type="button" @click="editing = null">
              {{ $t("admin.cancel") }}
            </button>
            <button
              class="btn"
              type="button"
              :disabled="busy || !editing.id"
              :title="!editing.id ? $t('admin.readme.saveFirst') : ''"
              @click="exportPdf('en')"
            >
              {{ $t("admin.readme.exportEn") }}
            </button>
            <button
              class="btn"
              type="button"
              :disabled="busy || !editing.id"
              :title="!editing.id ? $t('admin.readme.saveFirst') : ''"
              @click="exportPdf('de')"
            >
              {{ $t("admin.readme.exportDe") }}
            </button>
          </div>
        </form>
      </div>

      <div class="readme-editor__pane">
        <ReadmePreview :name="editing.name || ''" :markdown="bodyModel" :ctx="previewCtx" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { readmeApi, accessKeyApi } from "@/api/admin";
import { useEscClose } from "@/composables/useEscClose";
import { renderMermaidSvgs, type ReadmeContext } from "@/utils/readme";
import { slugify } from "@/utils/slugify";
import type { AccessKey, Readme, ReadmeWrite } from "@/api/types";
import MarkdownField from "@/components/base/MarkdownField.vue";
import ReadmePreview from "@/components/base/ReadmePreview.vue";

type Draft = Partial<ReadmeWrite> & { id?: number };

const items = ref<Readme[]>([]);
const keys = ref<AccessKey[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const editing = ref<Draft | null>(null);
const saveError = ref<string | null>(null);
const lang = ref<"en" | "de">("en");
const busy = ref(false);

type SortField = "name" | "created_at";
const sortField = ref<SortField>("created_at");
const sortDir = ref<"asc" | "desc">("desc"); // newest first by default

function setSort(field: SortField): void {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
  } else {
    sortField.value = field;
    sortDir.value = "asc";
  }
}

const sortedItems = computed(() =>
  [...items.value].sort((a, b) => {
    const cmp =
      sortField.value === "name"
        ? a.name.localeCompare(b.name)
        : new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    return sortDir.value === "asc" ? cmp : -cmp;
  }),
);

function sortIndicator(field: SortField): string {
  if (sortField.value !== field) return "";
  return sortDir.value === "asc" ? " ▲" : " ▼";
}

const STARTER = `## Quick Start

1. Open: {{access_url}}
2. Explore experience, education & projects
3. Optional for **Kira**: activate 🐶 Dog Mode

## Access

Personal data, certificates and diplomas available until: \`{{expires_at}}\`

## Application Flow

\`\`\`mermaid
flowchart TD
    A[Open CV] --> B{Interested?}
    B -- Yes --> C[Invite to Interview]
    B -- No --> E[Try again later]
\`\`\`

---

\`License: MIT (Mischler IT)\``;

const bodyModel = computed<string>({
  get: () =>
    lang.value === "de" ? (editing.value?.content_de ?? "") : (editing.value?.content ?? ""),
  set: (value) => {
    if (!editing.value) return;
    if (lang.value === "de") editing.value.content_de = value;
    else editing.value.content = value;
  },
});

function pad(n: number): string {
  return String(n).padStart(2, "0");
}
function formatDate(iso: string): string {
  const d = new Date(iso);
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()}`;
}
function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return `${formatDate(iso)} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

const previewCtx = computed<ReadmeContext>(() => {
  const key = keys.value.find((k) => k.id === editing.value?.access_key);
  return {
    accessUrl: key ? `${window.location.origin}/?key=${key.token}` : "",
    expiresAt: key ? formatDateTime(key.expires_at) : "",
    version: editing.value?.version ?? "",
    updated: formatDate(new Date().toISOString()),
  };
});

useEscClose(
  () => {
    editing.value = null;
  },
  computed(() => editing.value !== null),
);

onMounted(() => Promise.all([load(), loadKeys()]));

async function load(): Promise<void> {
  loading.value = true;
  try {
    const page = await readmeApi.list();
    items.value = page.results;
  } catch {
    error.value = "Failed to load.";
  } finally {
    loading.value = false;
  }
}

async function loadKeys(): Promise<void> {
  try {
    const page = await accessKeyApi.list();
    keys.value = page.results;
  } catch {
    // access keys are optional — README can be authored without linking one
  }
}

function openNew(): void {
  lang.value = "en";
  editing.value = {
    name: "",
    content: "",
    content_de: "",
    version: "v1.0.0",
    access_key: null,
    is_published: true,
  };
}

function openEdit(item: Readme): void {
  lang.value = "en";
  editing.value = {
    id: item.id,
    name: item.name,
    content: item.content,
    content_de: item.content_de,
    version: item.version,
    access_key: item.access_key,
    is_published: item.is_published,
  };
}

function applyTemplate(): void {
  if (!editing.value) return;
  if (lang.value === "de") editing.value.content_de = STARTER;
  else editing.value.content = STARTER;
}

async function persist(): Promise<Draft | null> {
  saveError.value = null;
  if (!editing.value) return null;
  try {
    const { id, ...payload } = editing.value;
    const saved = id ? await readmeApi.update(id, payload) : await readmeApi.create(payload);
    editing.value.id = saved.id;
    await load();
    return editing.value;
  } catch {
    saveError.value = "Save failed.";
    return null;
  }
}

async function save(): Promise<void> {
  busy.value = true;
  try {
    if (await persist()) editing.value = null;
  } finally {
    busy.value = false;
  }
}

async function exportPdf(target: "en" | "de"): Promise<void> {
  if (!editing.value) return;
  busy.value = true;
  try {
    // Save first so the server renders exactly the body we render diagrams for.
    const saved = await persist();
    if (!saved?.id) return;
    const body = target === "de" ? (saved.content_de ?? "") : (saved.content ?? "");
    const svgs = await renderMermaidSvgs(body);
    const blob = await readmeApi.pdf(saved.id, target, svgs, `${window.location.origin}/`);
    downloadBlob(blob, `${slugify(saved.name ?? "readme") || "readme"}.pdf`);
  } catch {
    saveError.value = "Export failed.";
  } finally {
    busy.value = false;
  }
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

async function remove(id: number): Promise<void> {
  if (!confirm("Delete this README?")) return;
  await readmeApi.destroy(id);
  await load();
}
</script>

<style scoped src="./admin-shared.css"></style>
<style scoped>
.readme-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.readme-table th,
.readme-table td {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.readme-table th {
  font-weight: 600;
  color: var(--color-fg-muted);
}

.readme-table__sortable {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.readme-table__sortable:hover {
  color: var(--color-fg);
}

.readme-table__actions {
  display: flex;
  gap: var(--space-1);
}

.readme-editor {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
  margin-top: var(--space-5);
}

.readme-editor__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.readme-editor__lang {
  display: flex;
  gap: var(--space-1);
}

@media (max-width: 900px) {
  .readme-editor {
    grid-template-columns: 1fr;
  }
}
</style>
