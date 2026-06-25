/**
 * Theme registry — the single source of truth for funny themes.
 *
 * To add a third funny theme: create `xyz.ts` exporting a `ThemePack`, add one
 * line to `FUNNY_PACKS`, and ship a `[data-theme="xyz"]` stylesheet imported in
 * `main.ts`. The store, admin dropdown, toggle button, and all consuming
 * components pick it up automatically — no other edits required.
 */

import { dogPack } from "./dog";
import { virusPack } from "./virus";
import type { ThemePack } from "./types";

export const FUNNY_PACKS = {
  dog: dogPack,
  virus: virusPack,
} as const;

export type FunnyThemeId = keyof typeof FUNNY_PACKS;
export type ThemeId = "normal" | FunnyThemeId;

/** Resolve a pack by id; `null` for "normal", "none", or any unknown id. */
export function packFor(id: string | null | undefined): ThemePack | null {
  if (!id) return null;
  return (FUNNY_PACKS as Record<string, ThemePack>)[id] ?? null;
}

/** True for a registered funny theme id. */
export function isFunnyTheme(id: string | null | undefined): id is FunnyThemeId {
  return !!id && id in FUNNY_PACKS;
}

/** Options for the admin dropdown (in registration order). */
export const FUNNY_OPTIONS: ReadonlyArray<{ id: FunnyThemeId; label: string }> = (
  Object.keys(FUNNY_PACKS) as FunnyThemeId[]
).map((id) => ({ id, label: FUNNY_PACKS[id].label }));
