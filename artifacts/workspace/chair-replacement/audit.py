import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('/Users/aadith/Projects/Portfolio/Website')
OUT=ROOT/'artifacts/workspace/chair-replacement'
def desc(obj):
    corners=[obj.matrix_world@Vector(c) for c in obj.bound_box] if obj.type=='MESH' else []
    return {'name':obj.name,'type':obj.type,'parent':obj.parent.name if obj.parent else None,'position':list(obj.matrix_world.translation),'rotation':list(obj.rotation_euler),'dimensions':list(obj.dimensions),'bounds':[[min(p[i] for p in corners) for i in range(3)],[max(p[i] for p in corners) for i in range(3)]] if corners else None,'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons) if obj.type=='MESH' else None,'materials':[m.name if m else None for m in obj.data.materials] if obj.type=='MESH' else []}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts/workspace/workspace.blend'))
bpy.context.view_layer.update()
chair=bpy.data.objects['chair']
report={'existing':[desc(o) for o in [chair,*chair.children_recursive]],'desk':[desc(o) for o in bpy.context.scene.objects if any(s in o.name.lower() for s in ['desktop','tabletop'])],'camera':desc(bpy.context.scene.camera)}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OUT/'source/source/OfficeChair.fbx'))
bpy.context.view_layer.update()
report['imported']=[desc(o) for o in bpy.context.scene.objects]
report['materials']=[{'name':m.name,'nodes':[(n.name,n.type,n.image.filepath if n.type=='TEX_IMAGE' and n.image else None) for n in m.node_tree.nodes] if m.use_nodes else []} for m in bpy.data.materials]
(OUT/'audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
