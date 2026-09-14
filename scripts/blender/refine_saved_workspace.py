"""Refine a backed-up authored scene, render QA angles, then optionally promote.

This applies bounded edit modules to the source backup; it never runs the original
scene generator. Promotion checks that the user's source has not changed meanwhile.
"""
import bpy, sys, importlib.util, json, hashlib, shutil, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'artifacts/workspace/reference-refinement'
SOURCE=ROOT/'artifacts/workspace/workspace.blend'
BACKUP=ART/'source-latest-before-refinement.blend'
CANDIDATE=ART/'workspace-refined.blend'
ART.mkdir(parents=True,exist_ok=True)

def module(name):
    path=ROOT/'scripts/blender'/f'{name}.py'
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def web(v):return Vector((v[0],-v[2],v[1]))
def look(camera,position,target):
    camera.location=web(position);camera.rotation_euler=(web(target)-camera.location).to_track_quat('-Z','Y').to_euler()

def render_views():
    scene=bpy.context.scene
    original_camera=scene.camera
    camera=bpy.data.objects.new('Refinement inspection camera',bpy.data.cameras.new('Refinement inspection camera'))
    scene.collection.objects.link(camera);scene.camera=camera
    scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
    prefs=bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type='METAL';prefs.get_devices()
        for device in prefs.devices:device.use=device.type=='METAL'
        scene.cycles.device='GPU'
    except Exception:scene.cycles.device='CPU'
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    # Match the elevated photo first, then test the normal visitor approach.
    shots=[
      ('reference',(1.05,4.6,2.6),(0,1.88,-.95),38,(1000,1200)),
      ('front',(0,2.55,3.7),(0,1.85,-1.1),43,(1400,1000)),
      ('left',(-2.4,3.4,2.6),(0,1.7,-1.1),44,(1300,1000)),
      ('right',(2.4,3.4,2.6),(0,1.7,-1.1),44,(1300,1000)),
      ('desktop',(.1,3.75,.95),(0,1.45,-1.1),43,(1400,950)),
      ('shelves',(0,2.9,1.2),(0,2.5,-1.55),45,(1400,1000)),
    ]
    selected=sys.argv[sys.argv.index('--shots')+1].split(',') if '--shots' in sys.argv else [s[0] for s in shots]
    for name,pos,target,lens,size in shots:
        if name not in selected:continue
        look(camera,pos,target);camera.data.type='PERSP';camera.data.lens=lens
        scene.render.resolution_x,scene.render.resolution_y=size
        scene.render.filepath=str(ART/f'refined-{name}.png')
        bpy.ops.render.render(write_still=True)
        print('REFINEMENT_RENDER',name,flush=True)
    scene.camera=original_camera;bpy.data.objects.remove(camera,do_unlink=True)

if '--promote' in sys.argv:
    current=hashlib.sha256(SOURCE.read_bytes()).hexdigest();backup=hashlib.sha256(BACKUP.read_bytes()).hexdigest()
    if current!=backup:raise RuntimeError('Source Blender file changed since backup; refusing to overwrite newer edits.')
    if not CANDIDATE.exists():raise RuntimeError('Render and inspect the candidate before promotion.')
    shutil.copy2(CANDIDATE,SOURCE)
    print('PROMOTED_REFINED_SOURCE',SOURCE)
else:
    bpy.ops.wm.open_mainfile(filepath=str(BACKUP))
    # The backup moved one directory deeper; resolve its original relative textures.
    for image in bpy.data.images:
        if image.source=='FILE' and not image.packed_file:
            texture=ROOT/'public/textures/workspace'/Path(image.filepath).name
            if texture.exists():image.filepath=str(texture);image.reload()
    audit=module('audit_reference_workspace');initial_lights=audit.lights_snapshot()
    layout=module('refine_reference_layout');layout_report=layout.apply_layout()
    props=module('refine_reference_props');props.apply_props()
    layout_report=layout.finalize_layout()
    module('refine_reference_surfaces').apply_surfaces()
    if audit.lights_snapshot()!=initial_lights:raise RuntimeError('Refinement changed authored lights.')
    # Lamp colors, powers and cones stay unchanged. The monitor emitter follows
    # its screen and preserves emitted power per area when its dimensions change.
    for obj in bpy.context.scene.objects:
        if obj.type!='LIGHT':continue
        if obj.name.startswith('Red lamp practical'):
            point=Vector((obj.location.x,obj.location.z,-obj.location.y))
            transform=layout_report.get('lamp_transform')
            if transform:
                point=Vector(transform['target_web'])+(point-Vector(transform['origin_web']))*transform['scale']
            else:
                point+=Vector(layout_report.get('lamp_displacement_web',(0,0,0)))
            obj.location=web(point)
        elif obj.name=='Monitor bounce':
            screen=bpy.data.objects['monitor_screen']
            points=[screen.matrix_world@v.co for v in screen.data.vertices]
            center=sum(points,Vector())/len(points)
            normal=(screen.matrix_world.to_3x3().inverted().transposed()@screen.data.polygons[0].normal).normalized()
            obj.location=center+normal*.001
            obj.rotation_euler=normal.to_track_quat('-Z','Y').to_euler()
            # The old 1.2-unit disk extended below the screen and intersected
            # desktop props. A screen-sized emitter avoids near-field cutoffs.
            original_area=math.pi*(obj.data.size/2)**2 if obj.data.shape=='DISK' else obj.data.size*getattr(obj.data,'size_y',obj.data.size)
            obj['authored_energy_before_screen_resize']=obj.data.energy
            obj.data.shape='RECTANGLE'
            obj.data.size=max(p.x for p in points)-min(p.x for p in points)
            obj.data.size_y=max(p.z for p in points)-min(p.z for p in points)
            obj.data.energy*=obj.data.size*obj.data.size_y/original_area
            obj['reference_attachment']='Aligned to monitor screen so its emitter plane does not cut through laptop lid.'
    bpy.context.view_layer.update()
    (ART/'layout-report.json').write_text(json.dumps(layout_report,indent=2)+'\n')
    module('audit_reference_workspace').audit('after')
    # Retain the user's camera object, and save a second camera for this footprint.
    camera=bpy.data.objects.new('Workspace reference camera',bpy.data.cameras.new('Workspace reference camera'))
    bpy.context.scene.collection.objects.link(camera)
    look(camera,(1.05,4.6,2.6),(0,1.88,-.95));camera.data.lens=38
    bpy.context.scene.camera=camera
    bpy.context.scene.render.resolution_x=1000;bpy.context.scene.render.resolution_y=1200
    # Keep images packed and every interactive assembly editable.
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
    if '--render' in sys.argv:render_views()
    print('REFINEMENT_CANDIDATE',CANDIDATE,flush=True)
