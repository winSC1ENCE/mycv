import { storeToRefs } from "pinia";
import { computed, type ComputedRef } from "vue";
import { useLocaleStore } from "@/stores/locale";

/**
 * Pick the locale-appropriate variant of a field that has `_de` and base variants.
 * Falls back to the base (English) when the German value is empty.
 */
export function useLocalized<T extends Record<string, unknown>>(
  source: ComputedRef<T | null | undefined>,
  field: keyof T & string,
): ComputedRef<string> {
  const { locale } = storeToRefs(useLocaleStore());
  return computed(() => {
    const obj = source.value;
    if (!obj) return "";
    const base = (obj[field] as unknown as string) ?? "";
    if (locale.value === "en") return base;
    const dePicker = `${field}_de` as keyof T & string;
    const de = (obj[dePicker] as unknown as string) ?? "";
    return de || base;
  });
}

export function pickLocalized(obj: unknown, field: string, locale: "en" | "de"): string {
  if (!obj || typeof obj !== "object") return "";
  const record = obj as Record<string, unknown>;
  const base = typeof record[field] === "string" ? (record[field] as string) : "";
  if (locale === "en") return base;
  const deField = `${field}_de`;
  const de = typeof record[deField] === "string" ? (record[deField] as string) : "";
  return de || base;
}
