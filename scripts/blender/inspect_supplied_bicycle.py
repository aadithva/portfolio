"""Inspect the supplied FBX in isolation, without changing the room."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/workspace/bicycle'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OUT/'source/source/road_bike.fbx'))
meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
bpy.context.view_layer.update()
report=[]
for obj in meshes:
    points=[obj.matrix_world@v.co for v in obj.data.vertices]
    report.append({'name':obj.name,'bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]],
                   'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons),
                   'materials':[m.name if m else None for m in obj.data.materials]})
images=[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]
(OUT/'supplied-inspection.json').write_text(json.dumps({'meshes':report,'images':images},indent=2))
print(json.dumps({'meshes':report,'images':images},indent=2))
points=[obj.matrix_world@v.co for obj in meshes for v in obj.data.vertices]
low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
center=(low+high)/2;span=max(high-low)
camera=bpy.data.objects.new('Inspection camera',bpy.data.cameras.new('Inspection camera'));bpy.context.collection.objects.link(camera)
camera.location=center+Vector((.25,-1,.3))*span*1.7
camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=span*1.2
scene=bpy.context.scene;scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.filepath=str(OUT/'supplied-inspection.png')
bpy.ops.render.render(write_still=True)
