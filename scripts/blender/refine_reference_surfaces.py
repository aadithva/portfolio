"""Reference surface repairs applied after the furniture and props modules."""
import bpy
from mathutils import Vector

def apply_surfaces():
    # Fine-textured ABS broadens the display reflection on the black controller.
    plastic=bpy.data.materials.get('Xbox textured charcoal')
    if plastic:
        plastic.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.62
    window = bpy.data.objects['window']
    pane = bpy.data.objects['window_glass']
    orientation = window.matrix_world.to_quaternion()
    vertices = [pane.matrix_world @ vertex.co for vertex in pane.data.vertices]
    center = sum(vertices, Vector()) / len(vertices)
    local = [orientation.inverted() @ (point-center) for point in vertices]
    width = max(p.x for p in local)-min(p.x for p in local)
    height = max(p.z for p in local)-min(p.z for p in local)
    # Cut the wall behind the existing recess. Moving the entire deep frame
    # forward would obscure shelf objects when viewed from the photo's angle.
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    cutter = bpy.context.object
    cutter.name = 'Temporary window aperture'
    cutter.data.materials.append(bpy.data.materials['Limewashed plaster'])
    cutter.rotation_euler = orientation.to_euler()
    cutter.dimensions = (width+.015, .75, height+.015)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for wall in [o for o in bpy.context.scene.objects if o.type=='MESH' and 'Limewashed plaster' in o.name]:
        modifier = wall.modifiers.new('Actual window opening', 'BOOLEAN')
        modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
        bpy.context.view_layer.objects.active=wall
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    window['reference_repair'] = 'Wall aperture cut behind the existing frame; glass and night exterior stay aligned.'
    bpy.context.view_layer.update()
