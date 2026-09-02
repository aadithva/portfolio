import type { WorkItem } from "@/types";

export const meetings: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "meetings",
  title: "Meetings",
  description:
    "Notes on source context in meeting responses and the line between interface, capability, and model problems.",
  label: "Meeting response UX / draft",
  year: "2025 to present",
  status: "draft",
  passwordProtected: true,
  confidentialityNote:
    "I have left out internal screens, metrics, names, and implementation details.",
  sections: [
    {
      type: "text",
      heading: "Meeting sources change over time",
      content:
        "A document sits still. A meeting unfolds as people speak, correct themselves, and make decisions. A useful recap needs enough source context for someone to understand what happened and return to the original material when needed.",
    },
    {
      type: "text",
      heading: "First decide what kind of problem it is",
      content:
        "Meeting responses can fail because of the interface, a missing capability, or the model output. A quality finding does not automatically call for a new component. The team needs to name the problem before choosing who should work on it.",
    },
    {
      type: "framework",
      label: "Interface questions",
      heading: "What the reader needs to understand",
      content:
        "For now, I am keeping this page to three questions about state, source context, and lists.",
      items: [
        {
          title: "Clarify the meeting state",
          content:
            "Show enough context for someone to understand what kind of meeting source they are looking at and what it can contain.",
        },
        {
          title: "Return to the source",
          content:
            "Give a meeting reference a clear route back to the source context available in the product.",
        },
        {
          title: "Explain the list",
          content:
            "When several meetings appear together, explain why each result is present and what the reader can do next.",
        },
      ],
    },
    {
      type: "text",
      heading: "Not every quality issue needs an interface change",
      content:
        "Some findings point to capability or model behaviour rather than presentation. Good design review includes knowing when another discipline needs to lead the next step. I am still documenting this chapter, so it stays at that high level for now.",
    },
  ],
};
