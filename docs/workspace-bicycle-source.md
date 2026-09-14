# Bicycle source and acquisition status

Checked 13 September 2026. **No bicycle model, source texture, or licensed export has been acquired.** The exact requested model cannot yet be integrated into Blender or the website.

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
