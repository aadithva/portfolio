"""Inspect JonasDichelle's supplied original without changing the room master."""
import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/workspace/cat'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT / 'source/cat.blend'), load_ui=False, use_scripts=False)
report = {
    'objects': [{
        'name': o.name, 'type': o.type,
        'dimensions': list(o.dimensions),
        'vertices': len(o.data.vertices) if o.type == 'MESH' else None,
        'vertexGroups': [g.name for g in o.vertex_groups] if o.type == 'MESH' else [],
        'modifiers': [m.type for m in o.modifiers],
        'bones': [b.name for b in o.data.bones] if o.type == 'ARMATURE' else [],
    } for o in bpy.data.objects],
    'actions': [{'name': a.name, 'range': list(a.frame_range)} for a in bpy.data.actions],
    'images': [{'name': i.name, 'path': i.filepath, 'packed': bool(i.packed_file)} for i in bpy.data.images],
    'materials': [{'name': m.name, 'nodes': [(n.name, n.type) for n in m.node_tree.nodes] if m.node_tree else []} for m in bpy.data.materials],
    'rig': [{'name': p.name, 'head': list(p.bone.head_local), 'tail': list(p.bone.tail_local), 'parent': p.parent.name if p.parent else None,
             'constraints': [{'type': c.type, 'name': c.name, 'subtarget': getattr(c, 'subtarget', ''), 'chain': getattr(c, 'chain_count', None)} for c in p.constraints]}
            for p in bpy.data.objects['Armature'].pose.bones],
    'scene': {'fps': bpy.context.scene.render.fps, 'frame': bpy.context.scene.frame_current},
    'materialImages': {m.name: [(n.name, n.image.name if n.image else None) for n in m.node_tree.nodes if n.type == 'TEX_IMAGE'] for m in bpy.data.materials if m.node_tree},
    'nla': [{'name': t.name, 'strips': [(s.name, s.action.name, s.frame_start, s.frame_end) for s in t.strips]} for t in bpy.data.objects['Armature'].animation_data.nla_tracks],
}
(OUT / 'inspection.json').write_text(json.dumps(report, indent=2))
print('Inspection saved:', OUT / 'inspection.json')
