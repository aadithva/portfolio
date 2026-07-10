import { aboutApproaches, aboutBio, aboutLead, aboutMilestones } from "@/data/about";
import { adventureRoute, adventureStory } from "@/data/adventures";
import { agentGroundingChunks } from "@/data/agentGrounding";
import { showcaseLabProjects } from "@/data/lab";
import { projects } from "@/data/projects";
import { siteConfig } from "@/data/siteConfig";
import { workItems } from "@/data/work";
import type {
  CaseStudySection,
  CompanionContextChunk,
  CompanionContextDocument,
} from "@/types";

export const companionSuggestions = [
  "What kind of problems does Aadith solve?",
  "What does he work on at Microsoft?",
  "Why did he start Owly?",
  "Which Lab project should I open first?",
];

const clean = (parts: Array<string | undefined | null>): string =>
  parts.filter((part): part is string => Boolean(part?.trim())).join("\n\n");

const sectionText = (section: CaseStudySection): string =>
  clean([
    section.label,
    section.heading,
    section.content,
    section.items
      ?.map((item) => `${item.title}: ${item.content}`)
      .join("\n"),
    section.stats
      ?.map((stat) => `${stat.label}: ${stat.value}`)
      .join("\n"),
    section.quote,
    section.attribution,
  ]);

const source = (
  chunk: CompanionContextChunk
): CompanionContextChunk => chunk;

export function buildCompanionContext(): CompanionContextDocument {
  const profileChunks: CompanionContextChunk[] = [
    source({
      id: "profile-overview",
      title: "About Aadith",
      path: "/about",
      category: "Profile",
      tags: [
        "aadith",
        "profile",
        "bio",
        "microsoft",
        "owly",
        "designer",
        "founder",
        "kerala",
        "iit guwahati",
      ],
      body: clean([
        siteConfig.bio,
        siteConfig.tagline,
        ...aboutBio,
        aboutLead,
      ]),
    }),
    source({
      id: "working-style",
      title: "How Aadith works",
      path: "/about",
      category: "Working style",
      tags: [
        "process",
        "working style",
        "research",
        "systems",
        "prototyping",
        "accessibility",
        "collaboration",
      ],
      body: aboutApproaches
        .map((approach) => `${approach.title}: ${approach.body}`)
        .join("\n\n"),
    }),
    source({
      id: "timeline",
      title: "Aadith's timeline",
      path: "/about",
      category: "Profile",
      tags: ["timeline", "education", "career", "iit", "microsoft", "owly"],
      body: aboutMilestones
        .map(
          (milestone) =>
            `${milestone.year} - ${milestone.title}: ${milestone.description}`
        )
        .join("\n\n"),
    }),
    source({
      id: "adventures",
      title: "Cycling across India",
      path: "/adventures",
      category: "Adventure",
      tags: [
        "cycling",
        "india",
        "kerala",
        "kashmir",
        "kanyakumari",
        "ride for unity",
        "endurance",
      ],
      body: clean([
        ...adventureStory,
        `Route: ${adventureRoute.start} to ${adventureRoute.finish}. Distance: ${adventureRoute.distance}. Time: ${adventureRoute.time}.`,
      ]),
    }),
    source({
      id: "contact",
      title: "Contact Aadith",
      path: "/contact",
      category: "Contact",
      tags: ["contact", "email", "linkedin", "behance", "collaborate", "hire"],
      body: `Email: ${siteConfig.email}\nLinkedIn: ${siteConfig.social.linkedin}\nBehance: ${siteConfig.social.behance}`,
    }),
  ];

  const workChunks = projects.map((project) =>
    source({
      id: `work-${project.slug}`,
      title: project.title,
      path: `/work/${project.slug}`,
      category: "Work",
      tags: [
        project.slug,
        project.title,
        project.client,
        project.category,
        project.role,
        project.year,
      ],
      body: clean([
        project.description,
        `Role: ${project.role}. Period: ${project.year}. Context: ${project.client}.`,
        project.confidentialityNote,
        ...project.sections.map(sectionText),
      ]),
    })
  );

  const workItemChunks = workItems.map((item) =>
    source({
      id: `work-${item.parentSlug}-${item.slug}`,
      title: item.title,
      path: `/work/${item.parentSlug}/${item.slug}`,
      category: "Focused work",
      tags: [
        item.parentSlug,
        item.slug,
        item.title,
        item.label,
        item.year,
        item.status,
      ],
      body: clean([
        item.description,
        `Area: ${item.label}. Period: ${item.year}. Status: ${item.status}.`,
        item.confidentialityNote,
        ...item.sections.map(sectionText),
      ]),
    })
  );

  const labChunks = showcaseLabProjects.map((project) =>
    source({
      id: `lab-${project.slug}`,
      title: project.title,
      path: `/lab/${project.slug}`,
      category: "Lab",
      tags: [
        project.slug,
        project.title,
        project.theme,
        project.category,
        project.status,
        ...project.tech,
      ].filter((tag): tag is string => Boolean(tag)),
      body: clean([
        project.tagline,
        project.problem,
        project.portfolio_signal,
        project.story,
        project.evidence?.join("\n"),
        project.limitations?.map((item) => `Limitation: ${item}`).join("\n"),
        project.learning,
        `Built with: ${project.tech.join(", ")}.`,
      ]),
    })
  );

  return {
    version: "2",
    owner: siteConfig.name,
    boundary:
      "Public-safe portfolio and biographical material only. Never disclose private health, financial, relationship, family, compensation, manager, promotion, account, third-party, or unpublished Microsoft details.",
    chunks: [
      ...profileChunks,
      ...agentGroundingChunks,
      ...workChunks,
      ...workItemChunks,
      ...labChunks,
    ],
  };
}
