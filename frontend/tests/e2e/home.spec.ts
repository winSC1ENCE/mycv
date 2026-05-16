import { test, expect } from "@playwright/test";
import { expectA11yClean } from "./helpers/a11y";

test("home page renders hero with seeded person name", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".hero__title")).toContainText("Nicolas Mischler");
});

test("home page sets dynamic <title>", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Nicolas Mischler.*CV/i);
});

test("home page emits Person JSON-LD", async ({ page }) => {
  await page.goto("/");
  const jsonLd = await page
    .locator('script[type="application/ld+json"]')
    .first()
    .textContent();
  expect(jsonLd, "JSON-LD script must be present").toBeTruthy();
  const data = JSON.parse(jsonLd ?? "{}");
  expect(data["@type"]).toBe("Person");
  expect(data.name).toBe("Nicolas Mischler");
  expect(Array.isArray(data.sameAs)).toBe(true);
});

test("home page passes axe in normal theme", async ({ page }) => {
  await page.goto("/");
  await page.waitForSelector(".hero__title");
  // GSAP timeline animation (~1.5s total) animates opacity from 0 → 1.
  // Wait for it to settle before running axe so colors are reported at full opacity.
  await page.waitForTimeout(1500);
  await expectA11yClean(page);
});

test("home page passes axe in dog theme", async ({ page }) => {
  await page.goto("/");
  await page.waitForSelector(".hero__title");
  await page.getByRole("button", { name: /Toggle theme|Theme wechseln/i }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dog");
  await page.waitForTimeout(1500);
  await expectA11yClean(page);
});
