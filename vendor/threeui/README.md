# Registered ThreeUI 3D Paper source

Fetched from https://threeui.com/source-code/3d-paper.json on 2026-09-13 at the user's request.

All six files under src/shaders are byte-for-byte registered sources, verified against source-manifest.json. The local package entry and package.json expose the configured import paths to this Astro project. They are integration files, not claimed upstream files.

The Original component supplies its own srcDoc sandbox and bundled Three.js r149. No ThreeUI documentation page is embedded. Runtime code, shaders, style, font URLs and variants remain unmodified. The application now derives its portfolio document from the canonical HTML through src/lib/ui/portfolio-paper-source.ts. This replaces certificate printing and adds portfolio navigation while retaining the original glass shader, lighting, and bending model. The canonical files in this vendor folder remain unmodified.

The canonical demo contains Nocturne Studio certificate artwork. The active portfolio adaptation is reserved for achievements. It opens with the user's original IIT Guwahati graduation certificate, then documented milestone content. Other sections use ordinary HTML panels. Certificate pages use a matte material and a portrait sheet ratio while retaining the original bending shader and deliberate drag interaction. Its transparent background shows the existing desk scene behind the paper, replacing the demo's black background and oversized wordmark.

Retain the Three.js authors' embedded MIT notice. That notice applies to the bundled Three.js runtime; it does not establish the license of the other authoring code in this source bundle.
