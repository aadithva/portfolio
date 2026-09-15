import bpy
from pathlib import Path
ROOT=Path('/Users/aadith/Projects/Portfolio/Website')
# Diffuse-only indirect baking omits the metallic label's bounced reflection.
# A small texture-colored fill restores legibility in the shadowed lower half.
for file in ['workspace.blend','workspace-saved-baked.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts/workspace'/file))
 m=bpy.data.materials['Diet Coke aluminium label'];shader=m.node_tree.nodes.get('Principled BSDF')
 texture=next(n for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'diet-coke-label' in n.image.filepath)
 m.node_tree.links.new(texture.outputs['Color'],shader.inputs['Emission Color']);shader.inputs['Emission Strength'].default_value=.22
 bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
 if file.endswith('baked.blend'):
  bpy.ops.object.select_all(action='DESELECT')
  for o in bpy.context.scene.objects:
   if o.type in {'MESH','EMPTY'} and not o.hide_render:o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/workspace-saved.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
import json,hashlib
p=ROOT/'public/models/workspace-saved.manifest.json';m=json.loads(p.read_text());m['revision']=hashlib.sha256((ROOT/'public/models/workspace-saved.glb').read_bytes()).hexdigest()[:12];m['bytes']=(ROOT/'public/models/workspace-saved.glb').stat().st_size;m['sourceRevision']=hashlib.sha256((ROOT/'artifacts/workspace/workspace.blend').read_bytes()).hexdigest()[:12];p.write_text(json.dumps(m,indent=2)+'\n')
