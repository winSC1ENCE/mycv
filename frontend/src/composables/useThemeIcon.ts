/**
 * Deterministic timeline-node icon picker for funny themes.
 *
 * Given the active theme id and a stable per-row uid (e.g. "experience-10"),
 * returns one of that theme's node icons. Same (theme, uid) → same icon across
 * reloads; new admin entries get a fresh pick via their new id. Returns "" for
 * themes without node icons (normal mode), so callers can skip rendering.
 */

import { packFor } from "@/themes/registry";

export function iconForTheme(themeId: string, uid: string): string {
  const icons = packFor(themeId)?.nodeIcons ?? [];
  if (icons.length === 0) return "";
  const h = Array.from(uid).reduce((a, c) => a + c.charCodeAt(0), 0);
  return icons[h % icons.length];
}
