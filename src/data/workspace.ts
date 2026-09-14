import { aboutBio, aboutLead, aboutMilestones } from "./about";
import { expeditionsIntro } from "./expeditions";
import { showcaseLabProjects } from "./lab";
import { projects } from "./projects";
import { siteConfig } from "./siteConfig";
import { writingNotes } from "./writing";
import { optimizedProjectPreview } from "./projectPreviews";

export type WorkspaceSection =
  | "work"
  | "about"
  | "writing"
  | "achievements"
  | "expeditions"
  | "experiments"
  | "contact"
  | "design"
  | "play";

export interface WorkspaceSectionContent {
  id: WorkspaceSection;
  label: string;
  objectLabel: string;
  kicker: string;
  title: string;
  description: string;
  href: string;
}

export interface WorkspaceProject {
  title: string;
  description: string;
  href: string;
  image: string;
  year: string;
  category: string;
}

export interface WorkspaceAchievement {
  id: "iitg-degree" | "ride-for-unity";
  title: string;
  description: string;
  year: string;
  image: string;
  href: string;
  certificate?: boolean;
  imageWidth?: number;
  imageHeight?: number;
}

/** Content and destinations are independent of scene meshes and camera logic. */
export const workspaceSections: WorkspaceSectionContent[] = [
  {
    id: "work",
    label: "Work",
    objectLabel: "Monitor",
    kicker: "On the monitor",
    title: "A few things I've worked on.",
    description:
      "AI products, early startups, and the decisions that make a complicated interface easier to use.",
    href: "/work",
  },
  {
    id: "about",
    label: "About",
    objectLabel: "Pegboard",
    kicker: "Pinned to the board",
    title: "Hello, I'm Aadith.",
    description: siteConfig.bio,
    href: "/about",
  },
  {
    id: "writing",
    label: "Writing",
    objectLabel: "Books & journals",
    kicker: "From the notebook",
    title: "Things I'm thinking through.",
    description:
      "Notes on AI in product design and the small messages that help a conversation make sense.",
    href: "/writing",
  },
  {
    id: "achievements",
    label: "Achievements",
    objectLabel: "Certificates, trophies & medal",
    kicker: "On the wall and shelf",
    title: "A few milestones.",
    description:
      "Some moments from the journey, in design and away from the desk.",
    href: "/achievements",
  },
  {
    id: "expeditions",
    label: "Expeditions",
    objectLabel: "Wall-mounted bicycle",
    kicker: "Away from the desk",
    title: "Across India, twice.",
    description: expeditionsIntro,
    href: "/expeditions",
  },
  {
    id: "experiments",
    label: "Experiments",
    objectLabel: "Sticker-covered laptop",
    kicker: "Open on the laptop",
    title: "Small builds. Useful questions.",
    description:
      "Working prototypes for reviewing AI output, mapping behaviour, and connecting Figma with code. Each project includes its current state and limits.",
    href: "/lab",
  },
  {
    id: "contact",
    label: "Contact",
    objectLabel: "Contact card",
    kicker: "Keep in touch",
    title: "Pull up a chair.",
    description:
      "Building an AI product or a creative tool? Curious about Owly? I'd like to hear from you. Design and cycling conversations are welcome too.",
    href: "/contact",
  },
  {
    id: "design",
    label: "Design tools",
    objectLabel: "Yellow Figma box",
    kicker: "Inside the yellow box",
    title: "Tools for the work between screens.",
    description:
      "A Figma bridge, a canvas for agent behaviour, and a small library of conversation patterns.",
    href: "/lab",
  },
  {
    id: "play",
    label: "A small distraction",
    objectLabel: "Controller",
    kicker: "One side quest",
    title: "Find the hidden stickers.",
    description:
      "Two stickers on the laptop have a little extra behind them. Head back to the desk and take a look.",
    href: "/lab",
  },
];

// Keep the existing /work routes, including their access gates. Never copy
// protected case-study sections into the scene or a browser-readable data file.
// The missing Copilot thumbnail is deliberately omitted until a public image
// is supplied. The other paths are existing, verified portfolio assets.
// Public case imagery shared with the work index. Protected case sections stay private.
const publicProjectPreviews: Record<string, string> = {
  "owly-studio": "/shots/owly-website/owly-website__home-desktop-hero.png",
  "daolens": "/images/projects/dao-denver-cover.png",
};
export const workspaceProjects: WorkspaceProject[] = projects.map((project) => ({
  title: project.title,
  description: project.description,
  href: `/work/${project.slug}`,
  image: project.slug === "microsoft-copilot" ? "" : optimizedProjectPreview(publicProjectPreviews[project.slug] ?? project.thumbnail),
  year: project.year,
  category: project.category,
}));

// Only screenshots already published in the Lab are used as preview imagery.
// These explicit URLs keep this module safe to import into the scene runtime.
const labPreviewImages: Record<string, string> = {
  "behavior-diff": "/shots/behavior-diff/behavior-diff__home-desktop-hero.png",
  "system-messages-site":
    "/shots/system-messages-site/system-messages-site__home-desktop-hero.png",
  "agent-canvas": "/shots/agent-canvas/agent-canvas__home-desktop-hero.png",
  "conversation-pattern-library":
    "/shots/conversation-pattern-library/conversation-pattern-library__home-desktop-hero.png",
};

export const workspaceExperiments: WorkspaceProject[] = showcaseLabProjects.map(
  (project) => ({
    title: project.title,
    description: project.tagline,
    href: `/lab/${project.slug}`,
    image: labPreviewImages[project.slug] ?? "",
    year: project.when,
    category: project.theme ?? project.category,
  }),
);

const designExperimentSlugs = new Set([
  "figma-redline-plugin",
  "agent-canvas",
  "conversation-pattern-library",
]);

export const workspaceDesignExperiments = workspaceExperiments.filter((project) =>
  designExperimentSlugs.has(project.href.split("/").at(-1) ?? ""),
);

export const workspaceWriting = writingNotes;
export const workspaceAbout = { lead: aboutLead, paragraphs: aboutBio };
export const workspaceContact = {
  email: siteConfig.email,
  linkedin: siteConfig.social.linkedin,
  behance: siteConfig.social.behance,
};

// Use verified documents only. Display trophies do not imply additional awards.
export const workspaceAchievements: WorkspaceAchievement[] = [
  {
    id: "iitg-degree",
    title: "Bachelor of Design · IIT Guwahati",
    description: "Completed my Bachelor of Design in May 2024. The degree was conferred by the Indian Institute of Technology Guwahati on 14 July 2024.",
    year: "2024",
    image: "/textures/workspace/iitg-degree.jpg",
    href: "/textures/workspace/iitg-degree.jpg",
    certificate: true,
    imageWidth: 1738,
    imageHeight: 2479,
  },
  {
    id: "ride-for-unity",
    title: "Ride for Unity medal",
    description: "Represented Kerala in the 2025 Ride for Unity from Kashmir to Kanyakumari, covering roughly 4,000 km in 16 days with about 150 riders. This is the medal from that ride.",
    year: "2025",
    image: "/textures/workspace/ride-for-unity-medal.jpg",
    href: "/expeditions#ride-for-unity",
    imageWidth: 3120,
    imageHeight: 4160,
  },
];
export const workspaceAchievementsMissing =
  "Award details have not been added yet. The trophies are part of this desk scene. The milestones below are from my biography.";

export const workspaceMilestones = aboutMilestones.filter((milestone) =>
  [
    "Microsoft - Product Designer",
    "Owly - Co-founded",
  ].includes(milestone.title),
);

export const workspaceReadingMissing =
  "The reading list is still empty. Book titles and reading notes will appear here when they're added.";
