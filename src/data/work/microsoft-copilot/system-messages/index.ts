import type { WorkItem } from "@/types";

export const systemMessages: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "system-messages",
  title: "System messages",
  description:
    "Designing the hidden instruction layer as product behaviour: tone, boundaries, recovery, and what the system should do when the happy path runs out.",
  label: "Agent behaviour / content systems",
  year: "2025–Present",
  status: "draft",
  passwordProtected: true,
  confidentialityNote:
    "Documentation in progress. No internal prompt text, policies, or confidential implementation details are published here.",
  sections: [
    {
      type: "text",
      heading: "The invisible interface still has users",
      content:
        "System messages sit behind the UI, but their decisions appear everywhere: how the assistant explains limits, asks for missing context, handles uncertainty, cites evidence, and recovers after a mistake. I want this page to document that work as interaction design rather than treating it as a mysterious block of prompt text.",
    },
    {
      type: "framework",
      label: "Behaviour layer",
      heading: "Instructions are only useful when their effects can be inspected",
      content:
        "The eventual case study will connect authored guidance to the behaviour a user actually experiences.",
      items: [
        {
          title: "Intent",
          content:
            "State the job the system is trying to do and the priorities that should survive edge cases.",
        },
        {
          title: "Boundaries",
          content:
            "Make limits and prohibited behaviour explicit without turning every response into defensive boilerplate.",
        },
        {
          title: "Recovery",
          content:
            "Describe what the assistant should do when context is missing, tools fail, or the user corrects it.",
        },
        {
          title: "Evaluation",
          content:
            "Pair instructions with scenarios and observable quality criteria so behaviour can be reviewed rather than merely hoped for.",
        },
      ],
    },
    {
      type: "image-full",
      images: ["/images/projects/microsoft-copilot/system-messages/hero.png"],
      caption: "System-message structure and behaviour examples — documentation in progress",
    },
  ],
};
