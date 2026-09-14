"""Create a chair-only review candidate from the latest saved workspace.

The imported FBX and grey PBR maps replace descendants of the existing chair
interaction root. The source room is backed up and never overwritten here.
"""
import hashlib
import json
import math
import shutil
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/workspace/chair-replacement'
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
BACKUP = OUT / 'source-before-chair.blend'
TEXTURES = ROOT / 'public/textures/workspace/office-chair'
OUT.mkdir(parents=True, exist_ok=True)
if not BACKUP.exists():
    shutil.copy2(SOURCE, BACKUP)
bpy.ops.wm.open_mainfile(filepath=str(BACKUP))
bpy.context.view_layer.update()
root = bpy.data.objects['chair']
excluded = {root.name, *(o.name for o in root.children_recursive)}

def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.name in excluded:
            continue
        vertices = [tuple(v.co) for v in obj.data.vertices] if obj.type == 'MESH' else []
        result[obj.name] = hashlib.sha256(repr((list(map(tuple, obj.matrix_world)), vertices)).encode()).hexdigest()
    return result

before = snapshot()
old_root_matrix = [list(row) for row in root.matrix_world]
old_names = [o.name for o in root.children_recursive]
for obj in list(root.children_recursive):
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.import_scene.fbx(filepath=str(OUT / 'source/source/OfficeChair.fbx'))
imported = list(bpy.context.selected_objects)
if len(imported) != 1 or imported[0].type != 'MESH':
    raise RuntimeError('The supplied FBX hierarchy differs from the audited asset.')
chair = imported[0]
chair.name = 'chair · Supplied ergonomic office chair'
original_world = chair.matrix_world.copy()
chair.data.transform(original_world)
chair.matrix_world = Matrix.Identity(4)
# The 75 cm desktop is 1.31 scene units high. Apply that same unit scale
# uniformly to the supplied metric chair: 116 cm high, 68 cm caster footprint.
scale = 1.31 / .75
floor = root.matrix_world.translation.z
minimum_z = min(v.co.z for v in chair.data.vertices)
chair.data.transform(Matrix.Rotation(math.pi, 4, 'Z') @ Matrix.Scale(scale, 4))
chair.data.transform(Matrix.Translation((0, 0, -minimum_z * scale)))
chair.parent = root
chair.matrix_parent_inverse = Matrix.Identity(4)
chair.matrix_basis = Matrix.Identity(4)
chair['sourceAsset'] = 'User supplied office-chair.zip / source/OfficeChair.fbx'
chair['sourceTriangles'] = sum(len(p.vertices) - 2 for p in chair.data.polygons)
chair['scaleFromMetres'] = scale
chair['greyTextureSource'] = 'Original UV-mapped PBR textures, recoloured by prepare_office_chair_textures.py'
for polygon in chair.data.polygons:
    polygon.use_smooth = True
if len(chair.data.uv_layers) != 1:
    raise RuntimeError('Expected a single authored UV set.')
chair.data.uv_layers[0].name = 'SourceUV'
# Leave the full supplied mesh editable; this non-destructive modifier brings
# the website copy near the old chair's geometry budget after normal export.
modifier = chair.modifiers.new('Web chair optimization', 'DECIMATE')
modifier.ratio = .30
modifier.use_collapse_triangulate = True
modifier.delimit = {'UV', 'MATERIAL', 'NORMAL'}

def material(name, net=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (.36, .37, .38, 1) if net else (.29, .29, .29, 1)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = 220 / 255 if net else .6
    shader.inputs['Specular IOR Level'].default_value = .28 if net else .38
    uv = nodes.new('ShaderNodeUVMap'); uv.uv_map = 'SourceUV'
    def texture(filename, non_color=False):
        node = nodes.new('ShaderNodeTexImage')
        node.image = bpy.data.images.load(str(TEXTURES / filename), check_existing=True)
        node.image.colorspace_settings.name = 'Non-Color' if non_color else 'sRGB'
        node.image.pack()
        links.new(uv.outputs['UV'], node.inputs['Vector'])
        return node
    color = texture('net-grey.png' if net else 'main-grey.jpg')
    links.new(color.outputs['Color'], shader.inputs['Base Color'])
    normal = texture('net-normal.jpg' if net else 'main-normal.jpg', True)
    normal_map = nodes.new('ShaderNodeNormalMap'); normal_map.uv_map = 'SourceUV'
    normal_map.inputs['Strength'].default_value = .65 if net else .8
    links.new(normal.outputs['Color'], normal_map.inputs['Color'])
    links.new(normal_map.outputs['Normal'], shader.inputs['Normal'])
    if net:
        links.new(color.outputs['Alpha'], shader.inputs['Alpha'])
        mat.surface_render_method = 'DITHERED'
        mat.use_backface_culling = False
    else:
        roughness = texture('main-roughness.png', True)
        metallic = texture('main-metallic.png', True)
        links.new(roughness.outputs['Color'], shader.inputs['Roughness'])
        links.new(metallic.outputs['Color'], shader.inputs['Metallic'])
    return mat

for i, slot in enumerate(chair.material_slots):
    is_net = slot.material.name == 'OfficeChair_Net'
    chair.data.materials[i] = material('Office chair · Grey woven mesh' if is_net else 'Office chair · Graphite frame and fabric', is_net)

bpy.context.view_layer.update()
excluded.add(chair.name)
after = snapshot()
if before != after:
    raise RuntimeError('Unrelated room objects changed; refusing to save.')
if old_root_matrix != [list(row) for row in root.matrix_world]:
    raise RuntimeError('The chair interaction root changed unexpectedly.')
points = [chair.matrix_world @ v.co for v in chair.data.vertices]
low = [min(v[i] for v in points) for i in range(3)]
high = [max(v[i] for v in points) for i in range(3)]
bpy.context.scene['chairAssetRevision'] = 'supplied-office-chair-grey-v1'
bpy.ops.file.pack_all()
candidate = OUT / 'workspace-grey-chair.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))
report = {'backupSha256': hashlib.sha256(BACKUP.read_bytes()).hexdigest(),
          'candidateSha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
          'unrelatedObjectsUnchanged': before == after,
          'chairRootPreserved': True, 'removedMeshes': old_names,
          'originalTriangles': chair['sourceTriangles'], 'scaleFromMetres': scale,
          'worldBoundsBlender': [low, high], 'floorHeight': floor,
          'physicalDimensionsMetres': [.67640698, .65576595, 1.16284859]}
(OUT / 'application.json').write_text(json.dumps(report, indent=2) + '\n')
print('CHAIR_REPLACEMENT_CANDIDATE', json.dumps(report), flush=True)
