<template>
  <div class="admin-page">
    <div class="admin-page__header">
      <h1 class="admin-page__title">{{ $t("nav.skills") }}</h1>
      <span class="pdf-count">{{ $t("admin.pdfCount", { count: pdfCount }) }}</span>
      <button class="btn" :disabled="pdfCount === 0" @click="deselectAllPdf">
        {{ $t("admin.pdfNone") }}
      </button>
      <button class="btn btn--primary" @click="openNewCategory">
        + {{ $t("admin.addCategory") }}
      </button>
    </div>

    <p v-if="loading" class="admin-page__status">{{ $t("common.loading") }}</p>
    <p v-else-if="error" class="admin-page__error">{{ error }}</p>

    <div v-else>
      <section v-for="cat in items" :key="cat.id" class="skill-category">
        <div class="entity-row">
          <div class="entity-row__info">
            <strong>{{ cat.name }}</strong>
            <span class="entity-row__sub">{{ cat.skills.length }} skills</span>
          </div>
          <div class="entity-row__actions">
            <button class="btn" @click="openNewSkill(cat.id)">+ {{ $t("admin.addSkill") }}</button>
            <button class="btn-icon" @click="openEditCategory(cat)">✏</button>
            <button class="btn-icon btn-icon--danger" @click="removeCategory(cat.id)">✕</button>
          </div>
        </div>
        <ul class="skill-list">
          <li v-for="skill in cat.skills" :key="skill.id" class="skill-row">
            <label class="label--checkbox skill-row__pdf">
              <input type="checkbox" :checked="skill.show_in_pdf" @change="togglePdf(skill)" />
              PDF
            </label>
            <span class="skill-row__name">{{ skill.name }}</span>
            <span class="skill-row__level">{{ levelLabel(skill.level) }}</span>
            <span class="skill-row__tech">
              {{ skill.technologies.map((t) => t.name).join(", ") }}
            </span>
            <div class="entity-row__actions">
              <button class="btn-icon" @click="openEditSkill(skill, cat.id)">✏</button>
              <button class="btn-icon btn-icon--danger" @click="removeSkill(skill.id)">✕</button>
            </div>
          </li>
        </ul>
      </section>
    </div>

    <!-- Category form panel -->
    <div v-if="editingCategory !== null" class="form-panel">
      <div class="form-panel__inner">
        <h2 class="form-panel__title">
          {{ editingCategory.id ? $t("admin.edit") : $t("admin.add") }}
        </h2>
        <form class="entity-form" @submit.prevent="saveCategory">
          <label
            >{{ $t("admin.fields.name") }}<input v-model="editingCategory.name" required
          /></label>
          <label>{{ $t("admin.fields.name_de") }}<input v-model="editingCategory.name_de" /></label>
          <label
            >{{ $t("admin.fields.slug") }}<input v-model="editingCategory.slug" required
          /></label>
          <label class="label--checkbox">
            <input v-model="editingCategory.is_published" type="checkbox" />
            {{ $t("admin.fields.published") }}
          </label>
          <p v-if="saveError" class="form-error">{{ saveError }}</p>
          <div class="form-panel__footer">
            <button class="btn btn--primary" type="submit">{{ $t("admin.save") }}</button>
            <button class="btn" type="button" @click="editingCategory = null">
              {{ $t("admin.cancel") }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Skill form panel -->
    <div v-if="editingSkill !== null" class="form-panel">
      <div class="form-panel__inner">
        <h2 class="form-panel__title">
          {{ editingSkill.id ? $t("admin.edit") : $t("admin.add") }}
        </h2>
        <form class="entity-form" @submit.prevent="saveSkill">
          <label>{{ $t("admin.fields.name") }}<input v-model="editingSkill.name" required /></label>
          <label>{{ $t("admin.fields.name_de") }}<input v-model="editingSkill.name_de" /></label>
          <label>
            {{ $t("admin.fields.category") }}
            <select v-model.number="editingSkill.category" required>
              <option v-for="cat in items" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </label>
          <label>
            {{ $t("admin.fields.level") }}
            <input v-model.number="editingSkill.level" type="number" min="1" max="5" required />
          </label>
          <label>
            {{ $t("admin.nav.technologies") }}
            <select v-model="editingSkill.technologies" multiple size="10">
              <optgroup v-for="[cat, techs] in groupedTechnologies" :key="cat" :label="cat">
                <option v-for="tech in techs" :key="tech.id" :value="tech.id">
                  {{ tech.name }}
                </option>
              </optgroup>
            </select>
            <span class="field-hint">{{ $t("admin.multiSelectHint") }}</span>
          </label>
          <label class="label--checkbox">
            <input v-model="editingSkill.is_published" type="checkbox" />
            {{ $t("admin.fields.published") }}
          </label>
          <label class="label--checkbox">
            <input v-model="editingSkill.show_in_pdf" type="checkbox" />
            {{ $t("admin.fields.showInPdf") }}
          </label>
          <p v-if="saveError" class="form-error">{{ saveError }}</p>
          <div class="form-panel__footer">
            <button class="btn btn--primary" type="submit">{{ $t("admin.save") }}</button>
            <button class="btn" type="button" @click="editingSkill = null">
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
import { skillApi, skillCategoryApi, technologyApi } from "@/api/admin";
import { useLevelLabel } from "@/composables/useLevelLabel";
import { useEscClose } from "@/composables/useEscClose";
import type { Skill, SkillCategory, SkillCategoryWrite, SkillWrite, Technology } from "@/api/types";

const levelLabel = useLevelLabel();

const groupedTechnologies = computed((): Array<[string, Technology[]]> => {
  const map = new Map<string, Technology[]>();
  for (const t of technologies.value) {
    const cat = t.category || "Other";
    const bucket = map.get(cat) ?? [];
    bucket.push(t);
    map.set(cat, bucket);
  }
  return [...map.entries()].sort(([a], [b]) => a.localeCompare(b));
});

type CategoryDraft = Partial<SkillCategoryWrite> & { id?: number };
type SkillDraft = Partial<SkillWrite> & { id?: number };

const items = ref<SkillCategory[]>([]);
const technologies = ref<Technology[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const editingCategory = ref<CategoryDraft | null>(null);
const editingSkill = ref<SkillDraft | null>(null);
const saveError = ref<string | null>(null);

onMounted(async () => {
  await Promise.all([load(), loadTechnologies()]);
});

useEscClose(
  () => {
    editingSkill.value = null;
    editingCategory.value = null;
  },
  computed(() => editingSkill.value !== null || editingCategory.value !== null),
);

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

const pdfCount = computed(
  () => items.value.flatMap((c) => c.skills).filter((s) => s.show_in_pdf).length,
);

async function togglePdf(skill: Skill): Promise<void> {
  const next = !skill.show_in_pdf;
  skill.show_in_pdf = next; // optimistic — revert on failure
  try {
    await skillApi.update(skill.id, { show_in_pdf: next });
  } catch {
    skill.show_in_pdf = !next;
    error.value = "Save failed.";
  }
}

async function deselectAllPdf(): Promise<void> {
  if (!confirm("Remove all skills from the PDF?")) return;
  const selected = items.value.flatMap((c) => c.skills).filter((s) => s.show_in_pdf);
  try {
    await Promise.all(selected.map((s) => skillApi.update(s.id, { show_in_pdf: false })));
  } catch {
    error.value = "Save failed.";
  }
  await load();
}

async function loadTechnologies(): Promise<void> {
  try {
    const page = await technologyApi.list();
    technologies.value = page.results;
  } catch {
    // technologies are optional — admin can still edit skills without picking any
  }
}

function openNewCategory(): void {
  editingCategory.value = { name: "", name_de: "", slug: "", is_published: true };
}

function openEditCategory(cat: SkillCategory): void {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { skills, ...rest } = cat;
  editingCategory.value = { ...rest };
}

async function saveCategory(): Promise<void> {
  saveError.value = null;
  if (!editingCategory.value) return;
  try {
    const { id, ...payload } = editingCategory.value;
    if (id) {
      await skillCategoryApi.update(id, payload);
    } else {
      await skillCategoryApi.create(payload);
    }
    editingCategory.value = null;
    await load();
  } catch {
    saveError.value = "Save failed.";
  }
}

async function removeCategory(id: number): Promise<void> {
  if (!confirm("Delete this category? Skills inside must be removed first.")) return;
  try {
    await skillCategoryApi.destroy(id);
    await load();
  } catch {
    error.value = "Delete failed — empty the category first.";
  }
}

function openNewSkill(categoryId: number): void {
  editingSkill.value = {
    name: "",
    name_de: "",
    category: categoryId,
    level: 3,
    technologies: [],
    is_published: true,
    show_in_pdf: true,
  };
}

function openEditSkill(skill: Skill, categoryId: number): void {
  editingSkill.value = {
    ...skill,
    category: categoryId,
    technologies: skill.technologies.map((t) => t.id),
    is_published: true,
  };
}

async function saveSkill(): Promise<void> {
  saveError.value = null;
  if (!editingSkill.value) return;
  try {
    const { id, ...payload } = editingSkill.value;
    if (id) {
      await skillApi.update(id, payload);
    } else {
      await skillApi.create(payload);
    }
    editingSkill.value = null;
    await load();
  } catch {
    saveError.value = "Save failed.";
  }
}

async function removeSkill(id: number): Promise<void> {
  if (!confirm("Delete this skill?")) return;
  await skillApi.destroy(id);
  await load();
}
</script>

<style scoped src="./admin-shared.css"></style>
<style scoped>
.skill-category {
  margin-bottom: var(--space-6);
}
.skill-list {
  list-style: none;
  padding: 0;
  margin: var(--space-2) 0 0 var(--space-6);
}
.skill-row {
  display: grid;
  grid-template-columns: auto 1fr auto 2fr auto;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-border);
}
.skill-row__pdf {
  font-size: 0.75rem;
  color: var(--color-fg-muted);
  white-space: nowrap;
  cursor: pointer;
}
.pdf-count {
  font-size: 0.85rem;
  color: var(--color-fg-muted);
  margin-left: auto;
  margin-right: var(--space-3);
}
.skill-row__name {
  font-weight: 500;
}
.skill-row__level {
  color: var(--color-accent);
  letter-spacing: 1px;
}
.skill-row__tech {
  font-size: 0.8rem;
  color: var(--color-fg-muted);
}
.field-hint {
  display: block;
  font-size: 0.75rem;
  color: var(--color-fg-muted);
  margin-top: 2px;
}
</style>
