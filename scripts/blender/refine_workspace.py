"""Refine the saved desk for a Cycles film. Never overwrite the source scene."""
import ast
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'artifacts/workspace'
SOURCE = ART / 'workspace.blend'
OUTPUT = ART / 'workspace-cycles.blend'
TEX = ROOT / 'public/textures/workspace'
random.seed(4813)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))

# Reuse only modeling helpers, not the original script's scene-building steps.
tree = ast.parse((ROOT / 'scripts/blender/build_workspace.py').read_text())
helpers = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef)], type_ignores=[])
exec(compile(helpers, '<workspace-modeling-helpers>', 'exec'))
M = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'M' for t in node.targets):
        for key, value in zip(node.value.keys, node.value.values):
            name = value.args[0].value
            M[key.value] = bpy.data.materials.get(name) or mat(name, (.5,.5,.5))
FONT = bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial.ttf')
reference_texture = TEX / 'laptop-reference.jpg'
if reference_texture.exists():
    material = bpy.data.materials.get('Laptop sticker collage')
    if material:
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                node.image = bpy.data.images.load(str(reference_texture), check_existing=True)

def texture_detail(material, scale, strength, distance, roughness):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = roughness
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = 3
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = distance
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], shader.inputs['Normal'])

for key, scale, strength, distance, roughness in [
    ('wall', 160, .23, .012, .88), ('white', 240, .13, .003, .38),
    ('edge', 280, .09, .002, .28), ('floor', 75, .12, .004, .19),
    ('mesh', 340, .5, .003, .86), ('black', 420, .25, .002, .66),
    ('dark', 280, .13, .002, .4), ('ivory', 330, .18, .002, .85),
    ('red', 230, .07, .001, .22), ('silver', 550, .1, .001, .24),
    ('gold', 260, .1, .001, .3), ('soil', 60, .6, .012, .98),
]:
    texture_detail(M[key], scale, strength, distance, roughness)
M['floor'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.49,.46,.39,1)
M['red'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.34,.009,.005,1)
M['red'].node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value = .38
M['green'].node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value = .32
M['amber'] = mat('Dried sunflower ochre', (.30,.12,.018), .8)
M['petal'] = mat('Dried sunflower petals', (.48,.255,.04), .76)
M['glassbottle'] = mat('Frosted small bottle', (.58,.61,.58), .23)
M['pinkcap'] = mat('Pink bottle cap', (.7,.006,.10), .32)

# Keep the source's individual object groups and corner transforms intact.
def wing_additions(side, build):
    before = set(bpy.context.scene.objects)
    build()
    wing = bpy.data.objects['workspace_' + side + '_wing']
    oldx = -1.6 if side == 'left' else 1.6
    transform = wing.matrix_world @ Matrix.Translation(-B((oldx,0,-.72)))
    for obj in set(bpy.context.scene.objects) - before:
        if obj.parent is None:
            obj.matrix_world = transform @ obj.matrix_world

def left_details():
    # Closed lower cabinet, slim reveal, hinge hardware, and a small finger pull.
    box('Inset left cabinet door',(-1.6,1.72,-.357),(1.06,.50,.045),'white',.008)
    box('Cabinet finger pull',(-1.18,1.89,-.329),(.12,.022,.018),'silver',.007)
    for y in [1.53,1.9]:
        cyl('Cabinet hardware',(-2.08,y,-.32),.012,.008,'silver',axis=(0,0,1),vertices=24)
    # A shelf stack with thin page signatures and slightly misaligned covers.
    for i in range(4):
        x=-1.66+random.uniform(-.035,.035);y=3.145+i*.027
        box('Sketchbook page block',(x,y,-.71),(.7,.022,.34),'ivory',.002)
        box('Sketchbook cloth cover',(x,y+.013,-.71),(.735,.005,.36),['rededge','dark','sage','ivory'][i],.002)
        for j in range(3):box('Paper signatures',(x,y-.008+j*.006,-.535),(.67,.001,.002),'cream',0)
    # Personal-looking stationery without invented biographical text.
    for i,(x,y,w,h) in enumerate([(-2.24,4.09,.28,.36),(-1.44,3.91,.30,.29),(-.91,4.17,.25,.22)]):
        paper=box('Overlapping pinned paper',(x,y,-1.145),(w,h,.009),['ivory','rededge','sage'][i],.002)
        paper.rotation_euler.y=math.radians((-1)**i*5)
        cyl('Paper pin',(x,y+h*.42,-1.122),.013,.017,'gold',axis=(0,0,1))
        for j in range(4):box('Paper ruled marks',(x,y+.07-j*.037,-1.132),(w*.68,.003,.002),'dark',0)
    # Add raised slot edges so pegboard holes have actual depth at grazing light.
    for row in range(10):
        for col in range(17):
            x=-2.45+col*.109;y=3.38+row*.105
            box('Pegboard slot recess',(x,y,-1.18),(.010,.029,.006),'dark',.005)
    for x in [-2.26,-2.11,-1.96]:
        curve('Bent pegboard hook',[(x,3.40,-1.17),(x,3.40,-1.03),(x,3.46,-1.01)],.006,'silver')
    for i in range(3):
        box('Small tray clip',(-2.12+i*.16,3.405,-.94),(.075,.12,.04),'dark',.008)
        ring('Clip wire loop',(-2.12+i*.16,3.50,-.92),.023,.003,'silver',axis=(0,0,1))

def right_details():
    # The reference's compact white keyboard, with separate sculpted keycaps.
    box('Shelf keyboard case',(1.60,2.66,-.57),(.97,.053,.30),'silver',.025)
    for row in range(4):
        for col in range(14):
            box('Keyboard keycap',(1.16+col*.065,2.70,-.68+row*.066),(.056,.026,.055),'edge',.006)
    box('Keyboard spacebar',(1.57,2.705,-.417),(.34,.026,.048),'edge',.006)
    # More small collectibles on the lower shelf, with wheels and layered shells.
    for i in range(4):
        x=1.22+i*.23
        box('Shelf miniature body',(x,2.10,-.63),(.15,.085,.17),['blue','red','yellow','sage'][i],.017)
        box('Shelf miniature roof',(x,2.16,-.66),(.105,.065,.09),'ivory',.012)
        for dx in [-.08,.08]:
            for z in [-.68,-.56]:cyl('Miniature rubber wheel',(x+dx,2.07,z),.027,.018,'dark',axis=(1,0,0),vertices=20)
    # The photo's tall yellow vessel with dried flower heads.
    lathe('Tall yellow flower vase',(2.07,3.12,-.75),[(0,.11),(.02,.14),(.30,.155),(.38,.16),(.39,.145),(.30,.13)],'yellow',segments=64)
    for i in range(7):
        a=i*2.399;x=2.07+math.cos(a)*.17;z=-.75+math.sin(a)*.13;y=3.67+(i%3)*.11
        curve('Dry flower stem',[(2.07,3.30,-.75),(x-.02,3.55,z),(x,y,z)],.004,'wood')
        sphere('Sunflower seed head',(x,y,z),(.055,.046,.025),'amber',segments=24,rings=16)
        for j in range(13):
            angle=j*math.tau/13
            petal=sphere('Curled dry petal',(x+math.cos(angle)*.065,y+math.sin(angle)*.065,z+.003),(.04,.018,.008),'petal',segments=12,rings=8)
            petal.rotation_euler.y=-angle

wing_additions('left',left_details)
wing_additions('right',right_details)

# Leaves gain smooth, thicker silhouettes rather than looking like folded triangles.
for obj in list(bpy.context.scene.objects):
    if obj.type=='MESH' and 'leaf' in obj.name.lower():
        mod=obj.modifiers.new('Soft organic leaf surface','SUBSURF');mod.levels=1;mod.render_levels=2

# The first pass's window plane was behind the solid room wall. Bring its complete
# inset forward into the room, preserving its orientation on the right wall.
window=bpy.data.objects['window']
window.location.y-=.22
bpy.context.view_layer.update()

# Desktop details: translucent bottle, coaster, cable connectors, and fasteners.
lathe('Small desk bottle',(1.35,1.365,.64),[(0,.048),(.015,.055),(.21,.052),(.23,.027),(.26,.026)],'glassbottle',segments=48)
cyl('Ribbed pink cap',(1.35,1.635,.64),.035,.055,'pinkcap',vertices=48)
for i in range(24):
    a=i*math.tau/24
    rod('Cap grip',(1.35+math.cos(a)*.035,1.61,.64+math.sin(a)*.035),(1.35+math.cos(a)*.035,1.66,.64+math.sin(a)*.035),.0015,'pinkcap',vertices=6)
cyl('Cork coaster',(.94,1.368,.60),.12,.008,'wood',vertices=64)
for i in range(4):
    x=-.48+i*.19
    curve('Soft cable slack',[(x,1.55,-.56),(x-.14,1.39,-.24),(x-.20,1.37,.02),(x-.06,1.37,.16)],.0045,'black')
    box('USB connector',(x-.06,1.375,.17),(.031,.018,.062),'dark',.004)

# Fine, curved chair threads. These are render geometry, not a flat mesh graphic.
chair=bpy.data.objects['chair']
for i in range(59):
    x=-.30+i*.0103
    points=[(-1.63+x,1.09+j*.55/8,1.98+.024*math.sin(j*math.pi/8)) for j in range(9)]
    obj=curve('Woven chair warp',points,.0012,'mesh')
    obj.matrix_world=chair.matrix_world @ Matrix.Translation(-B((-1.63,0,1.62))) @ obj.matrix_world
for i in range(53):
    y=1.09+i*.0105
    points=[(-1.94+j*.62/8,y,1.98+.024*math.sin(j*math.pi/8)) for j in range(9)]
    obj=curve('Woven chair weft',points,.0011,'mesh')
    obj.matrix_world=chair.matrix_world @ Matrix.Translation(-B((-1.63,0,1.62))) @ obj.matrix_world

# Each lamp has a physical socket and a warm emitter recessed inside its shade.
for i in range(1,4):
    g=bpy.data.objects[f'lamp_{i}']
    for j in range(4):
        obj=ring('Lamp socket thread',(0,.08+j*.012,0),.038,.003,'silver',segments=40)
        obj.matrix_world=g.matrix_world @ obj.matrix_world

scene=bpy.context.scene
for obj in list(scene.objects):
    if obj.type=='LIGHT':bpy.data.objects.remove(obj,do_unlink=True)
scene.render.engine='CYCLES'
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='METAL'
scene.cycles.device='GPU'
scene.cycles.samples=64
scene.cycles.use_denoising=True
scene.cycles.adaptive_threshold=.025
scene.cycles.max_bounces=8
scene.cycles.diffuse_bounces=4
scene.cycles.glossy_bounces=4
scene.cycles.transparent_max_bounces=8
scene.render.use_persistent_data=True
scene.world.use_nodes=True
background=scene.world.node_tree.nodes.get('Background')
background.inputs[0].default_value=(.10,.14,.22,1)
background.inputs[1].default_value=.12

def area_light(name,pos,target,power,color,size):
    bpy.ops.object.light_add(type='AREA',location=B(pos))
    obj=bpy.context.object;obj.name=name;obj.data.energy=power
    obj.data.color=color;obj.data.shape='DISK';obj.data.size=size
    obj.rotation_euler=(B(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

area_light('Warm ceiling bounce',(-1.2,5,1.3),(0,1.8,-.4),95,(1,.69,.39),3)
area_light('Quiet camera fill',(-1,4,5),(0,2,-.4),40,(.72,.80,1),4)
area_light('Blue night at window',(2.2,3.8,-.2),(0,1.8,-.3),65,(.35,.53,1),1.7)
area_light('Screen reflected light',(0,2.1,-.24),(0,1.3,.7),9,(.56,.74,.66),1)
for i in range(1,4):
    g=bpy.data.objects[f'lamp_{i}']
    position=g.matrix_world @ B((0,.30,0))
    target=g.matrix_world @ B((0,1.1,0))
    bpy.ops.object.light_add(type='AREA',location=position)
    light=bpy.context.object;light.name=f'Practical shade light {i}'
    light.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler()
    light.data.energy=55;light.data.color=(1,.64,.30);light.data.shape='DISK';light.data.size=.19

camera=scene.camera
camera.data.type='ORTHO';camera.data.ortho_scale=8.4
camera.location=B((.65,7.1,10.4))
camera.rotation_euler=(B((0,2.10,-.18))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=0
scene.render.fps=24;scene.frame_start=1;scene.frame_end=72
for frame,x in [(1,.45),(37,.05),(73,.45)]:
    camera.location=B((x,7.1,10.4))
    camera.rotation_euler=(B((0,2.10,-.18))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.keyframe_insert(data_path='location',frame=frame)
    camera.keyframe_insert(data_path='rotation_euler',frame=frame)
scene.frame_set(1)
scene.render.filepath=str(ART/'cycles-preview.png')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
if '--preview' in sys.argv:
    scene.render.resolution_percentage=65
    scene.cycles.samples=32
    bpy.ops.render.render(write_still=True)
print(f'Refined Cycles scene saved: {OUTPUT}')
