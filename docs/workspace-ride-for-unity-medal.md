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

- Attachment root in exported Y-up coordinates: `[0, 2.378942, -1.283]`.
- Overall bounds: `[-0.0699, 2.086442, -1.309]` to `[0.0699, 2.392942, -1.23783]`.
- Shaped body: `0.1398 × 0.1464 × 0.006` scene units, about `8 × 8.4 cm` with `3.4 mm` thickness at the desk scale.
- Clearance above the monitor screen: `0.107425` scene units.

## Source and verification

`scripts/blender/replace_ride_for_unity_medal.py` opens the current saved Blender scene, backs it up, changes only the medal families, and writes a review candidate. All 463 unrelated objects retain their geometry, material assignments and transforms, including the right-side certificate frame and supplied ergonomic chair. Existing lights are unchanged.

The candidate was checked in close-up and overview Cycles renders, then promoted after verifying the saved master hash. `scripts/blender/bake_saved_workspace.py` exported the promoted master and rebuilt its indirect-light atlases.

- Editable master: `artifacts/workspace/workspace.blend`.
- Master SHA-256: `5abd3a97927384af4f3df07c9e17e39c67f4971187dd5d9fc977a01c9d48b69d`.
- Web GLB revision: `55c88593f256`.
- Geometry: `179,562` triangles, down `3,064` from the previous export and within the `180,000` budget.
- Application and export audits: `artifacts/workspace/ride-for-unity-medal/application.json` and `export-validation.json`.
- Visual review: `artifacts/workspace/ride-for-unity-medal/overview.png` and `medal-closeup.png`.

Run the replacement script with `--source artifacts/workspace/ride-for-unity-medal/source-before-medal-53f595eedf48.blend` to reproduce this candidate from its pre-edit backup. It intentionally refuses a source that does not contain all three generic roots. Do not run `build_workspace.py` to reproduce this replacement; the saved scene is the source.
