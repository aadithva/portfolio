# Design-System Adoption Report

Generated from `design-system/ai/index.json` and `design-system/ai/metadata/` by `adoption-report.py`. Re-run after code changes.

## Freshness

- Index version: `0.2.0` (astro)
- Index generated at: `2026-07-10T02:55:18.641867+00:00`
- Metadata files: 19 (BaseLayout, BrandLockup, CaseStudySection, DottedIndiaMap, FeaturedWork, Footer, GridBackdrop, Header, Hero, HoverRevealList, LabCard, Line, ProfileSignals, ProjectHero, ProjectNav, Reveal, SectionLabel, WorkGate, WorkItemIndex)
- Caveat: utilization is static import-based; dynamic or runtime-only references may need manual review.

## Index stats

- Components scanned: **19**
- Routes scanned: **11**
- Data/helper files scanned: **14**
- Approx index token size: **4824 tokens**
- Duplicate page filenames preserved by full-path keys: **[slug].astro**

### Tier distribution

- Atoms: **5**
- Layouts: **1**
- Molecules: **4**
- Organisms: **9**

## Component utilization

Static import utilization: **19 used / 19 total** (100%).

### Components with direct usage

- `BrandLockup` (`src/components/atoms/BrandLockup.astro`) — used by Footer, Header.
- `GridBackdrop` (`src/components/atoms/GridBackdrop.astro`) — used by BaseLayout.
- `Line` (`src/components/atoms/Line.astro`) — used by CaseStudySection, FeaturedWork, ProfileSignals, ProjectNav, route /404, route /about, route /adventures, route /contact, route /lab/[slug], route /work/[parent]/[item], route /writing.
- `Reveal` (`src/components/atoms/Reveal.astro`) — used by CaseStudySection, FeaturedWork, Hero, HoverRevealList, ProfileSignals, ProjectHero, WorkItemIndex, route /404, route /about, route /adventures, route /contact, route /lab, route /lab/[slug], route /work, route /work/[parent]/[item], route /writing.
- `SectionLabel` (`src/components/atoms/SectionLabel.astro`) — used by FeaturedWork, ProfileSignals, WorkItemIndex, route /404, route /about, route /contact, route /lab/[slug], route /writing.
- `CaseStudySection` (`src/components/molecules/CaseStudySection.astro`) — used by route /work/[parent]/[item], route /work/[slug].
- `DottedIndiaMap` (`src/components/molecules/DottedIndiaMap.astro`) — used by route /adventures.
- `HoverRevealList` (`src/components/molecules/HoverRevealList.astro`) — used by FeaturedWork, route /work.
- `LabCard` (`src/components/molecules/LabCard.astro`) — used by route /lab.
- `FeaturedWork` (`src/components/organisms/FeaturedWork.astro`) — used by route /.
- `Footer` (`src/components/organisms/Footer.astro`) — used by BaseLayout.
- `Header` (`src/components/organisms/Header.astro`) — used by BaseLayout.
- `Hero` (`src/components/organisms/Hero.astro`) — used by route /.
- `ProfileSignals` (`src/components/organisms/ProfileSignals.astro`) — used by route /.
- `ProjectHero` (`src/components/organisms/ProjectHero.astro`) — used by route /work/[slug].
- `ProjectNav` (`src/components/organisms/ProjectNav.astro`) — used by route /work/[slug].
- `WorkGate` (`src/components/organisms/WorkGate.astro`) — used by route /work/[parent]/[item], route /work/[slug].
- `WorkItemIndex` (`src/components/organisms/WorkItemIndex.astro`) — used by route /work/[slug].
- `BaseLayout` (`src/layouts/BaseLayout.astro`) — used by route /, route /404, route /about, route /adventures, route /contact, route /lab, route /lab/[slug], route /work, route /work/[parent]/[item], route /work/[slug], route /writing.

### Components not directly imported

- None — every component is imported somewhere.

## Metadata coverage

Components documented in `metadata/`: **19 / 19**.

## Automated risk flags

- No structural risks detected: all components are used and documented.

## Adoption summary

The Astro portfolio runs an organism-led system: a `BaseLayout` shell, a data-driven `CaseStudySection`, the `HoverRevealList` work index, and the `LabCard` Lab grid are reusable and consistently tokenized. 19/19 components are imported and 19/19 are documented. The maintenance priority is to re-run the index/metadata/report generators on every component change so AI assistants keep choosing existing high-craft patterns before inventing new UI.
