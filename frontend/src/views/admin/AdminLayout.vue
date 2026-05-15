<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="admin-sidebar__brand">
        <RouterLink to="/" class="admin-sidebar__logo">{{ $t("nav.brand") }}</RouterLink>
        <span class="admin-sidebar__badge">Admin</span>
      </div>

      <nav class="admin-nav">
        <RouterLink class="admin-nav__link" :to="{ name: 'admin-dashboard' }">
          {{ $t("admin.nav.dashboard") }}
        </RouterLink>
        <RouterLink class="admin-nav__link" :to="{ name: 'admin-experiences' }">
          {{ $t("nav.experience") }}
        </RouterLink>
        <RouterLink class="admin-nav__link" :to="{ name: 'admin-education' }">
          {{ $t("nav.education") }}
        </RouterLink>
        <RouterLink class="admin-nav__link" :to="{ name: 'admin-skills' }">
          {{ $t("nav.skills") }}
        </RouterLink>
        <RouterLink class="admin-nav__link" :to="{ name: 'admin-certificates' }">
          {{ $t("nav.certificates") }}
        </RouterLink>
        <RouterLink class="admin-nav__link" :to="{ name: 'admin-projects' }">
          {{ $t("nav.projects") }}
        </RouterLink>
        <RouterLink class="admin-nav__link" :to="{ name: 'admin-timeline' }">
          {{ $t("admin.nav.timeline") }}
        </RouterLink>
        <RouterLink class="admin-nav__link" :to="{ name: 'admin-technologies' }">
          {{ $t("admin.nav.technologies") }}
        </RouterLink>
      </nav>

      <div class="admin-sidebar__footer">
        <span class="admin-sidebar__user">{{ auth.user?.username }}</span>
        <button class="admin-sidebar__logout" @click="handleLogout">
          {{ $t("admin.logout") }}
        </button>
      </div>
    </aside>

    <main class="admin-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

async function handleLogout(): Promise<void> {
  await auth.logout();
  router.push("/");
}
</script>

<style scoped>
.admin-shell {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

.admin-sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: var(--space-4) 0;
}

.admin-sidebar__brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-2);
}

.admin-sidebar__logo {
  font-weight: 700;
  color: var(--color-fg);
  text-decoration: none;
}

.admin-sidebar__badge {
  font-size: 0.7rem;
  background: var(--color-accent);
  color: #fff;
  padding: 1px 6px;
  border-radius: 4px;
}

.admin-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 var(--space-2);
}

.admin-nav__link {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-fg-muted);
  text-decoration: none;
  font-size: 0.9rem;
  transition: background 0.1s, color 0.1s;
}

.admin-nav__link:hover,
.admin-nav__link.router-link-active {
  background: var(--color-accent);
  color: #fff;
}

.admin-sidebar__footer {
  padding: var(--space-4);
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.admin-sidebar__user {
  font-size: 0.85rem;
  color: var(--color-fg-muted);
}

.admin-sidebar__logout {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-1) var(--space-3);
  font-size: 0.85rem;
  cursor: pointer;
  color: var(--color-fg);
}

.admin-main {
  flex: 1;
  padding: var(--space-8);
  overflow-y: auto;
}
</style>
