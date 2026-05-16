import { test, expect } from "@playwright/test";

test("Download CV button has correct href for current lang+theme", async ({ page }) => {
  await page.goto("/");

  // Stable selector — the href prefix never changes, but the text and title do per locale
  const downloadLink = page.locator('a[href^="/api/cv/pdf/"]');
  await expect(downloadLink).toBeVisible();
  await expect(downloadLink).toHaveAttribute(
    "href",
    "/api/cv/pdf/?lang=en&theme=normal",
  );

  // Switch to DE
  await page.getByRole("button", { name: /Switch language|Sprache wechseln/i }).click();
  await expect(downloadLink).toHaveAttribute(
    "href",
    "/api/cv/pdf/?lang=de&theme=normal",
  );

  // Switch to dog
  await page.getByRole("button", { name: /Toggle theme|Theme wechseln/i }).click();
  await expect(downloadLink).toHaveAttribute(
    "href",
    "/api/cv/pdf/?lang=de&theme=dog",
  );
});
