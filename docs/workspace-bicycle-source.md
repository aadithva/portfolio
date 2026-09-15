# Bicycle source and acquisition status

## Current horizontal mounting and frame support

The latest master uses a horizontal, wall-parallel bicycle, 20% larger than the
earlier horizontal adjustment and moved 0.80 scene units farther right. Tyre
bounds are 0.50–1.998 units high. The lamp no longer crosses the bicycle in the
desktop overview, with intentional cropping of the rear at the right edge.

Two rubber-lined U saddles support the actual upper frame tube. Their underside
contact heights are 1.635 and 1.572, fitted by ray-casting the saved frame mesh.
Short braced arms connect each cradle to a wall plate. The old misplaced rack
below the crank was removed. `scripts/blender/align_bicycle_frame_mount.py`
reproduces that fit without moving the bicycle or other room objects.
Current screenshots and reports are in `artifacts/workspace/bicycle-lamp-clearance/`.

## Revised mounting, 15 September 2026

The same supplied model is now on the lamp-side right wall, using the user's
wheel-hook reference. The front wheel is above the rear wheel, the wheel plane
is perpendicular to the wall, and the frame projects into the room. A black
padded hook and lower rubber pad replace the earlier side-profile supports.
The final user-requested adjustment makes the assembly 15% smaller and places
the lowest tyre point at 0.20 scene units, about 12 cm above the actual floor.
The former bicycle position now contains a sliding balcony door.
Current evidence is in `artifacts/workspace/balcony-door/`; the initial source
provenance below still applies. Use `artifacts/workspace/workspace.blend` for edits.

## Supplied model integrated, 14 September 2026

The user supplied `/Users/aadith/Downloads/road-bike.zip`. It contains only
`source/road_bike.fbx`, with 382,199 source triangles, material colors, and no
image textures. This supplied file is the integration source; its creator and
relationship to the older ChakkitPP listing below were not established by the archive.

The original FBX is retained in `artifacts/workspace/bicycle/source/source/`.
`scripts/blender/add_supplied_bicycle.py` creates a backed-up review candidate,
checks unrelated geometry/transforms/material assignments and lights, and adds
a vertical bike with a padded upper hook and lower wheel stabilizer. Uniform
scale calibrates the original tyre diameter to 69 cm. The frame stays within
the free left-wall span with 0.0798 scene units of minimum wall clearance.
Triangle intersection checks against the chair, left shelf wing, About/Contact
assemblies, monitor, and certificate returned zero intersections.

The candidate was promoted to `artifacts/workspace/workspace.blend` after the
source hash check. `npm run bake:workspace` updates the website normally.
The supplied meshes retain their original editable geometry and non-destructive
web modifiers. The exporter also reduces dense existing geometry on its copy,
bringing the complete scene including the bike to 178,215 triangles. The tested
mobile overview uses 199 draw calls with realtime shadows disabled.

The `bicycle` root opens Expeditions through the existing binding. Keyboard
activation and return focus have a dedicated browser test. Mobile retains the
desk-focused overview; the header and guide also open Expeditions.

Inspection, application report, candidate, source backup, Cycles renders, and
desktop/mobile website screenshots are in `artifacts/workspace/bicycle/`.

## Historical requested listing

The following acquisition notes were recorded before the user supplied the FBX.

## Identity

- Requested short URL: [skfb.ly/oTDHF](https://skfb.ly/oTDHF).
- Canonical listing: [Road Bike](https://sketchfab.com/3d-models/road-bike-f3e78143347644898e9f688bc1b64e9d).
- Creator: [ChakkitPP](https://sketchfab.com/chakkitpp).
- Model UID: `f3e78143347644898e9f688bc1b64e9d`.
- Published: 21 April 2024, as displayed by the listing.

The short URL redirects to this canonical listing. The public HTML title still contains “Buy Royalty Free 3D model” and “Sketchfab Store”; those are historical listing labels, not evidence that a purchase is currently available.

## Current availability and license evidence

The current public page was inspected in the browser while signed out. It offered Follow, Add To, Embed, Share, and Report. No Download, Buy, or Fab destination was displayed. No official downloadable archive or current purchase route was obtained. This is **not a confirmed login-only download gate**: no download action was present to test.

Public listing metadata identifies the legacy license as `Standard` (`slug: st`), with `free: false` and `isCc: false`, and links to [Sketchfab licenses](https://sketchfab.com/licenses). It also reports `inStore: false` and `price: null`. These fields establish that this is a former commercial listing, not a verified Creative Commons or free asset. They do not establish a license held by the portfolio owner or permission to redistribute the source files.

Sketchfab's [official announcement about the move to Fab](https://www.linkedin.com/posts/sketchfab_the-sketchfab-store-is-moving-over-to-fab-activity-7241812058202161152-JByf) states that Fab replaces the Sketchfab Store and ends buying and selling there. No migrated Fab listing for this exact model was verified during this bounded check.

An authorized path remains obtaining the source package under a valid license from the user, their previous purchase, or a creator-authorized distribution route. No purchase was attempted, no account was created, and no protected viewer assets were extracted. The public viewer or an embed is not an acquired Blender source asset.

## Advertised source package

The creator's [listing description](https://sketchfab.com/3d-models/road-bike-f3e78143347644898e9f688bc1b64e9d) advertises:

- Blender 2.90.1 source; `.blend`, `.fbx`, `.obj` with `.mtl`, and `.stl` formats.
- 42,202 polygons and 44,115 vertices; the viewer displays approximately 84,000 triangles and 44,100 vertices.
- Non-overlapping UVs, beveled edges, no subdivision modifier, and no required plugins.
- 2K PBR base color, height, metallic, normal, roughness, and ambient occlusion maps.

These are creator-reported package details. File contents, actual import behavior, texture completeness, real dimensions, wheel diameter, handlebar width, and bounding box have **not** been measured or verified. A GLB export was not advertised or acquired.

## Integration contract after acquisition

- Place the licensed original package under `artifacts/workspace/bicycle/source/`, retaining its license and provenance. That folder currently contains no acquired model from this listing.
- Import and inspect the original in Blender before assuming unit scale or wall clearances. Measure length, wheel diameter, and handlebar width from the actual geometry.
- Use the stable scene root name **`bicycle`** for the Blender assembly and exported glTF node so it matches the workspace runtime.
- Export a web-ready derivative only after confirming the applicable license permits its intended use. Preserve source/license attribution as required by that license.

No preview image or screenshot was copied into the project, and no unlicensed 3D data was redistributed. Only the normal public listing was read; its temporary HTML inspection copy is outside the repository.
