"""Resize and place the existing certificate to the right of the pegboard.

Only the certificate root transform changes. This script writes a review
candidate, preserving every original mesh, material, light and unrelated pose.
"""
import hashlib
import json
import math
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
OUT = ROOT / 'artifacts/workspace/certificate-frame/right-placement'
OUT.mkdir(parents=True, exist_ok=True)
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
backup = OUT / f'source-before-placement-{source_hash[:12]}.blend'
if not backup.exists():
    shutil.copy2(SOURCE, backup)
bpy.ops.wm.open_mainfile(filepath=str(backup))
bpy.context.view_layer.update()
root = bpy.data.objects.get('certificate_iitg')
if not root:
    raise RuntimeError('The current saved scene has no certificate root.')
family = {root.name, *(obj.name for obj in root.children_recursive)}


def poses():
    return {obj.name: [list(row) for row in obj.matrix_world]
            for obj in bpy.context.scene.objects if obj.name not in family}


def geometry():
    return {obj.name: hashlib.sha256(repr((
                [tuple(v.co) for v in obj.data.vertices],
                [tuple(p.vertices) for p in obj.data.polygons],
                [slot.material.name if slot.material else None for slot in obj.material_slots]
            )).encode()).hexdigest()
            for obj in bpy.context.scene.objects if obj.type == 'MESH'}


poses_before, meshes_before = poses(), geometry()
old_transform = [list(row) for row in root.matrix_world]
root.location = (-.20, 2.239, 2.9825)
root.rotation_euler = (0, 0, math.radians(45))
root.scale = (.75, .75, .75)
bpy.context.view_layer.update()
if poses_before != poses() or meshes_before != geometry():
    raise RuntimeError('Geometry, materials, or an unrelated transform changed.')
web = lambda p: (p.x, p.z, -p.y)


def bounds(objects):
    points = [web(obj.matrix_world @ vertex.co)
              for obj in objects if obj.type == 'MESH' for vertex in obj.data.vertices]
    return [[round(fn(p[i] for p in points), 6) for i in range(3)] for fn in (min, max)]


frame_bounds = bounds(root.children_recursive)
pegboard = bpy.data.objects['Pegboard slots']
pegboard_bounds = bounds([pegboard])
frame_y = (frame_bounds[0][1] + frame_bounds[1][1]) / 2
board_y = (pegboard_bounds[0][1] + pegboard_bounds[1][1]) / 2
gap = frame_bounds[0][0] - pegboard_bounds[1][0]
if gap < .05 or abs(frame_y - board_y) > .003 or frame_bounds[1][0] > -.005:
    raise RuntimeError('The frame does not clear the pegboard/corner or align vertically.')
bpy.context.scene['certificateAssetRevision'] = 'iitg-degree-right-of-pegboard-v2'
candidate = OUT / 'workspace-certificate-right.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))
report = {
    'sourceSha256': source_hash,
    'candidateSha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
    'interactiveRoot': root.name,
    'oldTransformBlender': old_transform,
    'newTransformBlender': [list(row) for row in root.matrix_world],
    'webCenter': list(web(root.location)),
    'uniformScale': .75,
    'outerDimensions': [.654 * .75, .8799666283084006 * .75, .042 * .75],
    'frameBounds': frame_bounds,
    'pegboardBounds': pegboard_bounds,
    'pegboardHorizontalGap': round(gap, 6),
    'verticalCenterDifference': round(frame_y - board_y, 6),
    'unrelatedObjectCount': len(poses_before),
    'unrelatedTransformsUnchanged': poses_before == poses(),
    'allGeometryAndMaterialAssignmentsUnchanged': meshes_before == geometry(),
    'meshCount': len(meshes_before),
}
(OUT / 'application.json').write_text(json.dumps(report, indent=2) + '\n')
print('CERTIFICATE_RIGHT_CANDIDATE', json.dumps(report), flush=True)
