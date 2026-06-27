import { http } from "./client";
import type {
  AccessKey,
  AccessKeyWrite,
  Certificate,
  CertificateWrite,
  Cv,
  Education,
  EducationWrite,
  Experience,
  ExperienceWrite,
  MediaAsset,
  Page,
  PersonWrite,
  Project,
  ProjectWrite,
  Readme,
  ReadmeWrite,
  Skill,
  SkillCategory,
  SkillCategoryWrite,
  SkillWrite,
  SocialLink,
  SocialLinkWrite,
  Technology,
  TechnologyWrite,
  TimelineEntry,
  TimelineEntryWrite,
} from "./types";

type Id = number;

function crud<T, W = T>(base: string) {
  return {
    async list(): Promise<Page<T>> {
      const { data } = await http.get<Page<T>>(`${base}/`);
      return data;
    },
    async retrieve(id: Id): Promise<T> {
      const { data } = await http.get<T>(`${base}/${id}/`);
      return data;
    },
    async create(payload: Partial<W>): Promise<T> {
      const { data } = await http.post<T>(`${base}/`, payload);
      return data;
    },
    async update(id: Id, payload: Partial<W>): Promise<T> {
      const { data } = await http.patch<T>(`${base}/${id}/`, payload);
      return data;
    },
    async destroy(id: Id): Promise<void> {
      await http.delete(`${base}/${id}/`);
    },
    async reorder(ids: Id[]): Promise<void> {
      await Promise.all(ids.map((id, index) => http.patch(`${base}/${id}/`, { order: index })));
    },
  };
}

export const experienceApi = crud<Experience, ExperienceWrite>("/experiences");
export const educationApi = crud<Education, EducationWrite>("/educations");
export const certificateApi = crud<Certificate, CertificateWrite>("/certificates");
export const projectApi = crud<Project, ProjectWrite>("/projects");
export const timelineApi = crud<TimelineEntry, TimelineEntryWrite>("/timeline");
export const technologyApi = crud<Technology, TechnologyWrite>("/technologies");
export const skillCategoryApi = crud<SkillCategory, SkillCategoryWrite>("/skill-categories");
export const skillApi = crud<Skill, SkillWrite>("/skills");
export const socialLinkApi = crud<SocialLink, SocialLinkWrite>("/social-links");

export const personApi = {
  async retrieve(): Promise<Cv> {
    // Admin endpoint returns unredacted data (staff-only, no ?key= needed).
    const { data } = await http.get<Cv>(`/admin/cv/`);
    return data;
  },
  async update(slug: string, payload: Partial<PersonWrite>): Promise<Cv> {
    const { data } = await http.patch<Cv>(`/cv/${slug}/`, payload);
    return data;
  },
};

export const accessKeyApi = crud<AccessKey, AccessKeyWrite>("/access-keys");

export const cvApi = {
  /**
   * Export the full CV as a PDF (staff-only, normal theme). `baseUrl` is the
   * visitor-facing origin — the backend's request Host is the internal proxy,
   * so the client supplies the real one (mirrors `readmeApi.pdf`).
   */
  async pdf(lang: "en" | "de", baseUrl: string): Promise<Blob> {
    const { data } = await http.get<Blob>(`/cv/pdf/`, {
      params: { lang, base_url: baseUrl },
      responseType: "blob",
    });
    return data;
  },
};

export const readmeApi = {
  ...crud<Readme, ReadmeWrite>("/admin/readmes"),
  /**
   * Export a README as PDF. `svgs` are the client-rendered Mermaid diagrams;
   * `baseUrl` is the visitor-facing origin (the backend's request Host is the
   * internal proxy target, so the client supplies the real one).
   */
  async pdf(
    id: Id,
    lang: "en" | "de",
    svgs: string[],
    baseUrl: string,
    doc: "readme" | "letter" = "readme",
  ): Promise<Blob> {
    const { data } = await http.post<Blob>(
      `/admin/readmes/${id}/pdf/`,
      { lang, svgs, base_url: baseUrl, doc },
      { responseType: "blob" },
    );
    return data;
  },
};

export async function uploadMedia(file: File): Promise<MediaAsset> {
  const form = new FormData();
  form.append("file", file);
  form.append("kind", file.type.startsWith("image/") ? "image" : "document");
  const { data } = await http.post<MediaAsset>("/media-assets/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
