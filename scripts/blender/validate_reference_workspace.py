"""Measure support contacts and mesh intersections on the editable candidate."""
import bpy
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'artifacts/workspace/reference-refinement'
bpy.ops.wm.open_mainfile(filepath=str(ART / 'workspace-refined.blend'))
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()

def members(name):
    root = bpy.data.objects[name]
    return [o for o in [root] + list(root.children_recursive) if o.type in {'MESH', 'CURVE', 'FONT'}]

def surface(objects):
    vertices, faces = [], []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        offset = len(vertices)
        vertices.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
        faces.extend([index + offset for index in poly.vertices] for poly in mesh.polygons)
        evaluated.to_mesh_clear()
    return BVHTree.FromPolygons(vertices, faces), vertices

cache = {}
def geometry(name):
    if name not in cache:
        cache[name] = surface(members(name))
    return cache[name]

checks = []
for a, b in [('monitor', 'workspace_left_wing'), ('monitor', 'workspace_right_wing'),
             ('trophy_1', 'plant_2'), ('trophy_2', 'plant_2'), ('trophy_1', 'trophy_2'),
             ('trophy_1', 'window'), ('trophy_2', 'window'),
             ('plant_2', 'window'),
             ('controller', 'laptop'), ('controller_black', 'laptop'), ('monitor', 'laptop')]:
    intersections = len(geometry(a)[0].overlap(geometry(b)[0]))
    checks.append({'check': 'mesh intersection', 'objects': [a, b], 'crossingFaces': intersections, 'pass': intersections == 0})

for name in ['monitor', 'controller', 'controller_black', 'trophy_1', 'trophy_2', 'speaker', 'books', 'pen_pot', 'chair']:
    objects = members(name)
    tree, points = surface(objects)
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    base = Vector(((low.x + high.x)/2, (low.y + high.y)/2, low.z))
    # Check the shelf/desktop directly below the base, excluding this assembly.
    support, _ = surface([o for o in bpy.context.scene.objects if o.type == 'MESH' and o not in objects and not o.hide_render])
    position, normal, index, distance = support.ray_cast(base + Vector((0, 0, .004)), Vector((0, 0, -1)), .2)
    gap = low.z-position.z if position is not None else None
    checks.append({'check': 'support contact', 'object': name, 'gap': round(gap, 5) if gap is not None else None,
                   'pass': gap is not None and -.006 <= gap <= .015})

names = set(bpy.data.objects.keys())
checks.append({'check': 'award object count', 'pass': {'trophy_1','trophy_2','medal_1','medal_2','medal_3'} <= names and 'trophy_3' not in names})

# The removable cover must clear the tray before it slides toward the visitor.
lid=bpy.data.objects['figma_lid'];position=lid.location.copy()
cover_members=set(members('figma_lid'))
stationary=[o for o in members('workspace_left_wing') if o not in cover_members]
stationary_surface=surface(stationary)[0]
for phase in [index/100 for index in range(101)]:
    lid.location=position.copy()
    lid.location.z+=min(1,phase/.65)*lid.get('openingDistance',.129)
    fraction=max(0,min(1,(phase-.68)/.32));reveal=fraction*fraction*(3-2*fraction)
    lid.location.y-=reveal*lid.get('openingForward',.22)
    bpy.context.view_layer.update()
    count=len(surface(list(cover_members))[0].overlap(stationary_surface))
    checks.append({'check':'cover opening clearance','phase':phase,'crossingFaces':count,'pass':count==0})
lid.location=position;bpy.context.view_layer.update()
report = {'checks': checks, 'passed': all(check['pass'] for check in checks)}
(ART / 'geometry-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print('GEOMETRY_VALIDATION', json.dumps({'passed':report['passed'],'checks':len(checks),'failures':[check for check in checks if not check['pass']]}), flush=True)
if not report['passed']:
    raise RuntimeError('Geometry QA failed; inspect geometry-validation.json before exporting.')
