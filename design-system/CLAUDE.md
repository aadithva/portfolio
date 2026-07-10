# CLAUDE.md — AI Instructions for This Portfolio Design System

Before editing UI in this repository:

1. Load `design-system/ai/index.json` to understand available components, pages, dependencies, and usage locations.
2. Load relevant files from `design-system/ai/metadata/` for component What/How/Why, usage guidance, and anti-patterns.
3. Follow `design-system/ai/ds-composer.md`: choose organisms first, molecules second, atoms last.
4. Reuse existing components and data before writing raw HTML or new one-off UI.
5. Respect `design-system/tokens.css` and `design-system/tokens.json` for color, typography, spacing, radii, container, motion, and breakpoints.
6. Preserve reduced-motion behavior for all motion-heavy UI.
7. Use full relative paths as unique identifiers in generated artifacts; never key by filename stem.
8. If components/pages change, rerun both generators (index first, then metadata):

```bash
python3 design-system/ai/codebase-index.py
python3 design-system/ai/component-metadata.py
```

9. Check version stamps (`generatedAt`, `lastUpdated`) before trusting generated artifacts. If stale, regenerate or verify against source.
10. When adding or changing reusable components, update metadata and future validation/adoption reports.

The runtime is **Astro** (static output). Components live under `src/components/{atoms,molecules,organisms}`, the shell under `src/layouts`, routes under `src/pages`, and data/helpers under `src/data` and `src/lib`. Entrance motion is driven by the global IntersectionObserver in `BaseLayout` (`.reveal`/`.line`/`.routemap` → `.is-visible`); do not reintroduce GSAP/Framer/Lenis. This `design-system/` folder is an additive AI/design-system foundation that mirrors `src/`.
