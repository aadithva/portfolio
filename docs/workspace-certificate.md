# IIT Guwahati certificate

The degree in the wall frame uses the original 1738 × 2479 JPEG extracted from the user's local `Degree.pdf`. The extraction is preserved at `artifacts/workspace/certificate-review/iitg-degree-original-000.jpg`. The academic transcript was not used. The printed image is not recreated, cropped, recolored or retyped. The same file is available to the achievement paper view at `public/textures/workspace/iitg-degree.jpg`.

The frame sits to the right of the pegboard, centered vertically beside it. Its stable interaction root is `certificate_iitg`, bound to `achievements` in `src/lib/workspace/config.ts`. The frame is 0.491 × 0.660 scene units, about 28 × 38 cm at the desk's scale. This is 25% smaller than its first placement. A slim charcoal timber frame surrounds a warm mat. Low-opacity glazing retains the scan's readability and does not cast an opaque shadow in the browser.

The root is centered at `[-0.20, 2.9825, -2.239]` in the exported Y-up coordinates. The frame and pegboard vertical centers differ by only 0.000119 units. Their bounding boxes have a 0.069949-unit horizontal gap, and the frame clears the corner seam. Its 44 px hotspot and achievement camera continue to follow the named root. The achievement camera adjusts its distance for portrait screens.

## Saved source and export

- Editable master: `artifacts/workspace/workspace.blend`
- Reproducible addition: `scripts/blender/add_iitg_certificate.py`
- Bounded placement adjustment: `scripts/blender/reposition_iitg_certificate.py`
- Current placement candidate and audit: `artifacts/workspace/certificate-frame/right-placement/`
- Web export: `public/models/workspace-saved.glb`, revision `1d1cff6b24dc`
- Master SHA-256: `53f595eedf4874b8294c45e5122ac9560e51411c9b5f64eb4ab6971ab5e3ae3d`

The addition script writes a candidate and snapshots every prior object's geometry and transform. The placement script changes only the certificate root's position and uniform scale. All 475 unrelated object transforms and all 430 meshes and their material assignments are unchanged. The supplied ergonomic chair and all authored lights are preserved. The candidate was promoted only after checking the master hash and rendering the frame. The existing `bake_saved_workspace.py` pipeline exported the promoted master and rebuilt the indirect-light atlases.

Run the addition script against a source without a frame, or explicitly pass the original backed-up source with `--source`. Do not run `build_workspace.py` to reproduce this change. It would rebuild earlier versions of the desk.

The final GLB contains the exact JPEG byte-for-byte. Its geometry remains 182,626 triangles after this placement adjustment. The frame originally added 652 triangles to the earlier desk. The existing 180,000-triangle performance check remains exceeded.

Current Cycles composition and alignment renders are in `artifacts/workspace/certificate-frame/right-placement/overview.png` and `wall-alignment.png`. Final source, texture and geometry verification is in `artifacts/workspace/certificate-frame/export-validation.json`. The reviewed placement has no frame/window, frame/pegboard or frame/lamp overlaps. Earlier screenshots in the parent certificate-frame directory document the superseded placement on the left.
