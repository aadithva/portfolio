import type { WorkItem } from "@/types";

export const deepCitations: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "deep-citations",
  title: "Deep citations",
  description:
    "Taking someone from a generated claim to the exact place in a long source document, without losing the conversation they came from.",
  label: "Verification / document preview",
  year: "2025–Present",
  status: "documented",
  passwordProtected: true,
  confidentialityNote:
    "Public-safe summary: the interaction model is described at a high level; confidential screens, rollout details, and internal data are excluded.",
  sections: [
    {
      type: "text",
      heading: "Opening a file is not the same as finding the evidence",
      content:
        "A normal link can take someone to a document and still leave them hunting through dozens of pages. Deep citation explored a more continuous verification path: preserve the answer, open the source beside it, move to the relevant page or section, and make the cited material easier to locate.",
    },
    {
      type: "framework",
      label: "Interaction model",
      heading: "Claim → context → exact evidence",
      content:
        "Each layer should answer the next question without forcing a reset.",
      items: [
        {
          title: "Claim",
          content:
            "Start from the statement the user is already reading and keep its source relationship visible.",
        },
        {
          title: "Context",
          content:
            "Use an excerpt or preview to show enough surrounding material for the user to judge whether opening the source is worthwhile.",
        },
        {
          title: "Exact location",
          content:
            "Navigate to the relevant page, section, table, chart, or source fragment rather than dropping the reader at the document cover.",
        },
        {
          title: "Return path",
          content:
            "Keep the conversation available so verification does not destroy the task the user was trying to complete.",
        },
      ],
    },
    {
      type: "image-full",
      images: ["/images/projects/microsoft-copilot/deep-citations/hero.png"],
      caption: "Side-by-side source verification flow — public-safe visuals to be added",
    },
    {
      type: "text",
      heading: "Why this mattered to me",
      content:
        "The interaction treats trust as a journey rather than a badge. An AI answer can be wrong with beautiful typography. The interface becomes more useful when it reduces the cost of checking, especially in long enterprise files where the evidence may be a paragraph, a slide, a table, or several fragments working together.",
    },
  ],
};
