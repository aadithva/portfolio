import bpy, math
from mathutils import Vector
from pathlib import Path
root=Path('/Users/aadith/Projects/Portfolio/Website')
bpy.ops.wm.open_mainfile(filepath=str(root/'artifacts/workspace/certificate-frame/workspace-iitg-certificate.blend'))
s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.render.filepath=str(root/'artifacts/workspace/certificate-frame/overview.png')
bpy.ops.render.render(write_still=True)
def b(p):return Vector((p[0],-p[2],p[1]))
s.camera.location=b((-.49,3.39,.17));target=b((-1.55,3.22,-.889));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=50
s.render.filepath=str(root/'artifacts/workspace/certificate-frame/frame-closeup.png')
bpy.ops.render.render(write_still=True)
