"""Add exportable matte microtexture maps to the saved room and black bicycle."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from surface_detail_uv import ensure_detail_uv

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
if '--inspect' in sys.argv:
    used={m for obj in bpy.context.scene.objects for m in getattr(obj.data,'materials',[]) if m}
    for m in sorted(used,key=lambda m:m.name):
        shader=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
        if shader:
            print('MATERIAL',m.name,'color',list(shader.inputs['Base Color'].default_value),
                  'rough',shader.inputs['Roughness'].default_value,'metal',shader.inputs['Metallic'].default_value,
                  'images',[n.image.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image],flush=True)
    raise SystemExit(0)

OUT=ROOT/'artifacts/workspace/matte-materials'
TEX=ROOT/'public/textures/workspace/surface-detail'
OUT.mkdir(exist_ok=True);TEX.mkdir(exist_ok=True)
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
backup=OUT/f'source-before-matte-{source_hash[:12]}.blend'
if not backup.exists():shutil.copy2(SOURCE,backup)

def image(name,array):
    h,w=array.shape[:2]
    rgba=np.ones((h,w,4),dtype=np.float32)
    rgba[:,:,:3]=array if array.ndim==3 else array[:,:,None]
    result=bpy.data.images.new(name,width=w,height=h,alpha=False)
    result.colorspace_settings.name='Non-Color'
    result.pixels.foreach_set(rgba.ravel())
    result.filepath_raw=str(TEX/(name+'.png'));result.file_format='PNG';result.save();result.pack()
    return result

# Seamless multiscale noise. Small height slopes provide grain, while the
# slower field breaks up perfectly uniform specular highlights.
rng=np.random.default_rng(15926)
noise=rng.random((256,256)).astype(np.float32)
soft=noise.copy()
for _ in range(10):
    soft=(soft+np.roll(soft,1,0)+np.roll(soft,-1,0)+np.roll(soft,1,1)+np.roll(soft,-1,1))/5
soft=(soft-soft.min())/(soft.max()-soft.min())
height=.65*soft+.35*noise
dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.8
dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.8
normal=np.stack((-dx,-dy,np.ones_like(dx)),axis=2)
normal/=np.linalg.norm(normal,axis=2,keepdims=True)
normal_image=image('matte-grain-normal',normal*.5+.5)
profiles={
    'powder':(.68,.15,.30,7),
    'plastic':(.74,.10,.16,11),
    'rubber':(.88,.08,.20,12),
    'plaster':(.94,.08,.35,2.8),
    'stone':(.85,.13,.28,4),
    'paper':(.92,.06,.12,10),
    'metal':(.52,.12,.09,14),
}
rough_images={key:image('matte-'+key+'-roughness',np.clip(base+(soft-.5)*variation+(noise-.5)*.035,0,1))
              for key,(base,variation,strength,density) in profiles.items()}

def profile_for(mat):
    name=mat.name.lower()
    if any(token in name for token in ['glazing','glass','bulb','display','night exterior','distant','invisible','office chair']):return None
    if 'lamp enamel' in name or 'lamp edge' in name or 'powder' in name or 'porcelain' in name or name in {'rama','orange.metal','blue'}:return 'powder'
    if any(token in name for token in ['rubber','seat.skin','wheel.','foam','soil']):return 'rubber'
    if 'plaster' in name or 'grout' in name:return 'plaster'
    if any(token in name for token in ['limestone','stone','terracotta']):return 'stone'
    if any(token in name for token in ['paper','card','printed','artwork','hardcover','ribbon','cotton','binding','mat','timber','walnut']):return 'paper'
    if any(token in name for token in ['brass','alumin','metal.silver','encoder','relief']):return 'metal'
    return 'plastic'

used={m for obj in bpy.context.scene.objects for m in getattr(obj.data,'materials',[]) if m}
changes=[]
black_values={'rama':.012,'orange.metal':.012,'Blue':.010,'wheel.orange':.006,'wheel.black':.006,
              'metal.black':.009,'seat.skin':.009,'seat.plastic':.012}
for mat in sorted(used,key=lambda m:m.name):
    shader=mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes else None
    key=profile_for(mat)
    if not shader or not key:continue
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    if mat.name in black_values:
        for link in list(shader.inputs['Base Color'].links):links.remove(link)
        value=black_values[mat.name]
        shader.inputs['Base Color'].default_value=(value,value,value,1)
        shader.inputs['Metallic'].default_value=.12 if mat.name in {'rama','orange.metal'} else 0
    if 'Lamp ' in mat.name:
        shader.inputs['Metallic'].default_value=.06
        shader.inputs['Coat Weight'].default_value=0
        shader.inputs['Specular IOR Level'].default_value=.3
    for node in list(nodes):
        if node.label=='Matte surface detail':nodes.remove(node)
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map='SurfaceDetail';uv.label='Matte surface detail'
    rough=nodes.new('ShaderNodeTexImage');rough.image=rough_images[key];rough.label='Matte surface detail'
    links.new(uv.outputs['UV'],rough.inputs['Vector']);links.new(rough.outputs['Color'],shader.inputs['Roughness'])
    if not shader.inputs['Normal'].is_linked or mat.get('matteDetail') or mat.name in black_values:
        texture=nodes.new('ShaderNodeTexImage');texture.image=normal_image;texture.label='Matte surface detail'
        bump=nodes.new('ShaderNodeNormalMap');bump.uv_map='SurfaceDetail';bump.label='Matte surface detail'
        bump.inputs['Strength'].default_value=profiles[key][2]
        links.new(uv.outputs['UV'],texture.inputs['Vector']);links.new(texture.outputs['Color'],bump.inputs['Color'])
        links.new(bump.outputs['Normal'],shader.inputs['Normal'])
    shader.inputs['Roughness'].default_value=profiles[key][0]
    mat['matteDetail']=key;mat['detailDensity']=profiles[key][3]
    changes.append({'material':mat.name,'profile':key,'black':mat.name in black_values})

for obj in bpy.context.scene.objects:ensure_detail_uv(obj)
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=source_hash:raise RuntimeError('Master changed during material edit')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
(OUT/'application.json').write_text(json.dumps({'sourceSha256':source_hash,'materials':changes,'textureFiles':8},indent=2)+'\n')
print('MATTE_MATERIALS_APPLIED',len(changes),flush=True)
