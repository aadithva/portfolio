"""Replace only the saved desktop slab with a smooth perimeter and rolled edges."""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_reference_layout import components

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
OUT = ROOT / 'artifacts/workspace/desktop-edge'
CANDIDATE = OUT / 'workspace-desktop-edge.blend'
REPORT = OUT / 'application.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if '--promote' in sys.argv:
    report = json.loads(REPORT.read_text())
    if digest(SOURCE) != report['sourceSha256'] or digest(CANDIDATE) != report['candidateSha256']:
        raise RuntimeError('Master or candidate changed after review.')
    shutil.copy2(CANDIDATE, SOURCE)
    print('DESKTOP_EDGE_PROMOTED', flush=True)
    raise SystemExit(0)

OUT.mkdir(parents=True, exist_ok=True)
source_hash = digest(SOURCE)
backup = OUT / f'source-before-edge-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.view_layer.update()
batch = bpy.data.objects['_static · Porcelain edges']
slabs = []
for ids in components(batch.data):
    ps = [batch.matrix_world @ batch.data.vertices[i].co for i in ids]
    low, high = min(p.z for p in ps), max(p.z for p in ps)
    if abs(high - 1.31) < .001 and abs(low - 1.2090459) < .001 and max(p.x for p in ps)-min(p.x for p in ps) > 2:
        slabs.append(ids)
if len(slabs) != 1:
    raise RuntimeError('Expected one saved desktop slab.')
removed = set(slabs[0])


def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.name == 'Corner desk smooth desktop':
            continue
        verts = [tuple(v.co) for v in obj.data.vertices
                 if obj != batch or v.index not in removed] if obj.type == 'MESH' else []
        light = (obj.data.energy, tuple(obj.data.color)) if obj.type == 'LIGHT' else None
        result[obj.name] = hashlib.sha256(repr((list(map(tuple, obj.matrix_world)), verts,
            [s.material.name if s.material else None for s in obj.material_slots], light)).encode()).hexdigest()
    return result


before = snapshot()
old_slab_triangles = sum(len(p.vertices)-2 for p in batch.data.polygons if p.vertices[0] in removed)
# Retain the saved MICKE footprint. Sample the front as a continuous cubic curve
# through the original design points, instead of the fourteen-sided slab.
anchors = [(2.43,.09),(1.68,.89),(1.40,.98),(1.06,.93),(.76,.84),(.39,.78),
           (0,.76),(-.39,.78),(-.76,.84),(-1.06,.93),(-1.40,.98),(-1.68,.89),(-2.43,.09)]
anchors = [Vector((x*.5085, 2.34-(z+2.34)*.5085)) for x,z in anchors]
rear = Vector((0,2.34))
perimeter = [rear]
for i in range(len(anchors)-1):
    a, b = anchors[i:i+2]
    previous = anchors[i-1] if i else a-(b-a)
    following = anchors[i+2] if i+2 < len(anchors) else b+(b-a)
    tangent_a, tangent_b = (b-previous)*.5, (following-a)*.5
    for j in range(10):
        t = j/10
        perimeter.append((2*t**3-3*t*t+1)*a + (t**3-2*t*t+t)*tangent_a
                         + (-2*t**3+3*t*t)*b + (t**3-t*t)*tangent_b)
perimeter.append(anchors[-1])
# Clockwise perimeter: its left-hand normal points out of the slab.
normals = []
insets = []
for i, p in enumerate(perimeter):
    incoming = (p-perimeter[i-1]).normalized()
    outgoing = (perimeter[(i+1)%len(perimeter)]-p).normalized()
    n1, n2 = Vector((-incoming.y,incoming.x)), Vector((-outgoing.y,outgoing.x))
    normal = (n1+n2).normalized()
    normals.append(normal)
    insets.append(normal/max(.25,normal.dot(n1)))

bottom, top, radius = 1.2090458869934082, 1.309999942779541, .006
profiles = []
for j in range(5):
    angle = j*math.pi/8
    profiles.append((radius*(1-math.sin(angle)), bottom+radius*(1-math.cos(angle)), math.sin(angle), -math.cos(angle)))
for j in range(5):
    angle = j*math.pi/8
    profiles.append((radius*(1-math.cos(angle)), top-radius+radius*math.sin(angle), math.cos(angle), math.sin(angle)))
verts, vertex_normals, faces = [], [], []
n = len(perimeter)
for inset, height, horizontal, vertical in profiles:
    for p, normal, offset in zip(perimeter,normals,insets):
        q = p-offset*inset
        verts.append((q.x,q.y,height))
        vertex_normals.append((normal.x*horizontal,normal.y*horizontal,vertical))
for ring in range(len(profiles)-1):
    for i in range(n):
        q = (i+1)%n
        faces.append((ring*n+i,(ring+1)*n+i,(ring+1)*n+q,ring*n+q))
for ring, upward in [(0,False),(len(profiles)-1,True)]:
    points = [Vector(v) for v in verts[ring*n:(ring+1)*n]]
    for tri in tessellate_polygon([points]):
        indices = [ring*n+i for i in tri]
        normal_z = (points[tri[1]]-points[tri[0]]).cross(points[tri[2]]-points[tri[0]]).z
        if (normal_z > 0) != upward:
            indices.reverse()
        faces.append(tuple(indices))
mesh = bpy.data.meshes.new('Smooth desktop perimeter with 3.4 mm edge radius')
mesh.from_pydata(verts,[],faces)
mesh.update()
for face in mesh.polygons:
    face.use_smooth = True
mesh.normals_split_custom_set([vertex_normals[loop.vertex_index] for loop in mesh.loops])
desktop = bpy.data.objects.new('Corner desk smooth desktop',mesh)
bpy.context.scene.collection.objects.link(desktop)
desktop.data.materials.append(bpy.data.materials['Porcelain edges'])
desktop['webOptimized'] = True
desktop['edgeQuality'] = '120 front curve samples; analytic rounded-edge normals'
# Keep this independently editable and prevent a second generic decimation pass.
surface = bpy.data.objects['desktop_surface']
world = desktop.matrix_world.copy()
desktop.parent = surface
desktop.matrix_world = world
bm = bmesh.new()
bm.from_mesh(batch.data)
bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.verts[i] for i in removed],context='VERTS')
bm.to_mesh(batch.data)
bm.free()
removed.clear()
bpy.context.view_layer.update()
if snapshot() != before:
    raise RuntimeError('Unrelated saved objects or other porcelain parts changed.')
check = bmesh.new()
check.from_mesh(mesh)
non_manifold = sum(not e.is_manifold for e in check.edges)
check.free()
if non_manifold:
    raise RuntimeError('Desktop must be a closed manifold slab.')
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report = {'sourceSha256':source_hash,'candidateSha256':digest(CANDIDATE),
          'backup':str(backup.relative_to(ROOT)), 'oldSlabTriangles':old_slab_triangles,
          'newSlabTriangles':sum(len(p.vertices)-2 for p in mesh.polygons),
          'perimeterSamples':n,'edgeRadius':radius,'topHeight':top,'bottomHeight':bottom,
          'nonManifoldEdges':non_manifold,'unrelatedObjectsUnchanged':True}
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print('DESKTOP_EDGE_CANDIDATE',json.dumps(report),flush=True)
