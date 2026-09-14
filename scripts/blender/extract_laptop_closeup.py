"""Perspective-rectify the user-supplied laptop close-up without redrawing art.

Usage:
  python3 scripts/blender/extract_laptop_closeup.py --source /path/to/photo.jpg
  python3 scripts/blender/extract_laptop_closeup.py  # rebuild from retained source

The measured corners apply to the supplied 3213x5712, EXIF-orientation-1 photo.
Output is landscape, with the source portrait's left edge at the top (90 deg CW).
Only pixels outside the rounded lid boundary receive a sampled dark edge color.
No white balance, sharpening, denoising, generative fill, or sticker replacement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from math import hypot
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageOps, ImageStat

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / 'artifacts/workspace/laptop-closeup'
SOURCE_BACKUP = ARTIFACTS / 'source.jpg'
TEXTURE = ROOT / 'public/textures/workspace/laptop-closeup-albedo.jpg'
SOURCE_SIZE = (3213, 5712)

# Portrait TL, TR, BR, BL. These are intersections of the straight black edges,
# inset approximately 6 source pixels on three clear black sides. The portrait
# right edge stays outside the rim to retain the Microsoft sticker's white edge;
# a separate measured silhouette clips background from that mildly bowed side.
PORTRAIT_CORNERS = [(243, 916), (2837, 899), (2931, 4543), (350, 4660)]
RIGHT_RIM = [(2830, 899), (2832, 1050), (2838, 1250), (2847, 1500),
             (2854, 1750), (2862, 2000), (2866, 2300), (2875, 2700),
             (2886, 3100), (2900, 3500), (2914, 4000), (2920, 4350),
             (2921, 4450), (2924, 4543)]
# Landscape TL, TR, BR, BL: move the source's left/hinge edge to image top.
LANDSCAPE_CORNERS = [PORTRAIT_CORNERS[i] for i in (3, 0, 1, 2)]
MASTER_SIZE = (3600, 2512)
WEB_SIZE = (2048, 1429)
CORNER_RADIUS = 106  # Master pixels; restricted to the otherwise empty lid rim.


def perspective_coefficients(destination, source):
    """Solve Pillow's destination-to-source projective transform without NumPy."""
    augmented = []
    for (x, y), (u, v) in zip(destination, source):
        augmented.append([x, y, 1, 0, 0, 0, -u*x, -u*y, u])
        augmented.append([0, 0, 0, x, y, 1, -v*x, -v*y, v])
    augmented = [list(map(float, row)) for row in augmented]
    for column in range(8):
        pivot = max(range(column, 8), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        if abs(divisor) < 1e-12:
            raise ValueError('Degenerate perspective corners')
        augmented[column] = [value/divisor for value in augmented[column]]
        for row in range(8):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [a-factor*b for a, b in zip(augmented[row], augmented[column])]
    return [row[-1] for row in augmented]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE_BACKUP)
    args = parser.parse_args()
    source_path = args.source.expanduser().resolve()
    if not source_path.is_file():
        parser.error('Source is missing. Supply --source with the original 3213x5712 photograph.')
    with Image.open(source_path) as opened:
        photo = ImageOps.exif_transpose(opened).convert('RGB')
    if photo.size != SOURCE_SIZE:
        parser.error(f'Corners were measured for {SOURCE_SIZE}; received {photo.size}. Remeasure before using another image.')

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    if source_path != SOURCE_BACKUP.resolve():
        shutil.copy2(source_path, SOURCE_BACKUP)
    source_digest = hashlib.sha256(SOURCE_BACKUP.read_bytes()).hexdigest()

    width, height = MASTER_SIZE
    destination = [(0, 0), (width-1, 0), (width-1, height-1), (0, height-1)]
    coefficients = perspective_coefficients(destination, LANDSCAPE_CORNERS)
    rectified = photo.transform(MASTER_SIZE, Image.Transform.PERSPECTIVE, coefficients, Image.Resampling.BICUBIC)

    # Keep the warp itself as a lossless audit artifact. It includes the tiny
    # source-background wedges outside the lid's rounded corners.
    rectified.save(ARTIFACTS / 'rectified-unmasked.png')
    edge_mask = Image.new('L', MASTER_SIZE, 0)
    ImageDraw.Draw(edge_mask).rounded_rectangle((0, 0, width-1, height-1), radius=CORNER_RADIUS, fill=255)
    source_rim_mask = Image.new('L', SOURCE_SIZE, 0)
    # Exclude the bright background transition, three native pixels outside
    # the dark rim. The Microsoft sticker's narrow white paper border remains.
    dark_rim = [(x-3, y) for x, y in RIGHT_RIM]
    ImageDraw.Draw(source_rim_mask).polygon([(0, 0), (dark_rim[0][0], 0), *dark_rim,
                                            (dark_rim[-1][0], SOURCE_SIZE[1]), (0, SOURCE_SIZE[1])], fill=255)
    rim_mask = source_rim_mask.transform(MASTER_SIZE, Image.Transform.PERSPECTIVE, coefficients, Image.Resampling.BICUBIC)
    edge_mask = Image.composite(edge_mask, Image.new('L', MASTER_SIZE, 0), rim_mask)
    # Four clear black patches just inside each corner, not sticker pixels.
    patches = [(20, 115, 60, 155), (width-60, 115, width-20, 155),
               (width-60, height-155, width-20, height-115), (20, height-155, 60, height-115)]
    corner_colors = [tuple(round(value) for value in ImageStat.Stat(rectified.crop(box)).median) for box in patches]
    # Smooth interpolation avoids a seam where corner fills meet along the
    # narrow outer boundary. This background is never applied over the art.
    background_samples = Image.new('RGB', (2, 2))
    background_samples.putdata([corner_colors[i] for i in (0, 1, 3, 2)])
    background = background_samples.resize(MASTER_SIZE, Image.Resampling.BILINEAR)
    master = Image.composite(rectified, background, edge_mask)
    master.save(ARTIFACTS / 'laptop-closeup-master.png')
    edge_mask.save(ARTIFACTS / 'corner-mask.png')
    master.resize(WEB_SIZE, Image.Resampling.LANCZOS).save(TEXTURE, quality=95, subsampling=0, optimize=True)

    # Visual audit sheet: source corner positions and both orientation choices.
    annotated = photo.resize((803, 1428), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(annotated)
    points = [(x*803/SOURCE_SIZE[0], y*1428/SOURCE_SIZE[1]) for x, y in PORTRAIT_CORNERS]
    draw.line(points+[points[0]], fill='#ff4238', width=3)
    for label, (x, y) in zip(('portrait TL', 'portrait TR', 'portrait BR', 'portrait BL'), points):
        draw.ellipse((x-5, y-5, x+5, y+5), fill='#ff4238')
        draw.text((max(2, min(700, x+8)), max(2, y-18)), label, fill='#ff4238')
    annotated.save(ARTIFACTS / 'measured-corners.jpg', quality=92)
    comparison = Image.new('RGB', (1024, 850), '#d9d8d3')
    draw = ImageDraw.Draw(comparison)
    draw.text((16, 12), 'NEW: source-left/hinge edge at top, rotated 90 deg clockwise', fill='#202020')
    comparison.paste(master.resize((640, 447), Image.Resampling.LANCZOS), (16, 34))
    old_path = ROOT / 'public/textures/workspace/reference-laptop-albedo.jpg'
    if old_path.exists():
        old = Image.open(old_path).convert('RGB')
        draw.text((16, 501), 'OLD UV TEXTURE: sticker landmarks are rotated 180 deg relative to new', fill='#202020')
        comparison.paste(old.resize((512, 328), Image.Resampling.NEAREST), (16, 522))
    draw.text((677, 12), 'NEW rotated 180 deg for comparison', fill='#202020')
    comparison.paste(master.transpose(Image.Transpose.ROTATE_180).resize((330, 230), Image.Resampling.LANCZOS), (677, 34))
    comparison.save(ARTIFACTS / 'orientation-comparison.jpg', quality=95)

    tl, tr, br, bl = PORTRAIT_CORNERS
    length = (hypot(bl[0]-tl[0], bl[1]-tl[1])+hypot(br[0]-tr[0], br[1]-tr[1]))/2
    depth = (hypot(tr[0]-tl[0], tr[1]-tl[1])+hypot(br[0]-bl[0], br[1]-bl[1]))/2
    metadata = {
        'source': 'source.jpg', 'source_sha256': source_digest, 'source_size': SOURCE_SIZE,
        'rebuild_input_path': str(source_path), 'exif_orientation_normalized': True,
        'portrait_corner_order': ['top-left', 'top-right', 'bottom-right', 'bottom-left'],
        'portrait_corners_px': PORTRAIT_CORNERS,
        'portrait_right_rim_contour_px': RIGHT_RIM,
        'portrait_right_rim_background_exclusion_px': 3,
        'landscape_corner_order': ['top-left', 'top-right', 'bottom-right', 'bottom-left'],
        'landscape_corners_in_source_px': LANDSCAPE_CORNERS,
        'orientation': '90 degrees clockwise: source portrait left edge maps to landscape top; not mirrored',
        'perspective_destination_to_source': coefficients, 'master_size': MASTER_SIZE, 'web_size': WEB_SIZE,
        'image_aspect': width/height, 'mean_projected_edge_aspect': length/depth,
        'aspect_caveat': 'Approximate near-frontal photo estimate, not a calibrated physical measurement.',
        'existing_printed_mesh_aspect': 1.5773, 'corner_mask_radius_master_px': CORNER_RADIUS,
        'edge_fill_rgb_by_corner_tl_tr_br_bl': corner_colors,
        'pixel_operations': ['bicubic perspective resampling', 'sampled dark fill outside rounded corners and measured portrait-right lid boundary only', 'Lanczos web downsampling', 'quality95 4:4:4 JPEG encoding'],
        'unchanged_artwork': 'No sticker redraw, replacement, rearrangement, white-balance, sharpening, or generative editing.',
    }
    (ARTIFACTS / 'extraction.json').write_text(json.dumps(metadata, indent=2)+'\n')
    (ARTIFACTS / 'README.md').write_text(
        '# Laptop close-up extraction\n\n'
        'The source is the user-supplied close-up, retained byte-for-byte as `source.jpg`. '
        'Rebuild with `python3 scripts/blender/extract_laptop_closeup.py` from the repository root.\n\n'
        '`laptop-closeup-master.png` is the 3600 × 2512 lossless rectified master. '
        '`rectified-unmasked.png` preserves the raw warp before corner cleanup. '
        '`corner-mask.png` records the only edited area: background outside the rounded black lid corners and the measured portrait-right rim. '
        'No sticker pixels are redrawn or replaced. The web texture is '
        '`public/textures/workspace/laptop-closeup-albedo.jpg`, 2048 × 1429, JPEG quality95, 4:4:4.\n\n'
        'Source-image corners and the projective coefficients are in `extraction.json`; '
        '`measured-corners.jpg` shows the chosen boundary. The output is rotated90° clockwise '
        'from the portrait source, with its left/hinge edge at the top. It is not mirrored.\n\n'
        'The old texture has its sticker landmarks rotated180° relative to this orientation. '
        'See `orientation-comparison.jpg` before choosing whether to preserve the old artwork rotation in Blender. '
        'The existing UV maps image top to the model rear hinge edge.\n\n'
        'The chosen ~1.433:1 aspect follows near-frontal photo edge measurements; it is not a calibrated physical measurement. '
        'The existing printed face is ~1.5773:1, so unchanged mapping stretches the artwork about10% horizontally. '
        'The Blender owner should explicitly decide whether to adjust the lid proportions.\n'
    )
    print(json.dumps({'texture': str(TEXTURE), 'master': str(ARTIFACTS/'laptop-closeup-master.png'),
                      'source_backup': str(SOURCE_BACKUP), 'master_size': MASTER_SIZE, 'web_size': WEB_SIZE,
                      'photo_edge_aspect': length/depth, 'web_bytes': TEXTURE.stat().st_size}, indent=2))


if __name__ == '__main__':
    main()
