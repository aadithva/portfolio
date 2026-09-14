"""Local MICKE proportion/layout repair for an already loaded Blender scene.

The caller owns load/save/export, lights, and render settings. This module never
loads the original generator, opens a file, changes a light, or saves a .blend.
apply_layout() is idempotent. finalize_layout() runs after the props module.
All exposed positions use Three.js coordinates: X right, Y up, Z toward viewer.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

VERSION='micke-reference-layout-6'
HORIZONTAL=.5085
OLD_TOP=1.3625
DESKTOP=1.31
SHELF_TOP=2.48
UPPER=(SHELF_TOP-DESKTOP)/(3.1165-OLD_TOP)
REAR=-2.34
LAMP_DELTA=Vector((-1.15,0,-.56))
LAMP_ORIGIN=Vector((2.63,0,.31))
LAMP_TARGET=Vector((1.48,0,-.25))
LAMP_SCALE=.80
def lamp_point(p):return LAMP_TARGET+(p-LAMP_ORIGIN)*LAMP_SCALE

def B(v):return Vector((v[0],-v[2],v[1]))
def W(v):return Vector((v.x,v.z,-v.y))
def fit_point(p):
    return Vector((p.x*HORIZONTAL, p.y*(DESKTOP/OLD_TOP) if p.y<=OLD_TOP else DESKTOP+(p.y-OLD_TOP)*UPPER, REAR+(p.z-REAR)*HORIZONTAL))
def all_meshes(root):return [o for o in [root,*root.children_recursive] if o.type=='MESH']
def points(root):return [W(o.matrix_world@v.co) for o in all_meshes(root) for v in o.data.vertices]
def bounds(root):
    ps=points(root)
    if not ps:return None
    return [Vector([min(p[i] for p in ps) for i in range(3)]),Vector([max(p[i] for p in ps) for i in range(3)])]
def ancestor_names(o):
    names=[]
    while o:
        names.append(o.name);o=o.parent
    return names
def move_root(root,target):
    world=root.matrix_world.copy();world.translation=B(target);root.matrix_world=world
    bpy.context.view_layer.update()
def ground_root(root,height):
    b=bounds(root)
    if b:
        p=W(root.matrix_world.translation);p.y+=height-b[0].y;move_root(root,p)
def transform_geometry(root,fn):
    for o in all_meshes(root):
        inv=o.matrix_world.inverted()
        for v in o.data.vertices:v.co=inv@B(fn(W(o.matrix_world@v.co)))
        o.data.update()
def delete_children(root):
    for o in list(root.children_recursive):bpy.data.objects.remove(o,do_unlink=True)
def components(mesh):
    adjacent=[[] for _ in mesh.vertices]
    for e in mesh.edges:
        a,b=e.vertices;adjacent[a].append(b);adjacent[b].append(a)
    seen=set();out=[]
    for i in range(len(adjacent)):
        if i in seen:continue
        stack=[i];seen.add(i);part=[]
        while stack:
            j=stack.pop();part.append(j)
            for k in adjacent[j]:
                if k not in seen:seen.add(k);stack.append(k)
        out.append(part)
    return out
def new_group(name,pos,parent=None):
    o=bpy.data.objects.get(name)
    if o is None:
        o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o)
    if parent:
        o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
    o.matrix_world=Matrix.Translation(B(pos));o['interactive']=True
    bpy.context.view_layer.update();return o
def material(name,color,metal=0,rough=.45):
    m=bpy.data.materials.get(name)
    if m:return m
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough
    return m
def finish(o,name,mat,g=None,bevel=0,smooth=False):
    o.name=name;o.data.materials.append(mat)
    if g:
        bpy.context.view_layer.update()
        world=o.matrix_world.copy();o.parent=g;o.matrix_world=world
    if smooth:
        for p in o.data.polygons:p.use_smooth=True
    if bevel:
        m=o.modifiers.new('Small edge radius','BEVEL');m.width=bevel;m.segments=3
        m=o.modifiers.new('Weighted edge normals','WEIGHTED_NORMAL');m.keep_sharp=True
    return o
def box(name,pos,size,mat,g=None,bevel=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=B(pos));o=bpy.context.object
    o.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,mat,g,bevel)
def cyl(name,pos,radius,height,mat,g=None,axis=(0,1,0),verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=height,location=B(pos));o=bpy.context.object
    o.rotation_mode='QUATERNION';o.rotation_quaternion=Vector((0,0,1)).rotation_difference(B(axis).normalized())
    return finish(o,name,mat,g,.002,True)
def rod(name,a,b,r,mat,g=None):
    a=Vector(a);b=Vector(b);return cyl(name,(a+b)/2,r,(b-a).length,mat,g,b-a,12)
def path(name,ps,r,mat,g=None):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=8;data.bevel_depth=r;data.bevel_resolution=2
    s=data.splines.new('BEZIER');s.bezier_points.add(len(ps)-1)
    for p,co in zip(s.bezier_points,ps):p.co=B(co);p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
    if g:
        world=o.matrix_world.copy();o.parent=g;o.matrix_world=world
    return o
def lathe(name,pos,profile,mat,g=None,n=32):
    ps=[];fs=[]
    for h,r in profile:
        for i in range(n):
            a=i*math.tau/n;ps.append(B((pos[0]+r*math.cos(a),pos[1]+h,pos[2]+r*math.sin(a))))
    for j in range(len(profile)-1):
        for i in range(n):fs.append((j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n))
    me=bpy.data.meshes.new(name);me.from_pydata(ps,[],fs);me.update()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return finish(o,name,mat,g,0,True)

def build_trophy(name,anchor,height=.31):
    g=bpy.data.objects.get(name)
    if g is None:g=new_group(name,anchor)
    else:delete_children(g);g.parent=None;g.matrix_world=Matrix.Translation(B(anchor))
    g['interactive']=True;g['contentStatus']='Unlabelled; achievement supplied by portfolio data'
    gold=material('Satin brass',(.61,.351,.068),.67,.29)
    wood=material('Walnut',(.185,.095,.033),0,.68)
    x,y,z=anchor
    box(name+' solid plinth',(x,y+.026,z),(.135,.052,.128),wood,g,.009)
    box(name+' blank plaque',(x,y+.028,z+.065),(.09,.023,.003),gold,g,.002)
    # The socket intersects the plinth by 2mm and the stem overlaps both fittings.
    cyl(name+' foot socket',(x,y+.057,z),.035,.015,gold,g)
    stem_top=y+height-.145
    cyl(name+' continuous stem',(x,(y+.057+stem_top)/2,z),.012,stem_top-(y+.057)+.012,gold,g)
    cyl(name+' cup collar',(x,stem_top,z),.028,.017,gold,g)
    lathe(name+' hollow cup',(x,stem_top-.003,z),[(0,.018),(.018,.026),(.06,.052),(.116,.073),(.13,.075),(.135,.073),(.135,.064),(.11,.063),(.055,.040),(.012,.013)],gold,g)
    for sign in [-1,1]:
        path(name+' attached handle',[(x+sign*.067,stem_top+.104,z),(x+sign*.105,stem_top+.111,z),(x+sign*.103,stem_top+.050,z),(x+sign*.047,stem_top+.038,z)],.006,gold,g)
    return g

def build_medal(name,pos,color):
    old=bpy.data.objects.get(name)
    if old:delete_children(old);bpy.data.objects.remove(old,do_unlink=True)
    g=new_group(name,pos);x,y,z=pos
    gold=material('Satin brass',(.61,.351,.068),.67,.29)
    silver=material('Brushed aluminium',(.66,.69,.68),.78,.3)
    ribbon=material(name+' woven ribbon',color,0,.9)
    # Each ring hooks over the bridge edge; two fabric tails meet the medal eyelet.
    path(name+' shelf hook',[(x,y+.013,z-.025),(x,y+.013,z+.007),(x,y-.025,z+.018)],.003,silver,g)
    for sign in [-1,1]:
        a=(x+sign*.016,y-.020,z+.021);b=(x+sign*.004,y-.129,z+.031)
        direction=Vector(b)-Vector(a)
        ob=box(name+' fabric ribbon',tuple((Vector(a)+Vector(b))/2),(.025,direction.length,.004),ribbon,g,.001)
        ob.rotation_euler.y=-sign*.105
    path(name+' eyelet',[(x-.009,y-.127,z+.031),(x,y-.143,z+.032),(x+.009,y-.127,z+.031)],.003,gold,g)
    cyl(name+' blank medallion',(x,y-.171,z+.034),.041,.009,gold,g,(0,0,1),40)
    cyl(name+' inset medallion face',(x,y-.171,z+.040),.034,.0015,gold,g,(0,0,1),40)
    return g

def apply_layout():
    scene=bpy.context.scene
    if scene.get('reference_layout_version')==VERSION:return finalize_layout()
    bpy.context.view_layer.update()
    meshes=[o for o in scene.objects if o.type=='MESH']
    oldmat={o:o.matrix_world.copy() for o in scene.objects}
    transformed={};delete_indices={};preserved=0
    # Uniform monitor dimensions preserve its screen aspect ratio. Its stand rests
    # on the desktop; its narrower back clears the inward-facing shelf panels.
    mon=bpy.data.objects.get('monitor');mon_b=bounds(mon);mon_low=mon_b[0].y
    screen_before=bounds(bpy.data.objects['monitor_screen'])
    screen_before=(screen_before[0]+screen_before[1])/2
    mon_anchor=Vector((0,DESKTOP+(2.12-mon_low)*.535,-1.17))
    def monitor_point(p):
        return Vector((p.x*.535,DESKTOP+(p.y-mon_low)*.535,mon_anchor.z+(p.z+.4)*.535))
    chair=bpy.data.objects.get('chair');ch_points=points(chair)
    ch_min=min(p.y for p in ch_points)
    chair_origin=W(chair.matrix_world.translation)
    def chair_point(p):
        q=p-chair_origin
        y=(p.y-ch_min)*1.04
        if y>.90:y=.90+(y-.90)*1.32
        return Vector((-.86+q.x*1.04,.004+y,-.03+q.z*1.04))
    for o in meshes:
        ns=ancestor_names(o);wp=[W(oldmat[o]@v.co) for v in o.data.vertices]
        changed=list(wp);remove=set()
        for indices in components(o.data):
            ps=[wp[i] for i in indices];lo=Vector([min(p[k] for p in ps) for k in range(3)]);hi=Vector([max(p[k] for p in ps) for k in range(3)])
            # Leave architecture and the physical window in their authored places.
            room=(o.name=='Room floor' or 'Limewashed plaster' in o.name or 'Tile grout' in o.name or 'window' in ns)
            baseboard=('Warm powder-coated white' in o.name and hi.y<.26 and (hi.x-lo.x>1.8 or hi.z-lo.z>1.8))
            black_controller=(lo.x>.60 and hi.x<1.20 and lo.y>1.30 and hi.y<1.54 and lo.z>-.29 and hi.z<.10 and o.parent is None)
            pen_pot=(lo.x>1.49 and hi.x<1.85 and lo.y>1.32 and hi.y<1.84 and lo.z>-.16 and hi.z<.16 and o.parent is None)
            old_monitor_stand=('monitor' in ns and hi.x-lo.x<.8 and lo.y<1.51 and hi.z<-.26)
            is_lamp=any(n.startswith('lamp_') for n in ns) or (lo.x>2.12 and hi.x<3.10 and hi.z<1.10 and o.parent is None)
            if old_monitor_stand or (pen_pot and not black_controller):
                remove.update(indices);continue
            if room or baseboard or black_controller:
                fn=lambda p:p;preserved+=1
            elif 'chair' in ns:fn=chair_point
            elif 'monitor' in ns:fn=monitor_point
            elif is_lamp:fn=lamp_point
            else:fn=fit_point
            for i in indices:changed[i]=fn(wp[i])
        transformed[o]=changed;delete_indices[o]=remove
    # Place pivots separately from vertex dimensions. New props can use unit scale
    # and every selected root keeps its original orientation in the room.
    empties=[o for o in scene.objects if o.type=='EMPTY']
    for o in sorted(empties,key=lambda ob:len(ancestor_names(ob))):
        ns=ancestor_names(o);p=W(oldmat[o].translation)
        if 'window' in ns:target=p
        elif o.name=='chair':target=Vector((-.86,.004,-.03))
        elif o.name=='monitor':target=mon_anchor
        elif o.name.startswith('lamp_'):target=lamp_point(p)
        else:target=fit_point(p)
        m=oldmat[o].copy();m.translation=B(target);o.matrix_world=m
        bpy.context.view_layer.update()
    for o,ps in transformed.items():
        inv=o.matrix_world.inverted()
        for v,p in zip(o.data.vertices,ps):v.co=inv@B(p)
        if delete_indices[o]:
            bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
            bmesh.ops.delete(bm,geom=[bm.verts[i] for i in delete_indices[o]],context='VERTS');bm.to_mesh(o.data);bm.free()
        o.data.update()
    bpy.context.view_layer.update()
    bracket_material=material('Soft charcoal plastic',(.021,.026,.023),0,.45)
    box('Monitor fitted rear mounting bracket',(0,1.505,-1.227),(.13,.13,.075),bracket_material,mon,.008)
    stand_material=material('Brushed aluminium',(.66,.69,.68),.78,.3)
    box('Monitor stand base behind Xbox',(0,DESKTOP+.0115,-1.56),(.35,.023,.18),stand_material,mon,.01)
    box('Monitor stand rear post',(0,1.455,-1.60),(.065,.27,.044),stand_material,mon,.01)
    path('Monitor arm above Xbox',[(0,1.566,-1.60),(0,1.586,-1.51),(0,1.575,-1.34),(0,1.54,-1.215)],.022,stand_material,mon)
    for name in ['laptop','sticker_1','sticker_2']:
        root=bpy.data.objects.get(name)
        if root:
            pos=W(root.matrix_world.translation);pos.z-=.03;move_root(root,pos)
    # The box and a compact set of journals share the left upper compartment,
    # entirely below the pegboard. The separate cover hinge is retained.
    left=bpy.data.objects['workspace_left_wing'];right=bpy.data.objects['workspace_right_wing']
    shelf_y=fit_point(Vector((0,2.6165,0))).y
    def on_wing(wing,x,y,z):return W(wing.matrix_world@B((x,y,z)))
    figma=bpy.data.objects.get('figma');move_root(figma,on_wing(left,-.13,shelf_y,0));figma.scale=(1,1,1)
    figma['layout_anchor']='bottom';figma['surface_y']=shelf_y
    books=bpy.data.objects.get('books');bp=W(books.matrix_world.translation)
    transform_geometry(books,lambda p:bp+(p-bp)*.54)
    move_root(books,on_wing(left,.183,shelf_y,.007));ground_root(books,shelf_y+.001)
    # Keep the book-cover pivot coincident with the transformed hinge geometry.
    cover=bpy.data.objects.get('books_cover')
    if cover:
        cb=bounds(cover)
        if cb:
            cp=points(cover);front=Vector((math.sqrt(.5),0,math.sqrt(.5)))
            across=Vector((math.sqrt(.5),0,-math.sqrt(.5)))
            hinge=across*(sum(p.dot(across) for p in cp)/len(cp))+front*max(p.dot(front) for p in cp)
            hinge.y=(cb[0].y+cb[1].y)/2
            old=cover.matrix_world.copy();new=old.copy();new.translation=B(hinge)
            children={ch:ch.matrix_world.copy() for ch in cover.children};cover.matrix_world=new
            for ch,m in children.items():ch.matrix_world=m
    speaker=bpy.data.objects.get('speaker');move_root(speaker,Vector((-.07,2.42,-1.635)))
    bridge_y=fit_point(Vector((0,2.965,0))).y;ground_root(speaker,bridge_y+.001)
    # Drop the invented third award slot and rebuild two mechanically continuous
    # blank cups with explicit plinth-to-shelf and stem-to-cup contact.
    third=bpy.data.objects.get('trophy_3')
    if third:delete_children(third);bpy.data.objects.remove(third,do_unlink=True)
    for name,x,h in [('trophy_1',-.192,.29),('trophy_2',.023,.34)]:
        build_trophy(name,on_wing(right,x,SHELF_TOP+.001,.012),h)
    for i,(x,color) in enumerate([(-.23,(.43,.025,.022)),(0,(.05,.14,.10)),(.23,(.10,.19,.27))],1):
        build_medal('medal_'+str(i),(x,bridge_y,-1.503),color)
    # Rebuild the pen vessel and its pens as one bounded, movable assembly clear
    # of the right shelf's front edge. Old merged islands were removed above.
    pen=new_group('pen_pot',(.82,DESKTOP,-.89))
    charcoal=material('Chair woven frame',(.13,.13,.097),0,.78)
    silver=material('Brushed aluminium',(.66,.69,.68),.78,.3)
    red=material('Lamp enamel vermilion',(.60,.036,.018),.19,.24)
    lathe('Pen pot with open rim',(.82,DESKTOP,-.89),[(0,.048),(.01,.053),(.137,.051),(.145,.052),(.145,.043),(.02,.04)],charcoal,pen,28)
    for i in range(4):
        x=.792+i*.018;z=-.90+(i%2)*.017
        rod('Pen safely inside holder',(x,DESKTOP+.022,z),(x+(i-1.5)*.007,DESKTOP+.225+(i%2)*.035,z),.005,red if i==2 else silver,pen)
    # All replacements are built about bottom contact anchors with unit scales.
    white=bpy.data.objects.get('controller');move_root(white,(-.478,DESKTOP+.026,-.894));white.scale=(1,1,1)
    black=new_group('controller_black',(.465,DESKTOP+.026,-1.13));black['layout_anchor']='bottom'
    white['layout_anchor']='bottom'
    surface=new_group('desktop_surface',(0,DESKTOP,-1.22));surface['interactive']=False
    surface['physical_height_cm']=75;surface['height_source']='inferred from the MICKE series height'
    surface['rear_wall_edge_cm']=100;surface['overall_cabinet_height_cm']=142
    surface['front_diagonal_units']=round(4.86*HORIZONTAL,5)
    scene['reference_layout_version']=VERSION
    scene['reference_layout_lamp_delta']=list(LAMP_DELTA)
    screen_after=bounds(bpy.data.objects['monitor_screen'])
    scene['reference_layout_monitor_delta']=list((screen_after[0]+screen_after[1])/2-screen_before)
    scene['reference_layout_dimensions_source']='IKEA MICKE India 203.542.84, 100 x 100 x 142 cm'
    return finalize_layout()

def finalize_layout():
    bpy.context.view_layer.update();scene=bpy.context.scene
    # The original window sill begins just above this shelf. Reduce both cups
    # about their contact pivots so the taller one clears the actual sill. Bake
    # that adjustment into child transforms, leaving runtime root scales at one.
    for name in ['trophy_1','trophy_2']:
        trophy=bpy.data.objects.get(name)
        if trophy and not trophy.get('layout_trophy_reduced'):
            original_scale=trophy.scale.copy();trophy.scale*=.82
            bpy.context.view_layer.update()
            child_world={child:child.matrix_world.copy() for child in trophy.children}
            trophy.scale=original_scale;bpy.context.view_layer.update()
            for child,matrix in child_world.items():child.matrix_world=matrix
            trophy['layout_trophy_reduced']=.82
            bpy.context.view_layer.update()
    plant=bpy.data.objects.get('plant_2')
    if plant and not plant.get('layout_window_clearance_forward'):
        forward=.135
        p=W(plant.matrix_world.translation)
        p+=Vector((-forward/math.sqrt(2),0,forward/math.sqrt(2)))
        move_root(plant,p);ground_root(plant,SHELF_TOP)
        plant['layout_window_clearance_forward']=forward
    # The props module authors controller bodies around their centre and the
    # Creator Micro tray about its bottom. Seat their actual vertices, not guessed
    # root offsets, after those replacements have been built.
    for name in ['controller','controller_black']:
        o=bpy.data.objects.get(name)
        if o and o.get('prop_dimensions'):
            if name=='controller':
                p=W(o.matrix_world.translation);p.x=-.513;move_root(o,p)
            ground_root(o,DESKTOP+.001)
    chair=bpy.data.objects.get('chair')
    if chair:ground_root(chair,-.015)
    figma=bpy.data.objects.get('figma')
    if figma and figma.get('reference_product'):
        ground_root(figma,fit_point(Vector((0,2.6165,0))).y+.001)
    result={'version':VERSION,'lamp_displacement_web':list(LAMP_DELTA),'desktop_surface_y':DESKTOP,
            'lamp_transform':{'origin_web':list(LAMP_ORIGIN),'target_web':list(LAMP_TARGET),'scale':LAMP_SCALE},
            'monitor_displacement_web':list(scene.get('reference_layout_monitor_delta',[0,0,0])),
            'rear_edge_units':round(3.43654*HORIZONTAL,5),'cabinet_top_y':SHELF_TOP,
            'source_dimensions_cm':[100,100,142],'objects':{},'clearances':{}}
    for name in ['monitor','books','figma','speaker','chair','controller','controller_black','trophy_1','trophy_2','plant_2','pen_pot','medal_1','medal_2','medal_3']:
        root=bpy.data.objects.get(name)
        if not root:continue
        bb=bounds(root)
        result['objects'][name]={'pivot':[round(v,5) for v in W(root.matrix_world.translation)],
            'bounds':[[round(v,5) for v in p] for p in bb] if bb else None}
    for name,surface in [('chair',-.015),('speaker',fit_point(Vector((0,2.965,0))).y+.001),('trophy_1',SHELF_TOP+.001),('trophy_2',SHELF_TOP+.001),('plant_2',SHELF_TOP),('pen_pot',DESKTOP)]:
        o=bpy.data.objects.get(name);bb=bounds(o) if o else None
        if bb:result['clearances'][name+'_base_gap']=round(bb[0].y-surface,6)
    a=bpy.data.objects.get('books');b=bpy.data.objects.get('Pegboard slots')
    if a and b:result['clearances']['books_below_pegboard']=round(bounds(b)[0].y-bounds(a)[1].y,5)
    def tree(root):
        verts=[];faces=[]
        for o in all_meshes(root):
            offset=len(verts);verts.extend([o.matrix_world@v.co for v in o.data.vertices])
            faces.extend([tuple(offset+i for i in p.vertices) for p in o.data.polygons])
        return BVHTree.FromPolygons(verts,faces,all_triangles=False) if faces else None
    monitor=bpy.data.objects.get('monitor');mt=tree(monitor) if monitor else None
    for side in ['left','right']:
        frame=bpy.data.objects.get('workspace_'+side+'_wing · Porcelain edges')
        ft=tree(frame) if frame else None
        if mt and ft:result['clearances']['monitor_'+side+'_frame_intersections']=len(mt.overlap(ft))
    laptop=bpy.data.objects.get('laptop');lt=tree(laptop) if laptop else None
    if mt and lt:result['clearances']['monitor_laptop_intersections']=len(mt.overlap(lt))
    controller=bpy.data.objects.get('controller');ct=tree(controller) if controller else None
    if ct and lt:result['clearances']['controller_laptop_intersections']=len(ct.overlap(lt))
    window=bpy.data.objects.get('window');wt=tree(window) if window else None
    plant=bpy.data.objects.get('plant_2');pt=tree(plant) if plant else None
    if pt and wt:result['clearances']['plant_window_intersections']=len(pt.overlap(wt))
    wing=bpy.data.objects.get('workspace_right_wing')
    frame=bpy.data.objects.get('workspace_right_wing · Porcelain edges')
    if wing and frame and plant:
        inv=wing.matrix_world.inverted()
        shelf=[W(inv@frame.matrix_world@v.co) for v in frame.data.vertices if abs(W(frame.matrix_world@v.co).y-SHELF_TOP)<.003]
        base=[W(inv@B(p)) for p in points(plant) if abs(p.y-SHELF_TOP)<.0005]
        if shelf and base:
            margins=[]
            for axis in [0,2]:
                margins.extend([min(p[axis] for p in base)-min(p[axis] for p in shelf),max(p[axis] for p in shelf)-max(p[axis] for p in base)])
            result['clearances']['plant_base_shelf_edge_margin']=round(min(margins),6)
    for name in ['trophy_1','trophy_2']:
        trophy=bpy.data.objects.get(name);tt=tree(trophy) if trophy else None
        if tt and wt:result['clearances'][name+'_window_intersections']=len(tt.overlap(wt))
        if tt and pt:result['clearances'][name+'_plant_intersections']=len(tt.overlap(pt))
    result['trophy_count']=sum(bpy.data.objects.get('trophy_'+str(i)) is not None for i in range(1,4))
    result['medal_count']=sum(bpy.data.objects.get('medal_'+str(i)) is not None for i in range(1,4))
    return result
