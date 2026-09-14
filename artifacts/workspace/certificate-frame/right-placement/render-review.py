import bpy
from pathlib import Path
from mathutils import Vector
root=Path('/Users/aadith/Projects/Portfolio/Website')
out=root/'artifacts/workspace/certificate-frame/right-placement'
bpy.ops.wm.open_mainfile(filepath=str(out/'workspace-certificate-right.blend'))
s=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
for d in p.devices:d.use=d.type=='METAL'
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.render.filepath=str(out/'overview.png');bpy.ops.render.render(write_still=True)
def b(p):return Vector((p[0],-p[2],p[1]))
s.camera.location=b((1.35,3.55,.28));t=b((-.40,2.99,-1.87));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=50
s.render.filepath=str(out/'wall-alignment.png');bpy.ops.render.render(write_still=True)
