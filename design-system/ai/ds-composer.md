# Design-System Composer: Reasoning Layer

This is the selection logic AI assistants should follow before creating UI in this
Astro codebase. Components live under `src/components/{atoms,molecules,organisms}`,
the shell under `src/layouts`, routes under `src/pages`, and data/helpers under
`src/data` and `src/lib`.

## Hierarchical decision framework

1. **Start with the layout / organisms**
   - Every route is wrapped by the `BaseLayout` shell (head, fonts, `Header`, `Footer`,
     scroll-reveal + mobile-menu JS). Pass `bare` for gated/standalone screens.
   - For full sections, prefer `Hero`, `FeaturedWork`, `ProjectHero`, or `ProjectNav`
     when the goal matches their intent.

2. **Work down to molecules**
   - Reuse a molecule pattern: `HoverRevealList` (numbered work list), `LabCard`
     (Lab grid card), or `CaseStudySection` (data-driven case-study block).
   - Keep molecule behavior aligned with existing typography, spacing, borders, and hover states.

3. **Reach for atoms last**
   - Use atoms (`Reveal` for entrance motion, `Line` for animated dividers,
     `SectionLabel` for uppercase eyebrows) to assemble a missing molecule or organism.
   - Avoid raw animation code: the global IntersectionObserver in `BaseLayout` drives
     `.reveal`, `.line`, and `.routemap`. Do not add GSAP/Framer/Lenis back in.

4. **Build custom only after fit checks**
   - Custom UI is appropriate when no existing organism or molecule matches the semantic
     purpose, content model, interaction model, or accessibility requirement.
   - New custom UI should still use `--ds-*` tokens, container rhythm, reduced-motion
     behavior, and should be documented in metadata.

## Decision checklist

- What route/page owns this UI?
- Is this a complete section? Try an organism first.
- Is this a repeated row/card/content block? Try a molecule (`HoverRevealList`, `LabCard`, `CaseStudySection`).
- Is this just reveal, divider, or eyebrow-label behavior? Use an atom (`Reveal`, `Line`, `SectionLabel`).
- Does the data already exist in `src/data/projects.ts`, `lab.ts`, `navigation.ts`, or `siteConfig.ts`?
- For Lab screenshots, are you reading them via `src/lib/shots.ts` (`getShots`/`getThumb`)?
- Are full relative paths used as keys when regenerating `index.json`?
- Are token values used instead of one-off colors/type/spacing?
- Does motion respect reduced-motion (content present in DOM, only opacity/transform animates)?
- Should metadata be added or updated?

## Worked examples

### Example 1: Add a selected-work section to another page

Need: show featured projects under an about narrative.

Decision:
1. Use organism `FeaturedWork` if the full selected-work section is acceptable.
2. If the heading/spacing must differ, compose molecule `HoverRevealList` with
   `getFeaturedProjects()` and wrap intro copy in `Reveal`.
3. Do not rebuild the numbered-row markup; `HoverRevealList` already owns it.

### Example 2: Add a new case-study content type for metrics

Need: display four metrics inside a project case study.

Decision:
1. Use `CaseStudySection` with `type: "stats"` in `src/data/projects.ts` if the data model fits.
2. The molecule composes `Line` and `Reveal` for the divider and staggered reveal.
3. Only create a new section type if the metrics need a meaningfully different layout.

### Example 3: Add a new Lab project

Need: surface another vibe-coded project in the Lab.

Decision:
1. Add the record to `src/data/lab.json` (slug, title, tagline, when, built_with,
   category, status, ui_type, story, capabilities, tech, routes, repo_url).
2. Drop screenshots into `public/shots/<slug>/` named `<slug>__<route>-<kind>.png`;
   `LabCard` and `/lab/[slug]` pick them up via `src/lib/shots.ts` automatically.
3. The Lab index groups by `category` via `getLabByCategory()`; no markup changes needed.

### Example 4: Add a compact editorial page

Need: create a writing/detail page with title, intro, divider, and text blocks.

Decision:
1. Follow the existing `writing`/`contact`/`about` page patterns.
2. Compose with `.container`, heading tokens, `Reveal`, `SectionLabel`, and `Line`.
3. Use the `.inline-link` / `.elsewhere-link` primitives for links.
4. Add metadata if the pattern becomes reusable.

## When to build custom

Build new components when:

- The UI has a distinct semantic role not covered by existing organisms/molecules.
- Existing components would require prop abuse or hidden conditionals.
- Accessibility requirements differ materially.
- The component will be reused in at least two contexts or clarifies a page template.

When adding custom UI:

1. Place it in the correct atomic folder: `src/components/atoms`, `molecules`, or
   `organisms` (or `src/layouts` for a shell).
2. Use tokenized colors, type, spacing, motion, and container widths.
3. Rerun `python3 design-system/ai/codebase-index.py` then
   `python3 design-system/ai/component-metadata.py` to refresh the index and metadata.
4. Update the adoption analysis if it changes utilization or introduces duplicated patterns.
