// Shared types for the portfolio site (ported from the original Next.js app).

export interface Project {
  slug: string;
  title: string;
  description: string;
  role: string;
  year: string;
  client: string;
  category: string;
  thumbnail: string;
  featured: boolean;
  passwordProtected?: boolean;
  confidentialityNote?: string;
  sections: CaseStudySection[];
}

export interface WorkItem {
  parentSlug: string;
  slug: string;
  title: string;
  description: string;
  label: string;
  year: string;
  status: "documented" | "draft" | "growing";
  passwordProtected?: boolean;
  confidentialityNote?: string;
  sections: CaseStudySection[];
}

export type CaseStudySectionType =
  | "text"
  | "image-full"
  | "image-grid"
  | "stats"
  | "quote"
  | "framework";

export interface CaseStudySection {
  type: CaseStudySectionType;
  label?: string;
  content?: string;
  heading?: string;
  images?: string[];
  caption?: string;
  stats?: { label: string; value: string }[];
  quote?: string;
  attribution?: string;
  columns?: 2 | 3;
  items?: { title: string; content: string }[];
}

export interface NavLink {
  label: string;
  href: string;
}

export interface SiteConfig {
  name: string;
  title: string;
  description: string;
  tagline: string;
  bio: string;
  email: string;
  url: string;
  social: {
    linkedin: string;
    behance: string;
  };
}

// A "vibe-coded" project in the Lab — discovered on disk, written up, and screenshotted.
export interface LabProject {
  slug: string;
  title: string;
  tagline: string;
  showcase?: boolean;
  rank?: number;
  theme?: string;
  problem?: string;
  portfolio_signal?: string;
  evidence?: string[];
  limitations?: string[];
  learning?: string;
  when: string;
  built_with: string;
  category: string;
  status: string;
  ui_type: string;
  story: string;
  capabilities: string[];
  tech: string[];
  runnable: string;
  run_cmd: string;
  port: number | null;
  dev_kind: string;
  needs_secrets: boolean;
  routes: string[];
  repo_url: string | null;
}
