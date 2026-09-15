"""Aim each saved shade and its own spotlight together around the existing hinge."""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_reference_layout import components

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
OUT = ROOT / 'artifacts/workspace/lamp-aim'
CANDIDATE = OUT / 'workspace-aimed-lamps.blend'
REPORT = OUT / 'application.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def B(p):
    return Vector((p[0], -p[2], p[1]))


def web(p):
    return [round(p.x, 6), round(p.z, 6), round(-p.y, 6)]


if '--promote' in sys.argv:
    report = json.loads(REPORT.read_text())
    if digest(SOURCE) != report['sourceSha256'] or digest(CANDIDATE) != report['candidateSha256']:
        raise RuntimeError('Master or candidate changed after review.')
    shutil.copy2(CANDIDATE, SOURCE)
    print('LAMP_AIM_PROMOTED', flush=True)
    raise SystemExit(0)

OUT.mkdir(parents=True, exist_ok=True)
source_hash = digest(SOURCE)
backup = OUT / f'source-before-aim-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.view_layer.update()
roots = [bpy.data.objects[f'lamp_{i}'] for i in range(1, 4)]
light_names = ['Red lamp practical.002', 'Red lamp practical.001', 'Red lamp practical']
extra = bpy.data.objects['Red lamp practical.003']
changed = {o.name for root in roots for o in [root, *root.children_recursive]} | set(light_names) | {extra.name}
arm_batch = bpy.data.objects['_static · Lamp edge red']
arm_ids = set()
for ids in components(arm_batch.data):
    ps = [arm_batch.matrix_world @ arm_batch.data.vertices[i].co for i in ids]
    if min(p.z for p in ps) > 1.95 and max(p.z for p in ps) < 2.25:
        arm_ids.update(ids)
if len(arm_ids) != 160:
    raise RuntimeError('Expected the saved middle articulated arm.')


def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.name in changed:
            continue
        geometry = [tuple(v.co) for v in obj.data.vertices if obj != arm_batch or v.index not in arm_ids] if obj.type == 'MESH' else []
        light = (obj.data.type, obj.data.energy, tuple(obj.data.color), list(obj.rotation_euler)) if obj.type == 'LIGHT' else None
        result[obj.name] = hashlib.sha256(repr((list(map(tuple,obj.matrix_world)), geometry,
            [s.material.name if s.material else None for s in obj.material_slots], light)).encode()).hexdigest()
    return result


def center(obj):
    return sum((obj.matrix_world @ v.co for v in obj.data.vertices), Vector())/len(obj.data.vertices)


def tree(objects):
    verts, faces = [], []
    graph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type not in {'MESH','CURVE'}:
            continue
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        offset = len(verts)
        verts.extend(obj.matrix_world @ v.co for v in mesh.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in mesh.polygons)
        evaluated.to_mesh_clear()
    return BVHTree.FromPolygons(verts, faces)


before = snapshot()
# Swing the middle support around its existing pole clamp. Simply turning its
# shade toward the bicycle would otherwise put the bell through the lamp pole.
clamp = B((1.48,2.072,-.25))
swing = Matrix.Translation(clamp) @ Matrix.Rotation(math.pi,4,'Z') @ Matrix.Translation(-clamp)
inverse = arm_batch.matrix_world.inverted()
for index in arm_ids:
    vertex = arm_batch.data.vertices[index]
    vertex.co = inverse @ swing @ arm_batch.matrix_world @ vertex.co
arm_batch.data.update()
roots[1].matrix_world = swing @ roots[1].matrix_world
bpy.context.view_layer.update()
targets = [(0,1.31,-.88), (2.5,1.25,.61), (-.93,.82,.08)]
labels = ['desk center', 'bicycle', 'chair seat']
report = {'sourceSha256':source_hash,'backup':str(backup.relative_to(ROOT)), 'heads':[]}
for i, (root, target, label, light_name) in enumerate(zip(roots,targets,labels,light_names),1):
    rim = bpy.data.objects[f'Lamp {i} rolled rim']
    bulb = bpy.data.objects[f'lamp_bulb_{i}']
    pivot = root.matrix_world.translation.copy()
    old_axis = (center(rim)-pivot).normalized()
    target = B(target)
    axis = (target-pivot).normalized()
    rotation = old_axis.rotation_difference(axis).to_matrix().to_4x4()
    root.matrix_world = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot) @ root.matrix_world
    bpy.context.view_layer.update()
    mouth = center(rim)
    # Just inside the rolled lip. The cone exits the shade instead of shining
    # through its back, and avoids self-shadowing from the decorative bulb.
    emitter = mouth-axis*.012
    light = bpy.data.objects[light_name]
    light.data.type = 'SPOT'
    light.data.energy = 113 if i == 1 else 42
    light.data.spot_size = math.radians(64 if i == 1 else 58 if i == 2 else 68)
    light.data.spot_blend = .6
    light.data.shadow_soft_size = .025
    light.parent = root
    light.matrix_world = Matrix.Translation(emitter) @ axis.to_track_quat('-Z','Y').to_matrix().to_4x4()
    light['lampRoot'] = root.name
    light['aimTarget'] = label
    root['aimTarget'] = label
    bpy.context.view_layer.update()
    actual_axis = (center(rim)-pivot).normalized()
    light_axis = light.matrix_world.to_quaternion() @ Vector((0,0,-1))
    error = math.degrees(actual_axis.angle(light_axis))
    shade_tree = tree([o for o in root.children_recursive if o.type != 'LIGHT'])
    collisions = {}
    for name in ['bicycle','chair','workspace_right_wing','monitor']:
        obj = bpy.data.objects[name]
        collisions[name] = len(shade_tree.overlap(tree([obj,*obj.children_recursive])))
    static = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj.parent is None
              and any(m and m.name in {'Lamp enamel vermilion','Lamp edge red'} for m in obj.data.materials)]
    collisions['lamp_stand'] = len(shade_tree.overlap(tree(static)))
    report['heads'].append({'root':root.name,'target':label,'targetWeb':web(target),'pivot':web(pivot),
        'opening':web(mouth),'emitter':web(emitter),'bulb':web(center(bulb)),'direction':web(actual_axis),
        'alignmentDegrees':error,'collisions':collisions})
    if error > .05:
        raise RuntimeError('Shade and spotlight axes diverged.')
    if any(value for name,value in collisions.items() if name != 'lamp_stand'):
        raise RuntimeError('A shade intersects the furniture.')
# Retain the historical extra light in the authoring file, disabled for baking
# and export. There are now exactly three active practical emitters.
extra.hide_render = True
extra.hide_viewport = True
if snapshot() != before:
    raise RuntimeError('An unrelated saved object changed.')
report['unrelatedObjectsUnchanged'] = True
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report['candidateSha256'] = digest(CANDIDATE)
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print('LAMP_AIM_CANDIDATE',json.dumps(report),flush=True)
