"""Widen the saved balcony away from the desk, retaining hardware thickness."""
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
OUT = ROOT / 'artifacts/workspace/balcony-width'
CANDIDATE = OUT / 'workspace-wide-balcony.blend'
REPORT = OUT / 'application.json'
C = Vector((0, 2.55, 0))
T = Vector((-1/math.sqrt(2), -1/math.sqrt(2), 0))
N = Vector((1/math.sqrt(2), -1/math.sqrt(2), 0))
START, OLD_END, NEW_END, TOP = 2.1, 4.4, 6.1, 3.86
EXTRA = NEW_END-OLD_END


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if '--promote' in sys.argv:
    report = json.loads(REPORT.read_text())
    if digest(SOURCE) != report['sourceSha256'] or digest(CANDIDATE) != report['candidateSha256']:
        raise RuntimeError('Master or candidate changed after review.')
    shutil.copy2(CANDIDATE, SOURCE)
    print('BALCONY_WIDTH_PROMOTED', flush=True)
    raise SystemExit(0)

OUT.mkdir(parents=True, exist_ok=True)
source_hash = digest(SOURCE)
backup = OUT / f'source-before-width-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.view_layer.update()
door = bpy.data.objects['balcony_door']
exterior = bpy.data.objects['balcony_exterior']
if abs(door.get('openingWidth', 0)-2.3) > .001:
    raise RuntimeError('Expected the original 2.3-unit balcony width.')
walls = [bpy.data.objects[n] for n in ['_static · Limewashed plaster', '_static · Warm powder-coated white']]
changed = {o.name for root in [door, exterior] for o in [root, *root.children_recursive]} | {o.name for o in walls}


def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.name in changed:
            continue
        geometry = [tuple(v.co) for v in obj.data.vertices] if obj.type == 'MESH' else []
        light = (obj.data.energy, tuple(obj.data.color)) if obj.type == 'LIGHT' else None
        result[obj.name] = hashlib.sha256(repr((list(map(tuple,obj.matrix_world)), geometry,
            [s.material.name if s.material else None for s in obj.material_slots], light)).encode()).hexdigest()
    return result


def span(obj):
    values = [(obj.matrix_world @ v.co-C).dot(T) for v in obj.data.vertices]
    return min(values), max(values)


def stretch(obj, left_shift, right_shift):
    low, high = span(obj)
    inverse = obj.matrix_world.inverted()
    for v in obj.data.vertices:
        p = obj.matrix_world @ v.co
        fraction = ((p-C).dot(T)-low)/(high-low)
        v.co = inverse @ (p + T*(left_shift+(right_shift-left_shift)*fraction))
    obj.data.update()


before = snapshot()
# Stretch only horizontal members and glass. Translate the slender stiles,
# seals and handles to their new positions so their cross-sections stay intact.
for obj in door.children:
    if obj.type != 'MESH':
        continue
    if 'inner jamb' in obj.name:
        continue
    stretch(obj, EXTRA if 'outer jamb' in obj.name else 0, EXTRA)
for name, base_shift in [('balcony_door_fixed_panel',0), ('balcony_door_sliding_panel',EXTRA/2)]:
    panel = bpy.data.objects[name]
    meshes = [o for o in panel.children_recursive if o.type == 'MESH']
    low = min(span(o)[0] for o in meshes)
    high = max(span(o)[1] for o in meshes)
    center = (low+high)/2
    for obj in meshes:
        a,b = span(obj)
        if b-a > .5:
            stretch(obj,base_shift,base_shift+EXTRA/2)
        else:
            shift = base_shift+(EXTRA/2 if (a+b)/2 > center else 0)
            stretch(obj,shift,shift)

balusters = []
for obj in exterior.children_recursive:
    if obj.type != 'MESH':
        continue
    if 'railing baluster' in obj.name:
        balusters.append(obj)
        continue
    stretch(obj,0,EXTRA)
# Continue the original railing pitch rather than stretching the gaps.
balusters.sort(key=lambda obj: sum(span(obj)))
count = 15
for index in range(count):
    if index < len(balusters):
        obj = balusters[index]
    else:
        obj = balusters[0].copy()
        obj.data = balusters[0].data.copy()
        bpy.context.scene.collection.objects.link(obj)
        changed.add(obj.name)
    center = sum(span(obj))/2
    destination = START+.05+index*(NEW_END-START-.1)/(count-1)
    stretch(obj,destination-center,destination-center)

# Cut the complete enlarged opening, overlapping the existing aperture.
bpy.ops.mesh.primitive_cube_add(size=1)
cutter = bpy.context.object
cutter.name = 'Temporary widened balcony aperture'
basis = Matrix((T,-N,Vector((0,0,1)))).transposed().to_4x4()
cutter.matrix_world = Matrix.Translation(C+T*((START+NEW_END)/2)+N*.04+Vector((0,0,(TOP-.12)/2))) @ basis @ Matrix.Diagonal(Vector((NEW_END-START,.65,TOP+.12,1)))
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for obj in walls:
    modifier = obj.modifiers.new('Wider balcony aperture','BOOLEAN')
    modifier.operation = 'DIFFERENCE'
    modifier.solver = 'FLOAT'
    modifier.object = cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(cutter,do_unlink=True)
bpy.context.view_layer.update()
samples = []
for s in [2.25,3.25,4.3,4.6,5.2,5.95]:
    for height in [.14,1.8,3.6]:
        for obj in walls:
            inverse = obj.matrix_world.inverted()
            origin = inverse @ (C+T*s+N*.5+Vector((0,0,height)))
            direction = inverse.to_3x3() @ -N
            if obj.ray_cast(origin,direction,distance=1)[0]:
                raise RuntimeError(f'Blocked aperture at {s}, {height}: {obj.name}')
        samples.append([s,height])
if snapshot() != before:
    raise RuntimeError('Unrelated scene objects changed.')
door['openingWidth'] = NEW_END-START
door['widthExtensionDirection'] = 'Away from desk; desk-side jamb retained'
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report = {'sourceSha256':source_hash,'candidateSha256':digest(CANDIDATE),
          'backup':str(backup.relative_to(ROOT)), 'oldWidth':OLD_END-START,
          'newWidth':NEW_END-START,'deskSideEdge':START,'farEdge':NEW_END,
          'height':TOP,'railingBalusters':count,'apertureClearSamples':samples,
          'unrelatedObjectsUnchanged':True}
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print('BALCONY_WIDTH_CANDIDATE',json.dumps(report),flush=True)
