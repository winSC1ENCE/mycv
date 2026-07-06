<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import MarkdownField from "@/components/base/MarkdownField.vue";
import ReadmePreview from "@/components/base/ReadmePreview.vue";
import type { AccessKey, ReadmeWrite } from "@/api/types";
import type { ReadmeContext } from "@/utils/readme";

type Draft = Partial<ReadmeWrite> & { id?: number };

const draft = defineModel<Draft>({ required: true });
const props = withDefaults(
  defineProps<{
    docType: "readme" | "letter";
    starter: string;
    keys?: AccessKey[];
    busy?: boolean;
    saveError?: string | null;
  }>(),
  { keys: () => [], busy: false, saveError: null },
);
const emit = defineEmits<{ save: []; cancel: []; export: [lang: "en" | "de"] }>();

const { t } = useI18n();
const lang = ref<"en" | "de">("en");
const isLetter = computed(() => props.docType === "letter");

const bodyModel = computed<string>({
  get: () => {
    if (isLetter.value) {
      return lang.value === "de"
        ? (draft.value.letter_content_de ?? "")
        : (draft.value.letter_content ?? "");
    }
    return lang.value === "de" ? (draft.value.content_de ?? "") : (draft.value.content ?? "");
  },
  set: (value) => {
    if (isLetter.value) {
      if (lang.value === "de") draft.value.letter_content_de = value;
      else draft.value.letter_content = value;
    } else {
      if (lang.value === "de") draft.value.content_de = value;
      else draft.value.content = value;
    }
  },
});

const badgeKey = computed(() => (isLetter.value ? "reference" : "version"));
const badgeValue = computed(() =>
  isLetter.value ? (draft.value.letter_reference ?? "") : (draft.value.version ?? ""),
);

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
  const key = props.keys.find((k) => k.id === draft.value.access_key);
  return {
    accessUrl: key ? `${window.location.origin}/?key=${key.token}` : "",
    expiresAt: key ? formatDateTime(key.expires_at) : "",
    version: draft.value.version ?? "",
    updated: formatDate(new Date().toISOString()),
  };
});

function applyTemplate(): void {
  bodyModel.value = props.starter;
}
</script>

<template>
  <div class="doc-editor">
    <div class="doc-editor__pane">
      <div class="doc-editor__toolbar">
        <h2 class="form-panel__title">{{ draft.id ? t("admin.edit") : t("admin.add") }}</h2>
        <button class="btn btn--ghost btn--sm" type="button" @click="applyTemplate">
          {{ t("admin.readme.newFromTemplate") }}
        </button>
      </div>

      <form class="entity-form" @submit.prevent="emit('save')">
        <label>
          {{ t("admin.fields.name") }}
          <input v-model="draft.name" :readonly="isLetter" required />
        </label>

        <template v-if="!isLetter">
          <label>
            {{ t("admin.readme.version") }}
            <input v-model="draft.version" placeholder="v1.0.0" />
          </label>
          <label>
            {{ t("admin.readme.accessKey") }}
            <select v-model="draft.access_key">
              <option :value="null">{{ t("admin.readme.noKey") }}</option>
              <option v-for="k in keys" :key="k.id" :value="k.id">
                {{ k.label || k.token.slice(0, 8) }} — {{ formatDateTime(k.expires_at) }}
              </option>
            </select>
          </label>
        </template>
        <template v-else>
          <label>
            {{ t("admin.fields.reference") }}
            <input v-model="draft.letter_reference" placeholder="JOB-2026-042" />
          </label>
        </template>

        <div class="doc-editor__lang">
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
          {{ lang === "de" ? t("admin.fields.content_de") : t("admin.fields.content") }}
          <MarkdownField v-model="bodyModel" :rows="20" hide-preview />
        </label>

        <p v-if="saveError" class="form-error">{{ saveError }}</p>

        <div class="form-panel__footer doc-editor__footer">
          <div class="doc-editor__group">
            <button class="btn btn--primary" type="submit" :disabled="busy">
              {{ t("admin.save") }}
            </button>
            <button class="btn" type="button" @click="emit('cancel')">
              {{ t("admin.cancel") }}
            </button>
          </div>
          <div class="doc-editor__group">
            <button
              class="btn"
              type="button"
              :disabled="busy || !draft.id"
              :title="!draft.id ? t('admin.readme.saveFirst') : ''"
              @click="emit('export', 'de')"
            >
              {{ t("admin.readme.exportDe") }}
            </button>
            <button
              class="btn"
              type="button"
              :disabled="busy || !draft.id"
              :title="!draft.id ? t('admin.readme.saveFirst') : ''"
              @click="emit('export', 'en')"
            >
              {{ t("admin.readme.exportEn") }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <div class="doc-editor__pane">
      <ReadmePreview
        :markdown="bodyModel"
        :ctx="previewCtx"
        :badge-key="badgeKey"
        :badge-value="badgeValue"
        :preserve-blanks="isLetter"
      />
    </div>
  </div>
</template>

<style scoped src="@/views/admin/admin-shared.css"></style>
<style scoped>
.doc-editor {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
}

.doc-editor__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.doc-editor__lang {
  display: flex;
  gap: var(--space-1);
}

.doc-editor__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.doc-editor__group {
  display: flex;
  gap: var(--space-2);
}

@media (max-width: 900px) {
  .doc-editor {
    grid-template-columns: 1fr;
  }
}
</style>
