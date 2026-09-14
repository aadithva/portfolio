import bpy
from pathlib import Path
from mathutils import Vector
r=Path('/Users/aadith/Projects/Portfolio/Website');o=r/'artifacts/workspace/ride-for-unity-medal'
bpy.ops.wm.open_mainfile(filepath=str(o/'workspace-ride-for-unity-medal.blend'))
s=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
for d in p.devices:d.use=d.type=='METAL'
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=48;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.render.filepath=str(o/'overview.png');bpy.ops.render.render(write_still=True)
def b(p):return Vector((p[0],-p[2],p[1]))
s.camera.location=b((.07,2.315,-.62));t=b((0,2.22,-1.246));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=70
s.render.filepath=str(o/'medal-closeup.png');bpy.ops.render.render(write_still=True)
