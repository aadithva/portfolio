"""Remove the overlapping can wall and rebuild a smooth, open label surface."""
import json
import math
import shutil
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];SOURCE=ROOT/'artifacts/workspace/workspace.blend'
OUT=ROOT/'artifacts/workspace/can-surface-fix';OUT.mkdir(exist_ok=True)
backup=OUT/'source-before-surface-fix.blend'
if backup.exists():raise RuntimeError('Surface fix already applied')
shutil.copy2(SOURCE,backup);bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
label=bpy.data.objects['Can label cylinder'];shell=bpy.data.objects['can · Brushed aluminium']
center=label.matrix_world.translation.copy()
low=min((label.matrix_world@v.co).z for v in label.data.vertices)
high=max((label.matrix_world@v.co).z for v in label.data.vertices)
bm=bmesh.new();bm.from_mesh(shell.data)
remove=[]
for face in bm.faces:
 points=[shell.matrix_world@v.co for v in face.verts]
 # Only the long straight torso wall overlaps the printable body. Keep shoulders,
 # base, lid, rolled rims, pull tab, and rivet in their existing geometry.
 if min(p.z for p in points)>=low-.009 and max(p.z for p in points)<=high+.009 and max(p.z for p in points)-min(p.z for p in points)>.10:
  remove.append(face)
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(shell.data);bm.free()
if not remove:raise RuntimeError('No overlapping shell faces identified')
segments=128;radius=.046375
vertices=[(radius*math.cos(i*2*math.pi/segments),radius*math.sin(i*2*math.pi/segments),z-center.z) for z in [low,high] for i in range(segments)]
faces=[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
mesh=bpy.data.meshes.new('Single smooth can label wall');mesh.from_pydata(vertices,[],faces);mesh.materials.append(bpy.data.materials['Diet Coke aluminium label']);mesh.update()
label.data=mesh;uv=mesh.uv_layers.new(name='UVMap')
front=math.atan2(-5.7-center.y,2.4-center.x)
for poly in mesh.polygons:
 poly.use_smooth=True
 values=[]
 for loop in poly.loop_indices:
  vertex=mesh.vertices[mesh.loops[loop].vertex_index].co
  values.append((loop,((math.atan2(vertex.y,vertex.x)-front)/(2*math.pi)+.25)%1,(vertex.z+center.z-low)/(high-low)))
 crosses=max(v[1] for v in values)-min(v[1] for v in values)>.5
 for loop,u,v in values:uv.data[loop].uv=(u+1 if crosses and u<.5 else u,v)
# Pin the material's source coordinates to this UV channel for baking/export.
for node in mesh.materials[0].node_tree.nodes:
 if node.type=='UVMAP':node.uv_map=uv.name
label['webOptimized']=True
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
(OUT/'application.json').write_text(json.dumps({'removedOverlappingFaces':len(remove),'surfaceSegments':segments,'openCaps':True},indent=2)+'\n');print('CAN_SURFACE_FIXED',len(remove),flush=True)
