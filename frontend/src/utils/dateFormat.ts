import type { Locale } from "@/stores/locale";

const LOCALE_TAG: Record<Locale, string> = { en: "en-GB", de: "de-CH" };

/** Parse an ISO `YYYY-MM-DD` string into a UTC Date, or null if malformed. */
function parseIso(iso: string): Date | null {
  const [y, m, d] = iso.split("-").map(Number);
  if (!y || !m || !d) return null;
  const date = new Date(Date.UTC(y, m - 1, d));
  return Number.isNaN(date.getTime()) ? null : date;
}

/**
 * Full date: German → `23.03.2025`, English → `23 Mar 2025`.
 * Returns the input unchanged if it cannot be parsed.
 */
export function formatDate(iso: string, locale: Locale): string {
  const date = parseIso(iso);
  if (!date) return iso;
  const opts: Intl.DateTimeFormatOptions =
    locale === "de"
      ? { day: "2-digit", month: "2-digit", year: "numeric", timeZone: "UTC" }
      : { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" };
  return new Intl.DateTimeFormat(LOCALE_TAG[locale], opts).format(date);
}

/** Month + year: German → `März 2025`, English → `Mar 2025`. */
export function formatMonthYear(iso: string, locale: Locale): string {
  const date = parseIso(iso);
  if (!date) return iso;
  return new Intl.DateTimeFormat(LOCALE_TAG[locale], {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(date);
}
