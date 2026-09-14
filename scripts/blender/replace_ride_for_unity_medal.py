"""Replace three generic medals with the supplied Ride for Unity medal.

Trace geometry directly in photo coordinates and map the unchanged full JPEG
through UVs. No crop, retouch, generated lettering or substituted branding is used.
Only the medal families change; the current room, certificate and trophies remain.
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
TEXTURE = ROOT / 'public/textures/workspace/ride-for-unity-medal.jpg'
OUT = ROOT / 'artifacts/workspace/ride-for-unity-medal'
OUT.mkdir(parents=True, exist_ok=True)
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
backup = OUT / f'source-before-medal-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(backup))
bpy.context.view_layer.update()
families = {obj.name for obj in bpy.context.scene.objects if obj.name.startswith(('medal_1', 'medal_2', 'medal_3'))}
if not all(name in bpy.data.objects for name in ('medal_1', 'medal_2', 'medal_3')):
    raise RuntimeError('Expected the three generic medal roots in the saved source.')


def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.name in families or obj.name.startswith('medal_1'):
            continue
        verts = [tuple(v.co) for v in obj.data.vertices] if obj.type == 'MESH' else []
        result[obj.name] = hashlib.sha256(repr((list(map(tuple, obj.matrix_world)), verts,
                         [slot.material.name if slot.material else None for slot in obj.material_slots])).encode()).hexdigest()
    return result


before = snapshot()
anchor = bpy.data.objects['medal_2'].matrix_world.translation.copy()
root = bpy.data.objects['medal_1']
for name in families:
    if name != 'medal_1':
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
root.parent = None
root.matrix_world = Matrix.Translation(anchor)
root['interactive'] = True
root['contentStatus'] = 'User supplied Ride for Unity medal photograph'
root['sourceAsset'] = 'ride-for-unity-medal.jpg, exact supplied photo'
root['referenceTexture'] = str(TEXTURE.relative_to(ROOT))
root['label'] = 'Ride for Unity · Kashmir to Kanyakumari'

# Coordinate traces use a 1368×1824 display of the 3120×4160 original.
# Both have the same 3:4 ratio; UVs address the original image directly.
PHOTO_W, PHOTO_H = 1368.0, 1824.0
SCALE = .00030
PHOTO_CENTER_X, HANGING_START_Y = 699.0, 225.0
FACE_Z = .038
THICKNESS = .006


def point(x, y, depth=FACE_Z):
    return ((x - PHOTO_CENTER_X) * SCALE, -depth, -(y - HANGING_START_Y) * SCALE)


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


brass = material('Unity medal · Aged brass edge', (.40, .25, .075), .46, .62)
printed = material('Unity medal · Original photographed relief', (1, 1, 1), .6, .18)
image = bpy.data.images.load(str(TEXTURE), check_existing=False)
image.colorspace_settings.name = 'sRGB'
image.pack()
node = printed.node_tree.nodes.new('ShaderNodeTexImage')
node.image = image
node.interpolation = 'Linear'
uv = printed.node_tree.nodes.new('ShaderNodeUVMap')
uv.uv_map = 'SourceUV'
shader = printed.node_tree.nodes.get('Principled BSDF')
printed.node_tree.links.new(uv.outputs['UV'], node.inputs['Vector'])
printed.node_tree.links.new(node.outputs['Color'], shader.inputs['Base Color'])
# Modest emission retains the photographed detail in the warm night setup.
printed.node_tree.links.new(node.outputs['Color'], shader.inputs['Emission Color'])
shader.inputs['Emission Strength'].default_value = .055
printed['referencePixelsUnchanged'] = True
printed['sourceSha256'] = hashlib.sha256(TEXTURE.read_bytes()).hexdigest()
ribbon_print = printed.copy()
ribbon_print.name = 'Unity medal · Original Fit India ribbon'
ribbon_shader = ribbon_print.node_tree.nodes.get('Principled BSDF')
ribbon_shader.inputs['Metallic'].default_value = 0
ribbon_shader.inputs['Roughness'].default_value = .94
ribbon_shader.inputs['Emission Strength'].default_value = .025
cloth = material('Unity medal · White ribbon reverse', (.76, .75, .72), .95)
hook_mat = bpy.data.materials.get('Brushed aluminium') or material('Unity medal · Shelf hook', (.42, .44, .43), .42, .75)


def new_mesh(name, vertices, faces, photo_coords=None, mat=printed, bevel=0):
    mesh = bpy.data.meshes.new('medal_1 · ' + name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('medal_1 · ' + name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    obj.data.materials.append(mat)
    if photo_coords:
        layer = mesh.uv_layers.new(name='SourceUV')
        for poly in mesh.polygons:
            for loop_id in poly.loop_indices:
                x, y = photo_coords[mesh.loops[loop_id].vertex_index]
                layer.data[loop_id].uv = (x / PHOTO_W, 1 - y / PHOTO_H)
    if bevel:
        mod = obj.modifiers.new('Small cast metal edge', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.affect = 'EDGES'
        normal = obj.modifiers.new('Weighted cast normals', 'WEIGHTED_NORMAL')
        normal.keep_sharp = True
    return obj


def plaque(name, trace, depth, thickness, bevel=.0006):
    n = len(trace)
    vertices = [point(x, y, depth) for x, y in trace] + [point(x, y, depth - thickness) for x, y in trace]
    # The trace runs clockwise in image coordinates, which faces into the room.
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    obj = new_mesh(name, vertices, faces, trace + trace, bevel=bevel)
    obj.data.materials.append(brass)
    for poly in obj.data.polygons:
        if poly.index > 0:
            poly.material_index = 1
    if obj.modifiers:
        obj.modifiers[0].material = 1
    return obj


# The silhouette follows the medal itself: rounded upper plate, projecting
# statues/temple, wide curved text banner, and the smaller rounded boat panel.
outline = [
    (548, 712), (813, 713), (837, 717), (854, 724), (868, 736),
    (878, 751), (886, 773), (887, 815), (893, 821), (897, 836),
    (903, 846), (912, 864), (916, 886), (913, 913), (911, 934),
    (911, 990), (916, 998), (916, 1025), (924, 1032), (924, 1044),
    (931, 1046), (932, 1099), (931, 1159), (892, 1146),
    (887, 1171), (877, 1185), (862, 1193), (840, 1197),
    (548, 1200), (531, 1195), (519, 1186), (511, 1172), (507, 1154),
    (468, 1163), (466, 1135), (469, 1066), (471, 1046),
    (477, 1040), (481, 1025), (486, 1021), (488, 1004),
    (495, 997), (496, 976), (501, 955), (502, 932),
    (505, 915), (504, 891), (510, 875), (512, 848),
    (515, 835), (513, 815), (513, 765), (515, 742), (521, 725), (533, 717),
]
body = plaque('Traced cast brass body', outline, FACE_Z, THICKNESS)
body['originalPhotoUV'] = True

# Selected relief is shallow physical geometry with exactly the same photo UVs.
# The lettering is never replaced with a font. The raised banner follows the
# original upward curve so it also reads as a cast part from oblique angles.
banner = [(473, 1047), (927, 1047), (929, 1155), (891, 1143),
          (852, 1131), (810, 1123), (765, 1117), (720, 1114),
          (679, 1116), (633, 1122), (588, 1133), (544, 1144), (471, 1159)]
plaque('Raised Kashmir to Kanyakumari banner', banner, FACE_Z + .0019, .0024, .00035)
mountains = [(633, 886), (649, 863), (674, 837), (694, 833), (718, 850),
             (739, 886), (769, 887), (794, 872), (813, 882), (833, 921),
             (851, 950), (860, 974), (834, 969), (803, 953), (754, 939),
             (707, 910), (675, 899), (651, 919)]
plaque('Shallow mountain relief', mountains, FACE_Z + .0009, .0011, .0002)


def ring_trace(name, outer, inner, depth, thickness=.002):
    n = len(outer)
    if len(inner) != n:
        raise RuntimeError('Eyelet trace mismatch')
    vertices = [point(x, y, depth) for x, y in outer + inner]
    vertices += [point(x, y, depth - thickness) for x, y in outer + inner]
    faces = []
    for i in range(n):
        q = (i + 1) % n
        faces.extend([(i, i + n, q + n, q), (i, q, q + 2 * n, i + 2 * n),
                      (i + n, i + 3 * n, q + 3 * n, q + n),
                      (i + 2 * n, q + 2 * n, q + 3 * n, i + 3 * n)])
    obj = new_mesh(name, vertices, faces, outer + inner + outer + inner)
    obj.data.materials.append(brass)
    for poly in obj.data.polygons:
        if poly.index % 4:
            poly.material_index = 1
    return obj


eyelet_outer = [(595, 663), (798, 663), (808, 669), (814, 684),
                (813, 707), (584, 707), (578, 696), (581, 675)]
eyelet_inner = [(601, 674), (795, 674), (799, 680), (800, 691),
                (797, 698), (600, 697), (593, 691), (594, 681)]
ring_trace('Open rectangular ribbon eyelet', eyelet_outer, eyelet_inner, FACE_Z + .0004, .0045)
for number, (cx, cy, radius) in enumerate([(652, 994, 38), (769, 994, 38)], 1):
    outer = [(cx + math.cos(t * math.tau / 40) * radius, cy + math.sin(t * math.tau / 40) * radius) for t in range(40)]
    inner = [(cx + math.cos(t * math.tau / 40) * (radius - 4), cy + math.sin(t * math.tau / 40) * (radius - 4)) for t in range(40)]
    ring_trace('Embossed bicycle wheel ' + str(number), outer, inner, FACE_Z + .0014, .0016)

# The photographed Fit India print runs down a narrow cloth strip. Vary depth
# along its length and across its width to form a soft ribbon rather than a box.
ribbon_rows = [(225, 598, 773), (255, 597, 777), (290, 596, 772),
               (320, 596, 772), (350, 596, 770), (375, 596, 767),
               (390, 596, 766), (415, 598, 768), (440, 600, 771),
               (470, 600, 777), (500, 600, 782), (525, 600, 786),
               (540, 600, 787), (562, 599, 790), (580, 601, 791),
               (635, 603, 792), (662, 604, 792), (677, 604, 792),
               (680, 605, 791)]
vertices, uv_coords = [], []
columns = 8
for row, (py, left, right) in enumerate(ribbon_rows):
    t = row / (len(ribbon_rows) - 1)
    for column in range(columns + 1):
        u = column / columns
        px = left + (right - left) * u
        depth = FACE_Z + .004 + math.sin(t * math.tau) * .002 + math.sin(u * math.pi) * .0012
        if py >= 677:
            depth -= (py - 677) / 15 * .0015
        vertices.append(point(px, py, depth)); uv_coords.append((px, py))
faces = []
for row in range(len(ribbon_rows) - 1):
    for column in range(columns):
        a = row * (columns + 1) + column
        faces.append((a + columns + 1, a + columns + 2, a + 1, a))
ribbon = new_mesh('Photographed Fit India cloth ribbon', vertices, faces, uv_coords, ribbon_print)
for poly in ribbon.data.polygons:
    poly.use_smooth = True
solid = ribbon.modifiers.new('Woven cloth thickness', 'SOLIDIFY'); solid.thickness = .00065
ribbon['originalPhotoUV'] = True

# A continuous cloth loop passes over the central shelf edge and returns
# behind the printed front. A small bent metal hook supports that loop.
cross_sections = [(0, .042), (.011, .036), (.014, .016), (.010, -.018),
                  (-.002, -.026), (-.047, -.021), (-.135, .035)]
vertices = []
for height, depth in cross_sections:
    vertices += [(-.024, -depth, height), (.028, -depth, height)]
faces = [(2*i, 2*i+1, 2*i+3, 2*i+2) for i in range(len(cross_sections)-1)]
loop = new_mesh('Cloth loop over shelf', vertices, faces, mat=cloth)
solid = loop.modifiers.new('Loop fabric thickness', 'SOLIDIFY'); solid.thickness = .0007
for poly in loop.data.polygons:
    poly.use_smooth = True

curve = bpy.data.curves.new('medal_1 shelf hook', 'CURVE')
curve.dimensions = '3D';curve.resolution_u = 4;curve.bevel_depth = .0024;curve.bevel_resolution = 2
spline = curve.splines.new('POLY')
hook_points = [(0, .016, -.037), (0, .016, .016), (0, .009, .026), (0, -.032, .026)]
spline.points.add(len(hook_points)-1)
for datum, (x, height, depth) in zip(spline.points, hook_points):
    datum.co = (x, -depth, height, 1)
hook = bpy.data.objects.new('medal_1 · Attached shelf hook', curve)
bpy.context.scene.collection.objects.link(hook);hook.parent=root;curve.materials.append(hook_mat)

bpy.context.view_layer.update()
if snapshot() != before:
    raise RuntimeError('An unrelated desk object changed.')
if bpy.data.objects.get('medal_2') or bpy.data.objects.get('medal_3'):
    raise RuntimeError('Generic medal roots remain.')
web = lambda p: (p.x, p.z, -p.y)
points = [web(obj.matrix_world @ v.co) for obj in root.children_recursive if obj.type == 'MESH' for v in obj.data.vertices]
bounds = [[round(fn(p[i] for p in points), 6) for i in range(3)] for fn in (min, max)]
screen = bpy.data.objects['monitor_screen']
screen_top = max((screen.matrix_world @ v.co).z for v in screen.data.vertices)
if bounds[0][1] <= screen_top + .065:
    raise RuntimeError('The medal does not clear the monitor screen.')
bpy.context.scene['medalAssetRevision'] = 'ride-for-unity-supplied-photo-v1'
bpy.ops.file.pack_all()
candidate = OUT / 'workspace-ride-for-unity-medal.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))
report = {
    'sourceSha256': source_hash, 'candidateSha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
    'textureSha256': hashlib.sha256(TEXTURE.read_bytes()).hexdigest(), 'textureSize': list(image.size),
    'photoPixelsEdited': False, 'mappedFromUnchangedFullImage': True,
    'interactiveRoot': root.name, 'removedRoots': ['medal_2', 'medal_3'],
    'unrelatedObjectCount': len(before), 'unrelatedObjectsUnchanged': snapshot() == before,
    'webRoot': list(web(root.matrix_world.translation)), 'webBounds': bounds,
    'bodyThickness': THICKNESS, 'bodyWidth': (max(x for x,y in outline)-min(x for x,y in outline))*SCALE,
    'bodyHeight': (max(y for x,y in outline)-min(y for x,y in outline))*SCALE,
    'monitorScreenClearance': round(bounds[0][1]-screen_top, 6),
    'medalFamilyCount': sum(obj.type=='EMPTY' and obj.name in {'medal_1','medal_2','medal_3'} for obj in bpy.context.scene.objects),
    'newObjects': [obj.name for obj in root.children_recursive],
}
(OUT / 'application.json').write_text(json.dumps(report, indent=2) + '\n')
print('UNITY_MEDAL_CANDIDATE', json.dumps(report), flush=True)
