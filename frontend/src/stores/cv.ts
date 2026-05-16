import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { fetchCv } from "@/api/client";
import type { Certificate, Cv, Education, Experience, TimelineEntry } from "@/api/types";

export type TimelineRow =
  | { kind: "experience"; date: string; data: Experience; certs: Certificate[] }
  | { kind: "education"; date: string; data: Education; certs: Certificate[] }
  | { kind: "certificate"; date: string; data: Certificate }
  | { kind: "milestone"; date: string; data: TimelineEntry };

function pickAnchorDate(start: string, end: string | null): string {
  // Sort by end-date (current roles use start as anchor since end is null).
  return end ?? start;
}

export const useCvStore = defineStore("cv", () => {
  const cv = ref<Cv | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isLoaded = computed(() => cv.value !== null);

  const timelineItems = computed<TimelineRow[]>(() => {
    if (!cv.value) return [];
    const c = cv.value;

    const expRows: TimelineRow[] = c.experiences.map((exp) => ({
      kind: "experience" as const,
      date: pickAnchorDate(exp.start_date, exp.end_date),
      data: exp,
      certs: c.certificates.filter((cert) => cert.experience === exp.id),
    }));

    const eduRows: TimelineRow[] = c.educations.map((edu) => ({
      kind: "education" as const,
      date: pickAnchorDate(edu.start_date, edu.end_date),
      data: edu,
      certs: c.certificates.filter((cert) => cert.education === edu.id),
    }));

    const standaloneCertRows: TimelineRow[] = c.certificates
      .filter((cert) => cert.experience === null && cert.education === null)
      .map((cert) => ({
        kind: "certificate" as const,
        date: cert.issue_date,
        data: cert,
      }));

    const milestoneRows: TimelineRow[] = c.timeline_entries.map((entry) => ({
      kind: "milestone" as const,
      date: entry.date,
      data: entry,
    }));

    return [...expRows, ...eduRows, ...standaloneCertRows, ...milestoneRows].sort((a, b) =>
      a.date < b.date ? 1 : a.date > b.date ? -1 : 0,
    );
  });

  async function load(): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      cv.value = await fetchCv();
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to load CV";
    } finally {
      loading.value = false;
    }
  }

  return { cv, loading, error, isLoaded, timelineItems, load };
});
