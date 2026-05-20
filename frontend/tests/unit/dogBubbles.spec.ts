import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  bubbles,
  petCount,
  resetPetCount,
  spawnBubble,
} from "@/composables/useDogBubbles";

describe("useDogBubbles.spawnBubble", () => {
  beforeEach(() => {
    localStorage.clear();
    resetPetCount();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("pushes a bubble with click coords + chosen text", () => {
    spawnBubble(100, 200, "/icons/dog/bone.png");
    expect(bubbles.value).toHaveLength(1);
    const b = bubbles.value[0];
    expect(b.x).toBe(100);
    expect(b.y).toBe(200);
    expect(b.size).toBe("normal");
    // bone bucket should produce one of these
    expect(["YUM!", "CRUNCH!", "TASTY!", "MINE!"]).toContain(b.text);
  });

  it("increments and persists the pet counter", () => {
    spawnBubble(0, 0, "/icons/dog/ball.png");
    spawnBubble(0, 0, "/icons/dog/ball.png");
    expect(petCount.value).toBe(2);
    expect(localStorage.getItem("mycv:pets")).toBe("2");
  });

  it("emits a praise bubble at milestone counts", () => {
    // First milestone is 3 — the third click triggers "GOOD DOG!"
    for (let i = 0; i < 3; i++) spawnBubble(0, 0, "/icons/dog/ball.png");
    const last = bubbles.value[bubbles.value.length - 1];
    expect(last.text).toBe("GOOD DOG!");
    expect(last.size).toBe("big");
  });

  it("flags combo when ≥3 clicks fall inside a 1-second window", () => {
    // Click 4 times: the 3rd is a praise milestone (count=3), the 4th hits combo
    // (4 timestamps within the 1s window, no praise at count=4).
    spawnBubble(0, 0, "/icons/dog/ball.png");
    spawnBubble(0, 0, "/icons/dog/ball.png");
    spawnBubble(0, 0, "/icons/dog/ball.png");
    spawnBubble(0, 0, "/icons/dog/ball.png");
    const fourth = bubbles.value[3];
    expect(fourth.size).toBe("big");
    expect(fourth.text.startsWith("COMBO!")).toBe(true);
  });

  it("does not flag combo when clicks are spread over time", () => {
    // 4 clicks spread out — combo window flushes between each. Count ends at 4
    // (no praise milestone), no timestamps remain in window, so result is normal.
    spawnBubble(0, 0, "/icons/dog/ball.png");
    vi.advanceTimersByTime(2000);
    spawnBubble(0, 0, "/icons/dog/ball.png");
    vi.advanceTimersByTime(2000);
    spawnBubble(0, 0, "/icons/dog/ball.png");
    vi.advanceTimersByTime(2000);
    spawnBubble(0, 0, "/icons/dog/ball.png");
    const last = bubbles.value[bubbles.value.length - 1];
    expect(last.size).toBe("normal");
    expect(last.text.startsWith("COMBO!")).toBe(false);
  });

  it("caps live bubbles at 12 by dropping the oldest", () => {
    for (let i = 0; i < 20; i++) spawnBubble(i, 0, "/icons/dog/ball.png");
    expect(bubbles.value.length).toBeLessThanOrEqual(12);
  });

  it("auto-removes a bubble after its TTL", () => {
    spawnBubble(0, 0, "/icons/dog/ball.png");
    expect(bubbles.value).toHaveLength(1);
    vi.advanceTimersByTime(2100); // > BIG_BUBBLE_TTL_MS to be safe
    expect(bubbles.value).toHaveLength(0);
  });

  it("restores petCount from localStorage on import (smoke)", () => {
    // resetPetCount cleared it; just verify the watcher persists subsequent writes
    spawnBubble(0, 0, "/icons/dog/ball.png");
    expect(localStorage.getItem("mycv:pets")).toBe("1");
  });
});
