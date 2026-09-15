"""Lay the bicycle parallel to its current wall, front end toward the lamp."""
import json
import math
import shutil
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
OUT=ROOT/'artifacts/workspace/bicycle-horizontal';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
backup=OUT/'source-before-horizontal.blend'
if backup.exists():raise RuntimeError('Horizontal edit already applied')
shutil.copy2(SOURCE,backup)
C=Vector((0,2.55,0));U=Vector((0,0,1))
T=Vector((1,-1,0)).normalized();N=Vector((-1,-1,0)).normalized()
bike=bpy.data.objects['bicycle'];mount=bpy.data.objects['bicycle_wall_mount']
old=Matrix((U,-T,N)).transposed()
new=Matrix((-T,N,U)).transposed()
rotation=(new@old.inverted()).to_4x4()
origin=bike.matrix_world.translation.copy()
bike.matrix_world=Matrix.Translation(C+3.45*T+1.75*U+.45*N)@rotation@Matrix.Scale(.72,4)@Matrix.Translation(-origin)@bike.matrix_world
bpy.context.view_layer.update()
def points(root):return [o.matrix_world@v.co for o in root.children_recursive if o.type=='MESH' for v in o.data.vertices]
p=points(bike);clearance=min((v-C).dot(N) for v in p)
bike.location += N*(.12-clearance)
bpy.context.view_layer.update()
for obj in list(mount.children_recursive):bpy.data.objects.remove(obj,do_unlink=True)
steel=bpy.data.materials['Bicycle mount · powder-coated steel']
rubber=bpy.data.materials['Bicycle mount · soft rubber']
def tube(name,coords,radius,material):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=3
 spline=data.splines.new('POLY');spline.points.add(len(coords)-1)
 for p,(s,y,n) in zip(spline.points,coords):p.co=(*(C+s*T+y*U+n*N),1)
 obj=bpy.data.objects.new('bicycle mount · '+name,data);bpy.context.collection.objects.link(obj);obj.parent=mount;data.materials.append(material)
# Two padded cradles carry the upper frame instead of hooking a raised wheel.
for s in [3.25,3.60]:
 tube('wall fixing plate',[(s,1.86,.085),(s,2.13,.085)],.042,steel)
 tube('frame support arm',[(s,1.90,.10),(s,1.96,.28),(s,1.96,.38)],.019,steel)
 tube('padded frame cradle',[(s,2.015,.26),(s,1.965,.31),(s,1.965,.37),(s,2.015,.42)],.026,rubber)
bike['mount']='Horizontal wall-parallel frame cradles; handlebars toward lamp and room corner'
bpy.context.view_layer.update()
p=points(bike)
report={'wallSpan':[min((v-C).dot(T) for v in p),max((v-C).dot(T) for v in p)],'height':[min(v.z for v in p),max(v.z for v in p)],'wallDepth':[min((v-C).dot(N) for v in p),max((v-C).dot(N) for v in p)],'frontDirection':'toward lamp / room corner'}
if report['height'][0]<.1 or report['wallDepth'][0]<.09:raise RuntimeError(str(report))
def tree(root):
 verts=[];faces=[];graph=bpy.context.evaluated_depsgraph_get()
 for o in [root]+list(root.children_recursive):
  if o.type not in {'MESH','CURVE'}:continue
  ev=o.evaluated_get(graph);mesh=ev.to_mesh();start=len(verts)
  verts.extend(o.matrix_world@v.co for v in mesh.vertices);faces.extend(tuple(start+i for i in f.vertices) for f in mesh.polygons);ev.to_mesh_clear()
 return BVHTree.FromPolygons(verts,faces)
bike_tree=tree(bike)
report['intersections']={name:len(bike_tree.overlap(tree(bpy.data.objects[name]))) for name in ['window','chair','workspace_right_wing','lamp_1','lamp_2','lamp_3']}
if any(report['intersections'].values()):raise RuntimeError('Bicycle collisions: '+str(report))
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
(OUT/'application.json').write_text(json.dumps(report,indent=2)+'\n');print('HORIZONTAL_BICYCLE',report,flush=True)
