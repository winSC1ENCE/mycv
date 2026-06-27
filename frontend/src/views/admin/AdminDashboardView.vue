<template>
  <div class="admin-dashboard">
    <h1 class="admin-page__title">{{ $t("admin.nav.dashboard") }}</h1>

    <section class="dashboard-exports">
      <h2 class="dashboard-exports__title">{{ $t("admin.exports.title") }}</h2>
      <div class="dashboard-exports__row">
        <span class="dashboard-exports__label">{{ $t("admin.exports.cv") }}</span>
        <button class="btn" :disabled="busy" @click="exportCv('en')">
          📄 {{ $t("admin.exports.en") }}
        </button>
        <button class="btn" :disabled="busy" @click="exportCv('de')">
          📄 {{ $t("admin.exports.de") }}
        </button>
      </div>
      <div class="dashboard-exports__row">
        <span class="dashboard-exports__label">{{ $t("admin.exports.certificates") }}</span>
        <button class="btn" :disabled="busy" @click="exportCerts('en')">
          🎓 {{ $t("admin.exports.en") }}
        </button>
        <button class="btn" :disabled="busy" @click="exportCerts('de')">
          🎓 {{ $t("admin.exports.de") }}
        </button>
      </div>
      <p v-if="error" class="admin-page__error">{{ error }}</p>
    </section>

    <div class="dashboard-grid">
      <RouterLink
        v-for="card in cards"
        :key="card.name"
        :to="{ name: card.route }"
        class="dashboard-card"
      >
        <span class="dashboard-card__title">{{ card.label }}</span>
        <span class="dashboard-card__arrow">→</span>
      </RouterLink>
    </div>

    <div class="dashboard-link">
      <RouterLink to="/">← {{ $t("admin.viewPublicCv") }}</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { cvApi } from "@/api/admin";
import { downloadBlob } from "@/utils/downloadBlob";

const { t } = useI18n();

const busy = ref(false);
const error = ref<string | null>(null);

async function runExport(
  fn: () => Promise<Blob>,
  filename: string,
  emptyMsg: string,
): Promise<void> {
  busy.value = true;
  error.value = null;
  try {
    downloadBlob(await fn(), filename);
  } catch (e) {
    // A 404 means there's nothing to export yet (no published CV / no attachments).
    const status = (e as { response?: { status?: number } }).response?.status;
    error.value = status === 404 ? emptyMsg : t("admin.exports.failed");
  } finally {
    busy.value = false;
  }
}

function exportCv(lang: "en" | "de"): Promise<void> {
  return runExport(
    () => cvApi.pdf(lang, `${window.location.origin}/`),
    `Nicolas_Mischler_CV_${lang.toUpperCase()}.pdf`,
    t("admin.exports.emptyCv"),
  );
}

function exportCerts(lang: "en" | "de"): Promise<void> {
  return runExport(
    () => cvApi.certificatesPdf(lang, `${window.location.origin}/`),
    `Nicolas_Mischler_Certificates_${lang.toUpperCase()}.pdf`,
    t("admin.exports.emptyCerts"),
  );
}

const cards = [
  { name: "person", route: "admin-person", label: t("admin.nav.person") },
  { name: "experience", route: "admin-experiences", label: t("nav.experience") },
  { name: "education", route: "admin-education", label: t("nav.education") },
  { name: "skills", route: "admin-skills", label: t("nav.skills") },
  { name: "certificates", route: "admin-certificates", label: t("nav.certificates") },
  { name: "projects", route: "admin-projects", label: t("nav.projects") },
  { name: "timeline", route: "admin-timeline", label: t("admin.nav.timeline") },
  { name: "technologies", route: "admin-technologies", label: t("admin.nav.technologies") },
  { name: "socialLinks", route: "admin-social-links", label: t("admin.nav.socialLinks") },
];
</script>

<style scoped>
.admin-page__title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: var(--space-6);
}

.dashboard-exports {
  margin-bottom: var(--space-6);
  padding: var(--space-5);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.dashboard-exports__title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: var(--space-4);
}

.dashboard-exports__row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.dashboard-exports__label {
  min-width: 7rem;
  font-weight: 600;
  color: var(--color-fg-muted);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-4);
}

.dashboard-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-fg);
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
}

.dashboard-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-sm);
}

.dashboard-card__title {
  font-weight: 600;
}

.dashboard-link {
  margin-top: var(--space-8);
  font-size: 0.875rem;
}

.dashboard-link a {
  color: var(--color-accent);
  text-decoration: none;
}
</style>
