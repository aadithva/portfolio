"""Extract print colors from the official can reference for an unlit wrap."""
import math
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'artifacts/workspace/diet-coke-fix/official-can.png'
im=Image.open(source).convert('RGB')
w,h=1024,640
out=Image.new('RGB',(w,h),(207,210,212));metal=Image.new('L',(w,h),115)
for x in range(w):
 # Repeat front/back panels. Undo the photographed cylinder's horizontal foreshortening.
 angle=((x%(w//2))/(w//2)-.5)*math.pi
 sx=max(3,min(230,round(117+114*math.sin(angle))))
 for y in range(h):
  sy=round(128+(1-y/(h-1))*476)
  r,g,b=im.getpixel((sx,sy))
  if r>95 and r>g*1.65 and r>b*1.55:
   out.putpixel((x,y),(205,15,26));metal.putpixel((x,y),8)
  elif max(r,g,b)<90:
   out.putpixel((x,y),(45,46,46));metal.putpixel((x,y),8)
# PIL top-down rows: the can top belongs at the texture top.
out=out.transpose(Image.Transpose.FLIP_TOP_BOTTOM);metal=metal.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
tex=ROOT/'public/textures/workspace'
out.save(tex/'diet-coke-label.webp',quality=96,method=6)
metal.save(tex/'diet-coke-metalness.png')
