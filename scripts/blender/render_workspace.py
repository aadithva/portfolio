"""Render a resumable, real Cycles camera loop plus a high-quality poster."""
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'artifacts/workspace'
FRAMES = ART / 'cycles-frames'
FRAMES.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ART / 'workspace-cycles.blend'))
scene = bpy.context.scene
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'METAL'
scene.cycles.device = 'GPU'
scene.render.use_persistent_data = True
scene.render.resolution_percentage = 100
scene.cycles.samples = 48
scene.cycles.adaptive_threshold = .035
poster_only = '--poster-only' in sys.argv
if poster_only:
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1440
    scene.cycles.samples = 192
    scene.cycles.adaptive_threshold = .012
frames = [1] if poster_only else range(1, 73)
for frame in frames:
    output = ART / 'cycles-poster.png' if poster_only else FRAMES / f'{frame:04d}.png'
    if output.exists():
        continue
    scene.frame_set(frame)
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    print(f'CYCLES_FRAME {frame}/72', flush=True)
