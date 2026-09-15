"""Fit two wall-mounted padded saddles to the saved bicycle's actual top tube."""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
OUT=ROOT/'artifacts/workspace/bicycle-lamp-clearance'
C=Vector((0,2.55,0))
T=Vector((1,-1,0)).normalized()
N=Vector((-1,-1,0)).normalized()
U=Vector((0,0,1))

def local(p):
    return Vector(((p-C).dot(T),(p-C).dot(N),p.z))

def world(p):
    return C+p[0]*T+p[1]*N+p[2]*U

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.view_layer.update()
bike=bpy.data.objects['bicycle']
mount=bpy.data.objects['bicycle_wall_mount']
frame=[o for o in bike.children_recursive if o.type=='MESH' and any(m and m.name=='rama' for m in o.data.materials)]
if '--inspect' in sys.argv:
    for obj in bike.children_recursive:
        if obj.type!='MESH':continue
        p=[local(obj.matrix_world@v.co) for v in obj.data.vertices]
        print('BIKE_PART',obj.name,[m.name for m in obj.data.materials if m],[[round(fn(v[i] for v in p),4) for i in range(3)] for fn in [min,max]],flush=True)
    for obj in frame:
        p=[local(obj.matrix_world@v.co) for v in obj.data.vertices]
        for s in [3.6,3.8,4.,4.2,4.4]:
            nearby=[v for v in p if abs(v.x-s)<.025]
            if nearby:
                print('FRAME_SECTION',s,[[round(v.y,4),round(v.z,4)] for v in sorted(nearby,key=lambda v:v.z)[-30:]],flush=True)
    raise SystemExit(0)

source_hash=digest(SOURCE)
backup=OUT/f'source-before-frame-mount-{source_hash[:12]}.blend'
if not backup.exists():shutil.copy2(SOURCE,backup)
old_mount=set([mount]+list(mount.children_recursive))
before={o.name:list(map(tuple,o.matrix_world)) for o in bpy.context.scene.objects if o not in old_mount}
main=bpy.data.objects['bicycle · 1']
mesh=main.data
tree=BVHTree.FromPolygons([main.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons])
contacts=[]
for s in [3.78,4.14]:
    top=tree.ray_cast(world((s,.4654,2.2)),-U,1.0)[0]
    if top is None:raise RuntimeError('No top tube at support location')
    underside=tree.ray_cast(top-.14*U,U,.15)[0]
    if underside is None:raise RuntimeError('Cannot locate underside of top tube')
    contacts.append(local(underside))
for obj in list(mount.children_recursive):bpy.data.objects.remove(obj,do_unlink=True)
mount.matrix_world=Matrix.Identity(4)
steel=bpy.data.materials['Bicycle mount · powder-coated steel']
rubber=bpy.data.materials['Bicycle mount · soft rubber']
silver=bpy.data.materials.get('Bicycle mount · fasteners') or bpy.data.materials['metal.silver']

def tube(name,coords,radius,material):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D'
    data.bevel_depth=radius;data.bevel_resolution=4
    spline=data.splines.new('POLY');spline.points.add(len(coords)-1)
    for p,value in zip(spline.points,coords):p.co=(*world(value),1)
    obj=bpy.data.objects.new('bicycle mount · '+name,data)
    bpy.context.collection.objects.link(obj);obj.parent=mount;data.materials.append(material)
    return obj

for index,(s,n,z) in enumerate(contacts,1):
    # Short wall plates and braced arms put the load directly beneath the tube.
    tube(f'{index} wall plate',[(s,.092,z-.25),(s,.092,z+.055)],.034,steel)
    for y in [z-.22,z+.025]:
        tube(f'{index} wall screw',[(s,.118,y),(s,.135,y)],.011,silver)
    tube(f'{index} load arm',[(s,.11,z-.06),(s,n-.055,z-.06),(s,n,z-.035)],.017,steel)
    tube(f'{index} diagonal brace',[(s,.115,z-.20),(s,n-.07,z-.065)],.011,steel)
    # A rubber-lined U cups the bottom of the frame rather than floating below.
    coords=[]
    for step in range(25):
        angle=math.pi+math.pi*step/24
        coords.append((s,n+.05*math.cos(angle),z+.036+.05*math.sin(angle)))
    tube(f'{index} padded frame saddle',coords,.014,rubber)
    tube(f'{index} saddle steel backing',[(x,y,h-.012) for x,y,h in coords],.011,steel)

bpy.context.view_layer.update()
after={o.name:list(map(tuple,o.matrix_world)) for o in bpy.context.scene.objects
       if o!=mount and o not in mount.children_recursive}
if before!=after:raise RuntimeError('Unrelated object transforms changed')
if digest(SOURCE)!=source_hash:raise RuntimeError('The master changed during mount fitting')
mount['attachment']='Two padded saddles contact the actual top-tube underside'
mount['contactPointsWallCoordinates']=json.dumps([list(p) for p in contacts])
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
report={'sourceSha256':source_hash,'resultSha256':digest(SOURCE),'topTubeContacts':[list(p) for p in contacts],
        'nominalPadContactGap':0,'unrelatedTransformsUnchanged':True}
(OUT/'mount-alignment.json').write_text(json.dumps(report,indent=2)+'\n')
print('FRAME_MOUNT_ALIGNED',json.dumps(report),flush=True)

if '--render' in sys.argv:
    scene=bpy.context.scene
    camera=bpy.data.objects.new('Frame mount review',bpy.data.cameras.new('Frame mount review'))
    scene.collection.objects.link(camera);scene.camera=camera
    target=world((3.96,.46,1.55))
    camera.location=world((2.95,2.5,2.3))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=55
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='METAL';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='METAL'
    scene.cycles.device='GPU'
    scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.render.filepath=str(OUT/'frame-mount-detail.png');bpy.ops.render.render(write_still=True)
