"""Enlarge and lower the horizontal bicycle, moving its front toward the lamp."""
import json
import shutil
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
OUT=ROOT/'artifacts/workspace/bicycle-horizontal-adjustment';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
backup=OUT/'source-before-adjustment.blend'
if backup.exists():raise RuntimeError('Adjustment already applied')
shutil.copy2(SOURCE,backup)
C=Vector((0,2.55,0));U=Vector((0,0,1));T=Vector((1,-1,0)).normalized();N=Vector((-1,-1,0)).normalized()
bike=bpy.data.objects['bicycle'];origin=bike.matrix_world.translation.copy()
# Fifteen percent larger, 0.60 lower, 0.25 closer to the lamp along the wall.
center=origin-.25*T-.60*U
bike.matrix_world=Matrix.Translation(center)@Matrix.Scale(1.15,4)@Matrix.Translation(-origin)@bike.matrix_world
bpy.context.view_layer.update()
points=[o.matrix_world@v.co for o in bike.children_recursive if o.type=='MESH' for v in o.data.vertices]
minimum=min((v-C).dot(N) for v in points)
normal_shift=.12-minimum
bike.location+=normal_shift*N
# Carry the frame supports through the same resize and placement change.
mount=bpy.data.objects['bicycle_wall_mount']
mount.matrix_world=Matrix.Translation(normal_shift*N)@Matrix.Translation(center)@Matrix.Scale(1.15,4)@Matrix.Translation(-origin)@mount.matrix_world
bpy.context.view_layer.update()
def tree(root):
 vertices=[];faces=[];graph=bpy.context.evaluated_depsgraph_get()
 for obj in [root]+list(root.children_recursive):
  if obj.type not in {'MESH','CURVE'}:continue
  ev=obj.evaluated_get(graph);mesh=ev.to_mesh();start=len(vertices)
  vertices.extend(obj.matrix_world@v.co for v in mesh.vertices)
  faces.extend(tuple(start+i for i in p.vertices) for p in mesh.polygons);ev.to_mesh_clear()
 return BVHTree.FromPolygons(vertices,faces)
t=tree(bike)
collisions={name:len(t.overlap(tree(bpy.data.objects[name]))) for name in ['window','chair','workspace_right_wing','lamp_1','lamp_2','lamp_3']}
if any(collisions.values()):raise RuntimeError('Collision in adjusted placement: '+str(collisions))
points=[o.matrix_world@v.co for o in bike.children_recursive if o.type=='MESH' for v in o.data.vertices]
report={'scaleMultiplier':1.15,'lowered':.60,'towardLamp':.25,'height':[min(p.z for p in points),max(p.z for p in points)],'wallSpan':[min((p-C).dot(T) for p in points),max((p-C).dot(T) for p in points)],'collisions':collisions}
if report['height'][0]<.1:raise RuntimeError('Bicycle too close to ground')
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE));(OUT/'application.json').write_text(json.dumps(report,indent=2)+'\n');print('BICYCLE_ADJUSTED',report,flush=True)
