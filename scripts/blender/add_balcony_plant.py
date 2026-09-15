"""Add one leafy floor plant in the desk-side exterior balcony corner."""
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
OUT = ROOT / 'artifacts/workspace/balcony-plant'
CANDIDATE = OUT / 'workspace-balcony-plant.blend'
REPORT = OUT / 'application.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if '--promote' in sys.argv:
    report = json.loads(REPORT.read_text())
    if digest(SOURCE) != report['sourceSha256'] or digest(CANDIDATE) != report['candidateSha256']:
        raise RuntimeError('Master or candidate changed after review.')
    shutil.copy2(CANDIDATE, SOURCE)
    print('BALCONY_PLANT_PROMOTED', flush=True)
    raise SystemExit(0)

OUT.mkdir(parents=True, exist_ok=True)
source_hash = digest(SOURCE)
backup = OUT / f'source-before-plant-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
if bpy.data.objects.get('balcony_plant'):
    raise RuntimeError('A balcony plant already exists.')


def snapshot():
    return {o.name: hashlib.sha256(repr((list(map(tuple,o.matrix_world)),
        [tuple(v.co) for v in o.data.vertices] if o.type == 'MESH' else [],
        [s.material.name if s.material else None for s in o.material_slots],
        (o.data.energy,tuple(o.data.color)) if o.type == 'LIGHT' else None)).encode()).hexdigest()
        for o in bpy.context.scene.objects if not o.name.startswith('balcony_plant')}


before = snapshot()
T = Vector((-1/math.sqrt(2),-1/math.sqrt(2),0))
N = Vector((1/math.sqrt(2),-1/math.sqrt(2),0))
origin = Vector((0,2.55,-.025))+T*2.67-N*.65
root = bpy.data.objects.new('balcony_plant',None)
bpy.context.scene.collection.objects.link(root)
root.location = origin
root['description'] = 'Rubber plant in a matte terracotta floor pot, outside the balcony glass'


def mesh(name,verts,faces,material):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts,[],faces)
    data.update()
    obj = bpy.data.objects.new('balcony_plant · '+name,data)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    data.materials.append(material)
    obj['webOptimized'] = True
    for p in data.polygons:
        p.use_smooth = True
    return obj


def lathe(name,profile,material):
    verts,faces = [],[]
    count = 48
    for z,r in profile:
        verts.extend((r*math.cos(i*math.tau/count),r*math.sin(i*math.tau/count),z) for i in range(count))
    for j in range(len(profile)-1):
        for i in range(count):
            q=(i+1)%count
            faces.append((j*count+i,j*count+q,(j+1)*count+q,(j+1)*count+i))
    return mesh(name,verts,faces,material)


pot_material = bpy.data.materials['Terracotta clay'].copy()
pot_material.name = 'Balcony plant · warm clay'
shader = pot_material.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value = (.32,.135,.065,1)
shader.inputs['Roughness'].default_value = .88
lathe('rounded tapered clay pot',[(.008,0),(.008,.16),(.015,.175),(.035,.18),(.35,.232),
      (.37,.24),(.397,.24),(.41,.231),(.41,.215),(.395,.207),(.36,.208),(.065,.154),(.055,0)],pot_material)
lathe('visible soil',[(.366,0),(.366,.207)],bpy.data.materials['Potting soil'])
stem_material = bpy.data.materials['Leaf shaded']


def tube(name,points,radius):
    curve = bpy.data.curves.new(name,'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for p,co in zip(spline.bezier_points,points):
        p.co = co
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    curve.resolution_u = 6
    obj = bpy.data.objects.new('balcony_plant · '+name,curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    curve.materials.append(stem_material)


foliage_materials = []
for name,color in [('deep green',(.028,.105,.037)),('fresh green',(.052,.18,.064))]:
    mat = bpy.data.materials.new('Balcony plant · '+name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color,1)
    shader.inputs['Roughness'].default_value = .56
    foliage_materials.append(mat)

for branch,(bx,by,height,phase) in enumerate([(-.06,.015,1.56,.3),(.065,-.03,1.29,2.5),(.015,.07,1.1,4.2)]):
    tube(f'stem {branch}',[(bx,by,.355),(bx*.6,by, height*.6),(bx+.035,by+.01,height)],.012)
    for leaf in range(6):
        z = .56+leaf*(height-.59)/5
        angle = phase+leaf*2.4
        direction = Vector((math.cos(angle),math.sin(angle),0))
        across = Vector((-direction.y,direction.x,0))
        start = Vector((bx+.035*(z/height),by,z))
        base = start+direction*.065+Vector((0,0,.035))
        length = .34 if leaf < 4 else .28
        width = .105 if leaf < 4 else .087
        tube(f'petiole {branch}-{leaf}',[start,base],.005)
        verts,faces = [],[]
        for row in range(13):
            t = row/12
            mid = base+direction*length*t+Vector((0,0,.12*math.sin(t*math.pi*.85)-.085*t*t))
            breadth = width*math.sin(math.pi*t)**.8
            for column in range(5):
                u = (column-2)/2
                point = mid+across*breadth*u+Vector((0,0,-.022*abs(u)*math.sin(math.pi*t)))
                verts.append(tuple(point))
        for row in range(12):
            for column in range(4):
                a=row*5+column
                faces.append((a,a+1,a+6,a+5))
        obj=mesh(f'curved leaf {branch}-{leaf}',verts,faces,foliage_materials[(branch+leaf)%2])
        solid=obj.modifiers.new('Leaf thickness','SOLIDIFY')
        solid.thickness=.0012

bpy.context.view_layer.update()
if snapshot() != before:
    raise RuntimeError('An existing object changed.')


def tree(objects):
    verts,faces=[],[]
    graph=bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type not in {'MESH','CURVE'}:
            continue
        evaluated=obj.evaluated_get(graph)
        data=evaluated.to_mesh()
        offset=len(verts)
        verts.extend(obj.matrix_world@v.co for v in data.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in data.polygons)
        evaluated.to_mesh_clear()
    return BVHTree.FromPolygons(verts,faces)


plant_tree=tree(root.children_recursive)
obstacles=[bpy.data.objects['balcony_door'],bpy.data.objects['balcony_exterior']]
collisions={o.name:len(plant_tree.overlap(tree([o,*o.children_recursive]))) for o in obstacles}
if any(collisions.values()):
    raise RuntimeError('Plant intersects the door or balcony: '+str(collisions))
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report={'sourceSha256':source_hash,'candidateSha256':digest(CANDIDATE),
        'backup':str(backup.relative_to(ROOT)),'positionWeb':[origin.x,origin.z,-origin.y],
        'height':1.56,'potDiameter':.48,'leaves':18,'unrelatedObjectsUnchanged':True,'collisions':collisions}
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print('BALCONY_PLANT_CANDIDATE',json.dumps(report),flush=True)
