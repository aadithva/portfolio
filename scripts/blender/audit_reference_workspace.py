"""Read source model bounds, component contacts, and authored lights for refinement QA."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/workspace/reference-refinement'
OUT.mkdir(parents=True,exist_ok=True)

def web(v): return [round(v.x,5),round(v.z,5),round(-v.y,5)]
def bounds(objects):
    # Rotated local bounding boxes exaggerate the chair and angled shelf widths.
    pts=[o.matrix_world@v.co for o in objects if o.type=='MESH' for v in o.data.vertices]
    if not pts:return None
    lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
    return {'min':[round(lo.x,5),round(lo.z,5),round(-hi.y,5)],'max':[round(hi.x,5),round(hi.z,5),round(-lo.y,5)],'size':[round(hi.x-lo.x,5),round(hi.z-lo.z,5),round(hi.y-lo.y,5)]}
def lights_snapshot():
    return [{'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'matrix':[list(row) for row in o.matrix_world]} for o in bpy.context.scene.objects if o.type=='LIGHT']
def audit(label):
    bpy.context.view_layer.update()
    names=['monitor','monitor_screen','laptop','controller','controller_black','chair','speaker','books','figma','pen_pot','trophy_1','trophy_2','trophy_3','medal_1','medal_2','medal_3','plant_1','plant_2','workspace_left_wing','workspace_right_wing']
    data={'source':bpy.data.filepath,'lights':lights_snapshot(),'groups':{},'meshes':[]}
    for name in names:
        o=bpy.data.objects.get(name)
        if o:data['groups'][name]={'position':web(o.matrix_world.translation),'bounds':bounds([o]+list(o.children_recursive)),'children':[c.name for c in o.children_recursive]}
    for o in bpy.context.scene.objects:
        if o.type=='MESH':data['meshes'].append({'name':o.name,'parent':o.parent.name if o.parent else None,'bounds':bounds([o]),'materials':[m.name if m else None for m in o.data.materials]})
    (OUT/(label+'.json')).write_text(json.dumps(data,indent=2))
    print('AUDIT',label,json.dumps({name:{'position':g['position'],'bounds':g['bounds']} for name,g in data['groups'].items()}))
    return data
if __name__=='__main__':
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts/workspace/workspace.blend'))
    audit('before')
