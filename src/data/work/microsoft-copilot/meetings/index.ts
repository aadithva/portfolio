import type { WorkItem } from "@/types";

export const meetings: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "meetings",
  title: "Meetings",
  description:
    "A dedicated chapter for meeting-related response UX: recaps, highlights, source identity, and the awkward question of what still matters after the call ends.",
  label: "Meeting intelligence / response UX",
  year: "2025–Present",
  status: "draft",
  passwordProtected: true,
  confidentialityNote:
    "Documentation in progress. This page currently sets the public-safe frame; product-specific screens and internal details are not included.",
  sections: [
    {
      type: "text",
      heading: "Meetings are sources with a timeline",
      content:
        "A document sits still. A meeting unfolds through speakers, decisions, corrections, and unfinished actions. Designing AI experiences around that material means preserving who said what, distinguishing a recap from evidence, and helping someone recover the moment that made a summary meaningful.",
    },
    {
      type: "framework",
      label: "What belongs in this chapter",
      heading: "From a long call to useful, inspectable context",
      content:
        "This folder is ready for the individual workstreams and artifacts as they are cleared for the portfolio.",
      items: [
        {
          title: "Recap and highlights",
          content:
            "How the system chooses, groups, and presents the moments worth returning to.",
        },
        {
          title: "Meeting as a source",
          content:
            "How a meeting is identified alongside files, messages, email, and web references.",
        },
        {
          title: "Attribution",
          content:
            "How speakers, timestamps, and surrounding conversation help a generated statement remain checkable.",
        },
        {
          title: "Follow-through",
          content:
            "How decisions and actions survive the transition from the meeting into the next piece of work.",
        },
      ],
    },
    {
      type: "image-full",
      images: ["/images/projects/microsoft-copilot/meetings/hero.png"],
      caption: "Meeting response UX and source states — documentation in progress",
    },
  ],
};
