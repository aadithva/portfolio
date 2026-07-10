import type { WorkItem } from "@/types";

export const turnN: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "turn-n",
  title: "Turn N",
  description:
    "The first answer gets the demo. Turn N gets the product: follow-ups, corrections, remembered context, and whether the conversation still makes sense later.",
  label: "Multi-turn conversation / continuity",
  year: "2025–Present",
  status: "draft",
  passwordProtected: true,
  confidentialityNote:
    "Documentation in progress. This page describes the design problem without exposing internal prompts, scenarios, or implementation details.",
  sections: [
    {
      type: "text",
      heading: "A good first turn can hide a fragile conversation",
      content:
        "AI demos are usually kind to the first answer. Real use is not. People refine the request, refer to something from three turns ago, change direction, correct the assistant, and expect the system to understand which parts should remain. Turn N is the chapter for that less photogenic but more important work.",
    },
    {
      type: "framework",
      label: "Continuity checks",
      heading: "What should survive as the conversation gets longer?",
      content:
        "The case study will collect scenarios, decisions, and evaluation criteria around multi-turn behaviour.",
      items: [
        {
          title: "Reference",
          content:
            "Resolve what “that,” “the second one,” or “use the earlier file” actually points to.",
        },
        {
          title: "Correction",
          content:
            "Let new information update the conversation without repeating the same mistake in a nicer sentence.",
        },
        {
          title: "Constraint",
          content:
            "Carry forward the rules that still matter and release the ones the user has intentionally changed.",
        },
        {
          title: "Recovery",
          content:
            "When continuity fails, ask a useful clarifying question instead of confidently inventing the missing link.",
        },
      ],
    },
    {
      type: "image-full",
      images: ["/images/projects/microsoft-copilot/turn-n/hero.png"],
      caption: "Multi-turn scenarios and behaviour comparisons — documentation in progress",
    },
  ],
};
