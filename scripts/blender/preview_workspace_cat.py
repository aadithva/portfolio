"""Render web-prepared cat poses for visual inspection, then measure room anchors."""
import bpy
import json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/workspace/cat'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'cat-web.blend'),use_scripts=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=900;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Preview world');scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.32,.35,.4,1)
scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
bpy.ops.object.camera_add(location=(13,-18,9))
camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,1))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=15;scene.camera=camera
bpy.ops.object.light_add(type='AREA',location=(4,-8,12))
light=bpy.context.object;light.data.energy=1800;light.data.shape='DISK';light.data.size=8
light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.image_settings.media_type='IMAGE'
scene.render.image_settings.file_format='PNG'
rig=bpy.data.objects['Armature']
for name,frame,label in [('Idle',1,'idle'),('Sit',1,'sit'),('Jump',6,'crouch'),('Jump',11,'launch'),('Jump',16,'flight'),('Jump',20,'landing')]:
    rig.animation_data.action=bpy.data.actions[name];scene.frame_set(frame)
    scene.render.filepath=str(OUT/f'cat-{label}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts/workspace/workspace.blend'),use_scripts=False)
report=[]
for o in bpy.data.objects:
    if any(s in o.name.lower() for s in ['chair','desktop','floor','rug','mat','desk_top']):
        pts=[o.matrix_world@Vector(v) for v in o.bound_box]
        report.append({'name':o.name,'type':o.type,'position':list(o.matrix_world.translation),
                       'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]})
(OUT/'room-anchors.json').write_text(json.dumps(report,indent=2))
