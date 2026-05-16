import { describe, it, expect } from "vitest";
import { buildPdfUrl } from "@/api/exports";

describe("buildPdfUrl", () => {
  it("uses /api as default base when VITE_API_BASE is unset", () => {
    expect(buildPdfUrl("en", "normal")).toBe("/api/cv/pdf/?lang=en&theme=normal");
  });

  it("encodes lang and theme in query string", () => {
    expect(buildPdfUrl("de", "dog")).toBe("/api/cv/pdf/?lang=de&theme=dog");
  });

  it("emits all four lang/theme combos correctly", () => {
    expect(buildPdfUrl("en", "normal")).toContain("lang=en");
    expect(buildPdfUrl("en", "dog")).toContain("theme=dog");
    expect(buildPdfUrl("de", "normal")).toContain("lang=de");
    expect(buildPdfUrl("de", "dog")).toContain("theme=dog");
  });
});
