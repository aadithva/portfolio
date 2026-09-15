# Ride for Unity medal

The three generic medal families have been replaced by one medal based on the user's photograph of the Ride for Unity, Kashmir to Kanyakumari medal. The stable interaction root is `medal_1`. `medal_2`, `medal_3` and their descendants are removed. Both trophies remain.

Clicking the medal opens `#desk-achievements/ride-for-unity`, showing its own photo
and verified ride details on the achievement sheet. The `medal-detail` camera
view focuses on the medal. The framed IIT Guwahati certificate and the general
Achievements menu keep their own destinations.

The original 3120 × 4160 JPEG is copied byte-for-byte to `public/textures/workspace/ride-for-unity-medal.jpg`. Its SHA-256 is `25e1e002c86362fbae856ea669d7e405d6fa7f96887fb961bd07cc36ce2db65f`. No image crop, retouch, AI recreation or replacement lettering is used. Photo-coordinate traces define the mesh perimeter and UVs, which address the unchanged full-resolution image directly. The face and Fit India ribbon both retain the original photo bytes in the GLB.

The metal outline follows the rounded upper plate, statue silhouettes, wide curved title banner and rounded lower boat panel. The body has real thickness and beveled brass edges. The banner, mountain and bicycle rims have shallow physical relief with matching photo UVs. Other fine relief and printed lettering remain photographic detail, including the photo's existing highlights and shadows.

The white ribbon has cloth thickness, slight folds and the original Fit India branding. A cloth loop passes over the shelf edge and returns behind the front strip. A bent metal hook supports the loop. The interaction pivot is at that shelf attachment so the existing restrained medal sway remains attached naturally.

## Placement and dimensions

- On September 15, the medal moved from the central bridge to the outer end of
  the trophy shelf, hanging down the cabinet side toward the red lamp.
- Attachment root in exported Y-up coordinates: `[1.041256, 2.464, -0.904819]`.
- Overall mesh bounds: `[1.0059, 2.1715, -0.943003]` to `[1.11826, 2.478, -0.82824]`.
- The complete assembly turns with the shelf end. Its hook rests at the shelf's
  `2.48` top height; the original ribbon, photo UVs and hanging pivot remain.
- Shaped body: `0.1398 × 0.1464 × 0.006` scene units, about `8 × 8.4 cm` with `3.4 mm` thickness at the desk scale.

`scripts/blender/reposition_medal_trophy_shelf.py` creates the placement candidate
and supports a hash-checked `--promote`. The backup, candidate, placement audit and
browser captures are in `artifacts/workspace/medal-trophy-placement/`.
Only the medal assembly's world pose changed. Geometry, material assignments,
unrelated poses and light settings match the preceding master. Intersection checks
against both trophies, the plant, lamp heads, toy and monitor returned zero.
The active export is revision `c413227c7fca`, with 178,215 triangles.
Desktop achievement/history checks, mobile medal taps and the geometry budget
check passed after the move.

## Original replacement source and verification

`scripts/blender/replace_ride_for_unity_medal.py` opens the current saved Blender scene, backs it up, changes only the medal families, and writes a review candidate. All 463 unrelated objects retain their geometry, material assignments and transforms, including the right-side certificate frame and supplied ergonomic chair. Existing lights are unchanged.

The candidate was checked in close-up and overview Cycles renders, then promoted after verifying the saved master hash. `scripts/blender/bake_saved_workspace.py` exported the promoted master and rebuilt its indirect-light atlases.

- Editable master: `artifacts/workspace/workspace.blend`.
- Master SHA-256: `5abd3a97927384af4f3df07c9e17e39c67f4971187dd5d9fc977a01c9d48b69d`.
- Web GLB revision: `55c88593f256`.
- Geometry: `179,562` triangles, down `3,064` from the previous export and within the `180,000` budget.
- Application and export audits: `artifacts/workspace/ride-for-unity-medal/application.json` and `export-validation.json`.
- Visual review: `artifacts/workspace/ride-for-unity-medal/overview.png` and `medal-closeup.png`.

Run the replacement script with `--source artifacts/workspace/ride-for-unity-medal/source-before-medal-53f595eedf48.blend` to reproduce this candidate from its pre-edit backup. It intentionally refuses a source that does not contain all three generic roots. Do not run `build_workspace.py` to reproduce this replacement; the saved scene is the source.
