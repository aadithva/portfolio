"""Composite Cycles alpha frames onto the site background and encode web video."""
from pathlib import Path
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / 'artifacts/workspace/cycles-frames'
MEDIA = ROOT / 'public/media/workspace'
MEDIA.mkdir(parents=True, exist_ok=True)
COMPOSITES = ROOT / 'artifacts/workspace/cycles-composited'
COMPOSITES.mkdir(exist_ok=True)
for frame in range(1, 73):
    source = FRAMES / f'{frame:04d}.png'
    if not source.exists():
        raise RuntimeError(f'Cycles render is incomplete: {source.name}')
    image = Image.open(source).convert('RGBA')
    background = Image.new('RGBA', image.size, '#eae6de')
    background.alpha_composite(image)
    rgb = background.convert('RGB')
    rgb.save(COMPOSITES / source.name)
poster = ROOT / 'artifacts/workspace/cycles-poster.png'
image = Image.open(poster if poster.exists() else FRAMES / '0001.png').convert('RGBA')
background = Image.new('RGBA', image.size, '#eae6de')
background.alpha_composite(image)
background.convert('RGB').save(MEDIA / 'desk-poster.webp', quality=95)
subprocess.run([
    'ffmpeg', '-y', '-framerate', '24', '-i', str(COMPOSITES / '%04d.png'),
    '-vf', 'scale=out_color_matrix=bt709',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
    '-movflags', '+faststart', '-an', str(MEDIA / 'desk-cycles.mp4'),
], check=True)
subprocess.run([
    'ffmpeg', '-y', '-i', str(MEDIA / 'desk-cycles.mp4'), '-vf', 'scale=960:-2',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
    '-movflags', '+faststart', '-an', str(MEDIA / 'desk-cycles-mobile.mp4'),
], check=True)
print('Cycles video and poster ready:', MEDIA)
