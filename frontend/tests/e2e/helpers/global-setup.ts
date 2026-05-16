import { execSync } from "node:child_process";
import { existsSync, rmSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const _here = dirname(fileURLToPath(import.meta.url));

/**
 * Prepare a fresh sqlite DB for the e2e backend:
 *   1. Delete any stale db.e2e.sqlite3
 *   2. Run Django migrations
 *   3. Seed CV data via the existing management command
 *   4. Create a superuser (idempotent)
 *   5. Write the superuser credentials to .auth.json for tests to read
 */
export default async function globalSetup(): Promise<void> {
  const backendDir = resolve(_here, "..", "..", "..", "..", "backend");
  const dbFile = resolve(backendDir, "db.e2e.sqlite3");

  const env = {
    ...process.env,
    DATABASE_URL: "sqlite:///db.e2e.sqlite3",
    DJANGO_SETTINGS_MODULE: "config.settings.dev",
    DEBUG: "True",
    SECRET_KEY: "e2e-not-secret",
    ALLOWED_HOSTS: "localhost,127.0.0.1",
    CORS_ALLOWED_ORIGINS: "http://localhost:3001",
  };

  const run = (cmd: string): void => {
    execSync(cmd, { cwd: backendDir, env, stdio: "inherit" });
  };

  // 1. Fresh DB
  if (existsSync(dbFile)) rmSync(dbFile);

  // 2. Migrate
  run("uv run python manage.py migrate --noinput");

  // 3. Seed
  run("uv run python manage.py load_cv_seed");

  // 4. Superuser (idempotent)
  const username = "e2e_admin";
  const password = "e2e-test-password-1234";
  const email = "e2e@example.com";
  run(
    `uv run python manage.py shell -c "` +
      `from django.contrib.auth import get_user_model; U = get_user_model(); ` +
      `U.objects.filter(username='${username}').delete(); ` +
      `U.objects.create_superuser('${username}', '${email}', '${password}')"`,
  );

  // 5. Hand credentials to specs
  const authFile = resolve(_here, "..", ".auth.json");
  writeFileSync(authFile, JSON.stringify({ username, password, email }, null, 2));
}
