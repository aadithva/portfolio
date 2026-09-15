# Desktop edge refinement

The September 15 refinement replaces the coarse desktop slab with a continuous
front curve, a 0.006-unit rounded edge and explicit smooth surface normals.
The top remains at 1.31 and the underside at 1.209046 scene units.

The slab is independently editable as `Corner desk smooth desktop`, under
`desktop_surface`. Its `webOptimized` property prevents the existing generic
export decimator from reducing the new curve. Its material remains `Porcelain edges`.
The rest of the original porcelain batch is preserved.

`scripts/blender/refine_desktop_edge.py` locates the original connected slab in
the latest master, backs up that save and creates a candidate. It checks that
all unrelated object poses, mesh vertices, material assignments and light values
are unchanged. `--promote` requires matching master and candidate hashes.
The resulting slab is closed and manifold, with 2,436 triangles instead of 316.
The front has 120 curve samples and four segments on each rounded edge.

Source backups, the candidate and validation report are under
`artifacts/workspace/desktop-edge/`. `web-desk-detail.png` and `web-mobile.png`
show the exported scene. The earlier Cycles close-up shows the same slab before
the operation was reapplied to a newer concurrent master save.

The normal `npm run bake:workspace` pipeline publishes the geometry and lighting.
The browser measured 190,159 scene triangles and 203 mobile overview draw calls.
The scene was already above the 180,000-triangle test budget before this change.
The mobile interaction flow reaches its final geometry assertion, which still
fails that limit. The monitor entry and focus-return test passed on recheck after
a development-server reload interrupted the first run. No budget was raised.
