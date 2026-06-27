import { describe, expect, it, vi } from "vitest";
import { FUNNY_OPTIONS, FUNNY_PACKS, isFunnyTheme, packFor } from "@/themes/registry";
import { iconForTheme } from "@/composables/useThemeIcon";
import { phrasesForIcon, praiseFor, randomPhrase } from "@/composables/useFunBubbles";

describe("theme registry", () => {
  it("resolves registered packs and rejects others", () => {
    expect(packFor("dog")?.id).toBe("dog");
    expect(packFor("virus")?.id).toBe("virus");
    expect(packFor("normal")).toBeNull();
    expect(packFor("none")).toBeNull();
    expect(packFor("nope")).toBeNull();
    expect(packFor(null)).toBeNull();
  });

  it("isFunnyTheme is a type guard over the registry", () => {
    expect(isFunnyTheme("dog")).toBe(true);
    expect(isFunnyTheme("virus")).toBe(true);
    expect(isFunnyTheme("normal")).toBe(false);
    expect(isFunnyTheme(undefined)).toBe(false);
  });

  it("FUNNY_OPTIONS lists every funny pack with a label", () => {
    expect(FUNNY_OPTIONS.map((o) => o.id)).toEqual(Object.keys(FUNNY_PACKS));
    for (const opt of FUNNY_OPTIONS) {
      expect(opt.label).toBe(FUNNY_PACKS[opt.id].label);
    }
  });
});

describe("iconForTheme", () => {
  it("is deterministic per (theme, uid)", () => {
    expect(iconForTheme("dog", "experience-10")).toBe(iconForTheme("dog", "experience-10"));
    expect(iconForTheme("virus", "milestone-42")).toBe(iconForTheme("virus", "milestone-42"));
  });

  it("always returns one of the active pack's node icons", () => {
    for (const id of ["dog", "virus"] as const) {
      const candidates = new Set(packFor(id)!.nodeIcons);
      for (let i = 0; i < 60; i++) {
        expect(candidates.has(iconForTheme(id, `experience-${i}`))).toBe(true);
      }
    }
  });

  it("returns empty string for themes without node icons", () => {
    expect(iconForTheme("normal", "experience-1")).toBe("");
  });

  it("spreads sequential ids across multiple icons", () => {
    const picks = new Set<string>();
    for (let i = 0; i < 50; i++) picks.add(iconForTheme("dog", `experience-${i}`));
    expect(picks.size).toBeGreaterThanOrEqual(6);
  });
});

describe("phrasesForIcon / randomPhrase / praiseFor (locale-aware)", () => {
  it("matches dog buckets per locale with a default fallback", () => {
    expect(phrasesForIcon("dog", "en", "/icons/dog/bone.png")).toContain("CRUNCH!");
    expect(phrasesForIcon("dog", "de", "/icons/dog/bone.png")).toContain("KNUSPER!");
    expect(phrasesForIcon("dog", "en", "/icons/dog/dog-face.png")).toContain("WUFF!");
  });

  it("switches virus buckets between EN and DE", () => {
    expect(phrasesForIcon("virus", "de", "/icons/virus/syringe.svg")).toContain("GEIMPFT!");
    expect(phrasesForIcon("virus", "en", "/icons/virus/syringe.svg")).toContain("VACCINATED!");
    expect(phrasesForIcon("virus", "de", "/icons/virus/dna.svg")).toContain("MUTIERT!");
    expect(phrasesForIcon("virus", "en", "/icons/virus/dna.svg")).toContain("MUTATED!");
    expect(phrasesForIcon("virus", "de", "/icons/virus/unknown.svg")).toContain("QUARANTÄNE!");
  });

  it("falls back to EN for an unknown locale", () => {
    expect(phrasesForIcon("virus", "fr", "/icons/virus/syringe.svg")).toContain("VACCINATED!");
  });

  it("returns no phrases for normal mode", () => {
    expect(phrasesForIcon("normal", "en", "/x.png")).toEqual([]);
    expect(randomPhrase("normal", "en", "/x.png")).toBe("");
  });

  it("randomPhrase draws from the matching bucket for the locale", () => {
    vi.spyOn(Math, "random").mockReturnValue(0);
    expect(randomPhrase("dog", "en", "/icons/dog/bone.png")).toBe("YUM!");
    expect(randomPhrase("dog", "de", "/icons/dog/bone.png")).toBe("MAMPF!");
    expect(randomPhrase("virus", "de", "/icons/virus/test-tube.svg")).toBe("POSITIV!");
    expect(randomPhrase("virus", "en", "/icons/virus/test-tube.svg")).toBe("POSITIVE!");
    vi.restoreAllMocks();
  });

  it("praiseFor returns milestone praise per theme + locale, else null", () => {
    expect(praiseFor("dog", "en", 3)).toBe("GOOD DOG!");
    expect(praiseFor("dog", "de", 3)).toBe("GUTER HUND!");
    expect(praiseFor("virus", "en", 3)).toBe("PATIENT ZERO!");
    expect(praiseFor("virus", "de", 3)).toBe("PATIENT NULL!");
    expect(praiseFor("dog", "en", 4)).toBeNull();
    expect(praiseFor("normal", "en", 3)).toBeNull();
  });
});
