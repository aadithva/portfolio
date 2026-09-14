"""Derive grey, web-sized PBR maps from the user-supplied office-chair archive."""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/chair-replacement/source/textures'
OUT = ROOT / 'public/textures/workspace/office-chair'
OUT.mkdir(parents=True, exist_ok=True)

def source(part, kind):
    return Image.open(SOURCE / f'OfficeChair_OfficeChair_{part}_{kind}.png')

albedo = source('Main', 'BaseColor').convert('RGB')
grey = ImageOps.grayscale(albedo).point(lambda p: round(137 + p * .30)).convert('RGB')
# Keep the source's chrome islands metallic, lifting only the plastic and cloth.
grey = Image.composite(albedo, grey, source('Main', 'Metallic').convert('L'))
grey.resize((2048, 2048), Image.Resampling.LANCZOS).save(OUT / 'main-grey.jpg', quality=94, subsampling=0)
for kind in ['Roughness', 'Metallic']:
    source('Main', kind).resize((1024, 1024), Image.Resampling.LANCZOS).save(OUT / f'main-{kind.lower()}.png', optimize=True)
source('Main', 'Normal').resize((1024, 1024), Image.Resampling.LANCZOS).save(OUT / 'main-normal.jpg', quality=94, subsampling=0)
net = source('Net', 'BaseColor').convert('RGBA')
fabric = Image.new('RGBA', net.size, (162, 164, 166, 255))
fabric.putalpha(net.getchannel('A'))
fabric.resize((1024, 1024), Image.Resampling.LANCZOS).quantize(colors=32).save(OUT / 'net-grey.png', optimize=True)
source('Net', 'Normal').resize((1024, 1024), Image.Resampling.LANCZOS).save(OUT / 'net-normal.jpg', quality=94, subsampling=0)
# Remove only superseded derivatives created by this script.
for name in ['main-normal.png', 'net-normal.png']:
    (OUT / name).unlink(missing_ok=True)
print({p.name: p.stat().st_size for p in OUT.iterdir()})
