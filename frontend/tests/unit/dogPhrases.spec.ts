import { describe, expect, it, vi } from "vitest";
import { phrasesForIcon, praiseFor, randomPhrase } from "@/composables/dogPhrases";

describe("phrasesForIcon", () => {
  it("matches by URL substring per icon bucket", () => {
    expect(phrasesForIcon("/icons/dog/bone.png")).toContain("CRUNCH!");
    expect(phrasesForIcon("/icons/dog/ball.png")).toContain("FETCH!");
    expect(phrasesForIcon("/icons/dog/bowl.png")).toContain("NOM NOM!");
    expect(phrasesForIcon("/icons/dog/doghouse.png")).toContain("HOME!");
    expect(phrasesForIcon("/icons/dog/rope-toy.png")).toContain("TUG!");
    expect(phrasesForIcon("/icons/dog/dog-sleeping.png")).toContain("Zzz…");
    expect(phrasesForIcon("/icons/dog/dog-skateboard.png")).toContain("WHEE!");
    expect(phrasesForIcon("/icons/dog/paws.png")).toContain("TAP TAP");
  });

  it("falls back to default barks for unknown icons", () => {
    const out = phrasesForIcon("/icons/dog/dog-face.png");
    expect(out).toContain("WUFF!");
  });

  it("falls back to default for an empty URL", () => {
    expect(phrasesForIcon("")).toContain("WOOF!");
  });
});

describe("randomPhrase", () => {
  it("returns a phrase from the matching bucket", () => {
    vi.spyOn(Math, "random").mockReturnValue(0);
    expect(randomPhrase("/icons/dog/bone.png")).toBe("YUM!");
    vi.restoreAllMocks();
  });

  it("varies across many calls", () => {
    const seen = new Set<string>();
    for (let i = 0; i < 50; i++) {
      seen.add(randomPhrase("/icons/dog/bone.png"));
    }
    expect(seen.size).toBeGreaterThanOrEqual(2);
  });
});

describe("praiseFor", () => {
  it("returns the praise string for milestone counts", () => {
    expect(praiseFor(10)).toBe("GOOD DOG!");
    expect(praiseFor(25)).toBe("WHO'S A GOOD BOY?");
    expect(praiseFor(50)).toBe("BEST FRIEND!");
    expect(praiseFor(100)).toBe("DOG WHISPERER!");
  });

  it("returns null for non-milestone counts", () => {
    expect(praiseFor(0)).toBeNull();
    expect(praiseFor(9)).toBeNull();
    expect(praiseFor(11)).toBeNull();
    expect(praiseFor(99)).toBeNull();
    expect(praiseFor(101)).toBeNull();
  });
});
