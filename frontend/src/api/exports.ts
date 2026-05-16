export type PdfLang = "en" | "de";
export type PdfTheme = "normal" | "dog";

export function buildPdfUrl(lang: PdfLang, theme: PdfTheme): string {
  const base = import.meta.env.VITE_API_BASE ?? "/api";
  return `${base}/cv/pdf/?lang=${lang}&theme=${theme}`;
}
