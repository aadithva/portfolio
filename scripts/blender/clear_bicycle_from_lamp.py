"""Uniformly enlarge the current horizontal bicycle and separate it from the lamp."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
OUT=ROOT/'artifacts/workspace/bicycle-lamp-clearance'
OUT.mkdir(exist_ok=True)
CANDIDATE=OUT/'workspace-bicycle-clearance.blend'
REPORT=OUT/'application.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if '--promote' in sys.argv:
    report=json.loads(REPORT.read_text())
    if digest(SOURCE)!=report['sourceSha256'] or digest(CANDIDATE)!=report['candidateSha256']:
        raise RuntimeError('The source or candidate changed during review.')
    shutil.copy2(CANDIDATE,SOURCE)
    print('BICYCLE_CLEARANCE_PROMOTED',flush=True)
    raise SystemExit(0)

source_hash=digest(SOURCE)
input_source=SOURCE
backup=OUT/f'source-before-clearance-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE,backup)
bpy.ops.wm.open_mainfile(filepath=str(input_source))
bpy.context.view_layer.update()
bike=bpy.data.objects['bicycle']
mount=bpy.data.objects['bicycle_wall_mount']
if bike.get('lampClearanceRevision') and '--refine' not in sys.argv:
    raise RuntimeError('The bicycle clearance correction is already applied.')

def family(root):
    return [root]+list(root.children_recursive)

def points(root):
    return [obj.matrix_world@v.co for obj in family(root) if obj.type=='MESH' for v in obj.data.vertices]

excluded=set(family(bike)+family(mount))
def snapshot():
    return {obj.name:repr((list(map(tuple,obj.matrix_world)),
            [tuple(v.co) for v in obj.data.vertices] if obj.type=='MESH' else [],
            [slot.material.name if slot.material else None for slot in obj.material_slots],
            (obj.data.energy,tuple(obj.data.color)) if obj.type=='LIGHT' else None))
            for obj in bpy.context.scene.objects if obj not in excluded}

before=snapshot()
C=Vector((0,2.55,0))
T=Vector((1,-1,0)).normalized()
N=Vector((-1,-1,0)).normalized()
U=Vector((0,0,1))
old_points=points(bike)
origin=bike.matrix_world.translation.copy()
scale=1.20
wall_shift=.80
floor_height=.50
if '--refine' in sys.argv:
    if bike.get('lampClearanceRevision')!=1:
        raise RuntimeError('Expected the first reviewed placement for refinement.')
    scale=1.20/1.30
    wall_shift=-.10
# One similarity transform preserves every wheel, frame member and handlebar
# proportion. The wall contact datum also keeps the support plates on the wall.
anchor=C+(origin-C).dot(T)*T+.075*N
height_shift=floor_height-min(p.z for p in old_points)*scale
transform=Matrix.Translation(wall_shift*T+height_shift*U)@Matrix.Translation(anchor)@Matrix.Scale(scale,4)@Matrix.Translation(-anchor)
for obj in (bike,mount):
    obj.matrix_world=transform@obj.matrix_world
bike['lampClearanceRevision']=2 if '--refine' in sys.argv else 1
bike['mount']='Horizontal wall-parallel frame cradles, separated from the lamp along the right wall'
bpy.context.view_layer.update()

def tree(objects):
    vertices=[]
    faces=[]
    graph=bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type not in {'MESH','CURVE'}:
            continue
        evaluated=obj.evaluated_get(graph)
        mesh=evaluated.to_mesh()
        start=len(vertices)
        vertices.extend(obj.matrix_world@v.co for v in mesh.vertices)
        faces.extend(tuple(start+i for i in p.vertices) for p in mesh.polygons)
        evaluated.to_mesh_clear()
    return BVHTree.FromPolygons(vertices,faces)

bike_tree=tree(family(bike))
collisions={name:len(bike_tree.overlap(tree(family(bpy.data.objects[name]))))
            for name in ['window','chair','workspace_right_wing','lamp_1','lamp_2','lamp_3']}
lamp_static=[obj for obj in bpy.context.scene.objects if obj.type=='MESH' and obj.parent is None
             and any(material and ('Lamp' in material.name or material.name=='Matte black rubber') for material in obj.data.materials)]
collisions['lamp_stand_and_base']=len(bike_tree.overlap(tree(lamp_static)))
if any(collisions.values()):
    raise RuntimeError('Bicycle intersects room geometry: '+str(collisions))
if snapshot()!=before:
    raise RuntimeError('Unrelated scene objects changed.')
new_points=points(bike)
if min((p-C).dot(N) for p in new_points)<.095:
    raise RuntimeError('The bicycle intersects the wall.')
if digest(SOURCE)!=source_hash:
    raise RuntimeError('The master changed during the correction.')
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report={'sourceSha256':source_hash,'candidateSha256':digest(CANDIDATE),'scaleMultiplier':scale,
        'rightwardWallShift':wall_shift,'height':[min(p.z for p in new_points),max(p.z for p in new_points)],
        'wallSpan':[min((p-C).dot(T) for p in new_points),max((p-C).dot(T) for p in new_points)],
        'uniformTransformScale':list(transform.to_scale()),'collisions':collisions,'unrelatedObjectsUnchanged':True}
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print('BICYCLE_CLEARANCE_CANDIDATE',json.dumps(report),flush=True)
