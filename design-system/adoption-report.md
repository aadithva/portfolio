# Design-System Adoption Report

Generated from `design-system/ai/index.json` and `design-system/ai/metadata/` by `adoption-report.py`. Re-run after code changes.

## Freshness

- Index version: `0.2.0` (astro)
- Index generated at: `2026-09-02T06:50:38.952292+00:00`
- Metadata files: 25 (AadithCompanion, BaseLayout, BrandLockup, CaseStudySection, DecryptedText, DottedIndiaMap, FeaturedWork, Footer, GridBackdrop, Header, Hero, HoverRevealList, LabCard, LetterGlitch, Line, PixelTransition, ProfileSignals, ProjectHero, ProjectNav, Reveal, SectionLabel, TrueFocus, WorkGate, WorkItemIndex, WorkingLoopMap)
- Caveat: utilization is static import-based; dynamic or runtime-only references may need manual review.

## Index stats

- Components scanned: **25**
- Routes scanned: **11**
- Data/helper files scanned: **19**
- Approx index token size: **5764 tokens**
- Duplicate page filenames preserved by full-path keys: **[slug].astro**

### Tier distribution

- Atoms: **9**
- Layouts: **1**
- Molecules: **5**
- Organisms: **10**

## Component utilization

Static import utilization: **25 used / 25 total** (100%).

### Components with direct usage

- `BrandLockup` (`src/components/atoms/BrandLockup.astro`) — used by Footer, Header.
- `DecryptedText` (`src/components/atoms/DecryptedText.js`) — used by AadithCompanion.
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
- `AadithCompanion` (`src/components/organisms/AadithCompanion.astro`) — used by BaseLayout.
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

Components documented in `metadata/`: **25 / 25**.

## Automated risk flags

- No structural risks detected: all components are used and documented.

## Adoption summary

The Astro portfolio runs an organism-led system: a `BaseLayout` shell, a data-driven `CaseStudySection`, the `HoverRevealList` work index, and the `LabCard` Lab grid are reusable and consistently tokenized. 25/25 components are imported and 25/25 are documented. The maintenance priority is to re-run the index/metadata/report generators on every component change so AI assistants keep choosing existing high-craft patterns before inventing new UI.
