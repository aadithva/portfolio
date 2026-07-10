# Component Inventory

Atomic-design inventory for the Astro portfolio implementation.
Generated from `design-system/ai/index.json` — do not edit by hand.

## Tokens

- **Source**: `design-system/tokens.css` / `design-system/tokens.json` (`--ds-*` custom properties).
- **Color**: background `#fff`, foreground `#0a0a0a`, muted `#f7f6f3`, muted-fg `#787774`, border `#eaeaea`.
- **Type**: IBM Plex Mono for the interface and Digibop exclusively for the AADITH wordmark.
- **Layout**: `.container` max-width 1440px with responsive side padding (20 / 48 / 80px).
- **Motion**: entrance reveals via the global IntersectionObserver (`.reveal`/`.line`/`.routemap` → `.is-visible`), with reduced-motion fallbacks.

## Atoms

| Component | Path | Purpose | Dependencies | Used by |
|---|---|---|---|---|
| `BrandLockup` | `src/components/atoms/BrandLockup.astro` | Aadith's reusable Digibop wordmark. | — | Footer, Header |
| `DecryptedText` | `src/components/atoms/DecryptedText.js` | React Bits decryption-text atom for newly resolved companion answers. | — | AadithCompanion |
| `GridBackdrop` | `src/components/atoms/GridBackdrop.astro` | Fixed large-cell grid behind the entire portfolio. | — | BaseLayout |
| `LetterGlitch` | `src/components/atoms/LetterGlitch.astro` | Tokenised canvas field of smoothly scrambling monospace characters. | — | Footer |
| `Line` | `src/components/atoms/Line.astro` | Tokenised 1px editorial divider. | — | CaseStudySection, FeaturedWork, ProfileSignals, ProjectNav, route /404, route /about, route /adventures, route /contact, route /lab/[slug], route /work/[parent]/[item], route /writing |
| `PixelTransition` | `src/components/atoms/PixelTransition.astro` | Dependency-free pixel-cover transition for swapping two visual layers. | — | HoverRevealList |
| `Reveal` | `src/components/atoms/Reveal.astro` | Semantic wrapper retained for optional restrained entrance behaviour. | — | CaseStudySection, FeaturedWork, Hero, HoverRevealList, ProfileSignals, ProjectHero, WorkItemIndex, route /404, route /about, route /adventures, route /contact, route /lab, route /lab/[slug], route /work, route /work/[parent]/[item], route /writing |
| `SectionLabel` | `src/components/atoms/SectionLabel.astro` | Small uppercase eyebrow label for section headings. | — | FeaturedWork, ProfileSignals, WorkItemIndex, route /404, route /about, route /contact, route /lab/[slug], route /writing |
| `TrueFocus` | `src/components/atoms/TrueFocus.jsx` | React Bits focus-frame atom for selected words in the homepage statement. | — | Hero |

## Molecules

| Component | Path | Purpose | Dependencies | Used by |
|---|---|---|---|---|
| `CaseStudySection` | `src/components/molecules/CaseStudySection.astro` | Data-driven renderer for case-study blocks: text, image-full, image-grid, stats, quote, and editorial frameworks. | `Line`, `Reveal` | route /work/[parent]/[item], route /work/[slug] |
| `DottedIndiaMap` | `src/components/molecules/DottedIndiaMap.astro` | Accurate dotted India map with the Kashmir-to-Kanyakumari cycling route. | — | route /adventures |
| `HoverRevealList` | `src/components/molecules/HoverRevealList.astro` | Numbered work index with a persistent left thumbnail and orange pixel swaps. | `PixelTransition`, `Reveal` | FeaturedWork, route /work |
| `LabCard` | `src/components/molecules/LabCard.astro` | Ranked editorial row for a shortlisted Lab project. | `shots` | route /lab |
| `WorkingLoopMap` | `src/components/molecules/WorkingLoopMap.astro` | Linked working-loop diagram for the Lab overview. | — | route /lab |

## Organisms

| Component | Path | Purpose | Dependencies | Used by |
|---|---|---|---|---|
| `AadithCompanion` | `src/components/organisms/AadithCompanion.astro` | Playful public-context portfolio sidekick with a responsive drawer fallback. | `DecryptedText`, `companion` | BaseLayout |
| `FeaturedWork` | `src/components/organisms/FeaturedWork.astro` | Homepage 'Selected Work' organism: section label plus the featured project list. | `HoverRevealList`, `Line`, `Reveal`, `SectionLabel`, `projects` | route / |
| `Footer` | `src/components/organisms/Footer.astro` | Global footer with a full-canvas orange glitch signature, identity, social links, and secondary nav. | `BrandLockup`, `LetterGlitch`, `siteConfig` | BaseLayout |
| `Header` | `src/components/organisms/Header.astro` | Static mono editorial header with Aadith's wordmark and wrapping primary navigation. | `BrandLockup`, `navigation`, `siteConfig` | BaseLayout |
| `Hero` | `src/components/organisms/Hero.astro` | Homepage hero: compact mono positioning and role line. | `Reveal`, `TrueFocus` | route / |
| `ProfileSignals` | `src/components/organisms/ProfileSignals.astro` | Homepage proof section connecting enterprise AI, founder work, and design-to-code practice. | `Line`, `Reveal`, `SectionLabel` | route / |
| `ProjectHero` | `src/components/organisms/ProjectHero.astro` | Case-study hero: title, Role/Year/Client/Category meta, and hero image. | `Reveal` | route /work/[slug] |
| `ProjectNav` | `src/components/organisms/ProjectNav.astro` | Previous/next navigation between work case studies. | `Line` | route /work/[slug] |
| `WorkGate` | `src/components/organisms/WorkGate.astro` | Reusable password gate for protected Microsoft work pages. | — | route /work/[parent]/[item], route /work/[slug] |
| `WorkItemIndex` | `src/components/organisms/WorkItemIndex.astro` | Editorial child-project index for multi-part Work chapters. | `Reveal`, `SectionLabel` | route /work/[slug] |

## Layouts

| Component | Path | Purpose | Dependencies | Used by |
|---|---|---|---|---|
| `BaseLayout` | `src/layouts/BaseLayout.astro` | App shell: document head, mono typography, route-aware companion, header/footer, and global client behaviour. | `AadithCompanion`, `Footer`, `GridBackdrop`, `Header`, `siteConfig` | route /, route /404, route /about, route /adventures, route /contact, route /lab, route /lab/[slug], route /work, route /work/[parent]/[item], route /work/[slug], route /writing |

## Routes

| Route | Page file | Imported components |
|---|---|---|
| `/404` | `src/pages/404.astro` | `Line`, `Reveal`, `SectionLabel`, `BaseLayout` |
| `/about` | `src/pages/about.astro` | `Line`, `Reveal`, `SectionLabel`, `BaseLayout` |
| `/adventures` | `src/pages/adventures.astro` | `Line`, `Reveal`, `DottedIndiaMap`, `BaseLayout` |
| `/contact` | `src/pages/contact.astro` | `Line`, `Reveal`, `SectionLabel`, `BaseLayout` |
| `/` | `src/pages/index.astro` | `FeaturedWork`, `Hero`, `ProfileSignals`, `BaseLayout` |
| `/lab` | `src/pages/lab.astro` | `Reveal`, `LabCard`, `WorkingLoopMap`, `BaseLayout` |
| `/lab/[slug]` | `src/pages/lab/[slug].astro` | `Line`, `Reveal`, `SectionLabel`, `BaseLayout` |
| `/work` | `src/pages/work.astro` | `Reveal`, `HoverRevealList`, `BaseLayout` |
| `/work/[parent]/[item]` | `src/pages/work/[parent]/[item].astro` | `Line`, `Reveal`, `CaseStudySection`, `WorkGate`, `BaseLayout` |
| `/work/[slug]` | `src/pages/work/[slug].astro` | `CaseStudySection`, `ProjectHero`, `ProjectNav`, `WorkGate`, `WorkItemIndex`, `BaseLayout` |
| `/writing` | `src/pages/writing.astro` | `Line`, `Reveal`, `SectionLabel`, `BaseLayout` |
