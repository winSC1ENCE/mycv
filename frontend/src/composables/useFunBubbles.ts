/**
 * Module-level reactive state for the funny-theme bubble game.
 *
 * Theme-agnostic: the click handler in TimelineSection calls
 * `spawnBubble(themeId, x, y, iconUrl)`, which picks a themed phrase from the
 * active pack, increments the persisted pet counter, detects combos, and
 * auto-cleans the bubble after a short timeout. Phrase/praise pools live in the
 * theme registry (`@/themes/registry`).
 */

import { ref } from "vue";
import { packFor } from "@/themes/registry";

export interface Bubble {
  id: number;
  x: number;
  y: number;
  text: string;
  size: "normal" | "big";
  rotate: number;
}

const MAX_BUBBLES = 12;
const COMBO_WINDOW_MS = 1000;
const COMBO_THRESHOLD = 3;
const BUBBLE_TTL_MS = 1500;
const BIG_BUBBLE_TTL_MS = 2000;

export const bubbles = ref<Bubble[]>([]);
export const petCount = ref<number>(0);

let nextId = 1;
const recentClickTimestamps: number[] = [];

/** Phrase pool for an icon url under the given theme + locale (with fallbacks). */
export function phrasesForIcon(themeId: string, locale: string, url: string): readonly string[] {
  const pack = packFor(themeId);
  if (!pack) return [];
  const phrases = pack.phrases[locale] ?? pack.phrases.en;
  // Match against the filename only, so the theme folder (e.g. "/icons/virus/")
  // can't accidentally match a like-named bucket key.
  const file = url.split("/").pop() ?? url;
  for (const key of Object.keys(phrases.iconPhrases)) {
    if (file.includes(key)) return phrases.iconPhrases[key];
  }
  return phrases.defaultPhrases;
}

export function randomPhrase(themeId: string, locale: string, url: string): string {
  const pool = phrasesForIcon(themeId, locale, url);
  if (pool.length === 0) return "";
  return pool[Math.floor(Math.random() * pool.length)];
}

export function praiseFor(themeId: string, locale: string, count: number): string | null {
  const pack = packFor(themeId);
  if (!pack) return null;
  return (pack.phrases[locale] ?? pack.phrases.en).praise[count] ?? null;
}

function isCombo(now: number): boolean {
  // Drop timestamps older than the window
  while (recentClickTimestamps.length && now - recentClickTimestamps[0] > COMBO_WINDOW_MS) {
    recentClickTimestamps.shift();
  }
  return recentClickTimestamps.length >= COMBO_THRESHOLD;
}

export function spawnBubble(
  themeId: string,
  locale: string,
  x: number,
  y: number,
  iconUrl: string,
): void {
  const now = Date.now();
  recentClickTimestamps.push(now);

  petCount.value += 1;

  const praise = praiseFor(themeId, locale, petCount.value);
  const combo = isCombo(now);

  let text: string;
  let size: "normal" | "big";
  if (praise) {
    text = praise;
    size = "big";
  } else if (combo) {
    text = `COMBO! ${randomPhrase(themeId, locale, iconUrl)}`;
    size = "big";
  } else {
    text = randomPhrase(themeId, locale, iconUrl);
    size = "normal";
  }

  const bubble: Bubble = {
    id: nextId++,
    x,
    y,
    text,
    size,
    rotate: Math.floor(Math.random() * 24) - 12,
  };

  bubbles.value.push(bubble);
  // Cap concurrent bubbles
  while (bubbles.value.length > MAX_BUBBLES) bubbles.value.shift();

  const ttl = size === "big" ? BIG_BUBBLE_TTL_MS : BUBBLE_TTL_MS;
  if (typeof window !== "undefined") {
    window.setTimeout(() => {
      bubbles.value = bubbles.value.filter((b) => b.id !== bubble.id);
    }, ttl);
  }
}

export function resetPetCount(): void {
  petCount.value = 0;
  bubbles.value = [];
  recentClickTimestamps.length = 0;
}
