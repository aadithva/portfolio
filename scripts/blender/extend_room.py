"""Extend only the saved corner architecture, preserving props and tile pitch."""
import hashlib
import json
import math
import shutil
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
OUT = ROOT / 'artifacts/workspace/room-extension'
OUT.mkdir(exist_ok=True)
backup = OUT / 'source-before-extension.blend'
if backup.exists():
    raise RuntimeError('Extension already applied; use the backup for a fresh iteration.')
shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
corner = Vector((0, 2.55, 0))
changed = {}
for name in ['_static · Limewashed plaster', '_static · Warm powder-coated white']:
    obj = bpy.data.objects[name]
    inverse = obj.matrix_world.inverted()
    count = 0
    for vertex in obj.data.vertices:
        point = obj.matrix_world @ vertex.co
        sign = -1 if point.x < 0 else 1
        tangent = Vector((sign / math.sqrt(2), -1 / math.sqrt(2), 0))
        length = (point-corner).dot(tangent)
        if length > 4.32 and ('plaster' in name or point.z < .3):
            point += tangent * 10
            count += 1
        if 'plaster' in name and point.z > 4.5:
            point.z += 5.5
            count += 1
        vertex.co = inverse @ point
    obj.data.update()
    changed[name] = count
    if not count:
        raise RuntimeError('No architecture vertices extended for '+name)
# Rebuild the slab alone. Its top stays at the existing -0.015 elevation.
floor = bpy.data.objects['Room floor']
outline = [(0,2.68),(14,-11.32),(14,-14),(-14,-14),(-14,-11.32)]
verts = [(x,y,z) for z in [-.185,-.015] for x,y in outline]
faces = [tuple(reversed(range(5))), tuple(range(5,10))]
faces += [(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)]
mesh = bpy.data.meshes.new('Extended limestone slab')
mesh.from_pydata(verts,[],faces)
normal_mesh = bmesh.new()
normal_mesh.from_mesh(mesh)
bmesh.ops.recalc_face_normals(normal_mesh, faces=list(normal_mesh.faces))
normal_mesh.to_mesh(mesh)
normal_mesh.free()
mesh.materials.append(bpy.data.materials['Warm limestone'])
floor.data = mesh
floor.matrix_world.identity()
# Continue the original 1.1-unit grid, inset from the wall faces.
grout = bpy.data.objects['_static · Tile grout']
bpy.data.objects.remove(grout,do_unlink=True)
verts, faces = [], []
def seam(x0,y0,x1,y1):
    i=len(verts)
    verts.extend([(x0,y0,-.012),(x1,y0,-.012),(x1,y1,-.012),(x0,y1,-.012)])
    faces.append((i,i+1,i+2,i+3))
for i in range(-10,15):
    x=-2.8+i*1.1
    if abs(x)<13.98:
        seam(x-.0025,-13.98,x+.0025,2.66-abs(x))
for i in range(-1,15):
    z=-1.5+i*1.1
    if z<13.98:
        half=min(13.98,z+2.65)
        seam(-half,-z-.0025,half,-z+.0025)
mesh=bpy.data.meshes.new('Extended tile grid')
mesh.from_pydata(verts,[],faces)
mesh.materials.append(bpy.data.materials['Tile grout'])
obj=bpy.data.objects.new('_static · Tile grout',mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
(OUT/'application.json').write_text(json.dumps({'backup':str(backup),'wallExtension':10,'wallHeight':10.08,'floorWidth':28,'floorFront':14,'tilePitch':1.1,'changedVertices':changed},indent=2)+'\n')
print('ROOM_EXTENDED',changed,flush=True)
