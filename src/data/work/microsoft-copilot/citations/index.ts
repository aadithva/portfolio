import type { WorkItem } from "@/types";

export const citations: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "citations",
  title: "Citations",
  description:
    "Designing citation patterns that keep source identity near the relevant claim without crowding the answer.",
  label: "Response UX / citations",
  year: "2025 to present",
  status: "documented",
  passwordProtected: true,
  confidentialityNote:
    "This public summary leaves out internal visuals, metrics, names, and implementation details.",
  sections: [
    {
      type: "text",
      heading: "A citation has to help without taking over the answer",
      content:
        "A citation needs to show that a claim has a source and help the reader recognise it without interrupting the answer. My part was working through inline references and the move into more source context with the wider team. Accessibility review sat alongside the visual work.",
    },
    {
      type: "framework",
      label: "Design questions",
      heading: "Keep the answer readable and the source easy to inspect",
      content:
        "Most of the work was deciding what to show beside the claim and what to leave for the next step.",
      items: [
        {
          title: "Show the source",
          content:
            "Use a readable source name or type instead of relying on a number alone.",
        },
        {
          title: "Keep it near the claim",
          content:
            "Place the reference near the text it supports so checking the source does not become a separate hunt.",
        },
        {
          title: "Add context when asked",
          content:
            "Let a compact reference open into a short preview, with a route to the source when the reader needs more.",
        },
        {
          title: "Test the awkward cases",
          content:
            "Review how the pattern behaves with more than one source, keyboard navigation, and limited space.",
        },
      ],
    },
  ],
};
