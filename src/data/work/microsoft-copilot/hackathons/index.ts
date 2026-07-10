import type { WorkItem } from "@/types";

export const hackathons: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "hackathons",
  title: "Hackathons & internal builds",
  description:
    "Fast experiments, culture-making, and small internal tools — useful work that does not belong inside the main product case study.",
  label: "Rapid prototyping / culture",
  year: "2024–Present",
  status: "growing",
  passwordProtected: true,
  confidentialityNote:
    "Growing collection. Individual projects will be added only when names, collaborators, ownership, and public-safe artifacts are confirmed.",
  sections: [
    {
      type: "text",
      heading: "A folder for the work that happened sideways",
      content:
        "Hackathons and internal builds gave me room to move between product prototypes, storytelling, brand, and culture. The outcomes range from practical tools to visual systems and event moments. They deserve their own chapter because squeezing them into the Copilot product narrative makes both stories less clear.",
    },
    {
      type: "framework",
      label: "Documentation rule",
      heading: "Every project should earn its own page",
      content:
        "I will add individual hackathon entries here as the evidence is organised. Each one needs the same basic honesty.",
      items: [
        {
          title: "Brief",
          content:
            "What problem or internal moment the team was trying to address.",
        },
        {
          title: "My part",
          content:
            "What I personally designed, built, wrote, organised, or helped ship — with collaborators named.",
        },
        {
          title: "Artifact",
          content:
            "A public-safe screenshot, prototype, identity, video frame, or implementation detail that proves the work existed.",
        },
        {
          title: "Afterlife",
          content:
            "Whether the idea shipped, taught us something, won recognition, became a resource, or simply ended when the hackathon did.",
        },
      ],
    },
    {
      type: "image-full",
      images: ["/images/projects/microsoft-copilot/hackathons/hero.png"],
      caption: "Hackathon projects and internal builds — collection in progress",
    },
  ],
};
