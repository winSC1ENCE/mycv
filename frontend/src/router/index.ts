import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: () => import("@/views/HomeView.vue") },
    {
      path: "/projects/:slug",
      name: "project",
      component: () => import("@/views/ProjectView.vue"),
      props: true,
    },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
    },
    {
      path: "/admin",
      component: () => import("@/views/admin/AdminLayout.vue"),
      meta: { requiresAuth: true },
      children: [
        { path: "", redirect: "/admin/dashboard" },
        {
          path: "dashboard",
          name: "admin-dashboard",
          component: () => import("@/views/admin/AdminDashboardView.vue"),
        },
        {
          path: "person",
          name: "admin-person",
          component: () => import("@/views/admin/AdminPersonView.vue"),
        },
        {
          path: "experiences",
          name: "admin-experiences",
          component: () => import("@/views/admin/AdminExperiencesView.vue"),
        },
        {
          path: "education",
          name: "admin-education",
          component: () => import("@/views/admin/AdminEducationView.vue"),
        },
        {
          path: "skills",
          name: "admin-skills",
          component: () => import("@/views/admin/AdminSkillsView.vue"),
        },
        {
          path: "certificates",
          name: "admin-certificates",
          component: () => import("@/views/admin/AdminCertificatesView.vue"),
        },
        {
          path: "projects",
          name: "admin-projects",
          component: () => import("@/views/admin/AdminProjectsView.vue"),
        },
        {
          path: "timeline",
          name: "admin-timeline",
          component: () => import("@/views/admin/AdminTimelineView.vue"),
        },
        {
          path: "technologies",
          name: "admin-technologies",
          component: () => import("@/views/admin/AdminTechnologiesView.vue"),
        },
        {
          path: "social-links",
          name: "admin-social-links",
          component: () => import("@/views/admin/AdminSocialLinksView.vue"),
        },
        {
          path: "access-keys",
          name: "admin-access-keys",
          component: () => import("@/views/admin/AdminAccessKeysView.vue"),
        },
        {
          path: "readmes",
          name: "admin-readmes",
          component: () => import("@/views/admin/AdminReadmesView.vue"),
        },
      ],
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/NotFoundView.vue"),
    },
  ],
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition;
    if (to.hash) return { el: to.hash, behavior: "smooth" };
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const auth = useAuthStore();
    if (!auth.isAuthenticated) {
      return { name: "login", query: { next: to.fullPath } };
    }
  }
});

export default router;
