<template>
  <div class="admin-dashboard">
    <h1 class="admin-page__title">{{ $t("admin.nav.dashboard") }}</h1>

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
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const cards = [
  { name: "experience", route: "admin-experiences", label: t("nav.experience") },
  { name: "education", route: "admin-education", label: t("nav.education") },
  { name: "skills", route: "admin-skills", label: t("nav.skills") },
  { name: "certificates", route: "admin-certificates", label: t("nav.certificates") },
  { name: "projects", route: "admin-projects", label: t("nav.projects") },
  { name: "timeline", route: "admin-timeline", label: t("admin.nav.timeline") },
  { name: "technologies", route: "admin-technologies", label: t("admin.nav.technologies") },
];
</script>

<style scoped>
.admin-page__title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: var(--space-6);
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
  transition: border-color 0.15s, box-shadow 0.15s;
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
