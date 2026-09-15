"""Add a soft, invisible warm emitter above the desk in the latest saved room."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
OUT = ROOT / 'artifacts/workspace/ceiling-fill'
CANDIDATE = OUT / 'workspace-ceiling-fill.blend'
REPORT = OUT / 'application.json'
NAME = 'Desk ceiling warm fill'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if '--promote' in sys.argv:
    report = json.loads(REPORT.read_text())
    if digest(SOURCE) != report['sourceSha256'] or digest(CANDIDATE) != report['candidateSha256']:
        raise RuntimeError('Master or candidate changed after review.')
    shutil.copy2(CANDIDATE, SOURCE)
    print('CEILING_FILL_PROMOTED', flush=True)
    raise SystemExit(0)

OUT.mkdir(parents=True, exist_ok=True)
source_hash = digest(SOURCE)
backup = OUT / f'source-before-fill-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
if bpy.data.objects.get(NAME):
    raise RuntimeError('The desk ceiling fill already exists.')
light = bpy.data.lights.new(NAME, 'AREA')
light.shape = 'RECTANGLE'
light.size = 2.8
light.size_y = 2.1
light.energy = 65
light.color = (1.0, .68, .34)
obj = bpy.data.objects.new(NAME, light)
bpy.context.scene.collection.objects.link(obj)
obj.location = (0, .7, 4.25)
# Blender area lights emit along local -Z, straight down here. No fixture mesh.
obj['purpose'] = 'Low warm overhead fill; intentionally no visible fixture'
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report = {'sourceSha256':source_hash,'candidateSha256':digest(CANDIDATE),
          'backup':str(backup.relative_to(ROOT)), 'light':NAME,
          'positionWeb':[0,4.25,-.7],'size':[2.8,2.1],'energy':65,
          'color':[1,.68,.34],'visibleFixture':False}
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print('CEILING_FILL_CANDIDATE',json.dumps(report),flush=True)
