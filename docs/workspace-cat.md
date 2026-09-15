# Workspace cat

## Selected asset

Aadith selected **Rigged and animated Cat** by **JonasDichelle**, preserving its
calico appearance, for the interactive workspace.

- Original: https://blendswap.com/blend/18519
- Original download: https://blendswap.com/blend/18519/download
- License: Creative Commons Attribution 3.0 Unported, according to the
  accompanying license in the public FBX distribution.
- License URL: https://creativecommons.org/licenses/by/3.0/
- Required credit: "Rigged and animated Cat by JonasDichelle, CC BY 3.0.
  Adapted for this website." Link the asset and license when publishing.

## Current implementation, 15 September 2026

### Floor-only revision, current

The user removed all furniture jumps and all added fur. The active GLB contains
only the matte body, eyes, and Idle/Walk clips. The original markings remain.
`cat-fur.ts` now only applies the matte material treatment; it adds no geometry.
Earlier fur/jump authoring code and review images are historical experiments.

The route crosses in front of the chair from right to left, pauses twice, leaves
on the left, waits 5–12 seconds, then returns left to right. Reduced motion rests
on the floor. Mobile overview framing is wider and lower to include this route.
The chair retains its previously requested 18-degree runtime adjustment.

A projected native button follows the cat and supports click, touch, Enter and
Space. Petting pauses its movement briefly and triggers `DeskAudio.meow()`, a
locally synthesized voiced sound. It works without enabling ambient music and
has a 1.1-second repeat limit. No audio autoplays. The Desk guide explains it.

Current checks cover floor-only routes, opposite-side returns, pointer and
keyboard meow activation, reduced motion, content pausing, and asset failure.
`verified-wandering.png` and `verified-mobile-day.png` show the current version.

### Earlier chair-only revision

The latest routine visits only the floor and chair. All desk destinations are
removed. The chair starts 18 degrees more open toward the room in the runtime;
its measured cushion anchor is preserved in local coordinates before rotating.
The cat keeps its landing heading while settling and sitting. It turns with
stepping feet only after standing up, before descending.

`cat-motion.json` shares timing between the Blender pose generator and runtime.
Chair jumps have planted preparation, a 0.4 second ballistic ascent, front-paw
contact, delayed hind-paw placement, and a cushioning phase. Descent has its own
pose timing. `cat_jump_animation.py` uses limb IK and body pitch rather than the
old simultaneous four-leg reach. These are authored approximations, not motion
capture.

Full-body alpha-masked fur cards and a skinned undercoat replace sparse spikes.
The undercoat uses eight layers on desktop and five on mobile. Coat materials
have roughness 1, zero specular response, no sheen or clearcoat, and no glossy
environment contribution. Eyes retain their separate material. Body lighting
remains diffuse so the cat retains its shape under the room lights.

References inspected: Wang et al., *Kinetic analysis of felines landing from
different heights*, PeerJ 2019, Figure 1, CC BY 4.0:
https://pmc.ncbi.nlm.nih.gov/articles/PMC6857581/
The sequence shows forelimb contact preceding hindlimb contact. Also consulted
Zhang et al., *Analysis of Cushioned Landing Strategies of Cats Based on Posture
Estimation*, 2024: https://doi.org/10.3390/biomimetics9110691
The Slow Mo Guys reference was located at
https://www.youtube.com/watch?v=-xN12kR4TLc but its video download returned 403,
so no claim of direct video analysis is made.

Current visual proof: `review-fur-closeup.png`, `review-jump-*.png`,
`browser-sitting-on-chair.png`, `browser-pausing-on-rug.png`, and the most recent
recorded routine under `video/`. Earlier desk screenshots are historical.

The homepage loads `public/models/workspace-cat.glb` after the room is ready.
`src/lib/workspace/cat.ts` controls the routine and `scene.ts` advances its clock.
The original downloaded archive was found at
`/Users/aadith/Downloads/Rigged and animated Cat.zip` and extracted to
`artifacts/workspace/cat/source/`. The room master was not modified.

The original contains its skeleton, Walk and run actions, and packed textures.
The web adaptation preserves the calico body map, uses short skinned fur ribbons,
and rebuilds the green eyes and pupils. Fur is shorter and simpler than the
original Cycles render. The 84-bone legacy rig is sampled into independent bones
to remove runtime IK dependencies. Self-referential Tail copy-rotation and Spine
pivot constraints are removed during preparation.

Eight exported clips: Walk, Run, Idle, Sit, SitDown, StandUp, Jump and JumpDown.
Sitting and jumping are new authored adaptations. Furniture traversal uses
scripted crouch/reach/landing hops and measured landing points rather than a
general collision engine or physically simulated climbing.

The first visit includes the floor, chair, desktop, chair again, floor, then an
offscreen departure. Later visits vary the chair rest and sometimes skip the
desktop. Offscreen waits last 5–12 seconds. The seat anchor follows the chair's
world transform. The cat pauses when content or the computer is open, or the tab
is hidden. Reduced motion gives it a static seated pose. The model loads
independently, so a cat download failure does not block the room.

Public attribution is in the Desk guide, with source and license links. The GLB
also includes creator, source, license and adaptation metadata.

## Rebuild and verification

```sh
"/Applications/Blender.app/Contents/MacOS/Blender" --background --disable-autoexec \
  --python-exit-code 1 --python scripts/blender/export_workspace_cat.py
npm run check:workspace
npm run test:workspace -- tests/workspace-cat.spec.ts
npm run build
node scripts/capture-workspace-cat.mjs
```

The export script saves the editable adaptation as
`artifacts/workspace/cat/cat-web.blend`. The source is read with embedded script
execution disabled. `export.json` records clip durations and export size.
`measure_cat_contacts.py` surveys the current saved furniture without saving it.
If furniture moves, remeasure and update the route anchors in `cat.ts`.

Evidence under `artifacts/workspace/cat/` includes original-file inspection,
pose renders, desktop and mobile screenshots, a recorded routine in `video/`,
and `browser-report.json`. Four browser checks cover a full return cycle, chair
rotation, reduced-motion changes, content pausing, asset failure and attribution.
The production build generates 33 pages.

## Earlier acquisition attempt

The original download required BlendSwap sign-in, so a public derivative was
inspected before Aadith supplied the original archive.

A credited FBX derivative was downloaded from the public Ylikuutio repository:

https://github.com/nrz/ylikuutio/tree/master/res/objects/www.blendswap.com/86110_rigged_and_animated_cat

Local inspection files:

- `artifacts/workspace/cat/source/cat.fbx`
- `artifacts/workspace/cat/source/LICENSE.html`

Blender inspection found one mesh, 22,650 vertices, three materials, no armature,
no vertex groups, no animation actions, and no texture images. This derivative
does not preserve the features needed for the selected animated, textured cat.
It is not installed on the website.

Inspect the supplied original with:

```sh
"/Applications/Blender.app/Contents/MacOS/Blender" --background \
  --python-exit-code 1 --python scripts/blender/inspect_workspace_cat.py
```
