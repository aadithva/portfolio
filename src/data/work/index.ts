import type { WorkItem } from "@/types";
import { citations } from "./microsoft-copilot/citations";
import { deepCitations } from "./microsoft-copilot/deep-citations";
import { meetings } from "./microsoft-copilot/meetings";
import { systemMessages } from "./microsoft-copilot/system-messages";
import { turnN } from "./microsoft-copilot/turn-n";
import { hackathons } from "./microsoft-copilot/hackathons";
import { daoDenver } from "./daolens/dao-denver";

export const workItems: WorkItem[] = [
  citations,
  deepCitations,
  meetings,
  systemMessages,
  turnN,
  hackathons,
  daoDenver,
];

export function getWorkItemsFor(parentSlug: string): WorkItem[] {
  return workItems.filter((item) => item.parentSlug === parentSlug);
}

export function getWorkItem(parentSlug: string, slug: string): WorkItem | undefined {
  return workItems.find((item) => item.parentSlug === parentSlug && item.slug === slug);
}

export function getAdjacentWorkItems(item: WorkItem): {
  prev: WorkItem | null;
  next: WorkItem | null;
} {
  const siblings = getWorkItemsFor(item.parentSlug);
  const index = siblings.findIndex((candidate) => candidate.slug === item.slug);
  return {
    prev: index > 0 ? siblings[index - 1] : null,
    next: index >= 0 && index < siblings.length - 1 ? siblings[index + 1] : null,
  };
}
