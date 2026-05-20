import { describe, expect, it, vi, beforeEach } from "vitest";

const tMock = vi.fn();
vi.mock("vue-i18n", () => ({
  useI18n: () => ({ t: tMock }),
}));

import { useLevelLabel } from "@/composables/useLevelLabel";

const EN: Record<string, string> = {
  "skills.levels.1": "Novice",
  "skills.levels.2": "Advanced Beginner",
  "skills.levels.3": "Competent",
  "skills.levels.4": "Proficient",
  "skills.levels.5": "Expert",
};

const DE: Record<string, string> = {
  "skills.levels.1": "Neuling",
  "skills.levels.2": "Fortgeschrittener Anfänger",
  "skills.levels.3": "Kompetent",
  "skills.levels.4": "Versiert",
  "skills.levels.5": "Experte",
};

describe("useLevelLabel", () => {
  beforeEach(() => {
    tMock.mockReset();
  });

  it("returns the EN label for each level 1..5", () => {
    tMock.mockImplementation((key: string) => EN[key] ?? key);
    const levelLabel = useLevelLabel();
    expect(levelLabel(1)).toBe("Novice");
    expect(levelLabel(2)).toBe("Advanced Beginner");
    expect(levelLabel(3)).toBe("Competent");
    expect(levelLabel(4)).toBe("Proficient");
    expect(levelLabel(5)).toBe("Expert");
  });

  it("clamps out-of-range values to 1..5", () => {
    tMock.mockImplementation((key: string) => EN[key] ?? key);
    const levelLabel = useLevelLabel();
    expect(levelLabel(0)).toBe("Novice");
    expect(levelLabel(-3)).toBe("Novice");
    expect(levelLabel(6)).toBe("Expert");
    expect(levelLabel(99)).toBe("Expert");
    // non-integer rounds before clamping
    expect(levelLabel(3.4)).toBe("Competent");
    expect(levelLabel(3.6)).toBe("Proficient");
  });

  it("returns the DE label when t() resolves German strings", () => {
    tMock.mockImplementation((key: string) => DE[key] ?? key);
    const levelLabel = useLevelLabel();
    expect(levelLabel(1)).toBe("Neuling");
    expect(levelLabel(4)).toBe("Versiert");
    expect(levelLabel(5)).toBe("Experte");
  });
});
