"""Prepare the supplied top-down product photo and trace its outer silhouette."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path('/Users/aadith/Downloads/vattenskruv-bath-mat-floral-pattern-multicolour__1396498_pe967312_s5.avif')
OUT=ROOT/'public/textures/workspace/floral-mat'
OUT.mkdir(exist_ok=True)
im=Image.open(SOURCE).convert('RGB')
# Flood only the exterior white background; white flower centers remain intact.
mask=Image.new('RGB',im.size)
mask.putdata([(255,255,255) if min(p)>225 and max(p)-min(p)<24 else (0,0,0) for p in im.getdata()])
ImageDraw.floodfill(mask,(0,0),(255,0,0),thresh=0)
cx,cy=450,450
contour=[]
for i in range(192):
 a=2*math.pi*i/192
 last=(cx,cy)
 for r in range(1,640):
  x,y=round(cx+r*math.cos(a)),round(cy+r*math.sin(a))
  if not(0<=x<900 and 0<=y<900) or mask.getpixel((x,y))==(255,0,0):break
  last=(x,y)
 contour.append(last)
im.save(OUT/'floral-mat.webp',quality=95,method=6)
(OUT/'outline.json').write_text(json.dumps({'size':list(im.size),'points':contour})+'\n')
print('Prepared floral mat texture and 192-point outline')
