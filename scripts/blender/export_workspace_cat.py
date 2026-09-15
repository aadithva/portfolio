"""Bake JonasDichelle's legacy rig and packed calico maps to a standalone web GLB.

Reads the downloaded original only. Never writes to the workspace master.
"""
import bpy
import json
import math
import random
import sys
from pathlib import Path
from mathutils import Matrix, Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cat_jump_animation import jump_frames

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/workspace/cat'
bpy.ops.wm.open_mainfile(filepath=str(OUT / 'source/cat.blend'), load_ui=False, use_scripts=False)
scene = bpy.context.scene
rig = bpy.data.objects['Armature']
body = bpy.data.objects['Cat']
meshes = [body, bpy.data.objects['Sphere'], bpy.data.objects['Sphere.001']]
for obj in list(bpy.data.objects):
    if obj not in meshes and obj != rig:
        bpy.data.objects.remove(obj, do_unlink=True)
for obj in meshes:
    obj.hide_set(False)
    obj.hide_viewport = False
    obj.hide_render = False
    for mod in list(obj.modifiers):
        if mod.type == 'PARTICLE_SYSTEM':
            obj.modifiers.remove(mod)
        elif mod.type == 'SUBSURF':
            mod.levels = 1 if obj == body else 0
            mod.render_levels = mod.levels
rig.hide_set(False)
rig.hide_viewport = False
# These self-referential legacy constraints form cycles in modern Blender.
for bone, kind in [('Tail', 'COPY_ROTATION'), ('Spine', 'PIVOT')]:
    for c in list(rig.pose.bones[bone].constraints):
        if c.type == kind:
            rig.pose.bones[bone].constraints.remove(c)
originals = {name: bpy.data.actions[name] for name in ['Walk', 'run']}
for track in rig.animation_data.nla_tracks:
    track.mute = True
samples = {}
def capture(name, count, setup):
    frames = []
    for frame in range(count + 1):
        setup(frame, count)
        bpy.context.view_layer.update()
        frames.append({p.name: p.matrix.copy() for p in rig.pose.bones})
    samples[name] = frames

for source, name, count in [('Walk', 'Walk', 27), ('run', 'Run', 14)]:
    rig.animation_data.action = originals[source]
    capture(name, count, lambda f, n: scene.frame_set(f + 1))

rig.animation_data.action = None
for p in rig.pose.bones:
    p.matrix_basis.identity()
bpy.context.view_layer.update()
neutral = {p.name: p.matrix_basis.copy() for p in rig.pose.bones}
def move(name, delta):
    p = rig.pose.bones[name]
    # Root controls translate in armature coordinates, not their angled bone axes.
    p.location = p.bone.matrix_local.to_3x3().inverted() @ Vector(delta)

def pose(sit=0, crouch=0, reach=0, look=0, breath=0):
    for p in rig.pose.bones:
        p.matrix_basis = neutral[p.name]
    move('Hip', (0, -1.2 * sit, -3.65 * sit - .8 * crouch))
    move('Spine_controller_1', (0, .7 * sit, -1.1 * sit - .65 * crouch + breath))
    move('Spine_controller_2', (0, 1.15 * sit, -.1 * sit - .7 * crouch + breath))
    move('Shoulder_front_L', (0, 1.15 * sit, -.1 * sit - .7 * crouch))
    move('Thigh_front_L', (0, 1.15 * sit, -.1 * sit - .7 * crouch))
    move('Thigh_front_R', (0, 1.15 * sit, -.1 * sit - .7 * crouch))
    move('Neck', (0, 1.15 * sit, -.1 * sit - .7 * crouch))
    move('Head_controller', (look * .25, 1.7 * sit - .25 * reach, .2 * sit - .55 * crouch + breath))
    for side in ['L', 'R']:
        move('Foot_front_IK_' + side, (0, .85 * sit - 1.0 * reach, 1.45 * reach))
        move('Knee_front_IK_' + side, (0, .8 * sit - .35 * reach, .6 * reach))
        move('Foot_Back_IK_' + side, (0, -1.2 * sit, .55 * reach))
        move('Knee_back_IK_' + side, (0, -1.5 * sit, -1.4 * sit - .25 * crouch))
    move('Tail_controller', (.6 * math.sin(look), -.65 * sit, -3.1 * sit - .8 * crouch))

capture('Idle', 72, lambda f,n: pose(look=math.sin(f/n*math.tau), breath=.025*math.sin(f/n*math.tau)))
capture('Sit', 72, lambda f,n: pose(sit=1, look=.6*math.sin(f/n*math.tau), breath=.025*math.sin(f/n*math.tau)))
capture('SitDown', 24, lambda f,n: pose(sit=(f/n)**2*(3-2*f/n)))
capture('StandUp', 24, lambda f,n: pose(sit=1-(f/n)**2*(3-2*f/n)))
def jump(f,n):
    t=f/n
    crouch = max(0, 1-abs(t-.16)/.16) * .9 + max(0,1-abs(t-.85)/.15)*.55
    reach = max(0, math.sin(math.pi * max(0,min(1,(t-.22)/.55))))
    pose(crouch=crouch,reach=reach,look=.1)
pose()
bpy.context.view_layer.update()

# A seated pose needs the pelvis on the cushion, with folded hind legs and a
# rising chest. The legacy hip controls alone only produce a shallow crouch.
# Construct a seated target from neutral deform matrices and solve each hind
# leg's two segments between its hip, forward knee and planted hock.
standing={p.name:p.matrix.copy() for p in rig.pose.bones}
motion=json.loads((ROOT/'src/lib/workspace/cat-motion.json').read_text())
samples['Jump']=jump_frames(rig,standing,motion['up'])
samples['JumpDown']=jump_frames(rig,standing,motion['down'])
seated={name:m.copy() for name,m in standing.items()}
def torso_point(point):
    p=point.copy()
    amount=max(0,min(1,(p.y+1.8)/5.4))
    p.z-=3.55*amount
    p.y=.6+(p.y-.6)*.48
    return p
torso_names=['Spine','Spine.001','Spine.002','Spine.003','Spine.004','Hip','Tail']
for name in torso_names:
    p=rig.pose.bones[name]
    head=torso_point(standing[name].translation)
    tail=torso_point(standing[name]@Vector((0,p.length,0)))
    q=Vector((0,1,0)).rotation_difference((tail-head).normalized())
    seated[name]=Matrix.LocRotScale(head,q,Vector((1,(tail-head).length/p.length,1)))
for name in rig.pose.bones.keys():
    if name.startswith('Tail.'):
        seated[name].translation+=Vector((0,-1.6,-3.55))
for side in ['L','R']:
    sign=1 if side=='L' else -1
    hip=Vector((sign*.22,2.05,-1.55))
    knee=Vector((sign*.85,.65,-2.15))
    hock=Vector((sign*.9,2.8,-2.65))
    foot=Vector((sign*.85,1.85,-2.68))
    for name,a,b in [('Thigh_Back_'+side,hip,knee),('Calf_back_'+side,knee,hock),('Foot_Back_'+side,hock,foot)]:
        p=rig.pose.bones[name]
        olddir=standing[name].to_3x3()@Vector((0,1,0))
        rot=olddir.rotation_difference((b-a).normalized())@standing[name].to_quaternion()
        seated[name]=Matrix.LocRotScale(a,rot,Vector((1,(b-a).length/p.length,1)))
    # The toe chain follows the foot's contact translation.
    toe='Foot_Back_L2' if side=='L' else 'Foot_Back_L2.002'
    delta=foot-standing[toe].translation
    branch=rig.pose.bones[toe]
    for p in [branch]+list(branch.children_recursive):
        seated[p.name].translation+=delta
for name in ['Sit','SitDown','StandUp']:
    for f,frame in enumerate(samples[name]):
        t=f/(len(samples[name])-1)
        amount=1 if name=='Sit' else t*t*(3-2*t) if name=='SitDown' else 1-t*t*(3-2*t)
        for bone in seated:
            if bone in torso_names or bone.startswith(('Tail.','Thigh_Back_','Calf_back_','Foot_Back_','toe_connector_L_back','Toe_back_')):
                frame[bone]=standing[bone].lerp(seated[bone],amount)

# Replace render-only shaders with PBR maps that glTF can carry.
calico = bpy.data.images['Untitled']
eye = bpy.data.images['green_eye_diff.jpg.001']
for image in [calico, eye]:
    if max(image.size) > 2048:
        factor = 2048/max(image.size)
        image.scale(round(image.size[0]*factor), round(image.size[1]*factor))
    image.pack()
def material(name, image=None, color=(.8,.8,.8,1), rough=.8):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=color
    shader.inputs['Roughness'].default_value=rough
    if image:
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image
        mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    return mat
coat=material('JonasDichelle calico coat',calico)
coat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1
coat.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=0
iris=material('Green iris',color=(.18,.26,.085,1),rough=.35)
dark=material('Pupil',color=(.008,.012,.009,1),rough=.25)
pink=material('Nose and ear skin',color=(.42,.15,.16,1))
for obj in meshes:
    if obj != body:
        import bmesh
        cornea_slots={i for i,s in enumerate(obj.material_slots) if s.material and s.material.name=='Cornea'}
        # Remove the outer glass shell; the original iris texture is underneath.
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in cornea_slots], context='FACES')
        bm.to_mesh(obj.data);bm.free()
    for i,slot in enumerate(obj.material_slots):
        name=slot.material.name if slot.material else ''
        obj.data.materials[i]=coat if obj==body and name!='Material.002' else pink if obj==body else dark if name=='Pupil' else iris

# Explicit pupil geometry replaces the old generated-coordinate eye shader.
for side in [-1,1]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=(side*.45,-4.25,3.06))
    pupil=bpy.context.object;pupil.name=f'Cat pupil {side}'
    pupil.scale=(.052,.04,.115)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    pupil.data.materials.append(dark)
    group=pupil.vertex_groups.new(name='Head');group.add(list(range(len(pupil.data.vertices))),1,'REPLACE')
    mod=pupil.modifiers.new('Armature','ARMATURE');mod.object=rig
    meshes.append(pupil)

# Apply subdivision in bind pose while preserving skin weights.
rig.data.pose_position='REST'
for obj in meshes:
    bpy.context.view_layer.objects.active=obj
    if obj.data.shape_keys:
        obj.shape_key_clear()
    for mod in list(obj.modifiers):
        if mod.type=='SUBSURF':
            if mod.levels:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            else:
                obj.modifiers.remove(mod)
rig.data.pose_position='POSE'

# A shared strand mask and per-root calico colors make full-body fur cards.
# UV0 is the strand atlas; vertex colors preserve the original coat markings.
import numpy as np
width_px,height_px=256,512
pixels=np.ones((height_px,width_px,4),dtype=np.float32)
pixels[:,:,3]=0
rng=random.Random(18519)
for strand in range(16):
    start=(strand+.5)/16
    tip=max(.08,min(.95,rng.uniform(.62,1)))
    bend=rng.uniform(-.06,.06)
    for row in range(int(tip*height_px)):
        t=row/height_px
        center=(start+bend*t*t)*width_px
        radius=(2.5+2.5*(1-t/tip))
        for col in range(max(0,int(center-radius-1)),min(width_px,int(center+radius+2))):
            alpha=max(0,min(1,radius-abs(col-center)))*(1-(t/tip)**7)
            pixels[row,col,3]=max(pixels[row,col,3],alpha)
mask=bpy.data.images.new('Calico groom strand mask',width=width_px,height=height_px,alpha=True)
mask.pixels.foreach_set(pixels.ravel());mask.pack()
fur_mat=material('Calico layered fur',mask,rough=.95)
nodes=fur_mat.node_tree.nodes;links=fur_mat.node_tree.links
shader=nodes.get('Principled BSDF');tex=next(n for n in nodes if n.type=='TEX_IMAGE')
links.new(tex.outputs['Alpha'],shader.inputs['Alpha'])
color_node=nodes.new('ShaderNodeVertexColor');color_node.layer_name='CoatColor'
links.new(color_node.outputs['Color'],shader.inputs['Base Color'])
shader.inputs['Sheen Weight'].default_value=0
shader.inputs['Roughness'].default_value=1
shader.inputs['Specular IOR Level'].default_value=0
fur_mat.surface_render_method='DITHERED'
fur_mat.use_backface_culling=False
coat_pixels=np.array(calico.pixels[:],dtype=np.float32).reshape(calico.size[1],calico.size[0],4)
random.seed(18519)
body.data.calc_loop_triangles()
verts=[];faces=[];uvs=[];weights=[];colors=[];normals=[]
uv=body.data.uv_layers.active.data
triangles=list(body.data.loop_triangles)
areas=[t.area for t in triangles]
for tri in random.choices(triangles, weights=areas, k=0):
    a,b,c=[body.data.vertices[i] for i in tri.vertices]
    r=math.sqrt(random.random());s=random.random();bary=(1-r,r*(1-s),r*s)
    pos=a.co*bary[0]+b.co*bary[1]+c.co*bary[2]
    normal=(a.normal*bary[0]+b.normal*bary[1]+c.normal*bary[2]).normalized()
    # Keep eyes, muzzle and contact pads clear; cheeks retain a short coat.
    if pos.y < -3.85 or pos.z < -2.65:
        continue
    rootuv=sum((uv[l].uv*w for l,w in zip(tri.loops,bary)),Vector((0,0)))
    groom=Vector((0,.65,-.5))
    if pos.y>3.25:groom=Vector((0,0,1))
    tangent=groom-normal*groom.dot(normal)
    if tangent.length<.01:tangent=normal.cross(Vector((1,0,0)))
    tangent.normalize()
    sideways=normal.cross(tangent).normalized()
    length=random.uniform(.22,.44)
    if pos.y < -2.8 or pos.z < -.8:length*=.48
    width=random.uniform(.06,.115)
    base=pos+normal*.008
    mid=base+tangent*length*.4+normal*length*.45
    tip=base+tangent*length*.85+normal*length*.55
    offset=len(verts)
    verts.extend([base-sideways*width,base+sideways*width,mid-sideways*width*.85,mid+sideways*width*.85,tip-sideways*width*.55,tip+sideways*width*.55])
    faces.extend([(offset,offset+1,offset+3,offset+2),(offset+2,offset+3,offset+5,offset+4)])
    uvs.extend([(0,0),(1,0),(0,.5),(1,.5),(0,1),(1,1)])
    col=coat_pixels[int(rootuv.y*(calico.size[1]-1))%calico.size[1],int(rootuv.x*(calico.size[0]-1))%calico.size[0]].copy()
    col[3]=1
    colors.extend([col]*6)
    normals.extend([tuple(normal)]*6)
    blend={}
    for v,w in zip([a,b,c],bary):
        for g in v.groups:
            name=body.vertex_groups[g.group].name
            if name in rig.data.bones:blend[name]=blend.get(name,0)+g.weight*w
    weights.extend([blend]*6)
mesh=bpy.data.meshes.new('Calico groomed fur cards');mesh.from_pydata(verts,[],faces);mesh.update()
fur=bpy.data.objects.new('Calico fur',mesh);scene.collection.objects.link(fur)
fur.matrix_world=body.matrix_world.copy();fur.parent=body.parent
fur.data.materials.append(fur_mat)
uvlayer=mesh.uv_layers.new(name='UVMap')
for loop in mesh.loops:uvlayer.data[loop.index].uv=uvs[loop.vertex_index]
attribute=mesh.color_attributes.new(name='CoatColor',type='BYTE_COLOR',domain='POINT')
for i,color in enumerate(colors):attribute.data[i].color=color
for polygon in mesh.polygons:polygon.use_smooth=True
if normals:mesh.normals_split_custom_set_from_vertices(normals)
for name in rig.data.bones.keys():fur.vertex_groups.new(name=name)
for i,blend in enumerate(weights):
    for name,w in blend.items():
        if w>.001:fur.vertex_groups[name].add([i],w,'REPLACE')
mod=fur.modifiers.new('Armature','ARMATURE');mod.object=rig
bpy.data.objects.remove(fur,do_unlink=True)

# Bake sampled pose matrices to independent deform bones. No legacy IK runs on web.
bone_names=list(rig.data.bones.keys())
rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
lengths={b.name:b.length for b in rig.data.bones}
rig.animation_data_clear()
for p in rig.pose.bones:
    for c in list(p.constraints):p.constraints.remove(c)
bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for b in rig.data.edit_bones:
    b.parent=None;b.use_connect=False
    b.matrix=rest[b.name];b.length=lengths[b.name]
bpy.ops.object.mode_set(mode='OBJECT')
rig.animation_data_create()
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)
for name,frames in samples.items():
    if name not in ['Idle','Walk']:continue
    action=bpy.data.actions.new(name)
    rig.animation_data.action=action
    for f,frame in enumerate(frames):
        for p in rig.pose.bones:
            p.rotation_mode='QUATERNION'
            p.matrix_basis=rest[p.name].inverted() @ frame[p.name]
            for path in ['location','rotation_quaternion','scale']:
                p.keyframe_insert(data_path=path,frame=1+f*(24/60 if name in ['Jump','JumpDown'] else 1),group=p.name)
    track=rig.animation_data.nla_tracks.new();track.name=name
    track.strips.new(name,1,action);track.mute=True
rig.animation_data.action=bpy.data.actions['Idle']
scene.frame_set(1)
scene.render.fps=24
scene.frame_start=1;scene.frame_end=73
for obj in bpy.context.selected_objects:obj.select_set(False)
for obj in meshes+[rig]:obj.select_set(True)
# Asset extras preserve public credit through conversion.
rig['author']='JonasDichelle'
rig['license']='CC BY 3.0'
rig['source']='https://blendswap.com/blend/18519'
rig['adaptation']='Matte calico coat, original walk cycle, floor-only wandering; no added fur'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cat-web.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/workspace-cat.glb'),
    export_format='GLB',use_selection=True,export_animations=True,
    export_animation_mode='ACTIONS',export_force_sampling=True,
    export_skins=True,export_extras=True,export_yup=True)
report={'clips':{k:(len(v)-1)/24 for k,v in samples.items() if k in ['Idle','Walk']},'furTriangles':0,
        'fileBytes':(ROOT/'public/models/workspace-cat.glb').stat().st_size,
        'objects':[{ 'name':o.name,'matrix':[list(row) for row in o.matrix_world], 'bounds':[list(v) for v in o.bound_box]} for o in meshes]}
(OUT/'export.json').write_text(json.dumps(report,indent=2))
print('CAT_EXPORT',json.dumps({k:v for k,v in report.items() if k!='objects'}))
