import type { WorkItem } from "@/types";

export const citations: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "citations",
  title: "Citations",
  description:
    "Making source identity visible inside an AI answer without turning every paragraph into a wall of references.",
  label: "Response UX / source grounding",
  year: "2025–Present",
  status: "documented",
  passwordProtected: true,
  confidentialityNote:
    "Public-safe summary: internal product visuals, metrics, names, and implementation details are intentionally omitted.",
  sections: [
    {
      type: "text",
      heading: "A tiny component with system-sized consequences",
      content:
        "A citation has to do several jobs at once. It should tell a reader that evidence exists, help them recognise the source, stay close to the claim, and avoid interrupting the answer so often that the answer becomes hard to read. My work explored that balance across inline references, multiple-source cases, hover states, accessibility, dark mode, and the transition into deeper source context.",
    },
    {
      type: "framework",
      label: "Design questions",
      heading: "Readable enough to continue. Verifiable enough to trust.",
      content:
        "The useful design work lived in the trade-offs, not in decorating a pill.",
      items: [
        {
          title: "Recognition",
          content:
            "Use a source name, type, or familiar marker so a reference means more than an abstract number.",
        },
        {
          title: "Proximity",
          content:
            "Keep evidence close enough to the claim that verification feels like a continuation of reading, not a separate research task.",
        },
        {
          title: "Escalation",
          content:
            "Let compact references open into excerpts, previews, and exact source context as the user asks for more.",
        },
        {
          title: "Edge cases",
          content:
            "Design for truncation, multiple sources, lists, tables, keyboard access, contrast, and narrow layouts before calling the component finished.",
        },
      ],
    },
    {
      type: "image-full",
      images: ["/images/projects/microsoft-copilot/citations/hero.png"],
      caption: "Citation evolution and interaction states — public-safe visuals to be added",
    },
    {
      type: "text",
      heading: "The part I keep returning to",
      content:
        "The best citation is neither invisible nor dominant. It appears when confidence needs support, then gets out of the way. That sounds simple until one answer contains files, web pages, messages, meetings, mixed source mappings, and a person using only a keyboard.",
    },
  ],
};
