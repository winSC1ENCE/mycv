import { describe, expect, it } from "vitest";
import { pickLocalized } from "@/composables/useLocalized";

describe("pickLocalized", () => {
  it("returns English when locale is en", () => {
    expect(pickLocalized({ title: "Hello", title_de: "Hallo" }, "title", "en")).toBe("Hello");
  });

  it("returns German when locale is de", () => {
    expect(pickLocalized({ title: "Hello", title_de: "Hallo" }, "title", "de")).toBe("Hallo");
  });

  it("falls back to English when German is empty", () => {
    expect(pickLocalized({ title: "Hello", title_de: "" }, "title", "de")).toBe("Hello");
  });

  it("returns empty string on null source", () => {
    expect(pickLocalized(null, "title", "en")).toBe("");
  });
});
