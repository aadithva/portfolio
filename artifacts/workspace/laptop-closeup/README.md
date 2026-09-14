# Laptop close-up extraction

The source is the user-supplied close-up, retained byte-for-byte as `source.jpg`. Rebuild with `python3 scripts/blender/extract_laptop_closeup.py` from the repository root.

`laptop-closeup-master.png` is the 3600 × 2512 lossless rectified master. `rectified-unmasked.png` preserves the raw warp before corner cleanup. `corner-mask.png` records the only edited area: background outside the rounded black lid corners and the measured portrait-right rim. No sticker pixels are redrawn or replaced. The web texture is `public/textures/workspace/laptop-closeup-albedo.jpg`, 2048 × 1429, JPEG quality95, 4:4:4.

Source-image corners and the projective coefficients are in `extraction.json`; `measured-corners.jpg` shows the chosen boundary. The output is rotated90° clockwise from the portrait source, with its left/hinge edge at the top. It is not mirrored.

The old texture has its sticker landmarks rotated180° relative to this orientation. See `orientation-comparison.jpg` before choosing whether to preserve the old artwork rotation in Blender. The existing UV maps image top to the model rear hinge edge.

The chosen ~1.433:1 aspect follows near-frontal photo edge measurements; it is not a calibrated physical measurement. The existing printed face is ~1.5773:1, so unchanged mapping stretches the artwork about10% horizontally. The Blender owner should explicitly decide whether to adjust the lid proportions.
