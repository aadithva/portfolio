# Exact ThreeUI paper and desk camera controls

Production validation, 2026-09-13:

- All six registered source checksums match; see source-validation.json.
- Production iframe srcDoc matches canonical SHA-256 8ec1b71c0dbcafbadf908100ae2a08045d0a1087c00a09d28245ef19366c7353 on desktop and mobile.
- Original bundled runtime is Three.js r149. Its shader, artwork, motion and sandbox are unmodified.
- Typecheck passes, 33 static pages build, all 30 browser tests pass.
- Production captures at 1440×1000 and 390×844 report no JavaScript errors or horizontal overflow.
- Verified expanded paper, drag and hover, Escape, browser history, live reduced motion, native HTML fallback, bounded camera drag, wheel/pinch zoom, keyboard controls and click suppression.
- capture.mjs waits for the source canvas to resize and paint before expanded screenshots. capture.json contains browser measurements.

The registered Original includes Nocturne demo artwork. A visible ThreeUI study caption separates that from actual portfolio content. Source provenance is in vendor/threeui. The obsolete approximation in src/lib/ui/paper-surface.ts was removed.
