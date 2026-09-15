"""Correct the can label's cylindrical mapping and printed-metal material."""
import math
import shutil
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
OUT=ROOT/'artifacts/workspace/diet-coke-fix'
backup=OUT/'source-before-texture-fix.blend'
if backup.exists():raise RuntimeError('Can texture fix already applied')
shutil.copy2(SOURCE,backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
obj=bpy.data.objects['Can label cylinder'];mesh=obj.data
uv=mesh.uv_layers.active
zmin=min(v.co.z for v in mesh.vertices);zmax=max(v.co.z for v in mesh.vertices)
front=math.atan2(-5.7-obj.matrix_world.translation.y,2.4-obj.matrix_world.translation.x)
for poly in mesh.polygons:
 coords=[]
 for loop in poly.loop_indices:
  v=mesh.vertices[mesh.loops[loop].vertex_index].co
  u=((math.atan2(v.y,v.x)-front)/(2*math.pi)+.25)%1
  coords.append((loop,u,(v.z-zmin)/(zmax-zmin)))
 # Preserve a continuous strip across the cylindrical seam.
 seam=max(c[1] for c in coords)-min(c[1] for c in coords)>.5
 for loop,u,v in coords:uv.data[loop].uv=(u+1 if seam and u<.5 else u,v)
mat=bpy.data.materials['Diet Coke aluminium label'];nodes=mat.node_tree.nodes;links=mat.node_tree.links
shader=nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.52
for node in nodes:
 if node.type=='TEX_IMAGE':
  node.image=bpy.data.images.load(str(ROOT/'public/textures/workspace/diet-coke-label.webp'));node.interpolation='Linear'
  links.new(node.outputs['Color'],shader.inputs['Emission Color']);shader.inputs['Emission Strength'].default_value=.22
  uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map=uv.name;links.new(uvnode.outputs['UV'],node.inputs['Vector'])
  break
metal=nodes.new('ShaderNodeTexImage');metal.image=bpy.data.images.load(str(ROOT/'public/textures/workspace/diet-coke-metalness.png'));metal.image.colorspace_settings.name='Non-Color'
links.new(uvnode.outputs['UV'],metal.inputs['Vector']);links.new(metal.outputs['Color'],shader.inputs['Metallic'])
obj['webOptimized']=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE));print('DIET_COKE_TEXTURE_FIXED',flush=True)
