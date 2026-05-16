import { defineConfig, devices } from "@playwright/test";

const BACKEND_PORT = 8001; // dedicated port for e2e to avoid clashing with `manage.py runserver`
const FRONTEND_PORT = 3001;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false, // shared DB; admin spec mutates state
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  globalSetup: "./tests/e2e/helpers/global-setup.ts",
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: `http://localhost:${FRONTEND_PORT}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      // Django backend on a dedicated sqlite + port
      command:
        "cd ../backend && uv run python manage.py runserver 0.0.0.0:8001 --noreload",
      url: `http://localhost:${BACKEND_PORT}/api/health/`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: {
        DATABASE_URL: "sqlite:///db.e2e.sqlite3",
        DJANGO_SETTINGS_MODULE: "config.settings.dev",
        DEBUG: "True",
        SECRET_KEY: "e2e-not-secret",
        ALLOWED_HOSTS: "localhost,127.0.0.1",
        CORS_ALLOWED_ORIGINS: `http://localhost:${FRONTEND_PORT}`,
      },
    },
    {
      // Vite dev server proxied to the e2e backend
      command: `npm run dev -- --port ${FRONTEND_PORT}`,
      url: `http://localhost:${FRONTEND_PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: {
        VITE_DEV_PROXY_TARGET: `http://localhost:${BACKEND_PORT}`,
      },
    },
  ],
});
