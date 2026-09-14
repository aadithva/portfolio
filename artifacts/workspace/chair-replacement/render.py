import bpy, math
from pathlib import Path
from mathutils import Vector
OUT=Path('/Users/aadith/Projects/Portfolio/Website/artifacts/workspace/chair-replacement')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'workspace-grey-chair.blend'))
scene=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for device in prefs.devices: device.use=device.type=='METAL'
scene.render.engine='CYCLES';scene.cycles.device='GPU';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.resolution_x=1000;scene.render.resolution_y=1000
scene.render.filepath=str(OUT/'reference-overview.png')
bpy.ops.render.render(write_still=True)
camera=scene.camera
camera.data.type='PERSP';camera.data.lens=42
camera.location=Vector((-2.7,-2.8,2.8))
target=Vector((-.86,.03,1.))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'chair-closeup.png')
bpy.ops.render.render(write_still=True)
camera.location=Vector((2.4,-5.7,3.7))
target=Vector((0,.9,1.7))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.angle=math.radians(36)
scene.render.resolution_x=1300;scene.render.resolution_y=900
scene.render.filepath=str(OUT/'website-overview.png')
bpy.ops.render.render(write_still=True)
print('CHAIR_REVIEW_RENDER_COMPLETE',flush=True)
