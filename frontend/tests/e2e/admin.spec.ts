import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const _here = dirname(fileURLToPath(import.meta.url));
const auth = JSON.parse(readFileSync(resolve(_here, ".auth.json"), "utf-8")) as {
  username: string;
  password: string;
};

test("admin login → create experience → see it on public CV", async ({ page }) => {
  // 1. Login
  await page.goto("/login");
  await page.fill("#username", auth.username);
  await page.fill("#password", auth.password);
  await page.locator('form button[type="submit"]').click();
  await page.waitForURL(/\/admin/);

  // 2. Navigate to Experiences admin
  await page.getByRole("link", { name: "Experience", exact: true }).click();
  await page.waitForURL(/\/admin\/experiences/);

  // 3. Open the create form
  const uniqueRole = `E2E Role ${Date.now()}`;
  await page.getByRole("button", { name: /Add$/ }).click();

  // 4. Fill required fields — labels include their input children via <label>...
  await page.getByLabel("Role", { exact: true }).fill(uniqueRole);
  await page.getByLabel("Company", { exact: true }).fill("E2E Company");
  await page.getByLabel("Start date", { exact: true }).fill("2026-01-01");

  // 5. Submit the form. Wait for the POST to confirm the backend accepted it.
  const postDone = page.waitForResponse(
    (r) => r.url().includes("/api/experiences/") && r.request().method() === "POST",
  );
  await page.locator(".form-panel button[type='submit']").click();
  const postResp = await postDone;
  expect(postResp.status(), "experience creation must succeed").toBe(201);
  await expect(page.locator(".form-panel")).toBeHidden();

  // 6. The public CV should now show the new role.
  //    Wait for /api/cv/ to be re-fetched after navigation.
  const cvResponse = page.waitForResponse(
    (r) => r.url().includes("/api/cv/") && r.request().method() === "GET",
  );
  await page.goto("/");
  await cvResponse;
  await expect(page.locator("body")).toContainText(uniqueRole);
});
