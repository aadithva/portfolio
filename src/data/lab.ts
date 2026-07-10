import labData from "./lab.json";
import type { LabProject } from "@/types";

export const labProjects: LabProject[] = labData.projects as LabProject[];
export const showcaseLabProjects: LabProject[] = labProjects
  .filter((project) => project.showcase)
  .sort((a, b) => (a.rank ?? Number.MAX_SAFE_INTEGER) - (b.rank ?? Number.MAX_SAFE_INTEGER));

// Display order of categories in the Lab.
export const labCategoryOrder = [
  "Prototypes",
  "Tools & CLIs",
  "Integrations",
  "Owly",
];

export function getLabProject(slug: string): LabProject | undefined {
  return labProjects.find((p) => p.slug === slug);
}

export function getAllLabSlugs(): string[] {
  return labProjects.map((p) => p.slug);
}

export function getShowcaseLabProjects(): LabProject[] {
  return showcaseLabProjects;
}

export function getLabByCategory(): { category: string; projects: LabProject[] }[] {
  const groups = new Map<string, LabProject[]>();
  for (const p of labProjects) {
    if (!groups.has(p.category)) groups.set(p.category, []);
    groups.get(p.category)!.push(p);
  }
  const ordered = [...labCategoryOrder.filter((c) => groups.has(c))];
  for (const c of groups.keys()) if (!ordered.includes(c)) ordered.push(c);
  return ordered.map((category) => ({ category, projects: groups.get(category)! }));
}

export function getAdjacentLab(slug: string): {
  prev: LabProject | null;
  next: LabProject | null;
} {
  const project = getLabProject(slug);
  const collection = project?.showcase ? showcaseLabProjects : labProjects;
  const i = collection.findIndex((p) => p.slug === slug);
  return {
    prev: i > 0 ? collection[i - 1] : null,
    next: i >= 0 && i < collection.length - 1 ? collection[i + 1] : null,
  };
}
