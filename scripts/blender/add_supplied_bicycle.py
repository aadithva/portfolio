"""Fit the user's road-bike FBX to the free left wall on a backed-up scene."""
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
OUT=ROOT/'artifacts/workspace/bicycle'
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
CANDIDATE=OUT/'workspace-bicycle.blend'
REPORT=OUT/'application.json'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

if '--promote' in sys.argv:
    report=json.loads(REPORT.read_text())
    if digest(SOURCE)!=report['sourceSha256']:raise RuntimeError('The master changed after the bicycle edit.')
    if digest(CANDIDATE)!=report['candidateSha256']:raise RuntimeError('The candidate changed after validation.')
    shutil.copy2(CANDIDATE,SOURCE)
    print('BICYCLE_PROMOTED',SOURCE)
    raise SystemExit(0)

source_hash=digest(SOURCE)
backup=OUT/f'source-before-bicycle-{source_hash[:12]}.blend'
if not backup.exists():shutil.copy2(SOURCE,backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
if bpy.data.objects.get('bicycle'):raise RuntimeError('The scene already contains a bicycle.')
bpy.context.view_layer.update()

def snapshot():
    result={}
    for obj in bpy.context.scene.objects:
        if obj.name.startswith('bicycle'):continue
        verts=[tuple(v.co) for v in obj.data.vertices] if obj.type=='MESH' else []
        light=(obj.data.type,obj.data.energy,tuple(obj.data.color)) if obj.type=='LIGHT' else None
        result[obj.name]=hashlib.sha256(repr((list(map(tuple,obj.matrix_world)),verts,
          [s.material.name if s.material else None for s in obj.material_slots],light)).encode()).hexdigest()
    return result

before=snapshot()
existing=set(bpy.context.scene.objects)
bpy.ops.import_scene.fbx(filepath=str(OUT/'source/source/road_bike.fbx'))
imported=list(set(bpy.context.scene.objects)-existing)
meshes=[o for o in imported if o.type=='MESH']
original_triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons)

def group(name):
    obj=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(obj);return obj

def web(v):return Vector((v[0],-v[2],v[1]))
T=web((-.70710678,0,.70710678));N=web((.70710678,0,.70710678));U=web((0,1,0))
C=web((0,0,-2.55))
# Actual tyre diameter is 1.59363 FBX units. Calibrate to a 69 cm adult tyre.
scale=(.69*1.31/.75)/1.59363
datum=Vector((.003073,0,.800735))
rotation=Matrix((U,-N,T)).transposed().to_4x4()
root=group('bicycle');root.location=C+3.25*T+.55*N+2.10*U
root['sourceAsset']='User supplied road-bike.zip / source/road_bike.fbx'
root['interactive']=True
root['sourceTriangles']=original_triangles
root['uniformScale']=scale
root['calibration']='69 cm tyre diameter; FBX units were not metric'
root['mount']='Vertical, front wheel up, padded upper hook and lower stabilizer'
for obj in meshes:
    original_name=obj.name
    obj.data.transform(rotation@Matrix.Scale(scale,4)@Matrix.Translation(-datum)@obj.matrix_world)
    obj.parent=root;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
    obj.name='bicycle · '+original_name
    # Keep the original editable geometry. The exporter applies these modifiers.
    triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)
    modifier=obj.modifiers.new('Web bicycle optimization','DECIMATE')
    modifier.ratio=.012 if original_name.startswith('protector') else .025 if triangles>40000 else .10 if triangles>2000 else .20
    modifier.use_collapse_triangulate=True
    obj['webOptimized']=True
    if not obj.data.materials:
        obj.data.materials.append(bpy.data.materials['metal.black'])
    for material in obj.data.materials:
        if material and material.use_nodes:
            shader=material.node_tree.nodes.get('Principled BSDF')
            if shader:
                # Preserve the supplied colors; translate material intent to PBR.
                shader.inputs['Metallic'].default_value=.72 if 'metal.silver' in material.name else .25 if material.name in {'rama','orange.metal'} else .05
                shader.inputs['Roughness'].default_value=.3 if 'silver' in material.name else .44 if material.name=='rama' else .7
for obj in imported:
    if obj.type!='MESH':bpy.data.objects.remove(obj,do_unlink=True)

mount=group('bicycle_wall_mount')
def material(name,color,metal=0,rough=.65):
    m=bpy.data.materials.new(name);m.use_nodes=True
    shader=m.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(*color,1)
    shader.inputs['Metallic'].default_value=metal;shader.inputs['Roughness'].default_value=rough
    return m
steel=material('Bicycle mount · powder-coated steel',(.045,.048,.045),.65,.42)
rubber=material('Bicycle mount · soft rubber',(.018,.02,.018))
silver=material('Bicycle mount · fasteners',(.3,.31,.32),.9,.3)
def point(s,y,n):return C+s*T+y*U+n*N
def box(name,position,size,mat):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj=bpy.context.object;obj.name='bicycle mount · '+name
    basis=Matrix((T,-N,U)).transposed().to_4x4()
    obj.matrix_world=Matrix.Translation(position)@basis@Matrix.Diagonal(Vector((*size,1)))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.parent=mount;obj.data.materials.append(mat)
    mod=obj.modifiers.new('Manufactured edges','BEVEL');mod.width=.008;mod.segments=2
    return obj
def tube(name,points,radius,mat):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=2
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for p,v in zip(spline.points,points):p.co=(*v,1)
    obj=bpy.data.objects.new('bicycle mount · '+name,data);bpy.context.collection.objects.link(obj)
    obj.parent=mount;data.materials.append(mat)
    return obj
front=2.10+(1.161736-datum.x)*scale
rear=2.10+(-1.155597-datum.x)*scale
radius=1.59363*scale/2
# Upper tyre wraps over a rounded hook; lower tyre rests in a shallow padded tray.
top=front+radius
for name,y in [('Upper wheel hook',top-.07),('Lower stabilizer',rear-radius+.07)]:
    box(name+' wall plate',point(3.25,y,.096),(.16,.042,.25),steel)
    for dy in [-.08,.08]:
        tube('Visible fixing',[point(3.25,y+dy,.114),point(3.25,y+dy,.13)],.014,silver)
tube('Upper steel arm',[point(3.25,top-.07,.12),point(3.25,top-.07,.45),point(3.25,top-.035,.53),point(3.25,top-.035,.595),point(3.25,top+.03,.62)],.012,steel)
tube('Upper rubber sleeve',[point(3.25,top-.035,.51),point(3.25,top-.035,.595)],.018,rubber)
bottom=rear-radius
box('Lower support arm',point(3.25,bottom-.018,.33),(.10,.43,.035),steel)
box('Lower padded tyre tray',point(3.25,bottom-.006,.55),(.17,.10,.015),rubber)
box('Lower tray stop',point(3.25,bottom+.032,.61),(.17,.018,.075),steel)
bpy.context.view_layer.update()

if before!=snapshot():raise RuntimeError('Unrelated room objects changed.')
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
wall_distance=min((p-C).dot(N)-.075 for p in points)
wall_s=[(p-C).dot(T) for p in points]
if wall_distance<.02 or min(p.z for p in points)<0 or max(wall_s)>4.47:raise RuntimeError('Bicycle exceeds the free wall envelope.')

def bvh(objects):
    vertices=[];polygons=[]
    for obj in objects:
        offset=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        polygons.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
    return BVHTree.FromPolygons(vertices,polygons)
bike_tree=bvh(meshes)
collisions={}
for name in ['chair','workspace_left_wing','about','contact','monitor','certificate_iitg']:
    obj=bpy.data.objects.get(name)
    if not obj:continue
    family=[o for o in [obj]+list(obj.children_recursive) if o.type=='MESH']
    if family:collisions[name]=len(bike_tree.overlap(bvh(family)))
if any(collisions.values()):raise RuntimeError('Bicycle overlaps room props: '+str(collisions))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report={'sourceSha256':source_hash,'candidateSha256':digest(CANDIDATE),'unrelatedObjectsUnchanged':True,
        'sourceTriangles':original_triangles,'scale':scale,'wheelDiameterScene':radius*2,
        'wallClearance':wall_distance,'wallSpan':[min(wall_s),max(wall_s)],'intersections':collisions,
        'positionWeb':[root.location.x,root.location.z,-root.location.y]}
REPORT.write_text(json.dumps(report,indent=2)+'\n');print('BICYCLE_CANDIDATE',json.dumps(report),flush=True)

if '--render' in sys.argv:
    scene=bpy.context.scene
    camera=bpy.data.objects.new('Bicycle review camera',bpy.data.cameras.new('Bicycle review camera'));scene.collection.objects.link(camera)
    scene.camera=camera;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='METAL'
    scene.cycles.device='GPU';scene.render.resolution_percentage=100
    for name,position,target,size in [('overview',(2.4,3.7,5.7),(0,1.7,-.9),(1440,1000)),('mounted-bike',(.9,2.5,3.3),(-2.0,2.1,.2),(1100,1300))]:
        camera.location=web(position);camera.rotation_euler=(web(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=40
        scene.render.resolution_x,scene.render.resolution_y=size
        scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
