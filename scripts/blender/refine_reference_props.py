"""Reference-led controller and Work Louder packaging refinement.

Import into an already-loaded scene, then call apply_props(). This module never
loads, saves, exports, renders, or changes the authoritative scene's lights.
All generated meshes use root-local coordinates and identity parent inverses.
"""
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
TEX = ROOT / 'public/textures/workspace'

# Source artwork was projectively rectified from Figma's own product photograph.
# The lid/front remove broad photographic illumination; side artwork is
# color-normalized while retaining the photographed marks. No generated art.
REFERENCE_PACKAGING_PHOTO = 'https://cdn.sanity.io/images/599r6htc/regionalized/f5c2b0369a963c2ef35bbc7561ba139a5093d805-6000x4000.jpg'
REFERENCE_OPEN_PACKAGE = 'https://cdn.sanity.io/images/599r6htc/regionalized/e4023647d03c0da9200759e097b8a40264c351a4-6000x4000.jpg'
REFERENCE_TEXTURE_QUADS_1600 = {
    'reference-figma-lid.png': [(523,414),(1016,495),(841,756),(295,650)],
    'reference-figma-front.png': [(295,652),(840,758),(835,988),(304,878)],
    'reference-figma-side.png': [(843,758),(1018,498),(1013,733),(840,985)],
}


def _material(name, color, roughness=.42, metal=0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    p = material.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metal
    return material


def _group(name, parent=None, location=(0,0,0)):
    ob = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(ob)
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.location = location
    return ob


def _attach(ob, name, parent, material, location=(0,0,0), bevel=0, smooth=False):
    ob.name = name
    ob.parent = parent
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.location = location
    if material: ob.data.materials.append(material)
    if smooth:
        for face in ob.data.polygons: face.use_smooth=True
    if bevel:
        mod=ob.modifiers.new('Small manufactured edge radius','BEVEL')
        mod.width=bevel; mod.segments=3
        mod=ob.modifiers.new('Weighted manufactured normals','WEIGHTED_NORMAL')
        mod.keep_sharp=True
    return ob


def _box(name, parent, pos, size, mat, bevel=.003):
    bpy.ops.mesh.primitive_cube_add(size=1)
    ob=bpy.context.object; ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return _attach(ob,name,parent,mat,pos,bevel)


def _cylinder(name, parent, pos, radius, depth, mat, segments=32, bevel=.002):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=radius,depth=depth)
    return _attach(bpy.context.object,name,parent,mat,pos,bevel,True)


def _torus(name, parent, pos, radius, thickness, mat, major=40, minor=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=thickness,major_segments=major,minor_segments=minor)
    return _attach(bpy.context.object,name,parent,mat,pos,0,True)


def _mesh(name, parent, verts, faces, material, smooth=False):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    return _attach(ob,name,parent,material,smooth=smooth)


def _label(name, parent, body, pos, size, mat, rotation=(0,0,0)):
    curve=bpy.data.curves.new(name,'FONT');curve.body=body
    curve.align_x='CENTER';curve.align_y='CENTER';curve.size=size
    curve.extrude=.0001;curve.resolution_u=2
    ob=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(ob)
    ob.parent=parent;ob.matrix_parent_inverse=Matrix.Identity(4)
    ob.location=pos;ob.rotation_euler=rotation;ob.data.materials.append(mat)
    return ob


def _clear_children(parent):
    for ob in list(parent.children_recursive):
        bpy.data.objects.remove(ob,do_unlink=True)


def _catmull_outline(points, steps=4):
    sampled=[]
    n=len(points)
    for i in range(n):
        p0,p1,p2,p3=[Vector(points[j % n]) for j in (i-1,i,i+1,i+2)]
        for k in range(steps):
            t=k/steps
            p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
            sampled.append((p.x,p.y))
    return sampled


def _sculpted_shell(name, parent, mat, z_offset=0, scale=1):
    # Shape follows the broad Xbox shoulder, two rounded hand grips, and the
    # concave lower notch. Dense curved outline, convex face, no separate lobes.
    points=[(-.173,.145),(.173,.145),(.231,.121),(.262,.055),(.278,-.106),
            (.252,-.166),(.219,-.174),(.184,-.140),(.119,-.052),
            (.078,-.039),(-.078,-.039),(-.119,-.052),(-.184,-.140),
            (-.219,-.174),(-.252,-.166),(-.278,-.106),(-.262,.055),(-.231,.121)]
    outline=_catmull_outline(points,4);n=len(outline)
    rings=[(.38,-.049),(.74,-.049),(.92,-.042),(.975,-.025),(1,-.007),(.992,.018),(.945,.038),(.77,.051),(.45,.055)]
    verts=[]
    for factor,z in rings:
        for x,y in outline:
            # Grip ends drop very slightly away from the raised central face.
            slope=max(0,-y-.03)*.085
            verts.append((x*factor*scale,y*factor*scale,(z-slope+z_offset)*scale))
    verts.append((0,0,(.055+z_offset)*scale));center=len(verts)-1
    verts.append((0,0,(-.049+z_offset)*scale));bottom=len(verts)-1
    faces=[(bottom,(i+1)%n,i) for i in range(n)]
    for j in range(len(rings)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    for i in range(n):faces.append(((len(rings)-1)*n+i,(len(rings)-1)*n+(i+1)%n,center))
    ob=_mesh(name,parent,verts,faces,mat,True)
    # One subdivision pass removes ring transitions, while preserving the
    # continuous manufactured silhouette at close range.
    sub=ob.modifiers.new('Continuous ergonomic shell','SUBSURF');sub.levels=1;sub.render_levels=1
    return ob


def _stick(name, parent, x, y, mats, scale=1):
    def p(z): return (x*scale,y*scale,z*scale)
    # Well and domed boot intersect the face skin. Thumb cap sits on the stem,
    # with a shallow inset cup and the serrated rim characteristic of Xbox.
    _cylinder(name+' inset well',parent,p(.050),.049*scale,.010*scale,mats['well'],40,.002*scale)
    _torus(name+' face seam',parent,p(.055),.046*scale,.0018*scale,mats['seam'])
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1)
    boot=bpy.context.object;boot.scale=(.035*scale,.035*scale,.023*scale)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    _attach(boot,name+' rubber boot',parent,mats['rubber'],p(.055),smooth=True)
    _cylinder(name+' short stem',parent,p(.080),.012*scale,.024*scale,mats['rubber'],24,.001*scale)
    _cylinder(name+' concave cap',parent,p(.096),.035*scale,.011*scale,mats['rubber'],40,.003*scale)
    _cylinder(name+' inset grip face',parent,p(.102),.027*scale,.002*scale,mats['grip'],40,.001*scale)
    _torus(name+' raised grip lip',parent,p(.1025),.031*scale,.003*scale,mats['rubber'],40,8)
    for i in range(24):
        a=i*math.tau/24
        ob=_box(name+' radial grip '+str(i),parent,((x+math.cos(a)*.032)*scale,(y+math.sin(a)*.032)*scale,.0995*scale),(.005*scale,.002*scale,.005*scale),mats['grip'],.0005*scale)
        ob.rotation_euler.z=a


def _controller(parent, black=False, scale=1):
    _clear_children(parent)
    prefix='Xbox black' if black else 'Xbox white'
    mats={
      'shell':_material('Xbox textured charcoal' if black else 'Xbox warm white shell',(.018,.020,.022) if black else (.88,.887,.867),.41),
      'rubber':_material('Xbox thumbstick rubber',(.010,.011,.012),.76),
      'grip':_material('Xbox fine grip edge',(.027,.030,.032),.70),
      'seam':_material('Xbox shell seam',(.025,.027,.028),.54),
      'well':_material('Xbox inset control wells',(.012,.014,.016),.35),
      'button':_material('Xbox glossy button resin',(.009,.011,.014),.22),
      'glyph':_material('Xbox white button graphics',(.78,.80,.80),.46),
      'A':_material('Xbox A green',(.18,.55,.08),.38),
      'B':_material('Xbox B red',(.71,.055,.018),.38),
      'X':_material('Xbox X blue',(.025,.26,.62),.38),
      'Y':_material('Xbox Y yellow',(.81,.57,.015),.38),
    }
    # All controls share a local root, preventing the former world/local split.
    shell=_sculpted_shell(prefix+' seamless ergonomic body',parent,mats['shell'],scale=scale)
    # Fine perimeter line around the body is a separate, nearly coincident
    # edge rather than a second visibly floating shell.
    points=_catmull_outline([(-.173,.145),(.173,.145),(.231,.121),(.262,.055),(.278,-.106),(.252,-.166),(.219,-.174),(.184,-.140),(.119,-.052),(.078,-.039),(-.078,-.039),(-.119,-.052),(-.184,-.140),(-.219,-.174),(-.252,-.166),(-.278,-.106),(-.262,.055),(-.231,.121)],3)
    c=bpy.data.curves.new(prefix+' casing join','CURVE');c.dimensions='3D';c.bevel_depth=.0014*scale;c.bevel_resolution=1
    spline=c.splines.new('POLY');spline.points.add(len(points)-1);spline.use_cyclic_u=True
    for v,(x,y) in zip(spline.points,points):v.co=(x*.997*scale,y*.997*scale,-.006*scale,1)
    ob=bpy.data.objects.new(c.name,c);bpy.context.collection.objects.link(ob);ob.parent=parent;ob.matrix_parent_inverse=Matrix.Identity(4);c.materials.append(mats['seam'])
    _stick(prefix+' left analog',parent,-.130,.047,mats,scale)
    _stick(prefix+' right analog',parent,.079,-.042,mats,scale)
    # Xbox's offset control layout. The d-pad dish contains a cross with
    # beveled wings, instead of four disconnected decorative cubes.
    x,y=-.074,-.047
    _cylinder(prefix+' Dpad inset',parent,(x*scale,y*scale,.052*scale),.045*scale,.011*scale,mats['well'],32,.003*scale)
    _cylinder(prefix+' faceted Dpad dish',parent,(x*scale,y*scale,.060*scale),.038*scale,.010*scale,mats['button'],8,.002*scale)
    _box(prefix+' Dpad horizontal',parent,(x*scale,y*scale,.066*scale),(.073*scale,.023*scale,.009*scale),mats['grip'],.004*scale)
    _box(prefix+' Dpad vertical',parent,(x*scale,y*scale,.066*scale),(.023*scale,.073*scale,.009*scale),mats['grip'],.004*scale)
    for label,x,y in [('Y',.160,.093),('B',.195,.059),('A',.160,.024),('X',.125,.059)]:
        _cylinder(prefix+' '+label+' recessed socket',parent,(x*scale,y*scale,.049*scale),.018*scale,.010*scale,mats['well'],28,.001*scale)
        _cylinder(prefix+' '+label+' button',parent,(x*scale,y*scale,.059*scale),.0144*scale,.015*scale,mats['button'],28,.003*scale)
        _label(prefix+' '+label+' print',parent,label,(x*scale,y*scale,.067*scale),.017*scale,mats[label])
    _cylinder(prefix+' Xbox guide button',parent,(0,.089*scale,.061*scale),.019*scale,.007*scale,mats['button'] if black else mats['glyph'],32,.002*scale)
    _label(prefix+' Xbox guide glyph',parent,'X',(0,.089*scale,.066*scale),.023*scale,mats['glyph'] if black else mats['seam'])
    for i,x in enumerate([-.037,.037]):
        _cylinder(prefix+' menu button '+str(i),parent,(x*scale,.026*scale,.059*scale),.009*scale,.007*scale,mats['button'],24,.002*scale)
        _label(prefix+' menu graphic '+str(i),parent,'≡' if i else '▣',(x*scale,.026*scale,.063*scale),.010*scale,mats['glyph'])
    _box(prefix+' share button',parent,(0,-.007*scale,.060*scale),(.018*scale,.016*scale,.006*scale),mats['button'],.004*scale)
    for side in (-1,1):
        ob=_box(prefix+' shoulder bumper '+str(side),parent,(side*.173*scale,.141*scale,.011*scale),(.142*scale,.033*scale,.027*scale),mats['button'],.012*scale)
        ob.rotation_euler.z=side*-.10
        ob=_box(prefix+' rear trigger '+str(side),parent,(side*.177*scale,.149*scale,-.017*scale),(.107*scale,.039*scale,.041*scale),mats['rubber'],.014*scale)
        ob.rotation_euler.z=side*-.10
    _box(prefix+' USB-C inset',parent,(0,.141*scale,.011*scale),(.027*scale,.005*scale,.011*scale),mats['well'],.004*scale)
    parent['reference_refinement']='Xbox-style continuous shell with attached controls; photo layout'
    parent['prop_dimensions']=[.56*scale,.34*scale,.16*scale]
    return shell


def _remove_old_black_controller():
    """Remove only old controller islands, including baked-in static batches."""
    removed=0
    for ob in list(bpy.context.scene.objects):
        if ob.name.lower().startswith('black controller'):
            bpy.data.objects.remove(ob,do_unlink=True);removed+=1;continue
        if ob.type!='MESH' or not ob.name.startswith('_static'):continue
        bm=bmesh.new();bm.from_mesh(ob.data);seen=set();delete=[]
        for first in bm.verts:
            if first in seen:continue
            stack=[first];seen.add(first);component=[]
            while stack:
                v=stack.pop();component.append(v)
                for edge in v.link_edges:
                    other=edge.other_vert(v)
                    if other not in seen:seen.add(other);stack.append(other)
            world=[ob.matrix_world @ v.co for v in component]
            # Original black controller location from build_workspace.py,
            # with enough margin for shoulder triggers and bevel vertices.
            if world and all(.64<p.x<1.19 and -.09<p.y<.28 and 1.33<p.z<1.51 for p in world):
                delete.extend(component);removed+=1
        if delete:
            bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(ob.data);ob.data.update()
        bm.free()
    return removed


def apply_props():
    """Rebuild owned props at existing layout anchors; return a compact report."""
    white=bpy.data.objects.get('controller')
    if white is None:raise RuntimeError('The layout must provide the controller root')
    _controller(white,False,.5357)
    removed=_remove_old_black_controller()
    black=bpy.data.objects.get('controller_black')
    if black is None:
        black=_group('controller_black',location=(.465,1.13,1.39))
        black.rotation_euler.z=math.radians(-15)
    _controller(black,True,.5089)
    _keyboard_packaging()
    packaging=_packaging()
    _authentic_laptop_texture()
    _finalize_meshes([white,black,bpy.data.objects.get('figma')])
    bpy.context.view_layer.update()
    return {'packaging':packaging,'controller':'controller','black_controller':'controller_black','removed_black_components':removed}


def _keyboard_packaging():
    """Yellow rigid Creator Micro packaging, with a 12-key/two-encoder device."""
    root=bpy.data.objects['figma'];_clear_children(root)
    yellow=_material('Creator Micro yellow packaging',(.95,.61,.015),.7)
    ink=_material('Creator Micro packaging black',(.012,.012,.01),.65)
    paper=_material('Creator Micro white insert',(.88,.87,.82),.85)
    white=_material('Creator Micro case',(.87,.89,.86),.32)
    # Source root is on the left shelf. Put its base on the upper face at 2.6165.
    matrix=root.matrix_world.copy();matrix.translation.z=2.617;root.matrix_world=matrix
    root.scale=(1,1,1)
    _box('Rigid box bottom',root,(0,0,.014),(.58,.40,.028),yellow,.005)
    for x in [-.282,.282]:_box('Packaging sidewall',root,(x,0,.10),(.016,.40,.18),yellow,.004)
    for y in [-.192,.192]:_box('Packaging front/back',root,(0,y,.10),(.55,.016,.18),yellow,.004)
    _box('Diecut keyboard insert',root,(0,0,.05),(.52,.34,.06),paper,.009)
    device=_group('Creator Micro keyboard',root,(0,0,.085))
    _box('Creator Micro chassis',device,(0,0,.016),(.235,.25,.032),white,.014)
    colors=[(.85,.06,.025),(.93,.36,.41),(.48,.20,.72),(.04,.43,.80),(.06,.60,.27)]
    for row in range(4):
        for col in range(3):
            color=_material('Creator Micro key '+str((row+col)%5),colors[(row+col)%5],.42)
            _box('Creator Micro keycap',device,(-.074+col*.060,-.082+row*.053,.044),(.05,.046,.023),color,.006)
    for y in [-.065,.055]:
        _cylinder('Creator Micro rotary encoder',device,(.084,y,.05),.023,.032,ink,32,.003)
        _box('Encoder index',device,(.084,y+.009,.067),(.003,.012,.001),white,.001)
    lid=_group('figma_lid',root,(0,.20,.205))
    _box('Yellow presentation lid',lid,(0,-.20,0),(.60,.42,.032),yellow,.006)
    _label('Figma packaging wordmark',root,'Figma',(0,-.203,.107),.065,ink,(math.pi/2,0,0))
    _label('Work Louder collaboration mark',root,'WORK LOUDER',(0,-.204,.057),.020,ink,(math.pi/2,0,0))
    _label('Creator Micro lid type',lid,'Creator Micro',(0,-.20,.017),.041,ink)
    root['reference_product']='Work Louder × Figma Creator Micro; yellow rigid packaging; 12 keys and 2 encoders'


def _texture(name, filename, roughness=.75):
    material=_material(name,(1,1,1),roughness)
    tree=material.node_tree;p=tree.nodes.get('Principled BSDF')
    old=[n for n in tree.nodes if n.type=='TEX_IMAGE']
    node=old[0] if old else tree.nodes.new('ShaderNodeTexImage')
    node.image=bpy.data.images.load(str(TEX/filename),check_existing=True)
    node.image.colorspace_settings.name='sRGB'
    tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    return material


def _plane(name, parent, corners, material):
    # Keep the explicit vertex order. A normal-recalculation round trip on an
    # open single face can reorder its loops and rotate a non-square texture.
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(corners,[],[(0,1,2,3)]);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    _attach(ob,name,parent,material)
    uv=ob.data.uv_layers.new(name='UVMap');coords=[(0,0),(1,0),(1,1),(0,1)]
    for face in mesh.polygons:
        for index in face.loop_indices:uv.data[index].uv=coords[mesh.loops[index].vertex_index]
    return ob


def _packaging():
    """Photo-scaled first-generation Creator Micro package, not Micro 2.

    Exact original package dimensions are not published in the consulted
    primary sources. The square .33 footprint and .15 height are editable
    proportional estimates matched to the desk photo and official product shot.
    """
    root=bpy.data.objects.get('figma')
    if root is None:raise RuntimeError('The layout must provide the figma shelf anchor')
    # The left upright intrudes 28 mm into the original layout anchor.
    # Use a 90-percent photo-estimated package, moved 14 mm right. The marker
    # makes repeated prop rebuilding idempotent on an already-refined scene.
    previous=float(root.get('reference_lateral_adjustment',0.0))
    matrix=root.matrix_world.copy()
    matrix.translation+=matrix.to_3x3() @ Vector((.014-previous,0,0))
    root.matrix_world=matrix;root['reference_lateral_adjustment']=.014
    root.scale=(.9,.9,.9)
    bpy.context.view_layer.update()
    _clear_children(root)
    # sRGB #FACA1B converted to linear values to match rectified print textures.
    yellow=_material('Reference Figma yellow cardboard',(.956,.591,.011),.74)
    white=_material('Reference Figma white inner tray',(.89,.88,.845),.82)
    black=_material('Reference Figma dense black packing foam',(.012,.014,.015),.98)
    grey=_material('Creator Micro frosted base',(.49,.55,.54),.48)
    plate=_material('Creator Micro pale PCB',(.71,.775,.75),.47,.12)
    ink=_material('Creator Micro printed black',(.012,.021,.020),.65)
    silver=_material('Creator Micro encoder brushed metal',(.43,.49,.49),.31,.76)
    switch=_material('Creator Micro exposed switch housings',(.021,.036,.036),.48)
    colors={
      'cyan':_material('Creator Micro key cyan',(.010,.51,.65),.39),
      'green':_material('Creator Micro key mint',(.20,.70,.36),.39),
      'purple':_material('Creator Micro key purple',(.29,.027,.49),.39),
      'pink':_material('Creator Micro key coral',(.88,.075,.155),.39),
      'red':_material('Creator Micro key red',(.79,.029,.035),.39),
    }
    # Rigid white bottom tray, exposed as a thin line when the yellow sleeve
    # is seated. Model all walls so the opened package remains physically solid.
    _box('Creator Micro white tray floor',root,(0,0,.004),(.322,.322,.008),white,.002)
    for side in (-1,1):
        _box('Creator Micro tray side '+str(side),root,(side*.158,0,.069),(.006,.322,.13),white,.002)
        _box('Creator Micro tray end '+str(side),root,(0,side*.158,.069),(.310,.006,.13),white,.002)
    _label('Creator Micro tray collaboration print',root,'Work Louder x Figma',(0,-.1612,.066),.0175,ink,(math.pi/2,0,0))
    # The fitted foam insert leaves a close square opening around the keypad.
    outer=.307;inner=.266;band=(outer-inner)/2
    for side in (-1,1):
        _box('Creator Micro foam border side '+str(side),root,(side*(inner+band)/2,0,.063),(band,outer,.11),black,.002)
        _box('Creator Micro foam border end '+str(side),root,(0,side*(inner+band)/2,.063),(inner,band,.11),black,.002)
    _box('Creator Micro foam support',root,(0,0,.040),(.266,.266,.065),black,.002)
    device=_group('figma_creator_micro',root,(0,0,0))
    _box('Creator Micro frosted acrylic base',device,(0,0,.078),(.254,.254,.016),grey,.016)
    _box('Creator Micro pale circuit plate',device,(0,0,.088),(.232,.232,.008),plate,.012)
    # Twelve keycaps on the original four-by-four staggered grid. Two vacant
    # cells contain encoders; the remaining corners carry branding/instructions.
    rows=[[(1,'cyan'),(2,'green')],[(0,'pink'),(1,'purple'),(2,'cyan'),(3,'green')],[(0,'red'),(1,'pink'),(2,'purple'),(3,'cyan')],[(1,'red'),(2,'pink')]]
    for row,keys in enumerate(rows):
        y=.078-row*.050
        for col,color in keys:
            x=-.075+col*.05
            _box(f'Creator Micro switch r{row}c{col}',device,(x,y,.097),(.032,.032,.012),switch,.003)
            _box(f'Creator Micro {color} key r{row}c{col}',device,(x,y,.110),(.044,.044,.020),colors[color],.006)
    # A tall black rotary knob occupies the upper left, while the lower left
    # uses a horizontal metal scroll wheel. Both are present in the 2023 edition.
    _cylinder('Creator Micro black rotary encoder',device,(-.075,.078,.115),.020,.044,ink,48,.002)
    _cylinder('Creator Micro knob top',device,(-.075,.078,.138),.018,.002,ink,48,.001)
    _box('Creator Micro knob index',device,(-.075,.085,.1395),(.002,.017,.0008),white,.0002)
    _box('Creator Micro scroll housing',device,(-.075,-.072,.100),(.045,.044,.015),plate,.004)
    scroll=_cylinder('Creator Micro horizontal metal scroll encoder',device,(-.075,-.072,.113),.017,.032,silver,48,.001)
    scroll.rotation_euler.y=math.pi/2
    for i in range(22):
        angle=i*math.tau/22
        ob=_box('Creator Micro scroll knurl '+str(i),device,(-.075,-.072+math.cos(angle)*.0174,.113+math.sin(angle)*.0174),(.031,.0012,.0012),silver,.0003)
        ob.rotation_euler.x=angle
    for x in (-.102,.102):
        for y in (-.102,.102):
            _cylinder('Creator Micro black fastening screw',device,(x,y,.094),.006,.006,ink,24,.001)
            _box('Creator Micro screw slot',device,(x,y,.0972),(.007,.001,.0005),silver,.0002)
    _label('Creator Micro plate attribution',device,'Work Louder x Figma © 2023',(0,-.109,.093),.007,ink)
    # Actual box shown in Figma's official photographs is a removable cover.
    # A local Y move in glTF is local Z in this Blender module.
    lid=_group('figma_lid',root,(0,0,0))
    lid['openingMotion']='lift';lid['openingDistance']=.137;lid['openingForward']=.22
    lid['referenceSource']='https://www.figma.com/blog/figma-work-louder-custom-keyboard/'
    _box('Creator Micro yellow cover top',lid,(0,0,.147),(.334,.334,.006),yellow,.0015)
    for side in (-1,1):
        _box('Creator Micro yellow cover side '+str(side),lid,(side*.165,0,.077),(.004,.334,.140),yellow,.001)
        _box('Creator Micro yellow cover end '+str(side),lid,(0,side*.165,.077),(.326,.004,.140),yellow,.001)
    top=_texture('Reference Figma original lid artwork','reference-figma-lid.png')
    front=_texture('Reference Figma original wordmark','reference-figma-front.png')
    side=_texture('Reference Figma original side artwork','reference-figma-side.png')
    _plane('Creator Micro actual top printed drawing',lid,[(-.165,-.165,.1502),(.165,-.165,.1502),(.165,.165,.1502),(-.165,.165,.1502)],top)
    _plane('Creator Micro actual front Figma print',lid,[(-.164,-.1672,.008),(.164,-.1672,.008),(.164,-.1672,.145),(-.164,-.1672,.145)],front)
    _plane('Creator Micro actual right side print',lid,[(.1672,-.164,.008),(.1672,.164,.008),(.1672,.164,.145),(.1672,-.164,.145)],side)
    _label('Creator Micro rear Work Louder print',lid,'work louder',(0,.1672,.072),.023,ink,(math.pi/2,0,math.pi))
    root['reference_product']='Figma x Work Louder Creator Micro, original 2023 edition'
    root['reference_dimensions']='Photo-proportioned .301 x .301 x .135; not manufacturer specifications'
    root['interactive']=True
    return {'root':'figma','lid':'figma_lid','device':'figma_creator_micro','openingMotion':'lift','openingDistance':.137,'openingForward':.22,'box_dimensions':[.3006,.3006,.135]}


def _authentic_laptop_texture():
    path=TEX/'reference-laptop-albedo.jpg'
    if not path.exists():return
    material=bpy.data.materials.get('Laptop sticker collage')
    if not material:return
    p=material.node_tree.nodes.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.8
    images=[n for n in material.node_tree.nodes if n.type=='TEX_IMAGE']
    if images:
        images[0].image=bpy.data.images.load(str(path),check_existing=True)
        images[0].image.colorspace_settings.name='sRGB'
        material['reference_source']='IMG_4813 2.jpg, projectively rectified by extract_reference_laptop.py'


def _finalize_meshes(roots):
    """Keep deliverable geometry directly exportable without evaluator quirks."""
    for root in roots:
        if root is None:continue
        for ob in list(root.children_recursive):
            if ob.type not in {'MESH','CURVE','FONT'}:continue
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(True);bpy.context.view_layer.objects.active=ob
            if ob.type in {'CURVE','FONT'}:bpy.ops.object.convert(target='MESH')
            for modifier in list(ob.modifiers):
                try:bpy.ops.object.modifier_apply(modifier=modifier.name)
                except RuntimeError:pass
    bpy.ops.object.select_all(action='DESELECT')
