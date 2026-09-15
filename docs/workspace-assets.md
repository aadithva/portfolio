# Interactive workspace assets

## Editable source and website export

The current editable scene is `artifacts/workspace/workspace.blend`. The homepage
loads `public/models/workspace-saved.glb`; its revision, lighting and geometry
counts are recorded in `public/models/workspace-saved.manifest.json`.

The monitor interaction now enters a CRT-style desktop before opening portfolio
content windows. See [the desktop interaction notes](workspace-computer.md).
The newly requested fizyman CRT housing is still pending its official download;
the saved Blender model has not been replaced by that asset yet.

The September 13 refinement is also retained at
`artifacts/workspace/reference-refinement/workspace-refined.blend`.
Two original saves remain intact in that directory:

- `source-before-refinement.blend`: the original September 12 save.
- `source-latest-before-refinement.blend`: the newer September 13, 12:29 save.

The newer save had identical geometry, object transforms, lights, world and
exposure to the earlier backup. The refinement was rebuilt from the newer save
to retain its other saved state. `source-save-comparison.json` records the check.
The promotion script refuses to replace a source that has changed since backup.

Blender 5.2.1 LTS is available at `/Applications/Blender.app/Contents/MacOS/Blender`.
These are editable Blender meshes and assemblies, exported to glTF, with no
runtime substitute desk built from generic boxes.

## Reference corrections

The photographed desk strongly matches the IKEA MICKE corner workstation,
India article 203.542.84. Its official footprint is 100 × 100 cm and its overall
cabinet height is 142 cm. The 75 cm desktop height is inferred from the MICKE
series documentation. The model uses 1.31 scene units for that desktop height;
scene units are therefore about 57.25 cm, not metres. The original cabinet dimensions
follow that scale. The later upper-shelf enlargement below intentionally adapts
the cabinet width to the monitor. Internal clearances, the front curve and smaller items remain
photo-proportioned rather than manufacturer-measured.

The refinement corrects the corner footprint, shelf proportions and chair scale.
The monitor is about 1.02 scene units wide, approximately 58.5 cm across its outer housing,
with a 0.9202 × 0.5243 screen. Its rebuilt base sits behind the console and its
raised support reaches the display without crossing the laptop or shelf wings.

Both controllers have continuous ergonomic shells, separate attached controls,
and grounded bases. The right controller has its own stable interaction root.
The chair has an adult-scale back and sits at the actual floor height. The speaker,
books and pen vessel were reseated with clear space around the shelf framing.

There are exactly two trophies and one hanging Ride for Unity medal, modeled from
the user's supplied photograph. The three generic medals were replaced. Trophy stems join their
bases and cups, and both trophies clear the plant and window sill. Their blank
faces are editable decoration. They do not assert an award, title or year.
Achievement content remains in `src/data/workspace.ts` and is not invented.
The [Ride for Unity medal notes](workspace-ride-for-unity-medal.md) record the
photo texture, traced geometry, attachment, and verified export.

The yellow package follows the original 2023 Figma × Work Louder Creator Micro:
a removable printed cover, white tray, dark insert, 12 colored keys, a tall rotary
knob and a horizontal encoder. Its dimensions are estimated from photographs.
The cover lifts 0.1233 scene units, then moves forward 0.198 units, clearing both the tray
and the shelf above. It does not rotate like a hinged chest.

The window has a real aperture through the room wall. Its existing pane and frame
remain aligned, and the night glass is visible instead of being hidden by plaster.

[Primary-source research, drawings and product images](workspace-reference-research.md)
contains the IKEA and Figma links, identification confidence and evidence limits.

## Upper-shelf monitor fit

The upper cabinet span is enlarged by 0.44 scene units. Each angled shelf unit
moves 0.22 outward and 0.22 toward the front along its wall; the central bridge
extends from 0.686475 to 1.126475 units. The monitor keeps its existing size and
moves 0.22 back, so the housing fits inside the opening. Shelf-mounted objects,
bridge brackets and decorations follow their supports. The pegboard, window,
desktop and legs retain their locations.

`scripts/blender/fit_monitor_shelves.py` reproduces the change from the captured
pre-fit save and writes a review candidate without replacing the active source.
The candidate and backup are in `artifacts/workspace/shelf-fit/`, alongside
matching front renders and an angled render. `validate_shelf_fit.py` accepts
`--source` and `--output` to check the candidate's opening, contacts, intersections
and moving keyboard-package cover before the ordinary bake/export workflow.

## Texture and lighting provenance

The September 15 material pass adds seamless, seeded surface-detail maps to 85
materials. These are fine normal and roughness textures, with separate levels
for powder-coated paint, plastic, rubber, plaster, stone, paper and metal. The
lamp keeps its red paint with roughness around 0.68 and reduced metallic/gloss
response. The bicycle frame is neutral black, and both tyre sidewalls and rims
are black. Original albedo artwork and existing office-chair textures remain.

`scripts/blender/apply_matte_materials.py` creates the maps and applies them to
the current saved scene. `surface_detail_uv.py` provides a separate, world-scaled
`SurfaceDetail` UV layer without replacing artwork UVs. Curves receive the same
mapping after export conversion. `scene.ts` uses the exported `bakedUV` index for
indirect lighting rather than assuming UV1. The GLB verification script checks
that the lamp, bicycle and architecture contain normal/roughness textures and
that every baked mesh has the correct UV attribute. Evidence and day/night
desktop/mobile captures are under `artifacts/workspace/matte-materials/`.

The active laptop uses `laptop-closeup-albedo.jpg`, a 2048 × 1429 extraction from
the user's newer 3213 × 5712 close-up. `extract_laptop_closeup.py` rectifies the
four lid edges, orients the hinge at the rear, and keeps the supplied sticker
pixels. It retains a 3600 × 2512 PNG master and the original photograph in
`artifacts/workspace/laptop-closeup/`. The measured boundary and perspective
coefficients are recorded beside the master. No sticker artwork was generated.

`apply_laptop_closeup.py` loads and packs the new image into the saved Blender
material. The lid keeps its width and gains about 10% depth to match the photo's
estimated aspect ratio without stretching the printed artwork. The previous
raised discovery markers use invisible hit regions, so the actual photograph
supplies their appearance while the two interactions remain available.

The older `reference-laptop-albedo.jpg` and its extraction script remain for
historical reproduction. That 512 × 328 version came from approximately 190
pixels across the laptop in the original desk photograph; it is no longer the
active laptop texture. Baking preserves the new JPEG resolution separately from
the lighting atlases, and the browser uses anisotropic filtering at desk angles.

`reference-figma-{lid,front,side}.png` contains rectified package artwork from the
official Figma product photographs. Links and extraction provenance are in the
research note and props script. Other surfaces use shared material colors,
roughness and metalness. Existing paper graphics and chair weave are retained.
Source albedo UVs remain separate from the indirect-light atlas UVs.

The user's room lights and lamp colors/powers are retained. Lamp lights move with
the resized lamp. The monitor emitter now sits on the screen and matches its
rectangle; its power scales with emitter area to retain luminance. This prevents
the old oversized disk from cutting through the laptop and controller. The
original light values remain in the source backups.

Cycles bakes indirect lighting into two 2048 px atlases. Full PNGs are retained
for authoring; the website loads compact quality-95 WebP derivatives as linear
data textures. Three.js recreates direct area/spot lighting from the manifest,
uses AgX tone mapping, caps pixel density, and renders on demand. Turning a lamp
off changes its direct lighting; the indirect bake represents the saved night
setup and is not recalculated per switch state.

## Exporting subsequent Blender edits

Save `artifacts/workspace/workspace.blend`, then run:

```sh
npm run bake:workspace
```

This updates the active GLB, indirect maps and manifest. It also saves the
export-only `artifacts/workspace/workspace-saved-baked.blend`; it does not save over
the editable source. Bake/export commands exit unsuccessfully on Python errors.

To regenerate this refinement from its captured pre-edit backup:

```sh
python3 scripts/blender/extract_reference_laptop.py
"/Applications/Blender.app/Contents/MacOS/Blender" --background --python-exit-code 1 \
  --python scripts/blender/refine_saved_workspace.py -- --render
"/Applications/Blender.app/Contents/MacOS/Blender" --background --python-exit-code 1 \
  --python scripts/blender/validate_reference_workspace.py
```

That workflow regenerates the candidate. It does not preserve later manual edits
to that candidate; use the normal bake command for later source edits.
`--promote` explicitly copies a checked candidate to the editable source, guarded
by the backup hash. Never use `assets:workspace` to publish manual source edits:
that older generator constructs the original scene from scratch.

The refinements are split into `refine_reference_layout.py`,
`refine_reference_props.py`, and `refine_reference_surfaces.py`. Content mappings,
camera views, and interaction behavior remain separate in `src/lib/workspace/`.
Screen focus and hotspot placement use the exported mesh's actual bounds.

## Inspection and validation

`reference-refinement/` contains six Cycles views, `after.json` with actual-vertex
bounds, `layout-report.json` with construction values, and
`geometry-validation.json` with support/contact/intersection checks.
The overview approximates the photograph's elevated angle; it is not a calibrated
camera reconstruction. The scene remains a stylized model, with approximate
foliage, chair construction, lamp heads and small stationery details.

The browser checks cover monitor/project navigation, three medal links, removal
of the third trophy, keyboard focus return, Back/Forward, mobile tap targets,
reduced motion, optional sound, loading failure, WebGL failure and no-JavaScript
navigation. Actual website captures and runtime metrics accompany the Blender
views. Performance totals are in the export manifest and capture logs, rather
than hard-coded here where later model edits would make them stale.

## Bicycle and Expeditions addition

### Current layout, 15 September 2026

The latest bicycle revision is horizontal and wall-parallel. It is uniformly
20% larger than the previous horizontal adjustment, shifted 0.80 units right
along the wall, with its tyres at height 0.50. Two braced padded saddles are fitted
directly beneath the upper frame tube. The previous low, detached supports have
been replaced. See `artifacts/workspace/bicycle-lamp-clearance/` for the mount
close-up, browser screenshots, contact report and placement collision checks.

### Earlier vertical placement

The bicycle now hangs on the right wall beside the red lamp. Its wheel plane is
perpendicular to the wall, matching the supplied wheel-hook photograph. A black
padded hook holds the front wheel and a small rubber pad receives the rear tyre.
The final adjustment uniformly reduces the bicycle and mount by 15% and lowers
the tyre bounds from 0.621–3.579 to 0.200–2.714 scene units.

A two-panel sliding glass balcony door fills the old bicycle position on the
left wall. It has a cut-through plaster/skirting opening, aluminum tracks, white
frames, seals, pull handles, a slightly open leaf and a shallow exterior railing.
The exterior backdrop follows the existing day/night setting. The door panels
remain separately editable Blender assemblies.

The September 15 width adjustment enlarges the opening from 2.30 to 4.00 scene
units, about 1.32 m to 2.29 m at the desk scale. The desk-side jamb remains at wall
coordinate 2.10; only the far edge moves, from 4.40 to 6.10. Both glass panels,
tracks, lintel, threshold, exterior slab and backdrop extend to fit. Vertical
stiles, seals and handles retain their thickness. Fifteen railing balusters keep
approximately the original spacing. `scripts/blender/widen_balcony_door.py`
creates a hash-checked candidate from the latest master and verifies the enlarged
aperture with ray tests. Backup, report, Cycles view and desktop/mobile captures
are in `artifacts/workspace/balcony-width/`. The exported revision is
`d08387230502`; all four camera interaction tests passed.

`scripts/blender/add_balcony_door.py` creates a backed-up candidate and checks the
doorway aperture, bicycle clearance, and unchanged unrelated objects before its
hash-guarded promotion. `scripts/blender/resize_mounted_bicycle.py` applies the
subsequent size/height adjustment to the current master. Both refuse duplicate
application. Captures and reports are in `artifacts/workspace/balcony-door/`.

### Earlier bicycle integration

The Expeditions HTML panel and `/expeditions` route use the two existing accounts
in `src/data/adventures.ts`. Editable entries live in `src/data/expeditions.ts`.
The new header and guide links also work without the bicycle, without WebGL and
without JavaScript. No ride photos, dates or distances have been invented.

The user's supplied `road-bike.zip` is now integrated into the master and website.
It contains a road-bike FBX with material colors, rather than the texture package
advertised by the earlier requested listing. See `workspace-bicycle-source.md`
for the actual supplied-file provenance, fitting, and verification.
`artifacts/workspace/bicycle/mount-plan.md` records the wall audit, a provisional
vertical adult-bike placement, support locations and dedicated camera framing.

The active root is `bicycle`, mapped to section `expeditions`. It was initially
mounted vertically on the left wall with physical supports. The existing Expeditions
camera now resolves the actual model bounds. The source backup and review
candidate remain in `artifacts/workspace/bicycle/`.

## Retained older experiments

`workspace-cycles.blend`, Cycles film frames, MP4s and poster images are retained
as separate experiments. They are not loaded by the current homepage.
`public/models/workspace.glb` is the older unbaked export path; `export:workspace`
updates that optional export only. The active homepage uses `workspace-saved.glb`.

### Room extension, September 15, 2026

Extended the saved corner walls and their baseboards another 10 units, raised the wall tops to 10.08 units, and rebuilt the limestone slab to span 28 units across and reach 14 units forward. Tile grout continues the original 1.1-unit pitch. Props and the existing window remain in place; balcony work is paused. The pre-extension scene is saved at `artifacts/workspace/room-extension/source-before-extension.blend`. `scripts/blender/extend_room.py` records the edit and refuses duplicate application. Rebuilt the served GLB and indirect lighting using `npm run bake:workspace`. Drag-limit screenshots are in `artifacts/workspace/room-extension/`. Workspace type checking and all four camera interaction tests passed.

### Floral desk mat, September 15, 2026

Added the supplied VATTENSKRUV floral mat as a thin shaped mesh beneath the desk and chair. The top-down product image supplies the actual floral texture; a traced 192-point silhouette preserves its rounded asymmetric outline, with green binding and subtle cotton bump. Authoring scripts are `scripts/blender/prepare_floral_mat.py` and `scripts/blender/add_floral_mat.py`. Source backup is `artifacts/workspace/floral-mat/source-before-mat.blend`; texture and outline are in `public/textures/workspace/floral-mat/`. Rebuild web lighting and GLB with `npm run bake:workspace`.

### Horizontal bicycle mount, September 15, 2026

Rotated the bicycle into the plane of its existing right wall with the front wheel and handlebars toward the lamp and room corner. Reduced its current scale to 72% so the horizontal bicycle fits beneath the window, and replaced the vertical wheel hook with two padded frame cradles. `scripts/blender/mount_bicycle_horizontal.py` saves a backup and checks evaluated geometry for collisions. The bicycle clears the wall by 0.12 units and has zero intersections with the window, chair, right shelf wing, and all three lamp heads. Backup, placement report, and review captures are in `artifacts/workspace/bicycle-horizontal/`. Rebuilt indirect lighting and the served GLB afterward.

### Lower bicycle placement, September 15, 2026

Enlarged the horizontal bicycle by 15%, lowered it by 0.60 units, and moved it 0.25 units toward the lamp. Its lowest point is now 0.726 units above the floor. Frame supports follow the adjustment. Evaluated geometry still has zero intersections with the lamp heads, window, chair, and right shelf wing. Script, backup, placement report, and captures are recorded under `scripts/blender/adjust_horizontal_bicycle.py` and `artifacts/workspace/bicycle-horizontal-adjustment/`.

### Chair centering, September 15, 2026

Moved the chair 0.42 units toward the desk center along X and 0.10 units closer to the desk. Preserved its rotation and height. The saved scene backup and placement report are in `artifacts/workspace/chair-centering/`; `scripts/blender/center_desk_chair.py` records the edit. Rebuilt the web GLB and lighting.

### Diet Coke texture correction, September 15, 2026

Replaced the original Arial placeholder artwork with print extracted from Coca-Cola India's official Diet Coke reference at `https://www.coca-cola.com/content/dam/onexp/in/en/home-page-test-img/brands/coca-cola/Diet-coke234-700.png`. Removed photographic shading from the silver background and corrected the cylinder UVs to use the full label height with a continuous seam. The silver base and nonmetallic ink now use separate metalness values. Scripts are `prepare_diet_coke_texture.py` and `fix_diet_coke_texture.py`; original scene backup and reference are in `artifacts/workspace/diet-coke-fix/`. New texture derivatives are `public/textures/workspace/diet-coke-label.webp` and `diet-coke-metalness.png`.

### Can surface seam correction, September 15, 2026

Removed 48 long torso faces from the aluminium body that overlapped the label cylinder at only 0.1 mm separation. Rebuilt the label wall as an open-ended 128-segment cylinder with radial smooth normals and continuous wrap UVs, avoiding smoothed cap normals and overlapping render surfaces. The lid, shoulder, base, and pull tab remain intact. `scripts/blender/fix_can_surface.py` records the change; backup, report, bake log, and close-up captures are in `artifacts/workspace/can-surface-fix/`.
