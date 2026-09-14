"""Enlarge the upper hutch around the display, starting from the saved model.

Blender --background --python-exit-code 1 --python scripts/blender/fit_monitor_shelves.py
Writes a review candidate; never replaces the editable source or web asset.
"""
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/workspace/shelf-fit'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
BACKUP = OUT / 'source-before-shelf-fit.blend'
if not BACKUP.exists():
    shutil.copy2(SOURCE, BACKUP)
bpy.ops.wm.open_mainfile(filepath=str(BACKUP))
if bpy.context.scene.get('shelfFitRevision'):
    raise RuntimeError('Use the original pre-fit backup; do not apply this displacement twice.')
spec = importlib.util.spec_from_file_location('layout', ROOT / 'scripts/blender/refine_reference_layout.py')
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
bpy.context.view_layer.update()

shift = .22
left, right = Vector((-shift, 0, shift)), Vector((shift, 0, shift))
changed = []


def translate(name, delta):
    obj = bpy.data.objects[name]
    matrix = obj.matrix_world.copy()
    matrix.translation += L.B(delta)
    obj.matrix_world = matrix
    bpy.context.view_layer.update()
    changed.append(name)


def edit_parts(name, ids, transform, expected_count=None):
    obj = bpy.data.objects[name]
    parts = L.components(obj.data)
    if expected_count is not None and len(parts) != expected_count:
        raise RuntimeError(f'{name}: expected {expected_count} components, found {len(parts)}')
    world, inverse = obj.matrix_world.copy(), obj.matrix_world.inverted()
    for part_id in ids:
        for index in parts[part_id]:
            vertex = obj.data.vertices[index]
            vertex.co = inverse @ L.B(transform(L.W(world @ vertex.co)))
    obj.data.update()
    changed.append(f'{name}: parts {list(ids)}')


# Wall-mounted pegboard and cards share a parent with the left cabinet. Only
# move the six cabinet boards and lower back; the wall geometry stays fixed.
edit_parts('workspace_left_wing · Porcelain edges', range(6), lambda p: p + left, 8)
edit_parts('workspace_left_wing · Warm powder-coated white', [0], lambda p: p + left, 3)
for name in ['books', 'figma', 'plant_1', 'Small aloe', 'Tiny jade plant']:
    translate(name, left)

# The right cabinet has no merged wall parts, but the window is a child too.
for child in list(bpy.data.objects['workspace_right_wing'].children):
    if child.name != 'window':
        translate(child.name, right)
for name in ['trophy_1', 'trophy_2']:
    translate(name, right)

# Extend the bridge to the relocated inner uprights, keeping its board depth,
# thickness and shelf height. Its brackets and decorations follow the shelf.
bridge_width = .686475
edit_parts('_static · Porcelain edges', [3],
           lambda p: Vector((p.x * (bridge_width + shift * 2) / bridge_width, p.y, p.z + shift)))
for part, side in [(6, -1), (7, 1)]:
    edit_parts('_static · Warm powder-coated white', [part],
               lambda p, side=side: p + Vector((side * shift, 0, shift)))
edit_parts('_static · Forest green', [0, 1, 2], lambda p: p + Vector((0, 0, shift)))
edit_parts('_static · Matte black rubber', [2], lambda p: p + left)
for name in ['speaker', 'medal_1', 'medal_2', 'medal_3']:
    translate(name, Vector((0, 0, shift)))

# The same-size display now sits within the wider opening. Its complete stand
# moves with it, preserving the tabletop contact and all interactive pivots.
for name in ['monitor', 'Monitor bounce']:
    translate(name, Vector((0, 0, -shift)))
bpy.context.view_layer.update()
bpy.context.scene['shelfFitRevision'] = 'upper-hutch-clearance-v1'
bpy.context.scene['shelfFitNotes'] = 'Upper cabinets widened 0.44 web units; bridge extended; display recessed 0.22. Wall/window fixed.'
bpy.ops.file.pack_all()
candidate = OUT / 'workspace-shelf-fit.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))
report = {
    'backup': str(BACKUP.relative_to(ROOT)),
    'sourceHash': hashlib.sha256(BACKUP.read_bytes()).hexdigest(),
    'candidate': str(candidate.relative_to(ROOT)),
    'shelfDisplacement': shift,
    'bridgeWidthBefore': bridge_width,
    'bridgeWidthAfter': bridge_width + shift * 2,
    'monitorSetback': shift,
    'changes': changed,
}
(OUT / 'changes.json').write_text(json.dumps(report, indent=2) + '\n')
print('SHELF_FIT_CANDIDATE', json.dumps(report), flush=True)
