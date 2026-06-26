/**
 * API types — mirror of the DRF serializers in backend/apps/cv/serializers.py.
 * Phase 3 will replace this with openapi-typescript generation from /api/schema/.
 */

export interface User {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
}

export interface MediaAsset {
  id: number;
  url: string;
  alt_text: string;
  kind: "image" | "document" | "video";
  order: number;
}

export interface Technology {
  id: number;
  name: string;
  slug: string;
  category: string;
  order: number;
}

export interface Skill {
  id: number;
  name: string;
  name_de: string;
  level: number;
  technologies: Technology[];
  order: number;
}

export interface SkillCategory {
  id: number;
  name: string;
  name_de: string;
  slug: string;
  skills: Skill[];
  order: number;
}

export interface Experience {
  id: number;
  role: string;
  role_de: string;
  company: string;
  location: string;
  start_date: string;
  end_date: string | null;
  description: string;
  description_de: string;
  technologies: Technology[];
  media: MediaAsset | null;
  order: number;
  is_published: boolean;
}

export interface Education {
  id: number;
  degree: string;
  degree_de: string;
  institution: string;
  location: string;
  start_date: string;
  end_date: string | null;
  description: string;
  description_de: string;
  technologies: Technology[];
  media: MediaAsset | null;
  order: number;
  is_published: boolean;
}

export interface Certificate {
  id: number;
  experience: number | null;
  education: number | null;
  name: string;
  name_de: string;
  issuer: string;
  issue_date: string;
  description: string;
  description_de: string;
  technologies: Technology[];
  media: MediaAsset | null;
  order: number;
  is_published: boolean;
}

export interface Project {
  id: number;
  name: string;
  name_de: string;
  slug: string;
  summary: string;
  summary_de: string;
  description: string;
  description_de: string;
  url: string;
  repo_url: string;
  technologies: Technology[];
  media: MediaAsset[];
  order: number;
  is_published: boolean;
}

export interface SocialLink {
  id: number;
  platform: string;
  label: string;
  url: string;
  order: number;
  is_published?: boolean;
}

export interface TimelineEntry {
  id: number;
  date: string;
  kind: "milestone" | "award" | "transition" | "other";
  title: string;
  title_de: string;
  description: string;
  description_de: string;
  order: number;
  is_published: boolean;
}

// ---------------------------------------------------------------------------
// Paginated list response shape (DRF PageNumberPagination)
// ---------------------------------------------------------------------------
export interface Page<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ---------------------------------------------------------------------------
// Write payloads (flat, FK fields as IDs)
// ---------------------------------------------------------------------------

export type ExperienceWrite = Omit<Experience, "technologies" | "media"> & {
  technologies: number[];
  media?: number | null;
  person?: number;
};
export type EducationWrite = Omit<Education, "technologies" | "media"> & {
  technologies: number[];
  media?: number | null;
  person?: number;
};
export type CertificateWrite = Omit<Certificate, "media" | "technologies"> & {
  technologies: number[];
  media: number | null;
  person?: number;
};
export type ProjectWrite = Omit<Project, "technologies" | "media"> & {
  technologies: number[];
  media: number[];
  person?: number;
};
export type TimelineEntryWrite = TimelineEntry & { person?: number };
export type TechnologyWrite = Technology & { is_published: boolean };
export type SkillCategoryWrite = Omit<SkillCategory, "skills"> & { is_published: boolean };
export type SkillWrite = Omit<Skill, "technologies"> & {
  technologies: number[];
  category: number;
  is_published: boolean;
};
export type SocialLinkWrite = SocialLink & { person?: number; is_published: boolean };
export interface PersonWrite {
  id?: number;
  slug: string;
  first_name: string;
  last_name: string;
  title: string;
  title_de: string;
  email: string;
  phone: string;
  location: string;
  address: string;
  zivilstand: string;
  zivilstand_de: string;
  date_of_birth: string | null;
  summary: string;
  summary_de: string;
  photo: number | null;
  active_funny_theme?: string;
  order: number;
  is_published: boolean;
}

export interface Cv {
  id: number;
  slug: string;
  first_name: string;
  last_name: string;
  full_name: string;
  title: string;
  title_de: string;
  email: string;
  phone: string;
  location: string;
  address: string;
  zivilstand: string;
  zivilstand_de: string;
  date_of_birth: string | null;
  access_granted: boolean;
  summary: string;
  summary_de: string;
  photo: MediaAsset | null;
  active_funny_theme: string;
  experiences: Experience[];
  educations: Education[];
  certificates: Certificate[];
  projects: Project[];
  social_links: SocialLink[];
  timeline_entries: TimelineEntry[];
  skill_categories: SkillCategory[];
}

export interface AccessKey {
  id: number;
  person: number;
  token: string;
  label: string;
  expires_at: string;
  is_active: boolean;
  created_at: string;
  is_valid: boolean;
}

export interface AccessKeyWrite {
  person: number;
  label: string;
  expires_at: string;
  is_active: boolean;
}

export interface Readme {
  id: number;
  name: string;
  content: string;
  content_de: string;
  version: string;
  access_key: number | null;
  access_url: string;
  expires_display: string;
  updated_display: string;
  order: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReadmeWrite {
  id?: number;
  person?: number;
  name: string;
  content: string;
  content_de: string;
  version: string;
  access_key: number | null;
  order: number;
  is_published: boolean;
}
