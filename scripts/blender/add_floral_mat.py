"""Add the supplied floral mat beneath the desk without changing other props."""
import json
import math
import shutil
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
OUT=ROOT/'artifacts/workspace/floral-mat'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
if bpy.data.objects.get('Floral desk mat'):
 raise RuntimeError('Floral mat already exists')
shutil.copy2(SOURCE,OUT/'source-before-mat.blend')
tex=ROOT/'public/textures/workspace/floral-mat'
data=json.loads((tex/'outline.json').read_text())
points=data['points']; n=len(points)
# Pixel coordinates map the photograph directly to the shaped surface.
def position(p,z):
 return ((p[0]-450)/790*1.65,(450-p[1])/860*1.80+.55,z)
verts=[position((450,450),.013)]+[position(p,.013) for p in reversed(points)]
ring=list(reversed(points))
faces=[(0,i+1,(i+1)%n+1) for i in range(n)]
verts += [position(p,-.011) for p in ring]
faces += [(i+1,n+i+1,n+(i+1)%n+1,(i+1)%n+1) for i in range(n)]
faces.append(tuple(reversed(range(n+1,2*n+1))))
mesh=bpy.data.meshes.new('Floral mat shaped textile');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('Floral desk mat',mesh);bpy.context.collection.objects.link(obj)
uv=mesh.uv_layers.new(name='SourceUV')
for poly in mesh.polygons:
 for loop in poly.loop_indices:
  v=mesh.vertices[mesh.loops[loop].vertex_index].co
  uv.data[loop].uv=((v.x/1.65*790+450)/900,((v.y-.55)/1.8*860+450)/900)
mat=bpy.data.materials.new('Floral mat · tufted cotton');mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links
bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.96
bs.inputs['Sheen Weight'].default_value=.25
image=nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(tex/'floral-mat.webp'))
links.new(image.outputs['Color'],bs.inputs['Base Color'])
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=350;noise.inputs['Detail'].default_value=2
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.003
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
mesh.materials.append(mat)
edge=bpy.data.materials.new('Floral mat · green binding');edge.use_nodes=True
shader=edge.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.018,.24,.09,1);shader.inputs['Roughness'].default_value=.95
mesh.materials.append(edge)
for p in mesh.polygons:
 if p.index>=n:p.material_index=1
bevel=obj.modifiers.new('Soft bound edge','BEVEL');bevel.width=.003;bevel.segments=2
obj['webOptimized']=True
obj['description']='Supplied VATTENSKRUV floral mat beneath the desk and chair'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
print('FLORAL_MAT_ADDED',flush=True)
