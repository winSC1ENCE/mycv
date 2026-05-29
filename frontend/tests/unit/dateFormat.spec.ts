import { describe, expect, it } from "vitest";
import { formatDate, formatMonthYear } from "@/utils/dateFormat";

describe("formatDate", () => {
  it("formats German as dd.mm.yyyy", () => {
    expect(formatDate("2025-03-23", "de")).toBe("23.03.2025");
  });

  it("formats English as 'd MMM yyyy'", () => {
    expect(formatDate("2025-03-23", "en")).toBe("23 Mar 2025");
  });

  it("returns the input unchanged when unparseable", () => {
    expect(formatDate("not-a-date", "de")).toBe("not-a-date");
    expect(formatDate("", "en")).toBe("");
  });
});

describe("formatMonthYear", () => {
  it("returns month abbreviation + year", () => {
    expect(formatMonthYear("2025-03-23", "en")).toBe("Mar 2025");
    expect(formatMonthYear("2025-03-23", "de")).toContain("2025");
  });

  it("returns the input unchanged when unparseable", () => {
    expect(formatMonthYear("garbage", "en")).toBe("garbage");
  });
});
