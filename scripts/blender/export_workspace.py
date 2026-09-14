"""Export the saved, editable corner scene without rebuilding or saving over it."""
import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/workspace/workspace.blend'
OUTPUT = ROOT / 'public/models/workspace.glb'
MANIFEST = OUTPUT.with_suffix('.manifest.json')

bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
for name in ('workspace_left_wing', 'workspace_right_wing', 'monitor_screen'):
    if name not in bpy.data.objects:
        raise RuntimeError(f'Missing corner-scene object: {name}')

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type in {'MESH', 'EMPTY', 'CURVE', 'FONT'}:
        obj.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=str(OUTPUT), export_format='GLB', use_selection=True,
    export_apply=True, export_yup=True, export_extras=True,
    export_cameras=False, export_lights=False, export_materials='EXPORT',
    export_texcoords=True, export_normals=True, export_image_format='AUTO',
    export_unused_images=False,
)

manifest = json.loads(MANIFEST.read_text())
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
manifest.update(
    source=str(SOURCE.relative_to(ROOT)),
    revision=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()[:12],
    bytes=OUTPUT.stat().st_size,
    meshCount=len(meshes),
    triangles=sum(len(p.vertices) - 2 for obj in meshes for p in obj.data.polygons),
    interactiveRoots={
        obj.name: [round(v, 4) for v in (
            obj.matrix_world.translation.x,
            obj.matrix_world.translation.z,
            -obj.matrix_world.translation.y,
        )]
        for obj in bpy.context.scene.objects
        if obj.type == 'EMPTY' and obj.get('interactive')
    },
)
MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Exported saved corner scene: {OUTPUT} ({manifest["bytes"]} bytes)')
