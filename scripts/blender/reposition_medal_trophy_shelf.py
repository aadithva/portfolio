"""Hang the existing medal from the lamp-side end of the trophy shelf."""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
OUT = ROOT / 'artifacts/workspace/medal-trophy-placement'
CANDIDATE = OUT / 'workspace-medal-trophies.blend'
REPORT = OUT / 'application.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if '--promote' in sys.argv:
    report = json.loads(REPORT.read_text())
    if digest(SOURCE) != report['sourceSha256'] or digest(CANDIDATE) != report['candidateSha256']:
        raise RuntimeError('The master or candidate changed since the placement review.')
    shutil.copy2(CANDIDATE, SOURCE)
    print('MEDAL_PLACEMENT_PROMOTED', flush=True)
    raise SystemExit(0)

OUT.mkdir(parents=True, exist_ok=True)
source_hash = digest(SOURCE)
backup = OUT / f'source-before-placement-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.view_layer.update()
medal = bpy.data.objects['medal_1']
family = {medal.name, *(obj.name for obj in medal.children_recursive)}


def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        geometry = [tuple(v.co) for v in obj.data.vertices] if obj.type == 'MESH' else []
        light = (obj.data.energy, tuple(obj.data.color)) if obj.type == 'LIGHT' else None
        pose = list(map(tuple, obj.matrix_world)) if obj.name not in family else None
        result[obj.name] = hashlib.sha256(repr((pose, geometry, light,
            [s.material.name if s.material else None for s in obj.material_slots])).encode()).hexdigest()
    return result


def tree(objects):
    verts, faces = [], []
    graph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type not in {'MESH', 'CURVE'}:
            continue
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        offset = len(verts)
        verts.extend(obj.matrix_world @ v.co for v in mesh.vertices)
        faces.extend(tuple(offset + i for i in p.vertices) for p in mesh.polygons)
        evaluated.to_mesh_clear()
    return BVHTree.FromPolygons(verts, faces)


before = snapshot()
old_transform = list(map(list, medal.matrix_world))
wing = bpy.data.objects['workspace_right_wing']
shelf = bpy.data.objects['workspace_right_wing · Porcelain edges']
points = [wing.matrix_world.inverted() @ shelf.matrix_world @ v.co for v in shelf.data.vertices]
top = max(p.z for p in points)
outer_edge = max(p.x for p in points if p.z > top - .05)
# The existing hook rests .016 above its root. Turn the complete assembly to
# face out from the cabinet's end toward the lamp, retaining its hanging pivot.
anchor = wing.matrix_world @ Vector((outer_edge, -.07, top - .016))
rotation = wing.matrix_world.to_quaternion().to_matrix().to_4x4() @ Matrix.Rotation(math.pi / 2, 4, 'Z')
medal.matrix_world = Matrix.Translation(anchor) @ rotation
bpy.context.view_layer.update()
if snapshot() != before:
    raise RuntimeError('Geometry, material assignments, lights or unrelated poses changed.')
medal_tree = tree(medal.children_recursive)
collisions = {}
for name in ['trophy_1', 'trophy_2', 'plant_2', 'lamp_1', 'lamp_2', 'lamp_3', 'toy', 'monitor']:
    obj = bpy.data.objects[name]
    collisions[name] = len(medal_tree.overlap(tree([obj, *obj.children_recursive])))
if any(collisions.values()):
    raise RuntimeError('Medal intersects another object: ' + str(collisions))
web = lambda p: [round(p.x, 6), round(p.z, 6), round(-p.y, 6)]
points = [web(obj.matrix_world @ v.co) for obj in medal.children_recursive
          if obj.type == 'MESH' for v in obj.data.vertices]
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report = {
    'sourceSha256': source_hash, 'candidateSha256': digest(CANDIDATE),
    'backup': str(backup.relative_to(ROOT)), 'interactiveRoot': medal.name,
    'oldTransformBlender': old_transform, 'newTransformBlender': list(map(list, medal.matrix_world)),
    'webRoot': web(anchor),
    'webBounds': [[fn(p[i] for p in points) for i in range(3)] for fn in (min, max)],
    'shelfTop': top, 'hookRestHeight': anchor.z + .016,
    'unrelatedPosesAndAllGeometryUnchanged': True, 'intersections': collisions,
}
REPORT.write_text(json.dumps(report, indent=2) + '\n')
print('MEDAL_PLACEMENT_CANDIDATE', json.dumps(report), flush=True)

if '--render' in sys.argv:
    scene = bpy.context.scene
    camera = bpy.data.objects.new('Medal placement review camera', bpy.data.cameras.new('Medal placement review camera'))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.location = (3.5, -2.8, 3.6)
    target = Vector((.98, .96, 2.43))
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 1.25
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUT / 'placement-closeup.png')
    bpy.ops.render.render(write_still=True)
