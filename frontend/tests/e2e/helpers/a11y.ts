import AxeBuilder from "@axe-core/playwright";
import { expect, type Page } from "@playwright/test";

/**
 * Run axe-core against the current page and fail the test if there are
 * any serious or critical WCAG 2.0 A / AA violations.
 */
export async function expectA11yClean(page: Page): Promise<void> {
  const { violations } = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
  const serious = violations.filter((v) => v.impact === "serious" || v.impact === "critical");
  expect(serious, `a11y violations:\n${JSON.stringify(serious, null, 2)}`).toEqual([]);
}
