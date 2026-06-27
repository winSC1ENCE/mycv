<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("admin.nav.readmes") }}</h1>
      <button class="btn btn--primary" @click="openNew">+ {{ $t("admin.add") }}</button>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <template v-else>
      <!-- New application editor (no row to attach to yet) -->
      <AdminDocEditor
        v-if="editing && !editing.id"
        v-model="editorModel"
        doc-type="readme"
        :keys="keys"
        :busy="busy"
        :save-error="saveError"
        :starter="STARTER"
        class="doc-editor--new"
        @save="save"
        @cancel="cancel"
        @export="exportPdf"
      />

      <table class="readme-table">
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
          <template v-for="item in sortedItems" :key="item.id">
            <tr>
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
                <RouterLink
                  class="btn-icon"
                  :to="{ name: 'admin-letters', query: { edit: item.id } }"
                  :title="$t('admin.readme.goToLetter')"
                >
                  ✉
                </RouterLink>
                <button class="btn-icon btn-icon--danger" @click="remove(item.id)">✕</button>
              </td>
            </tr>
            <tr v-if="editing && editing.id === item.id" class="readme-table__editor-row">
              <td :colspan="5">
                <AdminDocEditor
                  v-model="editorModel"
                  doc-type="readme"
                  :keys="keys"
                  :busy="busy"
                  :save-error="saveError"
                  :starter="STARTER"
                  @save="save"
                  @cancel="cancel"
                  @export="exportPdf"
                />
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { readmeApi, accessKeyApi } from "@/api/admin";
import { useEscClose } from "@/composables/useEscClose";
import { renderMermaidImages } from "@/utils/readme";
import { slugify } from "@/utils/slugify";
import type { AccessKey, Readme, ReadmeWrite } from "@/api/types";
import AdminDocEditor from "@/components/admin/AdminDocEditor.vue";

type Draft = Partial<ReadmeWrite> & { id?: number };

const items = ref<Readme[]>([]);
const keys = ref<AccessKey[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const editing = ref<Draft | null>(null);
const saveError = ref<string | null>(null);
const busy = ref(false);

const editorModel = computed<Draft>({
  get: () => editing.value ?? ({} as Draft),
  set: (value) => {
    editing.value = value;
  },
});

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

const STARTER = `# Application

{{badges}}

## Quick Start

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

function pad(n: number): string {
  return String(n).padStart(2, "0");
}
function formatDate(iso: string): string {
  const d = new Date(iso);
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()}`;
}

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
    // access keys are optional — an application can be authored without linking one
  }
}

function openNew(): void {
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

function cancel(): void {
  editing.value = null;
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
  // Save persists only — the editor stays open; close with Cancel or Esc.
  busy.value = true;
  try {
    await persist();
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
    // Mirror the backend's DE→EN fallback so the diagrams we rasterize line up
    // with the body the server actually renders.
    const body = target === "de" ? saved.content_de || saved.content || "" : (saved.content ?? "");
    const svgs = await renderMermaidImages(body);
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
  if (!confirm("Delete this application?")) return;
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

.readme-table__editor-row > td {
  background: var(--color-surface);
  padding: var(--space-4);
}

.doc-editor--new {
  margin-bottom: var(--space-5);
}
</style>
