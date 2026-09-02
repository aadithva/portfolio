import type { Project } from "@/types";

const projectArchive: Project[] = [
  {
    slug: "owly-studio",
    title: "Owly",
    description:
      "I'm building Owly with two friends I've known since school. It uses brand context to help marketing teams make video drafts they can direct, without sanding every brand down into the same AI look.",
    role: "Co-founder, product & design",
    year: "2025 to present",
    client: "Owly",
    category: "AI / Startup",
    thumbnail: "/shots/owly-studio/owly-studio__home-desktop-hero.png",
    featured: true,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "Building Owly with friends from school",
        content:
          "I started Owly with Adi and Hari, two friends I have known since school. I lead product, design, and customer storytelling. Adi works on the AI systems, and Hari builds the backend and runs operations. The roles are complementary, even when the daily task list is not. Owly brings in brand context, helps shape an idea into a video draft, and lets the marketer revise it without starting over.",
      },
      {
        type: "image-full",
        images: ["/shots/owly-website/owly-website__home-desktop-hero.png"],
        caption: "Owly's public marketing site",
      },
      {
        type: "text",
        heading: "The product did not begin here",
        content:
          "Owly first explored safer, more personal AI video for children. We cared about the idea, but finding buyers and getting frequent feedback was difficult. In 2025, we shifted to brands and growth teams that needed video more often and had budgets for it. One lesson carried over. Generated media is more useful when it reflects a familiar identity and gives people control over the result.",
      },
      {
        type: "text",
        heading: "Producing enough usable video",
        content:
          "Ads wear out, formats multiply, and a brief passes through strategy, production, edits, approvals, and publishing before it goes live. We kept seeing that the idea was not always the bottleneck. Producing enough usable versions of it was.",
      },
      {
        type: "text",
        heading: "A first draft you can actually direct",
        content:
          "Owly reads a brand's website and past creative, then uses that context to generate a video draft. A marketer can ask for changes in plain language, and the editor applies them to the work on screen. We are still improving that loop. We want to speed up the first draft without taking direction away from the person responsible for the brand.",
      },
      {
        type: "image-grid",
        images: [
          "/shots/owly-studio/owly-studio__home-desktop-hero.png",
          "/shots/owly-studio/owly-studio__login-desktop-hero.png",
        ],
        caption: "Studio dashboard and sign-in",
        columns: 2,
      },
      {
        type: "framework",
        label: "Product principles",
        heading: "Start with context and keep the marketer in control",
        content:
          "We use these four principles when deciding what to build.",
        items: [
          {
            title: "Learn the brand once",
            content:
              "Save the website, product catalog, tone, and past creative so the next brief does not begin with another blank prompt.",
          },
          {
            title: "Show the plan before the render",
            content:
              "Show scripts, storyboards, progress, and approval points before and during a long generation step.",
          },
          {
            title: "Change a scene, not the universe",
            content:
              "Support selective edits and regeneration. Full reruns are expensive in time, compute, and patience.",
          },
          {
            title: "Make the next brief smarter",
            content:
              "Use customer feedback and performance data from earlier work to inform the next production.",
          },
        ],
      },
      {
        type: "text",
        heading: "What should carry into the next project",
        content:
          "We want brand context, product catalogs, past creative, and performance history to carry from one project to the next. For now, hands-on customer work shows us which decisions repeat. Those are the parts we can turn into software. We have not built all of that yet.",
      },
      {
        type: "image-grid",
        images: [
          "/shots/owly-website/owly-website__features-desktop-hero.png",
          "/shots/owly-website/owly-website__pricing-desktop-hero.png",
          "/shots/owly-website/owly-website__about-desktop-hero.png",
        ],
        caption: "Features, pricing, and about pages on the marketing site",
        columns: 3,
      },
      {
        type: "text",
        heading: "Founder titles are suspiciously broad",
        content:
          "I lead product design, brand, and customer storytelling. Adi works on the AI architecture, Hari handles the backend and operations, and customers regularly prove our assumptions wrong. My work ranges from interaction flows and prototypes to the website, sales demos, and the words the editor uses when it needs clarification. The job changes every week.",
      },
      {
        type: "stats",
        stats: [
          { label: "Co-founders", value: "3" },
          { label: "Early paid customers", value: "8+" },
          { label: "Company", value: "Self-funded" },
          { label: "Current model", value: "Service + software" },
        ],
      },
      {
        type: "text",
        heading: "Paid work is product research with consequences",
        content:
          "We used early customer projects to learn where a polished generation demo stops being a usable workflow: inputs arrive messy, brand rules conflict, approvals take time, and one weak scene should not force a full rerender. Doing some of the work by hand is not the final model. It is how we learn which repeated decisions deserve to become software.",
      },
      {
        type: "text",
        heading: "Under the hood, for the curious",
        content:
          "The product uses Next.js, React, and Tailwind on the frontend, with FastAPI and Supabase behind it. A Python pipeline coordinates video, voice, and language models; brand context lives in Pinecone; and the editor builds on the open-source Friction project. The stack has changed more than once and will probably change again. We try to keep the product idea steadier than the model menu.",
      },
      {
        type: "quote",
        quote:
          "I want to build a tool a creative team would genuinely miss when it is gone.",
        attribution: "Aadith V A, Co-founder",
      },
    ],
  },
  {
    slug: "microsoft-copilot",
    title: "Microsoft Copilot",
    description:
      "I design and evaluate Copilot response experiences across Microsoft 365 as part of a large team. My work includes citations, response structure, accessibility, and design engineering.",
    role: "Product Designer",
    year: "2024 to present",
    client: "Microsoft",
    category: "AI / Enterprise",
    thumbnail: "/images/projects/copilot-thumb.jpg",
    featured: true,
    passwordProtected: true,
    confidentialityNote:
      "This public version leaves out confidential product visuals, metrics, and implementation details.",
    sections: [
      {
        type: "text",
        heading: "An AI answer is only part of the experience",
        content:
          "My part in a much larger team is shaping the experience around AI-generated responses. I work with product, engineering, research, quality, and accessibility partners on response structure, source presentation, and review. Most of my attention goes to the small interface decisions between a generated answer and the person reading it.",
      },
      {
        type: "framework",
        label: "What I work on",
        heading: "The work is mostly small decisions",
        content:
          "These parts of the role show up in reviews, prototypes, and quality evaluation rather than as one standalone feature.",
        items: [
          {
            title: "Clarify the response",
            content:
              "Use hierarchy so the answer, its sources, and available actions do not compete for attention.",
          },
          {
            title: "Keep sources close",
            content:
              "Place source identity near the relevant claim, with more context available when the reader needs it.",
          },
          {
            title: "Turn taste into a test",
            content:
              "Translate a design concern into reusable criteria and examples the team can review together.",
          },
          {
            title: "Stay close to implementation",
            content:
              "Use prototypes and low-risk presentation-layer fixes to check accessibility and visual fidelity.",
          },
        ],
      },
      {
        type: "text",
        heading: "01. Where did that answer come from?",
        content:
          "I designed citation and reference patterns with the wider team to help people trace generated responses back to source material. We worked through how much source identity and context to show without crowding the answer. The aim was to keep the response readable while making its basis easier to inspect.",
      },
      {
        type: "framework",
        label: "Citation flow",
        heading: "Start compact, then offer more source context",
        content:
          "We treated a citation as a path from the claim to enough source context for the reader to judge it, while keeping the answer readable.",
        items: [
          {
            title: "Show the source",
            content:
              "Place a readable source label near the relevant claim without filling the answer with controls.",
          },
          {
            title: "Preview the context",
            content:
              "Show a short excerpt or preview so the reader can judge relevance before opening the source.",
          },
          {
            title: "Open the source",
            content:
              "Let the reader continue into the source when the preview is not enough.",
          },
        ],
      },
      {
        type: "text",
        heading: "02. Useful parts can still crowd an answer",
        content:
          "I contributed to a wider team effort to modernize Copilot responses across layout, source hierarchy, actions, and visual clarity. Much of my part happened in critique and edge-case review, where we worked through how those pieces sat together in the product.",
      },
      {
        type: "text",
        heading: "03. Giving 'something feels off' a clearer name",
        content:
          "Designers often begin with 'something feels off.' I co-created a UX quality-evaluation framework with the team to turn that reaction into reusable criteria, labeled examples, and regression checks. The framework became operational and surfaced quality issues across multiple response experiences.",
      },
      {
        type: "text",
        heading: "04. Some details need a running prototype",
        content:
          "Even a careful specification leaves questions once the interaction is running. I use code and near-production prototypes to check those details, then contribute small, low-risk presentation-layer fixes alongside engineering and accessibility partners. The work has included spacing, typography, accessibility, and design-system fidelity.",
      },
      {
        type: "text",
        heading: "Review is part of the work",
        content:
          "I contribute to formal accessibility and design-spec reviews. The wider process includes recurring critique and cross-functional checks, where partners can raise constraints I may not see. That work is quieter than the final screen, but it belongs in the account of how the team worked.",
      },
      {
        type: "text",
        heading: "Sharing methods as we tested them",
        content:
          "I helped run an internal initiative that documented how designers were using AI in their work. I organized recurring sessions and demos, and contributed to the supporting website. We shared methods the team had tried, including what still needed work, rather than presenting one finished process.",
      },
      {
        type: "text",
        heading: "What I am still figuring out",
        content:
          "I am still working through how much source context is useful before it becomes clutter and which quality checks should remain a human judgment. In reviews, I bring concrete examples and ask what breaks with an unusual source or in the accessible version. I work through those questions with teammates who know other parts of the system better than I do.",
      },
    ],
  },
  {
    slug: "angel-one",
    title: "Angel One",
    description:
      "A six-month UX role near the end of college, working inside a large retail-finance product.",
    role: "UX Design",
    year: "Jan to Jun 2024",
    client: "Angel One",
    category: "Fintech / Product",
    thumbnail: "/images/projects/angel-one-placeholder.svg",
    featured: true,
    passwordProtected: false,
    confidentialityNote:
      "This public summary leaves out detailed product artifacts, metrics, and feature claims I cannot verify.",
    sections: [
      {
        type: "text",
        heading: "Six months at Angel One",
        content:
          "Near the end of my final year, I spent roughly six months doing UX work at Angel One. It was my first experience designing inside a large financial-services product, where people need to understand what they are doing before they tap. I do not have enough public material to describe individual features or outcomes here.",
      },
      {
        type: "image-full",
        images: ["/images/projects/angel-one-placeholder.svg"],
        caption: "Detailed product visuals are not included in this public summary",
      },
      {
        type: "text",
        heading: "Working on finance while researching it",
        content:
          "The role overlapped with my final semester and academic research into financial advice. The same questions appeared in both. What does someone need to understand before acting? How should an interface explain risk, cost, and uncertainty? Finance interfaces do not get to hide uncertainty behind a cheerful button.",
      },
      {
        type: "framework",
        label: "What I learned",
        heading: "Small decisions matter in finance interfaces",
        content:
          "These are the habits the work reinforced for me.",
        items: [
          {
            title: "Make the decision legible",
            content:
              "A person should understand what they are choosing, what changes next, and where to inspect the detail before committing.",
          },
          {
            title: "Design for hesitation",
            content:
              "Pauses, comparison, and second thoughts are not friction to bulldoze. In financial products, they are often signs that the interface needs to explain more clearly.",
          },
          {
            title: "Keep hierarchy honest",
            content:
              "Primary actions can stand out without hiding risk, cost, or constraints in fine print.",
          },
          {
            title: "Hand off the edge cases",
            content:
              "A neat happy path is not enough. States, validation, and exception behaviour need enough detail to survive implementation.",
          },
        ],
      },
      {
        type: "stats",
        stats: [
          { label: "Timeline", value: "6 months" },
          { label: "Domain", value: "Retail finance" },
          { label: "Context", value: "Final semester" },
        ],
      },
      {
        type: "quote",
        quote:
          "The question I kept returning to was simple: can someone tell what will happen before they tap?",
        attribution: "Aadith V A",
      },
    ],
  },
  {
    slug: "reachify",
    title: "Reachify",
    description:
      "An AI writing and scheduling companion built for one job: helping busy professionals show up consistently on LinkedIn without spending their evenings on it.",
    role: "Freelance Product Designer",
    year: "2023",
    client: "Reachify, early-stage startup",
    category: "AI / Product",
    thumbnail: "/images/projects/reachify-cover.png",
    featured: true,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "A personal brand is a lot of small, repeated effort",
        content:
          "Reachify started from a familiar problem: people know they should post on LinkedIn, then reach the end of a full workday with no idea what to say. Over four months, I worked solo across research, information architecture, UI, and a working AI-assisted prototype. I focused the product on the recurring work of finding an idea, writing it, scheduling it, and learning from it.",
      },
      {
        type: "image-full",
        images: ["/images/projects/reachify-cover.png"],
        caption: "Reachify, an AI-assisted LinkedIn writing and scheduling product",
      },
      {
        type: "text",
        heading: "First, find the people already doing the work",
        content:
          "I screened for active LinkedIn creators with roughly 2,000 to 10,000 followers. They had enough experience to have real posting habits, but usually not a team doing the work for them. More than 100 cold messages led to 15 to 20 interviews. People described inconsistent ideas, uncertainty about the algorithm, disconnected tools, limited time, and a hope that their expertise might eventually earn money.",
      },
      {
        type: "framework",
        label: "Product structure",
        heading: "One product, four recurring jobs",
        content:
          "The research led to four product areas based on the work participants repeated each week.",
        items: [
          {
            title: "Create",
            content:
              "Generate an idea, shape the writing with tone and category controls, add hashtags, and schedule the finished post.",
          },
          {
            title: "Engagement",
            content:
              "Understand who is responding, where a conversation is growing, and which relationships may be worth continuing.",
          },
          {
            title: "Analytics",
            content:
              "Read follower, impression, and post-level trends without turning every creative decision into a spreadsheet.",
          },
          {
            title: "Dashboard",
            content:
              "Use one dashboard to pick up the next small task instead of rebuilding the workflow across several tools.",
          },
        ],
      },
      {
        type: "image-grid",
        images: [
          "/images/projects/reachify-g1.png",
          "/images/projects/reachify-g2.png",
        ],
        caption: "Research, structure, and selected product screens",
        columns: 2,
      },
      {
        type: "text",
        heading: "Two days is not a lot of time",
        content:
          "Partway through the project, the investor timeline left two days for an MVP of onboarding and the Create module. I marked Analytics and Engagement as 'coming soon' and spent the sprint on the path from idea to scheduled post.",
      },
      {
        type: "image-full",
        images: ["/images/projects/reachify-g3.png"],
        caption: "The Create flow across web and mobile",
      },
      {
        type: "text",
        heading: "Doing the job the product was built for",
        content:
          "Alongside the product, I wrote and designed hooks, carousel posts, storytelling formats, and practical templates for Reachify's LinkedIn page. The page grew to 2,000 followers. Posting regularly gave me first-hand experience of the job Reachify was meant to help with.",
      },
      {
        type: "stats",
        stats: [
          { label: "Timeline", value: "4 months" },
          { label: "Screens", value: "30+" },
          { label: "Interviews", value: "15 to 20" },
          { label: "LinkedIn growth", value: "2,000" },
        ],
      },
      {
        type: "quote",
        quote:
          "I too face this problem of not knowing what to post and how. Have been trying to build a profile that catches eyeballs and ReachifyMe has been a very helpful tool.",
        attribution: "Early Reachify user",
      },
    ],
  },
  {
    slug: "metamask-ad",
    title: "MetaMask AD",
    description:
      "A semester thesis that asked whether advertising could be rebuilt as a MetaMask add-on — private by default, and paying viewers instead of quietly profiling them.",
    role: "UX & System Designer",
    year: "Jan–Mar 2023",
    client: "Academic thesis — Team 45",
    category: "UX / System Design",
    thumbnail: "/images/projects/metamask-ad-cover.png",
    featured: true,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "A thesis with an actual deadline",
        content:
          "MetaMask AD began as my semester thesis and became the ConsenSys problem statement for Team 45 at the Inter IIT Tech Meet. I was the sole designer on a six-person team with five developers. This was not a commissioned MetaMask product; it was a student system-design proposal with a real jury, a working technical team, and very little room for hand-wavy architecture.",
      },
      {
        type: "image-full",
        images: ["/images/projects/metamask-ad-cover.png"],
        caption: "MetaMask AD — decentralized advertising system concept",
      },
      {
        type: "text",
        heading: "People did not hate ads as much as feeling watched",
        content:
          "The research combined secondary market study, a viewer survey, advertiser conversations, stakeholder mapping, and a competitive review of Web3 advertising products. The most useful signal was not that everyone wanted advertising to disappear. People wanted more control over their data, clearer consent, and something in return for their attention. Advertisers still needed targeting, reporting, and campaign tools — just without rebuilding the same surveillance model on a blockchain.",
      },
      {
        type: "text",
        heading: "Why build inside MetaMask instead of around it",
        content:
          "A separate advertising app would have created another trust problem before solving the first one. MetaMask already had broad Web3 adoption, an open-source codebase, and a Snap architecture made for add-ons. I designed the system around that existing relationship: a demand-side platform for advertisers, connected to wallet-native payments and an opt-in viewer experience.",
      },
      {
        type: "framework",
        label: "Advertiser dashboard",
        heading: "One dashboard, five jobs",
        content:
          "The system had to feel like a practical campaign tool, not a blockchain diagram wearing buttons.",
        items: [
          {
            title: "Overview",
            content:
              "See weekly reach and wallet balance without beginning the day in a spreadsheet.",
          },
          {
            title: "Quick actions",
            content:
              "Deposit funds, create a campaign, or move directly into the tools needed next.",
          },
          {
            title: "Statistics",
            content:
              "Track impressions, clicks, click-through rate, and spend at a useful level of detail.",
          },
          {
            title: "Performance",
            content:
              "Compare stronger and weaker ads, then surface prompts for what an advertiser could adjust.",
          },
          {
            title: "Campaigns",
            content:
              "Create, schedule, fund, and monitor active campaigns in the same system.",
          },
        ],
      },
      {
        type: "image-grid",
        images: [
          "/images/projects/metamask-ad-g1.png",
          "/images/projects/metamask-ad-g2.png",
          "/images/projects/metamask-ad-g3.png",
        ],
        caption: "System maps, information architecture, and advertiser flows",
        columns: 3,
      },
      {
        type: "text",
        heading: "Teaching the fox to pay people",
        content:
          "The viewer side became Ad World, an opt-in area inside the wallet where people could choose to see ads and receive a proposed FOX token in return. The token, onboarding, consent, and wallet states were all conceptual. The important design question was real: could an ad experience make the exchange visible instead of pretending attention was free?",
      },
      {
        type: "text",
        heading: "Four steps, on purpose",
        content:
          "Publishing an ad came down to four decisions: upload the creative, write and preview the copy, link the destination, then set the budget and pay the gas fee from a MetaMask account. The prototype and motion walkthrough were made in a two-day design sprint. That constraint forced every screen to answer one question clearly: what does the advertiser need to decide next?",
      },
      {
        type: "image-grid",
        images: [
          "/images/projects/metamask-ad-g4.png",
          "/images/projects/metamask-ad-g5.png",
          "/images/projects/metamask-ad-g6.png",
        ],
        caption: "Wallet onboarding, campaign creation, and final dashboard",
        columns: 3,
      },
      {
        type: "text",
        heading: "A student project that travelled further than expected",
        content:
          "The team placed second at the Inter IIT Tech Meet. ConsenSys later invited us to present the work in a community call attended by more than 1,000 people. It still did not become a MetaMask product — and the portfolio should not pretend otherwise — but it was the first time one of my system-design exercises met a large, technically informed audience.",
      },
      {
        type: "stats",
        stats: [
          { label: "Competition result", value: "2nd place" },
          { label: "Community call", value: "1,000+" },
          { label: "Team", value: "6 people" },
          { label: "Timeline", value: "3 months" },
        ],
      },
      {
        type: "quote",
        quote:
          "It was never a MetaMask product — just a thesis that got taken seriously enough to present to a much bigger room.",
        attribution: "Aadith V A",
      },
    ],
  },
  {
    slug: "nomad",
    title: "Nomad",
    description:
      "A collaborative multi-city trip planner for travelers who love the idea of a group holiday and dread the group-chat logistics of planning one.",
    role: "Co-designer — with Aarya Kabara",
    year: "2023",
    client: "Concept project",
    category: "Product / Mobile",
    thumbnail: "/images/projects/nomad-cover.png",
    featured: false,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "The trip was exciting. The spreadsheet was not.",
        content:
          "Aarya Kabara and I designed Nomad around a very ordinary travel problem: a multi-city holiday sounds wonderful until routes, stays, budgets, activities, and several people’s opinions arrive in the same group chat. The brief was to connect points of interest across cities, account for the length of stay, and make lower-cost transport easier to find — without turning the plan into project management software.",
      },
      {
        type: "image-full",
        images: ["/images/projects/nomad-cover.png"],
        caption: "Nomad — collaborative multi-city trip planning",
      },
      {
        type: "text",
        heading: "Where the stress actually lived",
        content:
          "We interviewed eight travelers about the emotions, habits, and friction around planning. The planning stage itself ranked as more stressful than the travel or the stay. Money uncertainty, arranging transport, packing, and assembling the itinerary came up repeatedly. The problem was not a shortage of travel information. It was that the useful pieces were scattered, and group agreement had no real home.",
      },
      {
        type: "framework",
        label: "Two perspectives",
        heading: "One itinerary had to work for two very different travelers",
        content:
          "The personas helped us avoid designing only for the confident person already doing all the planning.",
        items: [
          {
            title: "Karan",
            content:
              "A 20-year-old student planning on a budget with friends, worried about cost estimates, local transport, and communication breaking down.",
          },
          {
            title: "Ashna",
            content:
              "A 40-year-old marketing consultant who plans carefully, distrusts booking sites, and wants reliable local recommendations rather than tourist traps.",
          },
        ],
      },
      {
        type: "text",
        heading: "Three competitors, three useful gaps",
        content:
          "TripIt organized plans well but made sharing with non-users awkward. Wanderlog felt uncluttered but had weak search and no calendar sync. TripAdvisor had enormous review depth but mixed booking choices with sponsored noise and price confusion. All three helped with travel. None treated group agreement as a first-class design problem.",
      },
      {
        type: "image-grid",
        images: [
          "/images/projects/nomad-g1.png",
          "/images/projects/nomad-g2.png",
        ],
        caption: "Research synthesis, structure, and selected flows",
        columns: 2,
      },
      {
        type: "text",
        heading: "Designing for indecision",
        content:
          "Our early ideation was full of voting systems, hosts, deadlines, shared documents, and ways to stop an itinerary debate from living forever. Not every sticky note survived. The principle did: planning, deciding, chatting, and splitting costs should sit close together because those activities keep interrupting one another in real life.",
      },
      {
        type: "text",
        heading: "Four places to put the chaos",
        content:
          "Nomad settled into Explore for themes, guides, packages, and nearby ideas; Plan for bookings, weather, saved places, and a draggable day-by-day itinerary; Messages for trip-linked conversation and shared expenses; and Profile for documents, past plans, and settings. Inter and a restrained blue-and-neutral palette kept dates, prices, maps, and cards from feeling like a travel-themed spreadsheet.",
      },
      {
        type: "image-full",
        images: ["/images/projects/nomad-g3.png"],
        caption: "Explore, plan, message, budget, and profile experiences",
      },
      {
        type: "stats",
        stats: [
          { label: "Research interviews", value: "8" },
          { label: "Competitors", value: "3" },
          { label: "Personas", value: "2" },
          { label: "Core areas", value: "4" },
        ],
      },
    ],
  },
  {
    slug: "daolens",
    title: "DaoLens",
    description:
      "Early startup work across product, brand, and marketing, including a documented two-week sprint for DAO Denver.",
    role: "Product, brand & marketing design",
    year: "2022 to 2023",
    client: "DaoLens",
    category: "Web3 / Startup",
    thumbnail: "/images/projects/daolens-placeholder.svg",
    featured: false,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "The startup where the brief rarely stayed in one lane",
        content:
          "I joined DaoLens when I was about twenty and worked across product, brand, and marketing. The surviving work includes onboarding, contributor dashboards, governance-related product work, campaigns, and visual systems. Old drafts use different titles, so I describe the role by the work. I was an early designer doing whatever the product and company needed.",
      },
      {
        type: "framework",
        label: "My working range",
        heading: "How product, brand, and marketing overlapped",
        content:
          "A product decision often changed what the brand or marketing work needed to explain, and the reverse was true too.",
        items: [
          {
            title: "Product",
            content:
              "The onboarding and contributor work had to explain unfamiliar Web3 concepts to people who did not already know the vocabulary.",
          },
          {
            title: "Brand",
            content:
              "The visual system had to work for a B2B product, community events, and marketing.",
          },
          {
            title: "Go-to-market",
            content:
              "I worked on event material, social posts, product explainers, and campaigns.",
          },
          {
            title: "Startup rhythm",
            content:
              "Briefs changed quickly, and there was rarely time to wait for every role boundary to become official.",
          },
        ],
      },
      {
        type: "text",
        heading: "What survives publicly",
        content:
          "The DAO Denver sprint has a complete Behance case study. I do not have enough public material to describe the broader product flows in the same detail, so this page stays at role-summary level.",
      },
      {
        type: "stats",
        stats: [
          { label: "Period", value: "2022 to 2023" },
          { label: "Environment", value: "Early startup" },
          { label: "Scope", value: "Product, brand, marketing" },
          { label: "Detailed case study", value: "DAO Denver" },
        ],
      },
      {
        type: "quote",
        quote:
          "My job description changed with whatever the company needed that week.",
        attribution: "Aadith V A",
      },
    ],
  },
  {
    slug: "crunch",
    title: "Crunch",
    description:
      "Dashboard and data-visualisation work for an analytics product, focused on making complex information easier to read.",
    role: "Dashboard & information design",
    year: "2022 to 2023",
    client: "CrunchIt",
    category: "Data / Product",
    thumbnail: "/images/projects/crunch-placeholder.svg",
    featured: false,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "Making dense data easier to read",
        content:
          "Crunch brought me into dashboard and data-visualisation work while I was juggling college, startup, and freelance projects. I organised dense information and made comparisons easier to read in the interface.",
      },
      {
        type: "image-full",
        images: ["/images/projects/crunch-placeholder.svg"],
        caption: "Original dashboard visuals are not included in this public summary",
      },
      {
        type: "text",
        heading: "I was not the data scientist",
        content:
          "I was clear that I did not have deep training in data science and had not built the underlying models. I brought dashboard experience and learned the domain as I worked. My responsibility was how the interface presented evidence, comparisons, status, and uncertainty.",
      },
      {
        type: "framework",
        label: "Information-design checklist",
        heading: "Four questions I used in the dashboard work",
        content:
          "The visual form changed with the data, but I kept returning to these questions.",
        items: [
          {
            title: "A starting point",
            content:
              "The page needs a clear first read before it asks someone to inspect charts, filters, and secondary metrics.",
          },
          {
            title: "A fair comparison",
            content:
              "Labels, scales, time ranges, and baselines should make comparison easier rather than quietly steering the conclusion.",
          },
          {
            title: "Visible uncertainty",
            content:
              "Show when data is incomplete or ambiguous instead of presenting every value with the same certainty.",
          },
          {
            title: "A next question",
            content:
              "Give the reader enough context to decide what to inspect next.",
          },
        ],
      },
      {
        type: "text",
        heading: "What I carried into later work",
        content:
          "The project gave me an early set of questions about hierarchy, comparison, and uncertainty. I still use them when working on citations, source panels, and evaluation reports.",
      },
      {
        type: "stats",
        stats: [
          { label: "Focus", value: "Dashboards" },
          { label: "Contribution", value: "Visualisation" },
          { label: "Domain", value: "Analytics" },
        ],
      },
    ],
  },
  {
    slug: "sarthebari",
    title: "Sarthebari",
    description:
      "A field-research, identity, and e-commerce concept about Assam’s bell-metal craft — and what happens when the object travels further than the name of its maker.",
    role: "Co-designer & Researcher — with Mohammed Nadil",
    year: "2023",
    client: "Academic project",
    category: "Research / Brand",
    thumbnail: "/images/projects/sarthebari-cover.png",
    featured: false,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "A lesson in looking slowly",
        content:
          "Sarthebari, less than 100 kilometres from Guwahati, is home to Assam’s second-largest handicraft industry: bell metal. Mohammed Nadil and I studied the craft through secondary research, stakeholder mapping, field observation, and conversations with a retail shop owner, a cooperative employee, and craftsmen. The subject had far more history than we did. Our first job was not to arrive with a logo. It was to understand what the work was carrying.",
      },
      {
        type: "image-full",
        images: ["/images/projects/sarthebari-cover.png"],
        caption: "Bell-metal craft in Sarthebari, Assam",
      },
      {
        type: "text",
        heading: "A regional economy built by hand",
        content:
          "The source material described an estimated 5,000+ workers, 280+ production units, two cooperatives, 41 shopkeepers, roughly 30 agents, and products worth an estimated ₹3.5 crore. The process moved through casting, heating up to 800°C, forging, reheating until the form was right, water quenching, quality checks, finishing, artwork, and finally the market. The neat diagram hid a less neat reality: aching hands, intense workshop noise, and fewer young people choosing the craft.",
      },
      {
        type: "text",
        heading: "The story that stayed with us was about a name",
        content:
          "Bhutiyataal cymbals made in Sarthebari travel through Nepal and Bhutan, where traders polish, chemically age, repackage, and sell them internationally as “Tibetan” or “ancient Chinese” cymbals. Old household vessels become imported-looking singing bowls. Dafla Kahi and Dafla Bati are aged before reaching buyers as prestige objects. The products travel. The original identity often does not.",
      },
      {
        type: "image-grid",
        images: [
          "/images/projects/sarthebari-g1.png",
          "/images/projects/sarthebari-g2.png",
        ],
        caption: "Field research, craft process, and voices from Sarthebari",
        columns: 2,
      },
      {
        type: "quote",
        quote:
          "These products come from Sarthebari, but they’re sold as Tibetan in other countries. We don’t get the credit, and our identity gets lost.",
        attribution: "ACBMUMSL employee, field interview",
      },
      {
        type: "text",
        heading: "Design a name people could keep",
        content:
          "Our concept became ABMI — Assam Bell Metal Industry. The mark combined a rhino, hill, sun, hammering gesture, and the curve of a singing bowl into a compact line symbol. Gold and pale yellow sat against near-black, with DM Sans keeping the system straightforward. The point was not to make the craft look newly fashionable. It was to give products, makers, and place a clearer shared origin.",
      },
      {
        type: "text",
        heading: "From identity to a storefront",
        content:
          "We extended the concept into an e-commerce product page with material, size, weight, price, shipping, and handcraft information; a social strategy built around products, process, testimonials, artisan stories, offers, and health-related messaging; and a set of targeted ads. The health claims came from the project’s source material and stakeholder beliefs, not medical research we conducted, so they belong in the work as brand messaging — not as facts I can certify.",
      },
      {
        type: "image-grid",
        images: [
          "/images/projects/sarthebari-g3.png",
          "/images/projects/sarthebari-g4.png",
          "/images/projects/sarthebari-g5.png",
        ],
        caption: "ABMI identity, e-commerce, and social concepts",
        columns: 3,
      },
      {
        type: "stats",
        stats: [
          { label: "Workers, estimated", value: "5,000+" },
          { label: "Production units", value: "280+" },
          { label: "Cooperatives", value: "2" },
          { label: "Product value", value: "₹3.5 Cr" },
        ],
      },
      {
        type: "text",
        heading: "What we did not solve",
        content:
          "We did not fix the physical strain in the workshops, reverse generational change, or restore every lost attribution. A student identity system could not do that. What Mohammed and I could do, as two outsiders allowed into the work for a while, was document the problem honestly and propose a way for the place behind the object to remain visible.",
      },
    ],
  },
  {
    slug: "junkea",
    title: "Junkea",
    description:
      "A group project that turned discarded department furniture and salvaged parts into a small orange-and-black collection that went into use at IIT Guwahati’s Media Lab.",
    role: "Collaborator — team project",
    year: "2022",
    client: "IIT Guwahati course project",
    category: "Product / Collaboration",
    thumbnail: "",
    featured: false,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "The project began with furniture everyone had learned to step around",
        content:
          "Discarded furniture had been collecting around our department building at IIT Guwahati. A group of seven-plus design students, supported by our mentor Dr. Mriganka Madhukalya, decided to treat it as material rather than background clutter. Junkea moved through three simple stages: collect what was available, let those forms suggest ideas, then build the useful version.",
      },
      {
        type: "text",
        heading: "The materials wrote part of the brief",
        content:
          "A funnel-shaped wire frame suggested the ring of a chair. A bent plastic rod pointed toward a round table. Old chair parts, bicycle rims and springs, metal rods, scrap plywood, used cloth, and sponge became the working material library. The final forms did not begin as pristine renders. They began as oddly specific objects that already had a history.",
      },
      {
        type: "text",
        heading: "Black, orange, and a little 1970s",
        content:
          "The visual language used orange as a spotlight against black. The project boards connected the colour to affordability, value, and a retro, slightly groovy character. It gave a mixed collection of salvaged materials one recognisable attitude without pretending the surfaces had all come from the same place.",
      },
      {
        type: "text",
        heading: "The useful ending",
        content:
          "We gathered informal reactions to early sketches, built the pieces in the workshop, and exhibited them at IIT Guwahati. The nicest outcome was not the exhibition photograph or the polished render: the furniture went into everyday use at the Media Lab. This was a team effort with no documented individual role split, so I am keeping it here as a collaboration rather than borrowing the whole story for myself.",
      },
      {
        type: "stats",
        stats: [
          { label: "Team", value: "7+" },
          { label: "Process", value: "3 stages" },
          { label: "Tools", value: "3" },
          { label: "Outcome", value: "In use" },
        ],
      },
      {
        type: "quote",
        quote:
          "The best image is not the render. It is the furniture already doing a real job in the Media Lab.",
        attribution: "Aadith V A",
      },
    ],
  },
];

const publicWorkSlugs = [
  "owly-studio",
  "microsoft-copilot",
  "angel-one",
  "reachify",
  "daolens",
  "crunch",
] as const;

export const projects: Project[] = publicWorkSlugs.map((slug) => {
  const project = projectArchive.find((item) => item.slug === slug);
  if (!project) throw new Error(`Missing public work project: ${slug}`);
  return project;
});

export function getProject(slug: string): Project | undefined {
  return projects.find((p) => p.slug === slug);
}

export function getFeaturedProjects(): Project[] {
  return projects.filter((p) => p.featured);
}

export function getAllSlugs(): string[] {
  return projects.map((p) => p.slug);
}

export function getAdjacentProjects(slug: string): {
  prev: Project | null;
  next: Project | null;
} {
  const index = projects.findIndex((p) => p.slug === slug);
  return {
    prev: index > 0 ? projects[index - 1] : null,
    next: index < projects.length - 1 ? projects[index + 1] : null,
  };
}
