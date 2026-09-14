"""Apply the supplied close-up to a backed-up laptop, preserving the saved room.

Writes a review candidate. Run the normal saved-scene bake after validation and
guarded promotion; never run the original desk generator to publish this edit.
"""
import hashlib
import json
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/workspace/laptop-closeup'
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
TEXTURE = ROOT / 'public/textures/workspace/laptop-closeup-albedo.jpg'
BACKUP = OUT / 'source-before-laptop-closeup.blend'
OUT.mkdir(parents=True, exist_ok=True)
if not TEXTURE.exists():
    raise RuntimeError('Run extract_laptop_closeup.py before applying the texture.')
if not BACKUP.exists():
    shutil.copy2(SOURCE, BACKUP)
bpy.ops.wm.open_mainfile(filepath=str(BACKUP))
if bpy.context.scene.get('laptopCloseupRevision'):
    raise RuntimeError('The input already has the close-up edit; use the pre-edit backup.')
bpy.context.view_layer.update()


def web(v):
    return Vector((v.x, v.z, -v.y))


def blender(v):
    return Vector((v.x, -v.z, v.y))


def mesh_bounds(obj):
    points = [web(obj.matrix_world @ v.co) for v in obj.data.vertices]
    return [Vector(tuple(min(p[i] for p in points) for i in range(3))),
            Vector(tuple(max(p[i] for p in points) for i in range(3)))]


def snapshot(excluded):
    """Guard every unrelated object's transform and raw geometry."""
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.name in excluded:
            continue
        vertices = [tuple(v.co) for v in obj.data.vertices] if obj.type == 'MESH' else []
        result[obj.name] = hashlib.sha256(repr((list(map(tuple, obj.matrix_world)), vertices)).encode()).hexdigest()
    return result


laptop = bpy.data.objects['laptop']
lid = bpy.data.objects['Laptop sticker printed lid']
low, high = mesh_bounds(lid)
old_ratio = (high.x - low.x) / (high.z - low.z)
new_image = bpy.data.images.load(str(TEXTURE), check_existing=False)
new_image.colorspace_settings.name = 'sRGB'
new_image.pack()
image_ratio = new_image.size[0] / new_image.size[1]
depth_factor = old_ratio / image_ratio
center = web(laptop.matrix_world.translation)
editable = [laptop, *laptop.children_recursive]
for name in ['sticker_1', 'sticker_2']:
    editable.extend([bpy.data.objects[name], *bpy.data.objects[name].children_recursive])
before = snapshot({obj.name for obj in editable})

# Match the clearer photo's lid aspect ratio so circular stickers stay circular.
# Width and tabletop contact stay fixed; the small depth change is centered.
for obj in laptop.children_recursive:
    if obj.type != 'MESH':
        raise RuntimeError(f'Unexpected laptop geometry: {obj.name} ({obj.type})')
    world, inverse = obj.matrix_world.copy(), obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        point = web(world @ vertex.co)
        point.z = center.z + (point.z - center.z) * depth_factor
        vertex.co = inverse @ blender(point)
    obj.data.update()

material = bpy.data.materials['Laptop sticker collage']
node = material.node_tree.nodes['Image Texture']
node.image = new_image
node.interpolation = 'Linear'
lid_shader = material.node_tree.nodes.get('Principled BSDF')
lid_shader.inputs['Roughness'].default_value = .84
lid_shader.inputs['Specular IOR Level'].default_value = .22
material['reference_source'] = 'User supplied laptop close-up; exact pixels rectified by extract_laptop_closeup.py'
material['reference_texture'] = str(TEXTURE.relative_to(ROOT))
material['reference_resolution'] = f'{new_image.size[0]} x {new_image.size[1]}'

# The photograph supplies the visible discovery stickers. Keep the named hit
# regions for the existing game, without raised discs covering the printed art.
hit_material = bpy.data.materials.new('Invisible photographed-sticker hit region')
hit_material.use_nodes = True
bsdf = hit_material.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Alpha'].default_value = 0
hit_material.diffuse_color = (0, 0, 0, 0)
for name in ['sticker_1', 'sticker_2']:
    root = bpy.data.objects[name]
    old_position = web(root.matrix_world.translation)
    old_position.z = center.z + (old_position.z - center.z) * depth_factor
    matrix = root.matrix_world.copy()
    matrix.translation = blender(old_position)
    root.matrix_world = matrix
    root['appearanceFromTexture'] = True
    for obj in root.children_recursive:
        if obj.type != 'MESH':
            raise RuntimeError(f'Unexpected discovery geometry: {obj.name}')
        obj.data.materials.clear()
        obj.data.materials.append(hit_material)
        obj['interactionOnly'] = True
        if hasattr(obj, 'visible_shadow'):
            obj.visible_shadow = False

bpy.context.view_layer.update()
after = snapshot({obj.name for obj in editable})
if before != after:
    raise RuntimeError('An unrelated room object changed; refuse to save.')
bpy.context.scene['laptopCloseupRevision'] = 'supplied-photo-v1'
bpy.ops.file.pack_all()
candidate = OUT / 'workspace-laptop-closeup.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))
report = {
    'backupSha256': hashlib.sha256(BACKUP.read_bytes()).hexdigest(),
    'candidateSha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
    'textureSha256': hashlib.sha256(TEXTURE.read_bytes()).hexdigest(),
    'textureSize': list(new_image.size), 'oldLidAspect': old_ratio,
    'newLidAspect': image_ratio, 'depthScale': depth_factor,
    'unrelatedObjectsUnchanged': before == after,
    'discoveryRootsPreserved': ['sticker_1', 'sticker_2'],
}
(OUT / 'application.json').write_text(json.dumps(report, indent=2) + '\n')
print('LAPTOP_CLOSEUP_CANDIDATE', json.dumps(report), flush=True)
