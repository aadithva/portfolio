# Design-System Adoption Report

Generated from `design-system/ai/index.json` and `design-system/ai/metadata/` by `adoption-report.py`. Re-run after code changes.

## Freshness

- Index version: `0.2.0` (astro)
- Index generated at: `2026-09-15T08:53:39.659824+00:00`
- Metadata files: 23 (BaseLayout, BrandLockup, CaseStudySection, DottedIndiaMap, FeaturedWork, Footer, GridBackdrop, Header, Hero, HoverRevealList, LabCard, LetterGlitch, Line, PixelTransition, ProfileSignals, ProjectHero, ProjectNav, Reveal, SectionLabel, TrueFocus, WorkGate, WorkItemIndex, WorkingLoopMap)
- Caveat: utilization is static import-based; dynamic or runtime-only references may need manual review.

## Index stats

- Components scanned: **26**
- Routes scanned: **13**
- Data/helper files scanned: **32**
- Approx index token size: **7052 tokens**
- Duplicate page filenames preserved by full-path keys: **[slug].astro**

### Tier distribution

- Atoms: **8**
- Other components: **3**
- Layouts: **1**
- Molecules: **5**
- Organisms: **9**

## Component utilization

Static import utilization: **18 used / 26 total** (69%).

### Components with direct usage

- `Line` (`src/components/atoms/Line.astro`) — used by CaseStudySection, FeaturedWork, ProfileSignals, ProjectNav, route /404, route /about, route /adventures, route /contact, route /lab/[slug], route /work/[parent]/[item], route /writing.
- `Reveal` (`src/components/atoms/Reveal.astro`) — used by CaseStudySection, FeaturedWork, Hero, ProfileSignals, ProjectHero, WorkItemIndex, route /404, route /about, route /adventures, route /contact, route /lab, route /lab/[slug], route /work, route /work/[parent]/[item], route /writing.
- `SectionLabel` (`src/components/atoms/SectionLabel.astro`) — used by FeaturedWork, ProfileSignals, WorkItemIndex, route /404, route /about, route /contact, route /lab/[slug], route /writing.
- `TrueFocus` (`src/components/atoms/TrueFocus.jsx`) — used by Hero.
- `CaseStudySection` (`src/components/molecules/CaseStudySection.astro`) — used by route /work/[parent]/[item], route /work/[slug].
- `DottedIndiaMap` (`src/components/molecules/DottedIndiaMap.astro`) — used by WorkspaceContent, route /adventures, route /expeditions.
- `HoverRevealList` (`src/components/molecules/HoverRevealList.astro`) — used by FeaturedWork, route /work.
- `LabCard` (`src/components/molecules/LabCard.astro`) — used by route /lab.
- `WorkingLoopMap` (`src/components/molecules/WorkingLoopMap.astro`) — used by route /lab.
- `Footer` (`src/components/organisms/Footer.astro`) — used by BaseLayout.
- `Header` (`src/components/organisms/Header.astro`) — used by BaseLayout.
- `ProjectHero` (`src/components/organisms/ProjectHero.astro`) — used by route /work/[slug].
- `ProjectNav` (`src/components/organisms/ProjectNav.astro`) — used by route /work/[slug].
- `WorkGate` (`src/components/organisms/WorkGate.astro`) — used by route /work/[parent]/[item], route /work/[slug].
- `WorkItemIndex` (`src/components/organisms/WorkItemIndex.astro`) — used by route /work/[slug].
- `ComputerDesktop` (`src/components/workspace/ComputerDesktop.astro`) — used by route /.
- `WorkspaceContent` (`src/components/workspace/WorkspaceContent.astro`) — used by route /.
- `BaseLayout` (`src/layouts/BaseLayout.astro`) — used by route /404, route /about, route /achievements, route /adventures, route /contact, route /expeditions, route /lab, route /lab/[slug], route /work, route /work/[parent]/[item], route /work/[slug], route /writing.

### Components not directly imported

- `BrandLockup` (`src/components/atoms/BrandLockup.astro`).
- `GridBackdrop` (`src/components/atoms/GridBackdrop.astro`).
- `LetterGlitch` (`src/components/atoms/LetterGlitch.astro`).
- `PixelTransition` (`src/components/atoms/PixelTransition.astro`).
- `FeaturedWork` (`src/components/organisms/FeaturedWork.astro`).
- `Hero` (`src/components/organisms/Hero.astro`).
- `ProfileSignals` (`src/components/organisms/ProfileSignals.astro`).
- `ThreeUIPaperScene` (`src/components/workspace/ThreeUIPaperScene.tsx`).

## Metadata coverage

Components documented in `metadata/`: **23 / 26**.

Missing metadata: `ComputerDesktop`, `ThreeUIPaperScene`, `WorkspaceContent`.

## Automated risk flags

- Unused component `BrandLockup` — confirm it is intentional or remove it.
- Unused component `GridBackdrop` — confirm it is intentional or remove it.
- Unused component `LetterGlitch` — confirm it is intentional or remove it.
- Unused component `PixelTransition` — confirm it is intentional or remove it.
- Unused component `FeaturedWork` — confirm it is intentional or remove it.
- Unused component `Hero` — confirm it is intentional or remove it.
- Unused component `ProfileSignals` — confirm it is intentional or remove it.
- Unused component `ThreeUIPaperScene` — confirm it is intentional or remove it.
- `ComputerDesktop` has no metadata entry — AI selection guidance is incomplete.
- `ThreeUIPaperScene` has no metadata entry — AI selection guidance is incomplete.
- `WorkspaceContent` has no metadata entry — AI selection guidance is incomplete.

## Adoption summary

The Astro portfolio runs an organism-led system: a `BaseLayout` shell, a data-driven `CaseStudySection`, the `HoverRevealList` work index, and the `LabCard` Lab grid are reusable and consistently tokenized. 18/26 components are imported and 23/26 are documented. The maintenance priority is to re-run the index/metadata/report generators on every component change so AI assistants keep choosing existing high-craft patterns before inventing new UI.
