import type { WorkItem } from "@/types";

export const hackathons: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "hackathons",
  title: "Hackathons and internal builds",
  description:
    "Notes on small team experiments that sit outside the main Copilot case study.",
  label: "Internal experiments / prototypes",
  year: "2024 to present",
  status: "draft",
  passwordProtected: true,
  confidentialityNote:
    "I will keep this page in draft until each entry has clear team attribution and a public-safe artifact.",
  sections: [
    {
      type: "text",
      heading: "Not every experiment belongs in the product story",
      content:
        "Some internal experiments sit outside the main Copilot product work. I will include one here only when I can separate the team's work from my contribution and support the account with a public-safe artifact.",
    },
    {
      type: "framework",
      label: "Publication check",
      heading: "Each entry needs evidence and clear attribution",
      content:
        "The page should make it easy to see what the team did, what I did, and what source supports the account.",
      items: [
        {
          title: "Brief",
          content:
            "Describe the team's problem in public-safe terms.",
        },
        {
          title: "My part",
          content:
            "Describe my contribution without absorbing the team's work.",
        },
        {
          title: "Artifact",
          content:
            "Include one public-safe artifact that supports the account.",
        },
        {
          title: "Outcome",
          content:
            "Say what happened next only when public-safe evidence supports it.",
        },
      ],
    },
  ],
};
