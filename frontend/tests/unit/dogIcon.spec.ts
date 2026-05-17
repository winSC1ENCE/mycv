import { describe, expect, it } from "vitest";
import { DOG_ICONS, dogIconFor } from "@/composables/useDogIcon";

describe("dogIconFor", () => {
  it("is deterministic per uid", () => {
    expect(dogIconFor("experience-10")).toBe(dogIconFor("experience-10"));
    expect(dogIconFor("milestone-42")).toBe(dogIconFor("milestone-42"));
  });

  it("always returns a known icon path", () => {
    const candidates = new Set(DOG_ICONS as readonly string[]);
    for (let i = 0; i < 100; i++) {
      expect(candidates.has(dogIconFor(`experience-${i}`))).toBe(true);
    }
  });

  it("spreads sequential ids across multiple icons", () => {
    const picks = new Set<string>();
    for (let i = 0; i < 50; i++) {
      picks.add(dogIconFor(`experience-${i}`));
    }
    // 50 sequential uids should land on at least 6 of the 10 icons
    expect(picks.size).toBeGreaterThanOrEqual(6);
  });
});
