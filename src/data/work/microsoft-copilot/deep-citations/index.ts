import type { WorkItem } from "@/types";

export const deepCitations: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "deep-citations",
  title: "Following a citation",
  description:
    "Exploring how a reader can move from a generated claim into useful source context without losing their place in the answer.",
  label: "Citations / source context",
  year: "2025 to present",
  status: "documented",
  passwordProtected: true,
  confidentialityNote:
    "This public summary stays at the level of source context and reading flow. It leaves out internal screens, rollout details, and product data.",
  sections: [
    {
      type: "text",
      heading: "Opening a source is not the same as finding useful context",
      content:
        "A link can open the source and still leave the reader searching for the relevant context. Our design work looked at a more continuous path from the claim to a preview and then into the source, while keeping the answer available.",
    },
    {
      type: "framework",
      label: "Reading flow",
      heading: "From claim to source context",
      content:
        "The reader should be able to see where a claim came from, judge a short preview, and open the source only when needed.",
      items: [
        {
          title: "Claim",
          content:
            "Keep the source relationship visible beside the statement the reader is checking.",
        },
        {
          title: "Context",
          content:
            "Show a short excerpt or preview so the reader can judge whether the source is relevant.",
        },
        {
          title: "Open the source",
          content:
            "Let the reader continue into the source while keeping the answer available.",
        },
      ],
    },
    {
      type: "text",
      heading: "A polished answer can still be wrong",
      content:
        "A short preview can make a source easier to inspect without forcing the reader to abandon the answer. In a long file, it can help someone decide whether to keep reading.",
    },
  ],
};
