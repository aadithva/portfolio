# Design-System Adoption Report

Generated from `design-system/ai/index.json` and `design-system/ai/metadata/` by `adoption-report.py`. Re-run after code changes.

## Freshness

- Index version: `0.2.0` (astro)
- Index generated at: `2026-09-12T18:16:31.749454+00:00`
- Metadata files: 23 (BaseLayout, BrandLockup, CaseStudySection, DottedIndiaMap, FeaturedWork, Footer, GridBackdrop, Header, Hero, HoverRevealList, LabCard, LetterGlitch, Line, PixelTransition, ProfileSignals, ProjectHero, ProjectNav, Reveal, SectionLabel, TrueFocus, WorkGate, WorkItemIndex, WorkingLoopMap)
- Caveat: utilization is static import-based; dynamic or runtime-only references may need manual review.

## Index stats

- Components scanned: **24**
- Routes scanned: **12**
- Data/helper files scanned: **22**
- Approx index token size: **6041 tokens**
- Duplicate page filenames preserved by full-path keys: **[slug].astro**

### Tier distribution

- Atoms: **8**
- Other components: **1**
- Layouts: **1**
- Molecules: **5**
- Organisms: **9**

## Component utilization

Static import utilization: **21 used / 24 total** (88%).

### Components with direct usage

- `BrandLockup` (`src/components/atoms/BrandLockup.astro`) — used by Footer, Header.
- `GridBackdrop` (`src/components/atoms/GridBackdrop.astro`) — used by BaseLayout.
- `LetterGlitch` (`src/components/atoms/LetterGlitch.astro`) — used by Footer.
- `Line` (`src/components/atoms/Line.astro`) — used by CaseStudySection, FeaturedWork, ProfileSignals, ProjectNav, route /404, route /about, route /adventures, route /contact, route /lab/[slug], route /work/[parent]/[item], route /writing.
- `PixelTransition` (`src/components/atoms/PixelTransition.astro`) — used by HoverRevealList.
- `Reveal` (`src/components/atoms/Reveal.astro`) — used by CaseStudySection, FeaturedWork, Hero, HoverRevealList, ProfileSignals, ProjectHero, WorkItemIndex, route /404, route /about, route /adventures, route /contact, route /lab, route /lab/[slug], route /work, route /work/[parent]/[item], route /writing.
- `SectionLabel` (`src/components/atoms/SectionLabel.astro`) — used by FeaturedWork, ProfileSignals, WorkItemIndex, route /404, route /about, route /contact, route /lab/[slug], route /writing.
- `TrueFocus` (`src/components/atoms/TrueFocus.jsx`) — used by Hero.
- `CaseStudySection` (`src/components/molecules/CaseStudySection.astro`) — used by route /work/[parent]/[item], route /work/[slug].
- `DottedIndiaMap` (`src/components/molecules/DottedIndiaMap.astro`) — used by route /adventures.
- `HoverRevealList` (`src/components/molecules/HoverRevealList.astro`) — used by FeaturedWork, route /work.
- `LabCard` (`src/components/molecules/LabCard.astro`) — used by route /lab.
- `WorkingLoopMap` (`src/components/molecules/WorkingLoopMap.astro`) — used by route /lab.
- `Footer` (`src/components/organisms/Footer.astro`) — used by BaseLayout.
- `Header` (`src/components/organisms/Header.astro`) — used by BaseLayout.
- `ProjectHero` (`src/components/organisms/ProjectHero.astro`) — used by route /work/[slug].
- `ProjectNav` (`src/components/organisms/ProjectNav.astro`) — used by route /work/[slug].
- `WorkGate` (`src/components/organisms/WorkGate.astro`) — used by route /work/[parent]/[item], route /work/[slug].
- `WorkItemIndex` (`src/components/organisms/WorkItemIndex.astro`) — used by route /work/[slug].
- `WorkspaceContent` (`src/components/workspace/WorkspaceContent.astro`) — used by route /.
- `BaseLayout` (`src/layouts/BaseLayout.astro`) — used by route /404, route /about, route /achievements, route /adventures, route /contact, route /lab, route /lab/[slug], route /work, route /work/[parent]/[item], route /work/[slug], route /writing.

### Components not directly imported

- `FeaturedWork` (`src/components/organisms/FeaturedWork.astro`).
- `Hero` (`src/components/organisms/Hero.astro`).
- `ProfileSignals` (`src/components/organisms/ProfileSignals.astro`).

## Metadata coverage

Components documented in `metadata/`: **23 / 24**.

Missing metadata: `WorkspaceContent`.

## Automated risk flags

- Unused component `FeaturedWork` — confirm it is intentional or remove it.
- Unused component `Hero` — confirm it is intentional or remove it.
- Unused component `ProfileSignals` — confirm it is intentional or remove it.
- `WorkspaceContent` has no metadata entry — AI selection guidance is incomplete.

## Adoption summary

The Astro portfolio runs an organism-led system: a `BaseLayout` shell, a data-driven `CaseStudySection`, the `HoverRevealList` work index, and the `LabCard` Lab grid are reusable and consistently tokenized. 21/24 components are imported and 23/24 are documented. The maintenance priority is to re-run the index/metadata/report generators on every component change so AI assistants keep choosing existing high-craft patterns before inventing new UI.
