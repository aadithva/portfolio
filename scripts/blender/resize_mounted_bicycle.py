"""Make the current wheel-hook bicycle smaller and lower without rebuilding room edits."""
import hashlib
import json
import shutil
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
OUT=ROOT/'artifacts/workspace/balcony-door'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
backup=OUT/f'source-before-bike-resize-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE,backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.view_layer.update()
bike=bpy.data.objects['bicycle']
mount=bpy.data.objects['bicycle_wall_mount']
if bike.get('balconySizeRevision'):
    raise RuntimeError('The bicycle already has this size adjustment.')

def points(root):
    return [obj.matrix_world@vertex.co for obj in root.children_recursive if obj.type=='MESH' for vertex in obj.data.vertices]

old_points=points(bike)
low=min(p.z for p in old_points)
scale=.85
floor_clearance=.20
datum=Vector((0,2.55,0))
tangent=Vector((2**-.5,-2**-.5,0))
normal=Vector((-2**-.5,-2**-.5,0))
position=bike.matrix_world.translation
wall_datum=datum+(position-datum).dot(tangent)*tangent+.075*normal
transform=Matrix.Translation(Vector((0,0,floor_clearance-low*scale)))@Matrix.Translation(wall_datum)@Matrix.Scale(scale,4)@Matrix.Translation(-wall_datum)
for obj in (bike,mount):
    obj.matrix_world=transform@obj.matrix_world
bike['balconySizeRevision']=1
bike['presentationScale']=scale
bpy.context.view_layer.update()
new_points=points(bike)
report={'sourceSha256':source_hash,'scale':scale,'previousHeight':[min(p.z for p in old_points),max(p.z for p in old_points)],
        'newHeight':[min(p.z for p in new_points),max(p.z for p in new_points)],'mountFollowsBicycle':True}
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=source_hash:
    raise RuntimeError('The master changed during adjustment.')
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
report['resultSha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
(OUT/'bicycle-resize.json').write_text(json.dumps(report,indent=2)+'\n')
print('BICYCLE_RESIZED',json.dumps(report),flush=True)
