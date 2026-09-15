"""Relocate the saved bicycle and fit a sliding balcony door to its former wall."""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/workspace/balcony-door'
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
CANDIDATE = OUT / 'workspace-balcony.blend'
REPORT = OUT / 'application.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def web(value):
    return Vector((value[0], -value[2], value[1]))


C = web((0, 0, -2.55))
T = web((-.70710678, 0, .70710678))
N = web((.70710678, 0, .70710678))
U = web((0, 1, 0))
RIGHT_T = web((.70710678, 0, .70710678))
RIGHT_N = web((-.70710678, 0, .70710678))


def family(root):
    return [root] + list(root.children_recursive)


def vertices(objects):
    return [obj.matrix_world @ v.co for obj in objects if obj.type == 'MESH' for v in obj.data.vertices]


def bounds(points, tangent=T, normal=N):
    coordinates = [((p-C).dot(tangent), p.z, (p-C).dot(normal)) for p in points]
    return [[round(fn(p[i] for p in coordinates), 5) for i in range(3)] for fn in (min, max)]


def snapshot(exclude):
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.name in exclude:
            continue
        geometry = [tuple(v.co) for v in obj.data.vertices] if obj.type == 'MESH' else []
        light = (obj.data.type, obj.data.energy, tuple(obj.data.color)) if obj.type == 'LIGHT' else None
        state = (list(map(tuple, obj.matrix_world)), geometry,
                 [s.material.name if s.material else None for s in obj.material_slots], light)
        result[obj.name] = hashlib.sha256(repr(state).encode()).hexdigest()
    return result


def tree(objects):
    verts, faces = [], []
    graph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type not in {'MESH', 'CURVE'}:
            continue
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        offset = len(verts)
        verts.extend(obj.matrix_world @ v.co for v in mesh.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in mesh.polygons)
        evaluated.to_mesh_clear()
    return BVHTree.FromPolygons(verts, faces)


if '--promote' in sys.argv:
    report = json.loads(REPORT.read_text())
    if digest(SOURCE) != report['sourceSha256'] or digest(CANDIDATE) != report['candidateSha256']:
        raise RuntimeError('The master or reviewed candidate changed. Inspect before promoting.')
    shutil.copy2(CANDIDATE, SOURCE)
    print('BALCONY_PROMOTED', SOURCE, flush=True)
    raise SystemExit(0)

OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE if '--inspect-candidate' in sys.argv else SOURCE))
bpy.context.view_layer.update()

if '--inspect' in sys.argv or '--inspect-candidate' in sys.argv:
    origin = C+3.25*T+2*U+2*N
    for _ in range(8):
        hit, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(), origin, -N, distance=6)
        if not hit:
            break
        print('DOOR_RAY', obj.name, 'normal', list(normal), 'point', list(location), flush=True)
        origin = location-.001*N
    for name in ['bicycle', 'bicycle_wall_mount', 'window', 'lamp_1', 'lamp_2', 'lamp_3',
                 'workspace_right_wing', 'chair']:
        obj = bpy.data.objects.get(name)
        if obj:
            print('ROOM_OBJECT', name, 'RIGHT_WALL', bounds(vertices(family(obj)), RIGHT_T, RIGHT_N))
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and (obj.parent is None or obj.name.startswith(('Balcony', 'balcony'))):
            points = vertices([obj])
            if not points:
                continue
            print('STATIC_OBJECT', obj.name, 'LEFT_WALL', bounds(points), 'RIGHT_WALL', bounds(points, RIGHT_T, RIGHT_N))
    raise SystemExit(0)

if bpy.data.objects.get('balcony_door'):
    raise RuntimeError('This scene already contains the balcony door.')
source_hash = digest(SOURCE)
backup = OUT / f'source-before-balcony-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)

bike = bpy.data.objects['bicycle']
mount = bpy.data.objects['bicycle_wall_mount']
walls = [o for o in bpy.context.scene.objects if o.type == 'MESH' and 'Limewashed plaster' in o.name]
# The saved scene batches the baseboards with other white, static geometry. A
# local cutter trims only the doorway rather than reconstructing that mesh.
trim = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.parent is None
        and any(m and m.name == 'Warm powder-coated white' for m in o.data.materials)]
changed = {o.name for root in (bike, mount) for o in family(root)} | {o.name for o in walls+trim}
before = snapshot(changed)
old_origin = bike.matrix_world.translation.copy()
new_origin = C + 3.91*RIGHT_T + .705*RIGHT_N + 2.10*U
# The reference wheel-hook arrangement is perpendicular to the wall. The
# bicycle's existing orientation becomes wall-normal on the opposite wall.
move = Matrix.Translation(new_origin) @ Matrix.Translation(-old_origin)
bike.matrix_world = move @ bike.matrix_world
for obj in list(mount.children_recursive):
    bpy.data.objects.remove(obj, do_unlink=True)
bike['mount'] = 'Reference-style front-wheel hook on the right wall; frame projects into the room'
bpy.context.view_layer.update()

def group(name, parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    return obj


def material(name, color, metal=0, rough=.6, emission=0, alpha=1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metal
    shader.inputs['Roughness'].default_value = rough
    shader.inputs['Alpha'].default_value = alpha
    shader.inputs['Emission Color'].default_value = (*color, 1)
    shader.inputs['Emission Strength'].default_value = emission
    if alpha < 1:
        mat.surface_render_method = 'DITHERED'
    return mat


def point(s, y, n):
    return C + s*T + y*U + n*N


def box(name, position, size, mat, parent=None, bevel=.008, tangent=T, normal=N):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = name
    basis = Matrix((tangent, U.cross(tangent), U)).transposed().to_4x4()
    s, y, n = position
    obj.matrix_world = Matrix.Translation(C+s*tangent+y*U+n*normal) @ basis @ Matrix.Diagonal(Vector((*size, 1)))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.parent = parent
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    return obj


def rack_box(name, position, size, mat, bevel=.008):
    return box('bicycle mount · '+name, position, size, mat, mount, bevel, RIGHT_T, RIGHT_N)


def rack_tube(name, points, radius, mat):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = radius
    data.bevel_resolution = 3
    spline = data.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, (s, y, n) in zip(spline.points, points):
        p.co = (*(C+s*RIGHT_T+y*U+n*RIGHT_N), 1)
    obj = bpy.data.objects.new('bicycle mount · '+name, data)
    bpy.context.collection.objects.link(obj)
    obj.parent = mount
    data.materials.append(mat)
    return obj


steel = bpy.data.materials['Bicycle mount · powder-coated steel']
rubber = bpy.data.materials['Bicycle mount · soft rubber']
silver = bpy.data.materials['Bicycle mount · fasteners']
rack_box('formed wheel-hook backplate', (3.91, 3.11, .093), (.18, .034, .66), steel, .035)
rack_box('lower wheel wall pad', (3.91, 1.22, .090), (.18, .029, .35), rubber, .02)
for y in [2.87, 3.14, 3.37]:
    rack_tube('recessed wall fixing', [(3.91, y, .11), (3.91, y, .119)], .013, silver)
for y in [2.96, 3.05, 3.23]:
    rack_tube('pressed plate chevron', [(3.86, y+.025, .113), (3.91, y, .118), (3.96, y+.025, .113)], .006, steel)
hook = [(3.91, 3.42, .113), (3.91, 3.45, .16), (3.91, 3.44, .24),
        (3.91, 3.39, .285), (3.91, 3.33, .27), (3.91, 3.32, .225)]
rack_tube('steel upper wheel hook', hook, .018, steel)
rack_tube('padded hook sleeve', hook[1:], .027, rubber)


frame = bpy.data.materials['Warm powder-coated white']
aluminum = material('Balcony · brushed track aluminum', (.32, .34, .34), .8, .32)
gasket = material('Balcony · dark rubber seals', (.015, .021, .023), 0, .85)
glass = material('Balcony · clear blue grey glazing', (.23, .34, .39), .1, .18, alpha=.16)
rail = material('Balcony · charcoal railing', (.055, .065, .067), .65, .4)
slab = material('Balcony · exterior stone', (.28, .29, .28), 0, .87)
sky = material('Balcony · night exterior', (.025, .043, .065), 0, 1, emission=.23)
root = group('balcony_door')
root['description'] = 'Two tracked sliding glass panels, open slightly onto a shallow balcony'
root['openingWidth'] = 2.30
root['openingHeight'] = 3.86
exterior = group('balcony_exterior')

# A real floor-to-lintel opening through the consolidated plaster and skirting.
start, end, top = 2.10, 4.40, 3.86
center = (start+end)/2
cutter = box('Temporary balcony aperture', (center, (top-.12)/2, .04),
             (end-start, .65, top+.12), frame, bevel=0)
for obj in walls+trim:
    # The older batched meshes carry mirrored transforms. Normalize their
    # winding in world space before cutting the solid doorway opening.
    obj.data.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    mesh.to_mesh(obj.data)
    mesh.free()
    bpy.context.view_layer.update()
    modifier = obj.modifiers.new('Balcony doorway opening', 'BOOLEAN')
    modifier.operation = 'DIFFERENCE'
    modifier.solver = 'FLOAT'
    modifier.object = cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(cutter, do_unlink=True)
bpy.context.view_layer.update()
for s in [2.3, 3.25, 4.2]:
    for y in [.14, 1.8, 3.6]:
        for obj in walls+trim:
            origin = obj.matrix_world.inverted() @ point(s, y, .5)
            direction = obj.matrix_world.inverted().to_3x3() @ -N
            if obj.ray_cast(origin, direction, distance=1)[0]:
                raise RuntimeError('Plaster or skirting still obstructs the doorway.')

# Slim jambs, two continuous parallel tracks, and a low walk-through threshold.
for s, name in [(start+.045, 'inner jamb'), (end-.045, 'outer jamb')]:
    box('Balcony door · '+name, (s, top/2, .025), (.09, .22, top), frame, root)
box('Balcony door · lintel', (center, top-.05, .025), (end-start, .22, .10), frame, root)
box('Balcony door · threshold', (center, .018, .04), (end-start, .30, .06), aluminum, root, .006)
for n in [-.045, .055]:
    box('Balcony door · lower sliding rail', (center, .061, n), (end-start-.15, .013, .022), aluminum, root, .003)
    box('Balcony door · upper sliding channel', (center, top-.09, n), (end-start-.15, .035, .035), gasket, root, .003)

leaf_width = (end-start-.16)/2+.035
bottom, leaf_top = .075, top-.10
height = leaf_top-bottom
for label, s, n in [('fixed panel', start+.08+leaf_width/2, -.045),
                    ('sliding panel', end-.08-leaf_width/2-.29, .055)]:
    leaf = group('balcony_door_'+label.replace(' ', '_'), root)
    leaf['trackAxis'] = list(T)
    leaf['travel'] = .29 if label == 'sliding panel' else 0
    for side in [-1, 1]:
        x = s+side*(leaf_width/2-.028)
        box('Balcony '+label+' · stile', (x, bottom+height/2, n), (.056, .07, height), frame, leaf, .005)
        box('Balcony '+label+' · vertical glazing seal', (x-side*.035, bottom+height/2, n+.007),
            (.013, .028, height-.09), gasket, leaf, .002)
    for y in [bottom+.037, leaf_top-.03]:
        box('Balcony '+label+' · horizontal frame', (s, y, n), (leaf_width, .07, .065), frame, leaf, .005)
    box('Balcony '+label+' · glass', (s, bottom+height/2, n),
        (leaf_width-.115, .009, height-.12), glass, leaf, .001)
    # A restrained pair of pull handles on the meeting stiles.
    handle_s = s+(leaf_width/2-.03)*(1 if label == 'fixed panel' else -1)
    for y in [1.62, 1.99]:
        box('Balcony '+label+' · handle foot', (handle_s, y, n+.065), (.024, .072, .028), rail, leaf, .006)
    box('Balcony '+label+' · pull handle', (handle_s, 1.805, n+.10), (.029, .028, .40), rail, leaf, .009)

# The shallow exterior and rail make the floor-height opening read as a balcony.
box('Balcony · stone slab', (center, -.09, -.67), (2.48, 1.44, .13), slab, exterior, .012)
box('Balcony · stone edge', (center, -.16, -1.36), (2.48, .08, .17), slab, exterior)
for i in range(9):
    s = start+.05+i*(end-start-.10)/8
    box('Balcony · railing baluster', (s, .85, -1.20), (.028, .035, 1.70), rail, exterior, .006)
box('Balcony · railing handrail', (center, 1.70, -1.20), (2.40, .075, .055), rail, exterior, .014)
box('Balcony · railing lower rail', (center, .18, -1.20), (2.35, .035, .035), rail, exterior, .006)
box('balcony_window_glass', (center, 1.94, -1.60), (2.30, .018, 3.88), sky, exterior, 0)

bpy.context.view_layer.update()
bike_points = vertices(family(bike))
bike_bounds = bounds(bike_points, RIGHT_T, RIGHT_N)
if bike_bounds[0][2] < .095 or bike_bounds[1][0] > 4.47 or bike_bounds[0][1] < 0:
    raise RuntimeError('Bicycle exceeds the right-wall envelope: '+str(bike_bounds))
bike_tree = tree(family(bike))
collisions = {}
for name in ['chair', 'workspace_right_wing', 'window', 'lamp_1', 'lamp_2', 'lamp_3', 'monitor', 'certificate_iitg']:
    obj = bpy.data.objects.get(name)
    if obj:
        collisions[name] = len(bike_tree.overlap(tree(family(obj))))
if any(collisions.values()):
    raise RuntimeError('Bicycle overlaps room objects: '+str(collisions))
after = snapshot(changed | {o.name for parent in (root, exterior, mount) for o in family(parent)})
if before != after:
    raise RuntimeError('Unrelated saved scene objects changed.')

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report = {'sourceSha256': source_hash, 'candidateSha256': digest(CANDIDATE),
          'backup': str(backup.relative_to(ROOT)), 'unrelatedObjectsUnchanged': True,
          'bicycleRightWallBounds': bike_bounds, 'bicycleIntersections': collisions,
          'doorOpening': {'wallSpan': [start, end], 'height': top, 'slidingOffset': .29},
          'bicyclePositionWeb': [new_origin.x, new_origin.z, -new_origin.y]}
REPORT.write_text(json.dumps(report, indent=2)+'\n')
print('BALCONY_CANDIDATE', json.dumps(report), flush=True)

if '--render' in sys.argv:
    scene = bpy.context.scene
    camera = bpy.data.objects.new('Balcony review camera', bpy.data.cameras.new('Balcony review camera'))
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == 'METAL'
    scene.cycles.device = 'GPU'
    scene.render.resolution_percentage = 100
    for name, position, target, size in [
        ('overview', (2.4, 3.7, 5.7), (0, 1.7, -.9), (1440, 1000)),
        ('lamp-wall', (-2.3, 3.4, 5.8), (1.6, 2.0, -.1), (1200, 1100)),
        ('door-detail', (1.0, 2.9, 4.9), (-1.95, 1.85, -.1), (1100, 1200)),
    ]:
        camera.location = web(position)
        camera.rotation_euler = (web(target)-camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera.data.lens = 40
        scene.render.resolution_x, scene.render.resolution_y = size
        scene.render.filepath = str(OUT/(name+'.png'))
        bpy.ops.render.render(write_still=True)
