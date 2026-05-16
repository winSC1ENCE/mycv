import { test, expect } from "@playwright/test";

test("unknown route renders polished 404 page", async ({ page }) => {
  await page.goto("/this-route-does-not-exist");
  await expect(page.locator(".not-found__code")).toContainText("404");
  await expect(page.locator(".not-found__title")).toBeVisible();
});

test("404 page has back-to-home link", async ({ page }) => {
  await page.goto("/garbage");
  await page.getByRole("link", { name: /home/i }).click();
  await expect(page).toHaveURL("/");
  await expect(page.locator(".hero__title")).toBeVisible();
});
