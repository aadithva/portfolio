"""Add the supplied IIT Guwahati degree beside the pegboard without rebuilding.

Creates a guarded, reviewable copy of the current saved scene. Original geometry,
transforms, lighting, textures and the supplied ergonomic chair stay unchanged.
The exact embedded scan is UV-mapped onto the framed print with its native ratio.
"""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
if '--source' in sys.argv:
    SOURCE = Path(sys.argv[sys.argv.index('--source') + 1]).resolve()
TEXTURE = ROOT / 'public/textures/workspace/iitg-degree.jpg'
OUT = ROOT / 'artifacts/workspace/certificate-frame'
OUT.mkdir(parents=True, exist_ok=True)
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
backup = OUT / f'source-before-certificate-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(backup))
if 'certificate_iitg' in bpy.data.objects:
    raise RuntimeError('This source already contains the certificate frame.')
bpy.context.view_layer.update()


def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.name.startswith('certificate_iitg'):
            continue
        vertices = [tuple(v.co) for v in obj.data.vertices] if obj.type == 'MESH' else []
        result[obj.name] = hashlib.sha256(repr((list(map(tuple, obj.matrix_world)), vertices)).encode()).hexdigest()
    return result


before = snapshot()
root = bpy.data.objects.new('certificate_iitg', None)
bpy.context.scene.collection.objects.link(root)
root.location = (-.20, 2.239, 2.9825)
root.rotation_euler.z = math.radians(45)
root.scale = (.75, .75, .75)
root['interactive'] = True
root['section'] = 'achievements'
root['label'] = 'IIT Guwahati graduation certificate'
root['sourceAsset'] = 'Exact embedded JPEG from the user\'s IITG degree PDF'
root['texturePath'] = str(TEXTURE.relative_to(ROOT))


def material(name, color, roughness, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Specular IOR Level'].default_value = .25
    mat.diffuse_color = (*color, 1)
    return mat


charcoal = material('Certificate · Charcoal stained timber', (.025, .028, .030), .47)
matboard = material('Certificate · Warm conservation mat', (.73, .70, .62), .95)
backing = material('Certificate · Backing board', (.12, .09, .06), .9)
print_material = material('Certificate · Exact IIT Guwahati degree', (1, 1, 1), .84)
image = bpy.data.images.load(str(TEXTURE), check_existing=False)
image.colorspace_settings.name = 'sRGB'
image.pack()
image_node = print_material.node_tree.nodes.new('ShaderNodeTexImage')
image_node.image = image
image_node.interpolation = 'Linear'
uv = print_material.node_tree.nodes.new('ShaderNodeUVMap')
uv.uv_map = 'SourceUV'
shader = print_material.node_tree.nodes.get('Principled BSDF')
print_material.node_tree.links.new(uv.outputs['UV'], image_node.inputs['Vector'])
print_material.node_tree.links.new(image_node.outputs['Color'], shader.inputs['Base Color'])
print_material.node_tree.links.new(image_node.outputs['Color'], shader.inputs['Emission Color'])
shader.inputs['Emission Strength'].default_value = .04
print_material['referenceSource'] = 'Exact pixels, no recreated typography or certificate details'
print_material['textureSha256'] = hashlib.sha256(TEXTURE.read_bytes()).hexdigest()


def box(name, center, size, mat, bevel=.002):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = 'certificate_iitg · ' + name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.parent = root
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = center
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Fine manufactured edge', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod = obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
        mod.keep_sharp = True
    return obj


print_width = .53
print_height = print_width * image.size[1] / image.size[0]
mat_width, mat_height = print_width + .08, print_height + .08
rail = .022
outer_width, outer_height = mat_width + 2 * rail, mat_height + 2 * rail
box('Timber backing', (0, .011, 0), (outer_width - .008, .012, outer_height - .008), backing)
box('Cream mat', (0, -.004, 0), (mat_width, .016, mat_height), matboard, .001)
for sign in (-1, 1):
    box('Vertical rail ' + str(sign), (sign * (mat_width + rail) / 2, -.006, 0),
        (rail, .042, outer_height), charcoal)
    box('Horizontal rail ' + str(sign), (0, -.006, sign * (mat_height + rail) / 2),
        (mat_width, .042, rail), charcoal)

# Local -Y faces the room. The supplied portrait stays upright and uncropped.
vertices = [(-print_width / 2, -.013, -print_height / 2),
            (print_width / 2, -.013, -print_height / 2),
            (print_width / 2, -.013, print_height / 2),
            (-print_width / 2, -.013, print_height / 2)]
mesh = bpy.data.meshes.new('certificate_iitg exact print UV mesh')
mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
mesh.update()
layer = mesh.uv_layers.new(name='SourceUV')
for datum, coordinate in zip(layer.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
    datum.uv = coordinate
printed = bpy.data.objects.new('certificate_iitg · Degree print', mesh)
bpy.context.scene.collection.objects.link(printed)
printed.parent = root
printed.data.materials.append(print_material)
printed['certificateOriginalPixels'] = True

# Low-opacity glazing keeps the paper legible instead of casting a dark pane.
# This thin plane exports as ordinary alpha-blended glTF, avoiding another
# real-time transmission pass for an object that is small in the overview.
glazing = material('Certificate · Anti-reflection glazing', (.68, .74, .78), .19)
glass_shader = glazing.node_tree.nodes.get('Principled BSDF')
glass_shader.inputs['Alpha'].default_value = .025
glass_shader.inputs['Specular IOR Level'].default_value = .38
glazing.surface_render_method = 'BLENDED'
glass_mesh = mesh.copy()
for vertex in glass_mesh.vertices:
    vertex.co.y = -.018
glass = bpy.data.objects.new('certificate_iitg · Glazing', glass_mesh)
bpy.context.scene.collection.objects.link(glass)
glass.parent = root
glass.data.materials.clear()
glass.data.materials.append(glazing)
glass.visible_shadow = False

bpy.context.view_layer.update()
after = snapshot()
if before != after:
    raise RuntimeError('An unrelated object changed; refusing to save.')
points = [o.matrix_world @ vertex.co for o in root.children_recursive if o.type == 'MESH'
          for vertex in o.data.vertices]
web = lambda p: (p.x, p.z, -p.y)
web_points = [web(p) for p in points]
bounds = [[round(fn(p[i] for p in web_points), 6) for i in range(3)] for fn in (min, max)]
if bounds[0][0] <= -.451 + .05 or bounds[1][0] >= -.005:
    raise RuntimeError('The frame does not fit between the pegboard and the corner seam.')
candidate = OUT / 'workspace-iitg-certificate.blend'
bpy.context.scene['certificateAssetRevision'] = 'iitg-degree-exact-scan-v1'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))
report = {
    'sourceSha256': source_hash,
    'candidateSha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
    'textureSha256': hashlib.sha256(TEXTURE.read_bytes()).hexdigest(),
    'textureSize': list(image.size), 'imageAspectPreserved': True,
    'unrelatedObjectsUnchanged': before == after,
    'originalObjectCount': len(before), 'newObjectCount': 1 + len(root.children_recursive),
    'interactiveRoot': root.name, 'webBounds': bounds,
    'webCenter': list(web(root.location)), 'outerDimensions': [outer_width * .75, outer_height * .75, .042 * .75],
    'uniformScale': .75,
    'pegboardHorizontalGap': round(bounds[0][0] - -.451, 6),
    'wallTopGap': round(4.58 - bounds[1][1], 6),
}
(OUT / 'application.json').write_text(json.dumps(report, indent=2) + '\n')
print('CERTIFICATE_FRAME_CANDIDATE', json.dumps(report), flush=True)
