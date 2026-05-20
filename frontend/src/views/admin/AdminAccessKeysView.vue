<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("admin.nav.accessKeys") }}</h1>
    </div>

    <!-- Create form -->
    <form class="entity-form entity-form--inline" @submit.prevent="create">
      <label>
        {{ $t("admin.fields.label") }}
        <input v-model="newLabel" :placeholder="$t('admin.fields.label')" />
      </label>
      <label>
        {{ $t("admin.fields.expires_at") }}
        <input v-model="newExpiry" type="datetime-local" required />
      </label>
      <div class="form-panel__footer">
        <button class="btn btn--primary" type="submit" :disabled="creating">
          {{ creating ? $t("common.loading") : $t("admin.add") }}
        </button>
      </div>
    </form>

    <!-- Created URL -->
    <div v-if="createdUrl" class="access-key-url">
      <p><strong>{{ $t("admin.accessKeys.urlReady") }}</strong></p>
      <code class="access-key-url__code">{{ createdUrl }}</code>
      <button class="btn btn--ghost" @click="copyUrl">{{ $t("admin.accessKeys.copyUrl") }}</button>
    </div>

    <!-- List -->
    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <table v-else class="access-key-table">
      <thead>
        <tr>
          <th>{{ $t("admin.fields.label") }}</th>
          <th>{{ $t("admin.fields.expires_at") }}</th>
          <th>{{ $t("admin.fields.is_active") }}</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="key in keys" :key="key.id" :class="{ 'access-key-table__row--inactive': !key.is_active }">
          <td>{{ key.label || "—" }}</td>
          <td>{{ key.expires_at }}</td>
          <td>{{ key.is_active ? "✓" : "✗" }}</td>
          <td>
            <button
              v-if="key.is_active"
              class="btn btn--danger btn--sm"
              @click="revoke(key.id)"
            >
              {{ $t("admin.accessKeys.revoke") }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { accessKeyApi } from "@/api/admin";
import { personApi } from "@/api/admin";
import type { AccessKey } from "@/api/types";

const keys = ref<AccessKey[]>([]);
const loading = ref(false);
const creating = ref(false);
const newLabel = ref("");
const newExpiry = ref("");
const createdUrl = ref("");
let personId = 0;

onMounted(async () => {
  loading.value = true;
  try {
    const [cv, page] = await Promise.all([personApi.retrieve(), accessKeyApi.list()]);
    personId = cv.id;
    keys.value = page.results;
  } finally {
    loading.value = false;
  }
});

async function create(): Promise<void> {
  creating.value = true;
  createdUrl.value = "";
  try {
    const key = await accessKeyApi.create({
      person: personId,
      label: newLabel.value,
      expires_at: new Date(newExpiry.value).toISOString(),
      is_active: true,
    });
    keys.value.unshift(key);
    createdUrl.value = `${window.location.origin}/?key=${key.token}`;
    newLabel.value = "";
    newExpiry.value = "";
  } finally {
    creating.value = false;
  }
}

async function revoke(id: number): Promise<void> {
  await accessKeyApi.update(id, { is_active: false });
  const found = keys.value.find((k) => k.id === id);
  if (found) found.is_active = false;
}

function copyUrl(): void {
  navigator.clipboard.writeText(createdUrl.value);
}
</script>

<style scoped src="./admin-shared.css"></style>
<style scoped>
.access-key-url {
  margin: var(--space-4) 0;
  padding: var(--space-3);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
}

.access-key-url__code {
  flex: 1;
  font-size: 0.85rem;
  word-break: break-all;
}

.access-key-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.access-key-table th,
.access-key-table td {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.access-key-table th {
  font-weight: 600;
  color: var(--color-fg-muted);
}

.access-key-table__row--inactive {
  opacity: 0.45;
}

.btn--danger {
  background: #dc2626;
  color: #fff;
  border: none;
}

.btn--sm {
  padding: 2px 8px;
  font-size: 0.8rem;
}
</style>
