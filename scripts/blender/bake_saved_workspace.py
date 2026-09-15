"""Bake the user's saved scene without rebuilding or saving over workspace.blend.

Each atlas is baked on a temporary joined copy, avoiding one bake launch per prop.
The exported meshes keep their original hierarchy, pivots and interaction names.
"""
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from surface_detail_uv import ensure_detail_uv
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
if '--source' in sys.argv:
    SOURCE=Path(sys.argv[sys.argv.index('--source')+1]).resolve()
TEX = ROOT / 'public/textures/workspace/saved-bake'
TEX.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:12]
export_revision = hashlib.sha256(SOURCE.read_bytes()+Path(__file__).read_bytes()).hexdigest()[:12]

def web(vector):
    return [round(vector.x,6), round(vector.z,6), round(-vector.y,6)]

lights=[]
for obj in scene.objects:
    if obj.type!='LIGHT' or obj.hide_render:
        continue
    light=obj.data
    lights.append({
        'name':obj.name, 'type':light.type, 'energy':light.energy,
        'lampRoot':obj.get('lampRoot'),
        'color':list(light.color), 'position':web(obj.matrix_world.translation),
        'direction':web(obj.matrix_world.to_quaternion() @ Vector((0,0,-1))),
        'size':getattr(light,'size',.1), 'sizeY':getattr(light,'size_y',getattr(light,'size',.1)),
        'shape':getattr(light,'shape','DISK'),
        'angle':getattr(light,'spot_size',math.pi/4),
        'blend':getattr(light,'spot_blend',.15),
    })
world_node=scene.world.node_tree.nodes.get('Background') if scene.world and scene.world.use_nodes else None
world={'color':list(world_node.inputs[0].default_value)[:3], 'strength':world_node.inputs[1].default_value} if world_node else {'color':[.15,.15,.15],'strength':.2}
manifest={'file':'/models/workspace-saved.glb','source':'artifacts/workspace/workspace.blend','revision':export_revision,'sourceRevision':source_hash,'lights':lights,'world':world,'exposure':scene.view_settings.exposure,'baked':True}
manifest['source']=str(SOURCE.relative_to(ROOT))

# Render a reference with the user's lighting before preparing export-only copies.
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='METAL'
scene.render.engine='CYCLES';scene.cycles.device='GPU';scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_percentage=60
scene.render.filepath=str(ROOT/'artifacts/workspace/saved-lighting-preview.png')
bpy.ops.render.render(write_still=True)

# Convert text, curves, and modifiers on the export copy, then consolidate only
# siblings sharing a material. Named roots and opening hinges remain selectable.
for obj in list(scene.objects):
    if obj.type in {'CURVE','FONT'}:
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        if obj.type=='CURVE':obj.data.resolution_u=min(obj.data.resolution_u,6)
        bpy.ops.object.convert(target='MESH')
    if obj.type=='MESH':
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):
            try:bpy.ops.object.modifier_apply(modifier=modifier.name)
            except RuntimeError:pass
        ensure_detail_uv(obj)
        fine_grip=any(material and material.name=='Xbox fine grip edge' for material in obj.data.materials)
        if not obj.get('webOptimized') and (fine_grip or 'seamless ergonomic body' in obj.name or sum(len(p.vertices)-2 for p in obj.data.polygons)>1000):
            modifier=obj.modifiers.new('Web geometry reduction','DECIMATE')
            modifier.ratio=.24 if fine_grip else .45 if 'seamless ergonomic body' in obj.name else .30 if obj.name.startswith('chair') else .60
            bpy.ops.object.modifier_apply(modifier=modifier.name)

# Colored keycaps and printed controller glyphs can share one material each.
# Store their individual colors per vertex so batching does not lose the artwork.
color_batches={}
for obj in scene.objects:
    if obj.type!='MESH' or len(obj.data.materials)!=1:continue
    material=obj.data.materials[0]
    family='Controller print' if material.name in {'Xbox A green','Xbox B red','Xbox X blue','Xbox Y yellow'} else 'Keyboard keys' if material.name.startswith('Creator Micro key ') else None
    if not family:continue
    color=material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value[:]
    attribute=obj.data.color_attributes.new(name='ProductColor',type='FLOAT_COLOR',domain='CORNER')
    for datum in attribute.data:datum.color=color
    if family not in color_batches:
        shared=bpy.data.materials.new(family);shared.use_nodes=True
        shader=shared.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.42
        vertex=shared.node_tree.nodes.new('ShaderNodeVertexColor');vertex.layer_name='ProductColor'
        shared.node_tree.links.new(vertex.outputs['Color'],shader.inputs['Base Color'])
        color_batches[family]=shared
    obj.data.materials[0]=color_batches[family]
preserved_meshes={'monitor_screen','window_glass','balcony_window_glass','Chair breathable mesh'}
buckets={}
for obj in scene.objects:
    if obj.type!='MESH' or obj.name in preserved_meshes or len(obj.data.materials)!=1:continue
    key=(obj.parent.name if obj.parent else '_static',obj.data.materials[0].name)
    buckets.setdefault(key,[]).append(obj)
for key,objects in buckets.items():
    if len(objects)<2:continue
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
    objects[0].name=f'{key[0]} · {key[1]}'

preserve=preserved_meshes
groups={'room':[],'objects':[]}
for obj in list(scene.objects):
    if obj.type!='MESH' or obj.name in preserve or obj.hide_render:continue
    area=sum(p.area for p in obj.data.polygons)
    groups['room' if area>8 else 'objects'].append(obj)

# Independent source materials retain explicit UV references while atlas UVs are active.
for objects in groups.values():
    for obj in objects:
        if len(obj.data.uv_layers):
            obj.data.uv_layers.active_index=0
            obj.data.uv_layers[0].name='SourceUV'
        for slot in obj.material_slots:
            material=slot.material
            if not material or not material.use_nodes:continue
            for node in list(material.node_tree.nodes):
                if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked:
                    uv=material.node_tree.nodes.new('ShaderNodeUVMap')
                    uv.uv_map='SourceUV'
                    material.node_tree.links.new(uv.outputs['UV'],node.inputs['Vector'])

scene.render.bake.margin=12
scene.render.bake.use_clear=True
scene.render.bake.use_selected_to_active=False
scene.cycles.samples=128
atlas_images={}
for group,objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
        obj.data.uv_layers.active=obj.data.uv_layers.new(name='CyclesAtlas')
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.004,area_weight=.5)
    bpy.ops.object.mode_set(mode='OBJECT')
    copies=[]
    for obj in objects:
        copy=obj.copy();copy.data=obj.data.copy();scene.collection.objects.link(copy)
        copies.append(copy)
        obj.hide_render=True
    bpy.ops.object.select_all(action='DESELECT')
    for obj in copies:obj.select_set(True)
    bpy.context.view_layer.objects.active=copies[0]
    bpy.ops.object.join()
    target=copies[0];target.name=f'Bake target {group}'
    materials=set(slot.material for slot in target.material_slots if slot.material)
    images={}
    for kind in ['indirect']:
        resolution=2048
        image=bpy.data.images.new(f'{group}-{kind}',width=resolution,height=resolution,float_buffer=kind=='indirect')
        image.colorspace_settings.name='sRGB' if kind=='color' else 'Non-Color'
        for material in materials:
            node=material.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
            material.node_tree.nodes.active=node
        scene.render.bake.use_pass_direct=False
        scene.render.bake.use_pass_indirect=kind=='indirect'
        scene.render.bake.use_pass_color=kind=='color'
        print(f'BAKE_START {group} {kind}',flush=True)
        bpy.ops.object.bake(type='NORMAL' if kind=='normal' else 'DIFFUSE')
        image.filepath_raw=str(TEX/f'{group}-{kind}.png');image.file_format='PNG';image.save()
        # Keep the full PNG for authoring; serve a compact diffuse-light derivative.
        # These maps contain linear lighting data, so neither version has an ICC profile.
        subprocess.run(['/opt/homebrew/bin/python3','-c',
            'from PIL import Image; import sys; Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2],format="WEBP",quality=95,method=6)',
            image.filepath_raw,str(TEX/f'{group}-{kind}.webp')],check=True)
        images[kind]=image
        print(f'BAKE_DONE {group} {kind}',flush=True)
    atlas_images[group]=images
    bpy.data.objects.remove(target,do_unlink=True)
    for obj in objects:obj.hide_render=False

# Keep the original high-detail color textures on UV0, and indirect lighting on UV1.
for group,objects in groups.items():
    for obj in objects:
        atlas=obj.data.uv_layers['CyclesAtlas']
        source=obj.data.uv_layers.get('SourceUV')
        if source:
            obj.data.uv_layers.active=source;source.active_render=True
        # Record the actual UV channel for meshes without an original texture UV.
        obj['bakedUV']=list(obj.data.uv_layers).index(atlas)
        obj['bakedAtlas']=group

bpy.ops.object.select_all(action='DESELECT')
for obj in scene.objects:
    if obj.type in {'MESH','EMPTY'} and not obj.hide_render:obj.select_set(True)
output=ROOT/'public/models/workspace-saved.glb'
bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
manifest['bytes']=output.stat().st_size
manifest['lightmapBytes']=sum((TEX/f'{group}-indirect.webp').stat().st_size for group in groups)
manifest['triangles']=sum(len(p.vertices)-2 for obj in scene.objects if obj.type=='MESH' for p in obj.data.polygons)
(ROOT/'public/models/workspace-saved.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'artifacts/workspace/workspace-saved-baked.blend'))
print('SAVED_BAKE_COMPLETE',json.dumps(manifest),flush=True)
