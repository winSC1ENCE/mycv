/**
 * Theme-pack abstraction.
 *
 * A "funny" theme (Dog, Virus, …) is a self-contained data pack. The generic
 * composables/components (`useThemeIcon`, `useFunBubbles`, `FunBubbles.vue`,
 * `ProfileSection`, `SkillsSection`, the easter-egg modal) read the *active*
 * pack rather than hardcoding a theme id. Adding a new funny theme = add one
 * `xyz.ts` pack + register it in `registry.ts` + ship a `[data-theme="xyz"]`
 * stylesheet. Nothing else needs to know the id.
 */

/** A localized hover quip for a skill/technology name (Virus Mode etc.). */
export interface SkillQuip {
  en: string;
  de: string;
}

/** Bubble phrase pools for a single locale. */
export interface PhrasePack {
  /** Phrase pools keyed by an icon-filename substring (for click bubbles). */
  iconPhrases: Readonly<Record<string, readonly string[]>>;
  /** Fallback phrases when no `iconPhrases` bucket matches. */
  defaultPhrases: readonly string[];
  /** Milestone → praise phrase (shown as a "big" bubble at that pet count). */
  praise: Readonly<Record<number, string>>;
}

/** One row of the easter-egg payload (e.g. an R₀ reproduction-number row). */
export interface EasterEggRow {
  /** i18n key resolving to the row label. */
  labelKey: string;
  /** Locale-agnostic value shown verbatim (e.g. "3.4"). */
  value: string;
}

/** Optional floating-button + modal easter egg for a theme. */
export interface EasterEggConfig {
  /** i18n key for the floating button label. */
  buttonKey: string;
  /** i18n key for the modal title. */
  titleKey: string;
  /** i18n key for the intro line above the table. */
  introKey: string;
  /** i18n key for the footnote/warning below the table. */
  footnoteKey: string;
  /** i18n key for the table's value-column header. */
  valueHeadKey: string;
  rows: EasterEggRow[];
}

/** Optional themed hero block shown in the profile section. */
export interface HeroBlock {
  /** i18n key for the lead line (e.g. "Spezialist für die Eindämmung von:"). */
  leadKey: string;
  /** i18n key resolving to a string[] of checklist items (read via `tm()`). */
  itemsKey: string;
}

export interface ThemePack {
  /** `data-theme` value, e.g. "dog" | "virus". */
  id: string;
  /** Human label for the admin dropdown + toggle button, e.g. "Dog". */
  label: string;
  /** Toggle-button glyph, e.g. "🐕" / "🦠". */
  emoji: string;
  /** Hero photo asset under `public/`. */
  profilePhoto: string;
  /** i18n key for the bubble counter chip (e.g. "timeline.pet_counter"). */
  counterKey: string;
  /** Timeline-node icon URLs; empty disables node icons + bubbles for the theme. */
  nodeIcons: readonly string[];
  /** Bubble phrase pools per locale code; MUST include "en" as the fallback. */
  phrases: Readonly<Record<string, PhrasePack>>;
  /** Optional per-skill hover quips (by skill/technology name). */
  skillQuips?: Readonly<Record<string, SkillQuip>>;
  /** Optional themed hero block in the profile section. */
  hero?: HeroBlock;
  /** Optional floating easter-egg button + modal. */
  easterEgg?: EasterEggConfig;
}
