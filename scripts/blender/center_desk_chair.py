"""Move the chair a little toward the desk's central seat position."""
import json
import shutil
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
OUT=ROOT/'artifacts/workspace/chair-centering';OUT.mkdir(exist_ok=True)
backup=OUT/'source-before-chair-centering.blend'
if backup.exists():raise RuntimeError('Chair centering already applied')
shutil.copy2(SOURCE,backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
chair=bpy.data.objects['chair'];before=chair.matrix_world.translation.copy()
chair.location+=Vector((.42,.10,0))
bpy.context.view_layer.update()
report={'before':list(before),'after':list(chair.matrix_world.translation),'offset':[.42,.10,0]}
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE));(OUT/'application.json').write_text(json.dumps(report,indent=2)+'\n');print('CHAIR_CENTERED',report,flush=True)
