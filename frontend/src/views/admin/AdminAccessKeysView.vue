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
        <input v-model="newExpiry" type="datetime-local" :min="minExpiry" required />
      </label>
      <div class="form-panel__footer">
        <button class="btn btn--primary" type="submit" :disabled="creating">
          {{ creating ? $t("common.loading") : $t("admin.add") }}
        </button>
      </div>
      <p v-if="formError" class="form-error">{{ formError }}</p>
    </form>

    <!-- Created URL -->
    <div v-if="createdUrl" class="access-key-url">
      <p><strong>{{ $t("admin.accessKeys.urlReady") }}</strong></p>
      <code class="access-key-url__code">{{ createdUrl }}</code>
      <button class="btn btn--ghost" @click="copyUrl">{{ $t("admin.accessKeys.copyUrl") }}</button>
      <span v-if="copied" class="access-key-url__copied">
        {{ $t("admin.accessKeys.copied") }}
      </span>
    </div>

    <!-- List -->
    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <table v-else class="access-key-table">
      <thead>
        <tr>
          <th>{{ $t("admin.fields.label") }}</th>
          <th>{{ $t("admin.fields.expires_at") }}</th>
          <th>{{ $t("admin.fields.status") }}</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="key in keys"
          :key="key.id"
          :class="{ 'access-key-table__row--inactive': keyStatus(key) !== 'active' }"
        >
          <td>{{ key.label || "—" }}</td>
          <td>{{ formatExpiry(key.expires_at) }}</td>
          <td>
            <span class="access-key-status" :class="`access-key-status--${keyStatus(key)}`">
              {{ $t(`admin.accessKeys.status.${keyStatus(key)}`) }}
            </span>
          </td>
          <td>
            <button
              v-if="keyStatus(key) !== 'revoked'"
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
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { accessKeyApi } from "@/api/admin";
import { personApi } from "@/api/admin";
import type { AccessKey } from "@/api/types";

const { t } = useI18n();

const keys = ref<AccessKey[]>([]);
const loading = ref(false);
const creating = ref(false);
const newLabel = ref("");
const newExpiry = ref("");
const createdUrl = ref("");
const copied = ref(false);
const formError = ref<string | null>(null);
let personId = 0;

function toLocalDatetimeInput(d: Date): string {
  const pad = (n: number): string => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

const minExpiry = computed(() => toLocalDatetimeInput(new Date(Date.now() + 60_000)));

function keyStatus(key: AccessKey): "active" | "expired" | "revoked" {
  if (!key.is_active) return "revoked";
  if (new Date(key.expires_at).getTime() <= Date.now()) return "expired";
  return "active";
}

function formatExpiry(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

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
  formError.value = null;
  const expiryDate = new Date(newExpiry.value);
  if (Number.isNaN(expiryDate.getTime()) || expiryDate.getTime() <= Date.now()) {
    formError.value = t("admin.accessKeys.errors.pastExpiry");
    return;
  }
  creating.value = true;
  createdUrl.value = "";
  try {
    const key = await accessKeyApi.create({
      person: personId,
      label: newLabel.value,
      expires_at: expiryDate.toISOString(),
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

async function copyUrl(): Promise<void> {
  try {
    await navigator.clipboard.writeText(createdUrl.value);
    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  } catch {
    // clipboard unavailable — leave the URL <code> selectable so the user can copy manually
  }
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

.access-key-url__copied {
  font-size: 0.85rem;
  color: var(--color-success, #16a34a);
  font-weight: 600;
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
  opacity: 0.55;
}

.access-key-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.access-key-status--active {
  background: rgba(22, 163, 74, 0.15);
  color: #16a34a;
}

.access-key-status--expired {
  background: rgba(234, 88, 12, 0.15);
  color: #ea580c;
}

.access-key-status--revoked {
  background: rgba(220, 38, 38, 0.15);
  color: #dc2626;
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
