import type { Project } from "@/types";

const projectArchive: Project[] = [
  {
    slug: "owly-studio",
    title: "Owly",
    description:
      "I’m building Owly with two long-time friends: a brand-aware creative system that helps marketing teams reach a controllable video draft without sanding every brand down into the same AI look.",
    role: "Co-founder & CEO",
    year: "2025–Present",
    client: "Owly",
    category: "AI / Startup",
    thumbnail: "/shots/owly-studio/owly-studio__home-desktop-hero.png",
    featured: true,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "Three friends, one very large idea",
        content:
          "I started Owly with Adi and Hari, two friends I have known since school. I lead product, design, and much of the customer story; Adi works on the AI systems; Hari builds the backend and operational spine. The roles are complementary, even when the daily task list is not. We are building a creative system for marketing teams: bring in brand context, shape an idea, make a first video draft, refine it without starting over, and learn from what ships.",
      },
      {
        type: "image-full",
        images: ["/shots/owly-website/owly-website__home-desktop-hero.png"],
        caption: "owly.studio — public marketing site",
      },
      {
        type: "text",
        heading: "The product did not begin here",
        content:
          "Owly first explored safer, more personal AI video for children. The emotional idea was strong, but the buyer, feedback loop, and economics were slow. In 2025, we moved toward brands and growth teams, where the need for frequent video was immediate and budgeted. The pivot changed the customer, not the useful insight: generated media becomes more valuable when it carries familiar identity, clear context, and meaningful control.",
      },
      {
        type: "text",
        heading: "The relay race between brief and live",
        content:
          "Creative teams often work on a slower clock than the platforms they feed. Ads fatigue, formats multiply, and a good brief gets stuck in a relay race across strategy, production, edits, approvals, and publishing. We kept seeing the same gap: the idea was not always the bottleneck; turning it into enough usable creative was.",
      },
      {
        type: "text",
        heading: "A first draft you can actually direct",
        content:
          "Owly reads a brand’s website and past creative, then uses that context to help generate a video draft. The useful part is not a shiny Generate button; it is what happens next. A marketer can respond in plain language, and the editor makes changes to the work on screen. We are still improving the loop, but the goal stays simple: make the first draft faster without taking direction away from the person responsible for the brand.",
      },
      {
        type: "image-grid",
        images: [
          "/shots/owly-studio/owly-studio__home-desktop-hero.png",
          "/shots/owly-studio/owly-studio__login-desktop-hero.png",
        ],
        caption: "Studio app — dashboard and auth",
        columns: 2,
      },
      {
        type: "framework",
        label: "The product thesis",
        heading: "Context first. Control second. Generation somewhere in the middle.",
        content:
          "The system we are working toward is less a model wrapper and more a repeatable creative workflow. Four ideas keep the product honest.",
        items: [
          {
            title: "Learn the brand once",
            content:
              "Bring the website, product catalog, tone, and past creative into a reusable context layer instead of restarting from a blank prompt.",
          },
          {
            title: "Show the plan before the render",
            content:
              "Use scripts, storyboards, progress, and approval points so a long generation step never feels like a sealed box.",
          },
          {
            title: "Change a scene, not the universe",
            content:
              "Support selective edits and regeneration. Full reruns are expensive in time, compute, and patience.",
          },
          {
            title: "Make the next brief smarter",
            content:
              "Carry customer feedback and performance context forward so repeat production improves instead of merely repeating.",
          },
        ],
      },
      {
        type: "text",
        heading: "The bet we’re making",
        content:
          "Our long-term bet is that brand context, product catalogs, past creative, and performance history become reusable infrastructure. The hands-on service layer helps us learn and earn now; the company becomes more interesting when each customer improves a repeatable system rather than creating another bespoke workflow. We are not there yet. That is the work.",
      },
      {
        type: "image-grid",
        images: [
          "/shots/owly-website/owly-website__features-desktop-hero.png",
          "/shots/owly-website/owly-website__pricing-desktop-hero.png",
          "/shots/owly-website/owly-website__about-desktop-hero.png",
        ],
        caption: "Marketing site — features, pricing, about",
        columns: 3,
      },
      {
        type: "text",
        heading: "Founder titles are suspiciously broad",
        content:
          "I lead product design, brand, and founder-led storytelling, but not in a vacuum. Adi pushes the AI architecture, Hari carries backend and operational execution, customers puncture our assumptions, and the work changes weekly. My part ranges from interaction flows and prototypes to the website, sales demos, and the words an AI editor uses when it needs clarification. It is less “owning every surface” and more keeping the many surfaces in the same conversation.",
      },
      {
        type: "stats",
        stats: [
          { label: "Co-founders", value: "3" },
          { label: "Early paid customers", value: "8+" },
          { label: "Company", value: "Self-funded" },
          { label: "Service-to-software bridge", value: "Hybrid" },
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
          "We are not trying to win a generation demo. We are trying to build a tool a creative team would genuinely miss when it is gone.",
        attribution: "Aadith V A, Co-founder",
      },
    ],
  },
  {
    slug: "microsoft-copilot",
    title: "Microsoft Copilot",
    description:
      "Making Copilot answers easier to read, question, verify, and use — through citations, response design, UX evaluation, accessibility, and the occasional detour into code.",
    role: "Product Designer",
    year: "2024–Present",
    client: "Microsoft",
    category: "AI / Enterprise",
    thumbnail: "/images/projects/copilot-thumb.jpg",
    featured: true,
    passwordProtected: true,
    confidentialityNote:
      "Public-safe version: I’ve kept the thinking and left out confidential product visuals, metrics, and implementation details.",
    sections: [
      {
        type: "text",
        heading: "AI can sound certain. People still deserve receipts.",
        content:
          "My role is one small part of a very large team effort: shaping the experience around an AI-generated answer. I work with designers, product managers, engineers, researchers, quality specialists, and accessibility partners to make those answers easier to scan, trace back to evidence, evaluate, and improve. I do not make Copilot alone — thankfully. I focus on the moments where the model meets a person, because that is often where trust is earned or lost.",
      },
      {
        type: "framework",
        label: "My part of the puzzle",
        heading: "Less magic. More clarity.",
        content:
          "I keep returning to four practical habits. None is flashy on its own, but together they help an AI response feel less like a polished black box and more like something a person can understand, question, and use.",
        items: [
          {
            title: "Make it scannable",
            content:
              "Give complex responses a clear rhythm so the answer, evidence, and next action do not compete for attention.",
          },
          {
            title: "Bring receipts",
            content:
              "Keep source evidence close enough to a claim that verification feels natural, not like a second task.",
          },
          {
            title: "Turn taste into a test",
            content:
              "Convert “something feels off” into criteria, examples, and checks a wider team can actually reuse.",
          },
          {
            title: "Mind the last 10%",
            content:
              "Use prototypes and small code fixes to protect the accessibility and craft that can disappear during handoff.",
          },
        ],
      },
      {
        type: "stats",
        stats: [
          { label: "Product world", value: "Microsoft 365" },
          { label: "My lane", value: "Response UX" },
          { label: "Recurring question", value: "Can I verify this?" },
          { label: "Often between", value: "Figma ↔ code" },
        ],
      },
      {
        type: "text",
        heading: "01 — “Nice answer. Where did that come from?”",
        content:
          "Generated answers arrive quickly; trust usually takes another beat. I worked on citation and reference patterns that connect claims to source material without turning every response into a legal appendix. The goal was quiet confidence: show evidence near the claim, reveal enough context to judge it, and keep the full source one step away.",
      },
      {
        type: "framework",
        label: "A verification ladder",
        heading: "Let the evidence deepen only when the person asks.",
        content:
          "A citation is not one component. It is a sequence that should preserve reading flow while giving someone a credible path from a claim to its basis.",
        items: [
          {
            title: "Recognize the source",
            content:
              "Keep a compact, readable source identity near the relevant claim so the answer does not become a field of controls.",
          },
          {
            title: "Inspect useful context",
            content:
              "Reveal an excerpt or preview that helps someone judge relevance without abandoning the answer.",
          },
          {
            title: "Open the exact evidence",
            content:
              "When the stakes are higher, carry the person into the source context instead of making them search a long document again.",
          },
          {
            title: "Keep meaning after reuse",
            content:
              "Preserve structure, source clarity, and accessible semantics when content is copied, read aloud, or moved into a less capable surface.",
          },
        ],
      },
      {
        type: "text",
        heading: "02 — AI responses collect a lot of furniture",
        content:
          "Citations, actions, cards, previews, artifacts — useful pieces can still become a crowded room. I contributed to a wider team effort to modernize how those pieces fit together, simplifying layout and hierarchy so people could find the answer, the evidence, and the next action without decoding the interface first. Most of the work happened in critique, edge cases, and the stubborn details that only appear when a concept meets a real product.",
      },
      {
        type: "text",
        heading: "03 — Taste is useful. A repeatable quality bar is better.",
        content:
          "Designers are good at saying, “Something feels off.” That does not scale especially well. As a named designer on a UX evaluation initiative, I helped turn qualitative judgment into reusable criteria, labeled examples, rubrics, and prompt-based checks. The framework became operational and surfaced quality issues across multiple response experiences — giving the team a way to catch problems earlier and discuss them with more than vibes.",
      },
      {
        type: "text",
        heading: "04 — Pixels have a habit of wandering",
        content:
          "Even a careful specification can arrive in the product slightly… sideways. I use code and near-production prototypes to test interactions and contribute small, low-risk presentation-layer fixes. Accessibility, spacing, typography, and component behavior are not always glamorous, but they are often the difference between a design that looks complete and one that feels considered.",
      },
      {
        type: "text",
        heading: "Good work survives a lot of questions",
        content:
          "Formal accessibility reviews, design-spec reviews, critique, and cross-functional checks rarely produce a dramatic portfolio thumbnail. They do produce better decisions. I contribute to those review layers, raise questions early, and lean on partners who see risks or constraints I do not. The point is not to be the person with every answer; it is to help the team notice the right problems.",
      },
      {
        type: "text",
        heading: "Sharing the messy middle",
        content:
          "Outside feature work, I helped run an internal design-enablement initiative about using AI across research, synthesis, prototyping, evaluation, and implementation. I organized recurring sessions, demos, and supporting website work — not as a guru with a perfect method, but as a curious practitioner documenting what worked, what did not, and what others might borrow.",
      },
      {
        type: "text",
        heading: "What I am still figuring out",
        content:
          "Plenty. How much evidence is reassuring before it becomes clutter? When should an evaluation automate a check, and when should a person keep the final say? How do patterns stay coherent across products without becoming rigid? I am still working through those questions with people who know different parts of the system better than I do. That uncertainty is not a footnote to the work; it is the interesting part.",
      },
      {
        type: "text",
        heading: "How I tend to show up",
        content:
          "I ask a lot of small questions: Is the evidence close enough to the claim? Can someone scan this in five seconds? What happens with an odd source? Did the accessible version keep the same meaning? Can we test this judgment instead of debating it forever? I work best in the messy middle between design, research, quality, and engineering, where the answer usually gets better when nobody pretends to know everything.",
      },
      {
        type: "quote",
        quote:
          "I’m not trying to make AI look all-knowing. I’m trying to make it easier for people to know when it’s useful.",
        attribution: "Aadith V A",
      },
    ],
  },
  {
    slug: "angel-one",
    title: "Angel One",
    description:
      "A short fintech design role near the end of college — and my first close look at how trust, legibility, and hesitation behave inside a large financial product.",
    role: "UX Design",
    year: "Jan–Jun 2024",
    client: "Angel One",
    category: "Fintech / Product",
    thumbnail: "/images/projects/angel-one-placeholder.svg",
    featured: true,
    passwordProtected: false,
    confidentialityNote:
      "Public-safe role summary: detailed product artifacts are not included here, and I am not attaching a shipped metric or feature claim that I cannot verify.",
    sections: [
      {
        type: "text",
        heading: "A short role, and a useful change of scale",
        content:
          "Near the end of my final year, I spent roughly six months doing UX work in Angel One’s product environment. I do not have a polished Behance board for this one, and the surviving public artifacts are thinner than the work itself, so I am keeping the story appropriately modest. What I can stand behind is the context: a large financial-services product, high-stakes information, and people who need to understand what they are doing before they tap.",
      },
      {
        type: "image-full",
        images: ["/images/projects/angel-one-placeholder.svg"],
        caption: "Project visuals will be added after a public-safe artifact pass",
      },
      {
        type: "text",
        heading: "The useful overlap with my thesis",
        content:
          "The role overlapped with my final academic semester and research around financial advising. That made the work feel less like a sudden domain switch and more like theory meeting a product with real scale. Finance interfaces do not get to hide uncertainty behind a cheerful button. Labels, hierarchy, confirmation, and edge cases carry more weight because the cost of misunderstanding is not abstract.",
      },
      {
        type: "framework",
        label: "What the context sharpened",
        heading: "Trust is usually made from small, unglamorous decisions",
        content:
          "I am not presenting these as patented fintech principles. They are the practical habits the environment reinforced.",
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
              "Primary actions should look primary, but risk, cost, and constraints should not be visually negotiated into fine print.",
          },
          {
            title: "Hand off the edge cases",
            content:
              "A neat happy path is not enough. States, validation, and exception behaviour need enough detail to survive implementation.",
          },
        ],
      },
      {
        type: "text",
        heading: "No inflated impact slide",
        content:
          "I could make this page sound larger by borrowing the language of shipped impact, but I do not have the primary material to support that claim here. The honest value of Angel One in my story is the bridge it created: from early startup work and academic finance research into a much larger, more consequential product system.",
      },
      {
        type: "stats",
        stats: [
          { label: "Timeline", value: "6 months" },
          { label: "Domain", value: "Retail finance" },
          { label: "Context", value: "Final semester" },
          { label: "Public claim", value: "Intentionally narrow" },
        ],
      },
      {
        type: "quote",
        quote:
          "High-stakes products do not reward decorative certainty. They reward interfaces that help people understand what happens next.",
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
    client: "Reachify — early-stage startup",
    category: "AI / Product",
    thumbnail: "/images/projects/reachify-cover.png",
    featured: true,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "A personal brand is a lot of small, repeated effort",
        content:
          "Reachify started from a familiar problem: people know they should post on LinkedIn, then reach the end of a full workday with no idea what to say. Over four months, I worked solo across research, information architecture, UI, and a working AI-assisted prototype. The aim was not to manufacture a personal brand overnight. It was to make the small, recurring work of finding an idea, writing it well, scheduling it, and learning from it feel manageable.",
      },
      {
        type: "image-full",
        images: ["/images/projects/reachify-cover.png"],
        caption: "Reachify — an AI-assisted LinkedIn writing and scheduling product",
      },
      {
        type: "text",
        heading: "First, find the people already doing the work",
        content:
          "I screened for active LinkedIn creators with roughly 2,000–10,000 followers — enough experience to have real habits, but not so much that a team was already doing the work for them. More than 100 cold messages led to 15–20 interviews. The themes were practical rather than glamorous: inconsistent ideas, uncertainty about the algorithm, too many disconnected tools, limited time, and a vague hope that expertise might eventually turn into income.",
      },
      {
        type: "framework",
        label: "Product structure",
        heading: "One product, four recurring jobs",
        content:
          "The research became a product organised around the work people repeated every week, rather than a dashboard full of impressive-looking AI buttons.",
        items: [
          {
            title: "Create",
            content:
              "Generate an idea, shape the writing with tone and category controls, add hashtags, and schedule the finished post.",
          },
          {
            title: "Engage",
            content:
              "Understand who is responding, where a conversation is growing, and which relationships may be worth continuing.",
          },
          {
            title: "Measure",
            content:
              "Read follower, impression, and post-level trends without turning every creative decision into a spreadsheet.",
          },
          {
            title: "Return",
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
          "Partway through the project, the investor timeline compressed into a two-day MVP sprint for onboarding and the Create module. Analytics and Engagement became honest “coming soon” states while the core flow had to work. It was not the process I would plan on purpose, but it clarified the product quickly: if idea → write → schedule was not useful, the rest of the roadmap was decoration.",
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
          "Alongside the product, I wrote and designed content for Reachify’s own LinkedIn page — hooks, carousel posts, storytelling formats, and practical templates. The page grew to 2,000 followers. I liked the symmetry of that: the fastest way to understand a tool for consistent posting was to become one of the people consistently posting.",
      },
      {
        type: "stats",
        stats: [
          { label: "Timeline", value: "4 months" },
          { label: "Screens", value: "30+" },
          { label: "Interviews", value: "15–20" },
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
      "Early startup design across product, brand, and go-to-market — with a two-week DAO Denver sprint as the clearest surviving public artifact.",
    role: "Product, brand & marketing design",
    year: "2022–2023",
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
          "I joined DaoLens at around twenty and worked across a young Web3 company where product, brand, and go-to-market problems regularly arrived in the same week. The surviving records point to onboarding, contributor dashboards, governance-oriented experiences, marketing, and visual systems. My exact title changes across old drafts, so I prefer the less dramatic truth: I was an early designer doing whatever the product and company needed, often before the boundaries were tidy.",
      },
      {
        type: "framework",
        label: "My working range",
        heading: "Product, brand, and go-to-market kept borrowing from one another",
        content:
          "The useful lesson was not that I could do several kinds of design. It was seeing how decisions in one layer created constraints in the others.",
        items: [
          {
            title: "Product",
            content:
              "Onboarding, contributor dashboards, access, and governance-oriented experiences had to explain unfamiliar Web3 concepts without assuming every user already spoke the language.",
          },
          {
            title: "Brand",
            content:
              "The visual system needed enough technical credibility for a B2B product while remaining flexible across community and marketing moments.",
          },
          {
            title: "Go-to-market",
            content:
              "Events, social content, product explainers, and campaigns translated the product into reasons for someone to stop, understand, and continue the conversation.",
          },
          {
            title: "Startup rhythm",
            content:
              "The brief moved quickly and ownership was broad. I learned to make progress without waiting for every role boundary to become official.",
          },
        ],
      },
      {
        type: "text",
        heading: "The public record is uneven, so the structure is honest",
        content:
          "The DAO Denver sprint has a complete Behance trail and now lives as its own case study above. The broader product work needs a careful artifact pass before I describe individual flows in detail. I would rather leave a clear gap than fill it with a confident reconstruction.",
      },
      {
        type: "stats",
        stats: [
          { label: "Period", value: "2022–2023" },
          { label: "Environment", value: "Early startup" },
          { label: "Working range", value: "Product → brand" },
          { label: "Detailed chapter", value: "DAO Denver" },
        ],
      },
      {
        type: "quote",
        quote:
          "DaoLens was where I learned that an early designer does not get to protect a tidy job description from the needs of the company.",
        attribution: "Aadith V A",
      },
    ],
  },
  {
    slug: "crunch",
    title: "Crunch",
    description:
      "Dashboard and data-visualisation work for an analytics product — and an early lesson in making complex information readable without pretending I was the data scientist.",
    role: "Dashboard & information design",
    year: "2022–2023",
    client: "CrunchIt",
    category: "Data / Product",
    thumbnail: "/images/projects/crunch-placeholder.svg",
    featured: false,
    passwordProtected: false,
    sections: [
      {
        type: "text",
        heading: "The job was to explain the data, not invent it",
        content:
          "Crunch brought me into dashboard and data-visualisation work while I was still moving between college, startup, and freelance projects. The contribution sat at the interface layer: organise dense information, make comparisons easier, and help a person find the signal without flattening everything into one heroic number.",
      },
      {
        type: "image-full",
        images: ["/images/projects/crunch-placeholder.svg"],
        caption: "Project visuals will be added after the original dashboard material is recovered",
      },
      {
        type: "text",
        heading: "I said the quiet part out loud",
        content:
          "In related project conversations, I was clear that I was not deeply trained in data science. I had dashboard experience, curiosity, and the willingness to learn the domain; I did not have a reason to pretend I had built the underlying models. That boundary made the design work better. It kept my attention on the part I could own: how evidence, comparison, status, and uncertainty reached the reader.",
      },
      {
        type: "framework",
        label: "Information-design checklist",
        heading: "A useful dashboard owes the reader four things",
        content:
          "The visuals may change with the domain. These questions survive surprisingly well.",
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
              "Incomplete or ambiguous data should look incomplete or ambiguous. Confidence is part of the information architecture.",
          },
          {
            title: "A next question",
            content:
              "A dashboard becomes more useful when it helps someone move from observation to the next sensible investigation.",
          },
        ],
      },
      {
        type: "text",
        heading: "A small project with a long afterlife",
        content:
          "The work was not as broad as Owly or as deeply documented as Reachify. Its influence is quieter. The same information-design muscle now shows up when I work on citations, source panels, evaluation reports, and AI outputs that need to communicate evidence without acting more certain than they are.",
      },
      {
        type: "stats",
        stats: [
          { label: "Focus", value: "Dashboards" },
          { label: "Contribution", value: "Visualisation" },
          { label: "Domain", value: "Analytics" },
          { label: "Model work", value: "Not claimed" },
        ],
      },
      {
        type: "quote",
        quote:
          "My job was not to make the data look impressive. It was to help someone read it without getting lost.",
        attribution: "Aadith V A",
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
