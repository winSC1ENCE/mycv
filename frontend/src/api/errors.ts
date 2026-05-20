import type { AxiosError } from "axios";

export function extractApiError(err: unknown, fallback = "Save failed."): string {
  const detail = (err as AxiosError<Record<string, unknown> | string>)?.response?.data;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (typeof detail === "object") {
    return Object.entries(detail)
      .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : String(v)}`)
      .join("; ");
  }
  return fallback;
}
