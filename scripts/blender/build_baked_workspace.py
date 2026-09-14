"""Refine the editable desk and bake Cycles surface/indirect maps for Three.js."""
import ast
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'artifacts/workspace'
TEX = ROOT / 'public/textures/workspace/baked'
TEX.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ART / 'workspace-cycles.blend'))
tree = ast.parse((ROOT / 'scripts/blender/build_workspace.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[]), '<helpers>', 'exec'))
M = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'M' for t in node.targets):
        for key, value in zip(node.value.keys, node.value.values):
            name = value.args[0].value
            M[key.value] = bpy.data.materials.get(name) or mat(name, (.5,.5,.5))

def clear_children(root):
    for child in list(root.children_recursive):
        bpy.data.objects.remove(child, do_unlink=True)

def local_parts(root, build):
    before = set(bpy.context.scene.objects)
    build()
    for obj in set(bpy.context.scene.objects)-before:
        obj.parent=root
        # Helpers create parts around the local origin; no inverse is needed.

# The reference has rounded, cylindrical task shades, not pointed conical bells.
for obj in list(bpy.context.scene.objects):
    if obj.name.startswith('Lamp socket thread'):
        bpy.data.objects.remove(obj,do_unlink=True)
for i in range(1,4):
    root=bpy.data.objects[f'lamp_{i}'];clear_children(root)
    def shade():
        lathe('Rounded red task shade',(0,0,0),[(0,.035),(.018,.075),(.055,.115),(.11,.137),(.22,.16),(.35,.184),(.40,.19),(.414,.185),(.414,.173),(.36,.171),(.22,.147),(.11,.124),(.055,.10),(.025,.033)],'red',segments=64)
        lathe('Ivory enamel reflector',(0,0,0),[(.08,.112),(.20,.139),(.35,.165),(.40,.174)],'ivory',segments=64)
        ring('Rolled shade lip',(0,.408,0),.18,.006,'rededge',segments=64)
        cyl('Ceramic bulb socket',(0,.11,0),.039,.095,'ivory',vertices=32)
        sphere(f'lamp_bulb_{i}',(0,.245,0),(.058,.09,.058),'bulb',segments=32,rings=20)
        cyl('Black knurled switch',(0,-.018,0),.027,.041,'dark',vertices=32)
        for angle in range(0,360,45):
            a=math.radians(angle)
            sphere('Shade ventilation recess',(.093*math.cos(a),.052,.093*math.sin(a)),(.008,.017,.008),'dark',segments=12,rings=8)
        ring('Shade swivel collar',(0,0,0),.042,.009,'silver',segments=32)
    local_parts(root,shade)
    direction=[(-.65,-.40,.52),(-.55,-.70,.30),(-.35,-.86,.26)][i-1]
    root.rotation_mode='QUATERNION'
    root.rotation_quaternion=Vector((0,0,1)).rotation_difference(B(direction).normalized())

# Rebuild the mesh chair with the reference's taller curved back, lumbar yoke,
# broad seat, padded adjustable arms, and double-wheel casters.
for obj in list(bpy.context.scene.objects):
    if obj.name.startswith(('Woven chair warp','Woven chair weft')):
        bpy.data.objects.remove(obj,do_unlink=True)
chair=bpy.data.objects['chair'];clear_children(chair)
def chair_parts():
    cyl('Gas lift chrome',(0,.48,0),.042,.69,'silver',vertices=32)
    cyl('Gas lift sleeve',(0,.28,0),.066,.34,'dark',vertices=32)
    for i in range(5):
        a=i*math.tau/5
        end=(math.cos(a)*.51,.12,math.sin(a)*.51)
        curve('Tapered chair spoke',[(0,.25,0),(end[0]*.6,.18,end[2]*.6),end],.029,'mesh')
        for side in [-1,1]:
            cyl('Double caster',(end[0]+side*.026,.075,end[2]),.060,.038,'dark',axis=(1,0,0),vertices=24)
    box('Seat underframe',(0,.79,0),(.60,.07,.53),'dark',.06)
    sphere('Contoured upholstered seat',(0,.89,.015),(.40,.10,.37),'mesh',segments=40,rings=20)
    for sign in [-1,1]:
        curve('Curved back upright',[(sign*.34,.93,.24),(sign*.39,1.35,.37),(sign*.38,1.88,.29)],.026,'mesh')
        curve('Adjustable arm support',[(sign*.30,.80,0),(sign*.43,.96,0),(sign*.43,1.22,0)],.024,'dark')
        box('Soft arm pad',(sign*.44,1.24,.015),(.13,.065,.41),'mesh',.045)
    curve('Back top rim',[(-.38,1.88,.29),(0,1.94,.32),(.38,1.88,.29)],.03,'mesh')
    curve('Back lower rim',[(-.34,1.03,.29),(0,1.01,.34),(.34,1.03,.29)],.028,'mesh')
    curve('Lumbar crossbar',[(-.32,1.19,.39),(0,1.16,.45),(.32,1.19,.39)],.035,'dark')
    curve('Central back support',[(0,.81,.23),(0,1.01,.43),(0,1.41,.40)],.047,'mesh')
    # A curved alpha-textured sheet gives fine fabric without thousands of rods.
    verts=[];faces=[];nx=20;ny=24
    for y in range(ny+1):
        t=y/ny
        for x in range(nx+1):
            u=x/nx
            verts.append(B(((u-.5)*(.66+.08*t),1.05+.83*t,.31+.055*math.sin(t*math.pi)+.018*math.sin(u*math.pi))))
    for y in range(ny):
        for x in range(nx):
            a=y*(nx+1)+x;faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh=bpy.data.meshes.new('Ergonomic woven back');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('Chair breathable mesh',mesh);bpy.context.collection.objects.link(obj)
    mesh.materials.append(M['chairmesh']);uv=mesh.uv_layers.new(name='UVMap')
    for polygon in mesh.polygons:
        polygon.use_smooth=True
        for li in polygon.loop_indices:
            vi=mesh.loops[li].vertex_index;uv.data[li].uv=((vi%(nx+1))/nx*9,(vi//(nx+1))/ny*10)
local_parts(chair,chair_parts)
chair.rotation_euler.z=math.radians(-12)

scene=bpy.context.scene
bpy.context.view_layer.update()
for i in range(1,4):
    lamp=bpy.data.objects[f'lamp_{i}'];light=bpy.data.objects.get(f'Practical shade light {i}')
    if light:
        light.location=lamp.matrix_world @ B((0,.30,0))
        target=lamp.matrix_world @ B((0,1.2,0))
        light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
scene.camera.animation_data_clear()
scene.camera.location=B((.55,7.3,10.4))
scene.camera.rotation_euler=(B((0,2,-.25))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ART/'workspace-refined-preview.png')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'workspace-refined.blend'))

# Prepare a separate export copy. Consolidate static pieces and preserve the
# named interaction roots, hinges, monitor screen, window and fabric sheet.
for obj in list(scene.objects):
    if obj.type in {'CURVE','FONT'}:
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        if obj.type=='CURVE':obj.data.bevel_resolution=1;obj.data.resolution_u=5
        bpy.ops.object.convert(target='MESH')
    if obj.type=='MESH':
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):
            if modifier.type=='SUBSURF':modifier.levels=1
            try:bpy.ops.object.modifier_apply(modifier=modifier.name)
            except RuntimeError:pass
preserve={'monitor_screen','window_glass','Chair breathable mesh'}
buckets={}
for obj in scene.objects:
    if obj.type!='MESH' or obj.name in preserve:continue
    key=(obj.parent.name if obj.parent else '_static',obj.data.materials[0].name if obj.data.materials else '')
    buckets.setdefault(key,[]).append(obj)
for (parent_name,material),objects in buckets.items():
    if len(objects)<2:continue
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
    objects[0].name=f'{parent_name} · {material}'

prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='METAL'
scene.cycles.device='GPU';scene.cycles.samples=32
scene.render.bake.margin=8;scene.render.bake.use_clear=False
scene.render.bake.use_selected_to_active=False
scene.render.image_settings.file_format='PNG'
meshes=[o for o in scene.objects if o.type=='MESH' and o.name not in preserve]
groups={'room':[],'objects':[]}
for obj in meshes:
    world_area=sum(p.area for p in obj.data.polygons)
    groups['room' if world_area>8 else 'objects'].append(obj)
manifest={'file':'/models/workspace-baked.glb','source':'artifacts/workspace/workspace-refined.blend','baked':True,'atlases':{}}
for group,objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
        layer=obj.data.uv_layers.new(name='CyclesAtlas')
        obj.data.uv_layers.active=layer
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.003,area_weight=.5,correct_aspect=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    # Preserve original texture coordinates for source textures during baking.
    materials={}
    for obj in objects:
        for slot in obj.material_slots:
            original=slot.material
            if original.name not in materials:
                copy=original.copy();materials[original.name]=copy
                for node in list(copy.node_tree.nodes):
                    if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked:
                        uvnode=copy.node_tree.nodes.new('ShaderNodeUVMap');uvnode.uv_map='UVMap'
                        copy.node_tree.links.new(uvnode.outputs['UV'],node.inputs['Vector'])
            slot.material=materials[original.name]
    images={}
    for kind in ['color','indirect']:
        image=bpy.data.images.new(f'{group}-{kind}',width=2048 if group=='room' else 4096,height=2048 if group=='room' else 4096,float_buffer=kind=='indirect')
        image.colorspace_settings.name='Non-Color' if kind=='indirect' else 'sRGB'
        image.generated_color=(0,0,0,1)
        for material in materials.values():
            node=material.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
            material.node_tree.nodes.active=node
        scene.render.bake.use_pass_direct=False
        scene.render.bake.use_pass_indirect=kind=='indirect'
        scene.render.bake.use_pass_color=kind=='color'
        print(f'BAKING {group} {kind}',flush=True)
        bpy.ops.object.bake(type='DIFFUSE')
        image.filepath_raw=str(TEX/f'{group}-{kind}.png');image.file_format='PNG';image.save()
        images[kind]=image
    manifest['atlases'][group]={'indirect':f'/textures/workspace/baked/{group}-indirect.png'}
    for obj in objects:
        # Export the atlas as UV0. All objects retain their local pivots.
        atlas=obj.data.uv_layers['CyclesAtlas']
        for layer in list(obj.data.uv_layers):
            if layer!=atlas:obj.data.uv_layers.remove(layer)
        atlas.name='UVMap'
        material=bpy.data.materials.new(f'Baked_{group}');material.use_nodes=True
        shader=material.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Roughness'].default_value=.55
        texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=images['color']
        material.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
        obj.data.materials.clear();obj.data.materials.append(material)
        obj['bakedAtlas']=group

bpy.ops.object.select_all(action='DESELECT')
for obj in scene.objects:
    if obj.type in {'MESH','EMPTY'}:obj.select_set(True)
output=ROOT/'public/models/workspace-baked.glb'
bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
manifest['revision']=hashlib.sha256(output.read_bytes()).hexdigest()[:12]
manifest['bytes']=output.stat().st_size
manifest['triangles']=sum(len(p.vertices)-2 for o in scene.objects if o.type=='MESH' for p in o.data.polygons)
(ROOT/'public/models/workspace-baked.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'workspace-baked.blend'))
print('BAKE_COMPLETE',json.dumps(manifest),flush=True)
