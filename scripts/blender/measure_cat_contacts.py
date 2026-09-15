"""Measure support surfaces from the current room, in exported Y-up coordinates."""
import bpy
import json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts/workspace/workspace.blend'),use_scripts=False)
deps=bpy.context.evaluated_depsgraph_get()
chair=bpy.data.objects['chair']
def ray(x,y,top=3):
    hit,loc,normal,idx,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x,y,top)),Vector((0,0,-1)))
    return {'point':[loc.x,loc.z,-loc.y],'normal':list(normal),'object':obj.name} if hit else None
report={'chairOrigin':[chair.location.x,chair.location.z,-chair.location.y],
        'chairSamples':[ray(x,y,1.15) for x in [-.65,-.45,-.25,0] for y in [-.1,.1,.3,.5]],
        'deskSamples':[ray(x,y,1.4) for x in [-.4,0,.35,.6,.85] for y in [.85,1,1.15]]}
(ROOT/'artifacts/workspace/cat/contacts.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
