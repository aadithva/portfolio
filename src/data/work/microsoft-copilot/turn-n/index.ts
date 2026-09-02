import type { WorkItem } from "@/types";

export const turnN: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "turn-n",
  title: "Longer conversations",
  description:
    "Notes on how follow-ups, corrections, and changing context affect a longer AI conversation.",
  label: "Conversation UX / follow-ups",
  year: "2025 to present",
  status: "draft",
  passwordProtected: true,
  confidentialityNote:
    "I have kept this to the design question and left out internal prompts, scenarios, and implementation details.",
  sections: [
    {
      type: "text",
      heading: "A good first turn can hide a fragile conversation",
      content:
        "A first answer does not show whether a longer conversation will hold together. People follow up, correct the assistant, and change direction while expecting relevant context to carry forward. This draft examines those later turns without describing internal scenarios.",
    },
    {
      type: "framework",
      label: "Later-turn questions",
      heading: "What should survive as the conversation gets longer?",
      content:
        "The open question is what context should carry forward, what should change, and how the interface should recover when the connection is unclear.",
      items: [
        {
          title: "Follow-up references",
          content:
            "Clarify what words like 'that' or 'the earlier file' point to.",
        },
        {
          title: "Updates and corrections",
          content:
            "Carry forward the constraints that still matter and replace the ones the person changes.",
        },
        {
          title: "Clarification",
          content:
            "Ask a useful question when a follow-up does not point clearly to earlier context.",
        },
      ],
    },
  ],
};
