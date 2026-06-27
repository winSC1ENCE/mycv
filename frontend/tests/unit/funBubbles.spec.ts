import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { bubbles, petCount, resetPetCount, spawnBubble } from "@/composables/useFunBubbles";

describe("useFunBubbles.spawnBubble", () => {
  beforeEach(() => {
    localStorage.clear();
    resetPetCount();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("pushes a bubble with click coords + a themed phrase", () => {
    spawnBubble("dog", "en", 100, 200, "/icons/dog/bone.png");
    expect(bubbles.value).toHaveLength(1);
    const b = bubbles.value[0];
    expect(b.x).toBe(100);
    expect(b.y).toBe(200);
    expect(b.size).toBe("normal");
    expect(["YUM!", "CRUNCH!", "TASTY!", "MINE!"]).toContain(b.text);
  });

  it("uses the active theme's phrase pool for the given locale", () => {
    spawnBubble("virus", "de", 0, 0, "/icons/virus/syringe.svg");
    expect(["GEIMPFT!", "DOSIS!", "PIKS!", "IMMUN!"]).toContain(bubbles.value[0].text);
    resetPetCount();
    spawnBubble("virus", "en", 0, 0, "/icons/virus/syringe.svg");
    expect(["VACCINATED!", "DOSE!", "JAB!", "IMMUNE!"]).toContain(bubbles.value[0].text);
  });

  it("increments the pet counter", () => {
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    expect(petCount.value).toBe(2);
  });

  it("emits a praise bubble at milestone counts", () => {
    for (let i = 0; i < 3; i++) spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    const last = bubbles.value[bubbles.value.length - 1];
    expect(last.text).toBe("GOOD DOG!");
    expect(last.size).toBe("big");
  });

  it("flags combo when ≥3 clicks fall inside a 1-second window", () => {
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    const fourth = bubbles.value[3];
    expect(fourth.size).toBe("big");
    expect(fourth.text.startsWith("COMBO!")).toBe(true);
  });

  it("does not flag combo when clicks are spread over time", () => {
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    vi.advanceTimersByTime(2000);
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    vi.advanceTimersByTime(2000);
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    vi.advanceTimersByTime(2000);
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    const last = bubbles.value[bubbles.value.length - 1];
    expect(last.size).toBe("normal");
    expect(last.text.startsWith("COMBO!")).toBe(false);
  });

  it("caps live bubbles at 12 by dropping the oldest", () => {
    for (let i = 0; i < 20; i++) spawnBubble("dog", "en", i, 0, "/icons/dog/ball.png");
    expect(bubbles.value.length).toBeLessThanOrEqual(12);
  });

  it("auto-removes a bubble after its TTL", () => {
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    expect(bubbles.value).toHaveLength(1);
    vi.advanceTimersByTime(2100);
    expect(bubbles.value).toHaveLength(0);
  });

  it("starts each session at zero (no localStorage persistence)", () => {
    spawnBubble("dog", "en", 0, 0, "/icons/dog/ball.png");
    resetPetCount();
    expect(petCount.value).toBe(0);
  });
});
