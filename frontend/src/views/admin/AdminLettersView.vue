<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("admin.nav.letters") }}</h1>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <table v-else class="readme-table">
      <thead>
        <tr>
          <th class="readme-table__sortable" @click="setSort('name')">
            {{ $t("admin.fields.name") }}{{ sortIndicator("name") }}
          </th>
          <th>{{ $t("admin.fields.reference") }}</th>
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
            <td>{{ item.letter_reference || "—" }}</td>
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
            </td>
          </tr>
          <tr v-if="editing && editing.id === item.id" class="readme-table__editor-row">
            <td :colspan="5">
              <AdminDocEditor
                v-model="editorModel"
                doc-type="letter"
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
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { readmeApi } from "@/api/admin";
import { useEscClose } from "@/composables/useEscClose";
import { renderMermaidImages } from "@/utils/readme";
import { slugify } from "@/utils/slugify";
import { downloadBlob } from "@/utils/downloadBlob";
import type { Readme, ReadmeWrite } from "@/api/types";
import AdminDocEditor from "@/components/admin/AdminDocEditor.vue";

type Draft = Partial<ReadmeWrite> & { id?: number };

const items = ref<Readme[]>([]);
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
const sortDir = ref<"asc" | "desc">("desc");

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

const STARTER = `{{badges}}

Dear Hiring Team,

I am writing to express my strong interest in the position.

With a background in data engineering and full-stack development, I bring …

Kind regards,
Nicolas Mischler`;

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

const route = useRoute();

onMounted(async () => {
  await load();
  // Deep-link from the Applications section: ?edit=<id> opens that letter.
  const editId = Number(route.query.edit);
  if (!editId) return;
  const item = items.value.find((i) => i.id === editId);
  if (!item) return;
  openEdit(item);
  await nextTick();
  document
    .querySelector(".readme-table__editor-row")
    ?.scrollIntoView({ behavior: "smooth", block: "center" });
});

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

function openEdit(item: Readme): void {
  editing.value = {
    id: item.id,
    name: item.name,
    letter_reference: item.letter_reference,
    letter_content: item.letter_content,
    letter_content_de: item.letter_content_de,
  };
}

function cancel(): void {
  editing.value = null;
}

async function persist(): Promise<Draft | null> {
  saveError.value = null;
  if (!editing.value?.id) return null;
  try {
    await readmeApi.update(editing.value.id, {
      letter_reference: editing.value.letter_reference,
      letter_content: editing.value.letter_content,
      letter_content_de: editing.value.letter_content_de,
    });
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
    const saved = await persist();
    if (!saved?.id) return;
    // Mirror the backend's DE→EN fallback so the diagrams we rasterize line up
    // with the body the server actually renders.
    const body =
      target === "de"
        ? saved.letter_content_de || saved.letter_content || ""
        : (saved.letter_content ?? "");
    const svgs = await renderMermaidImages(body);
    const blob = await readmeApi.pdf(
      saved.id,
      target,
      svgs,
      `${window.location.origin}/`,
      "letter",
    );
    downloadBlob(blob, `${slugify(saved.name ?? "letter") || "letter"}-letter.pdf`);
  } catch {
    saveError.value = "Export failed.";
  } finally {
    busy.value = false;
  }
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
</style>
