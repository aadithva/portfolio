"""Validate an enlarged hutch without saving or exporting its Blender source.

Blender --background --python scripts/blender/validate_shelf_fit.py --
  --source artifacts/workspace/shelf-fit/workspace-shelf-fit.blend
  --output artifacts/workspace/shelf-fit/geometry-validation.json
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=ROOT / 'artifacts/workspace/shelf-fit/workspace-shelf-fit.blend')
parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/workspace/shelf-fit/geometry-validation.json')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
source = args.source.resolve()
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
checks = []


def web(point):
    return Vector((point.x, point.z, -point.y))


def blender(point):
    return Vector((point[0], -point[2], point[1]))


def members(name):
    root = bpy.data.objects[name]
    return [obj for obj in [root, *root.children_recursive] if obj.type in {'MESH', 'CURVE', 'FONT'}]


def surface(objects):
    vertices, faces = [], []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            offset = len(vertices)
            vertices.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
            faces.extend(tuple(offset + index for index in face.vertices) for face in mesh.polygons)
        finally:
            evaluated.to_mesh_clear()
    if not faces:
        raise ValueError('An expected mesh assembly has no surfaces')
    return BVHTree.FromPolygons(vertices, faces), vertices


cache = {}


def geometry(name):
    if name not in cache:
        cache[name] = surface(members(name))
    return cache[name]


def bounds(points):
    points = [web(point) for point in points]
    return [Vector(tuple(min(point[i] for point in points) for i in range(3))),
            Vector(tuple(max(point[i] for point in points) for i in range(3)))]


def intersection(a, b):
    count = len(geometry(a)[0].overlap(geometry(b)[0]))
    checks.append({'check': 'mesh intersection', 'objects': [a, b],
                   'crossingFaces': count, 'pass': count == 0})


def support_contact(name):
    objects = set(members(name))
    low, high = bounds(geometry(name)[1])
    point = blender(((low.x + high.x) / 2, low.y + .004, (low.z + high.z) / 2))
    other = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj not in objects and not obj.hide_render]
    hit, _, _, _ = surface(other)[0].ray_cast(point, Vector((0, 0, -1)), .2)
    gap = low.y - hit.z if hit is not None else None
    checks.append({'check': 'support contact', 'object': name,
                   'gap': round(gap, 6) if gap is not None else None,
                   'pass': gap is not None and -.006 <= gap <= .015})


# Retain the original eleven collision checks and nine support contacts.
original_pairs = [
    ('monitor', 'workspace_left_wing'), ('monitor', 'workspace_right_wing'),
    ('trophy_1', 'plant_2'), ('trophy_2', 'plant_2'), ('trophy_1', 'trophy_2'),
    ('trophy_1', 'window'), ('trophy_2', 'window'), ('plant_2', 'window'),
    ('controller', 'laptop'), ('controller_black', 'laptop'), ('monitor', 'laptop'),
]
for pair in original_pairs:
    intersection(*pair)
for name in ['monitor', 'controller', 'controller_black', 'trophy_1', 'trophy_2', 'speaker', 'books', 'pen_pot', 'chair']:
    support_contact(name)

names = set(bpy.data.objects.keys())
checks.append({'check': 'award object count',
               'pass': {'trophy_1', 'trophy_2', 'medal_1', 'medal_2', 'medal_3'} <= names and 'trophy_3' not in names})

# Keep the full lid motion test, including its tray and both shelf uprights.
lid = bpy.data.objects['figma_lid']
original_position = lid.location.copy()
cover_members = set(members('figma_lid'))
stationary = surface([obj for obj in members('workspace_left_wing') if obj not in cover_members])[0]
try:
    for step in range(101):
        phase = step / 100
        lid.location = original_position.copy()
        lid.location.z += min(1, phase / .65) * lid.get('openingDistance', .129)
        fraction = max(0, min(1, (phase - .68) / .32))
        lid.location.y -= fraction * fraction * (3 - 2 * fraction) * lid.get('openingForward', .22)
        bpy.context.view_layer.update()
        count = len(surface(cover_members)[0].overlap(stationary))
        checks.append({'check': 'cover opening clearance', 'phase': phase,
                       'crossingFaces': count, 'pass': count == 0})
finally:
    lid.location = original_position
    bpy.context.view_layer.update()

for name in ['pen_pot', 'controller', 'controller_black', 'laptop']:
    for side in ['left', 'right']:
        intersection(name, 'workspace_' + side + '_wing')
for name in ['figma', 'plant_1', 'plant_2', 'Small aloe', 'Tiny jade plant']:
    if name in names:
        support_contact(name)


def components(mesh):
    adjacency = [[] for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].append(b)
        adjacency[b].append(a)
    seen = set()
    for index in range(len(mesh.vertices)):
        if index in seen:
            continue
        stack, part = [index], []
        seen.add(index)
        while stack:
            vertex = stack.pop()
            part.append(vertex)
            for neighbor in adjacency[vertex]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        yield part


# The hutch roots also contain the pegboard/window. Measure only the cabinet frame.
frames, front_tips = {}, []
for side in ['left', 'right']:
    frame = bpy.data.objects['workspace_' + side + '_wing · Porcelain edges']
    frames[side] = surface([frame])[0]
    side_parts = []
    for indices in components(frame.data):
        points = [frame.matrix_world @ frame.data.vertices[index].co for index in indices]
        low, high = bounds(points)
        if low.y < 1.4 and .8 < high.y - low.y < 1.5:
            side_parts.append((points, low, high))
    if len(side_parts) != 2:
        checks.append({'check': 'hutch support panel identification', 'side': side,
                       'panels': len(side_parts), 'pass': False})
        continue
    inner = min(side_parts, key=lambda part: abs((part[1].x + part[2].x) / 2))
    front_tips.append(inner[2].z)
    excluded = set(members('workspace_' + side + '_wing'))
    support_tree = surface([obj for obj in bpy.context.scene.objects
                            if obj.type == 'MESH' and obj not in excluded and not obj.hide_render])[0]
    samples = []
    for points, low, _ in side_parts:
        for world_point in points:
            point = web(world_point)
            if point.y > low.y + .001:
                continue
            hit, _, _, _ = support_tree.ray_cast(blender((point.x, point.y + .06, point.z)), Vector((0, 0, -1)), .12)
            gap = point.y - hit.z if hit is not None else None
            # Existing side panels seat .012 units into the desktop's edge thickness.
            valid = gap is not None and -.018 <= gap <= .01
            samples.append({'position': [round(v, 6) for v in point],
                            'gap': round(gap, 6) if gap is not None else None, 'pass': valid})
    checks.append({'check': 'hutch base corner supports', 'side': side,
                   'samples': samples, 'pass': bool(samples) and all(sample['pass'] for sample in samples)})

housing_low, housing_high = bounds(geometry('Monitor outer housing')[1])
screen_low, screen_high = bounds(geometry('monitor_screen')[1])
screen_front = (screen_low.z + screen_high.z) / 2
profile = []
for yi in range(5):
    y = housing_low.y + .008 + (housing_high.y - housing_low.y - .016) * yi / 4
    for zi in range(7):
        z = housing_low.z + (screen_front - housing_low.z) * zi / 6
        hits = {}
        for side, sign in [('left', -1), ('right', 1)]:
            hit, _, _, _ = frames[side].ray_cast(blender((0, y, z)), Vector((sign, 0, 0)), 2)
            hits[side] = abs(hit.x) if hit is not None else None
        width = sum(hits.values()) if all(value is not None for value in hits.values()) else None
        profile.append({'y': round(y, 6), 'z': round(z, 6),
                        'width': round(width, 6) if width is not None else None})
minimum_opening = min((sample['width'] for sample in profile if sample['width'] is not None), default=None)
checks.append({'check': 'monitor fits hutch opening', 'housingWidth': round(housing_high.x - housing_low.x, 6),
               'minimumOpening': minimum_opening, 'requiredOpening': 1.2, 'samples': profile,
               'pass': minimum_opening is not None and minimum_opening >= 1.2})
recess = min(front_tips) - screen_front if len(front_tips) == 2 else None
checks.append({'check': 'monitor sits inside hutch', 'screenFrontZ': round(screen_front, 6),
               'recessDepth': round(recess, 6) if recess is not None else None,
               'pass': recess is not None and recess >= .04})

report = {'source': str(source), 'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'checks': checks, 'passed': all(check['pass'] for check in checks)}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2) + '\n')
print('SHELF_FIT_VALIDATION', json.dumps({'passed': report['passed'], 'checks': len(checks),
                                       'failures': [check for check in checks if not check['pass']]}), flush=True)
if not report['passed']:
    raise RuntimeError('Shelf fit validation failed; inspect the JSON report.')
