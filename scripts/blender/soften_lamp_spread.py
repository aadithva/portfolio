"""Broaden the aligned practicals without changing the heads or their aim."""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
OUT = ROOT / 'artifacts/workspace/lamp-spread'
CANDIDATE = OUT / 'workspace-soft-lamps.blend'
REPORT = OUT / 'application.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if '--promote' in sys.argv:
    report = json.loads(REPORT.read_text())
    if digest(SOURCE) != report['sourceSha256'] or digest(CANDIDATE) != report['candidateSha256']:
        raise RuntimeError('Master or candidate changed after review.')
    shutil.copy2(CANDIDATE, SOURCE)
    print('SOFT_LAMPS_PROMOTED', flush=True)
    raise SystemExit(0)

OUT.mkdir(parents=True, exist_ok=True)
source_hash = digest(SOURCE)
backup = OUT / f'source-before-spread-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
settings = {'lamp_1': (112, 100), 'lamp_2': (108, 60), 'lamp_3': (116, 70)}
report = {'sourceSha256': source_hash, 'backup': str(backup.relative_to(ROOT)), 'lights': []}
for obj in bpy.context.scene.objects:
    if obj.type != 'LIGHT' or obj.hide_render or obj.get('lampRoot') not in settings:
        continue
    light = obj.data
    angle, power = settings[obj['lampRoot']]
    old = {'angle': math.degrees(light.spot_size), 'power': light.energy, 'blend': light.spot_blend}
    light.spot_size = math.radians(angle)
    light.spot_blend = .85
    light.shadow_soft_size = .085
    light.energy = power
    report['lights'].append({'root': obj['lampRoot'], 'before': old,
                            'angle': angle, 'power': power, 'blend': .85, 'radius': .085})
if len(report['lights']) != 3:
    raise RuntimeError('Expected exactly three aligned lamp lights.')
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report['candidateSha256'] = digest(CANDIDATE)
REPORT.write_text(json.dumps(report, indent=2)+'\n')
print('SOFT_LAMPS_CANDIDATE', json.dumps(report), flush=True)
