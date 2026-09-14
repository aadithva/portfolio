"""Rectify the laptop lid from the supplied desk photograph for the film asset."""
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[2]
photo = Image.open('/Users/aadith/Downloads/IMG_4813.jpg').convert('RGB')
print('Reference size:', photo.size)
# Coordinates refer to the 1206 × 1548 reference supplied with the brief.
sx, sy = photo.width / 1206, photo.height / 1548
quad = [(526,946),(539,1051),(727,1018),(683,917)]
coords = tuple(value for x,y in quad for value in (x*sx,y*sy))
lid = photo.transform((1400,900), Image.Transform.QUAD, coords, Image.Resampling.BICUBIC)
lid = ImageEnhance.Brightness(lid).enhance(1.25)
lid.save(ROOT / 'public/textures/workspace/laptop-reference.jpg', quality=96)
