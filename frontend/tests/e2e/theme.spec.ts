import { test, expect } from "@playwright/test";

test("theme toggle switches normal → dog and persists across reload", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "normal");

  // Toggle button has a localized aria-label — match either EN or DE
  const toggle = page.getByRole("button", { name: /Toggle theme|Theme wechseln/i });
  await toggle.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dog");

  // Persist across reload
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dog");

  // Toggle back
  await toggle.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "normal");
});
