"""Build Aadith's desk as an editable Blender scene and web-ready glTF asset.

Usage:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/blender/build_workspace.py
  ... -- --render

All authored positions below use web coordinates: X right, Y up, Z toward the
visitor. B() converts them to Blender coordinates; glTF restores that convention.
No external modeling add-ons are required. Pillow is used only for source texture
art and can be installed in a normal system Python. The GLB contains its textures.
"""
import bpy, math, os, random, sys, json, subprocess
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'public/models'
TEX = ROOT / 'public/textures/workspace'
ART = ROOT / 'artifacts/workspace'
for folder in (OUT, TEX, ART): folder.mkdir(parents=True, exist_ok=True)
random.seed(4813)
WING_LEFT=set()
WING_RIGHT=set()
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
    for block in list(datablocks):
        if block.users == 0: datablocks.remove(block)

# Small reusable raster artwork. The laptop texture may be supplied independently.
TEXTURE_CODE = r'''
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random, math, sys
p=Path(sys.argv[1]); random.seed(4813)
font='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
regular='/System/Library/Fonts/Supplemental/Arial.ttf'
def F(n,bold=True):
 try: return ImageFont.truetype(font if bold else regular,n)
 except: return ImageFont.load_default()
im=Image.new('RGB',(768,640),(221,219,201)); d=ImageDraw.Draw(im)
for y in range(24,640,40):
 for x in range(22,768,40):
  d.rounded_rectangle((x-4,y-9,x+5,y+9),radius=4,fill=(237,235,218))
  d.rounded_rectangle((x-4,y-8,x+4,y+7),radius=4,fill=(120,119,103))
  d.rounded_rectangle((x-3,y-6,x+3,y+6),radius=3,fill=(91,89,74))
im.save(p/'pegboard.png',optimize=True)
im=Image.new('RGB',(1024,576),(24,61,48));d=ImageDraw.Draw(im)
d.text((58,45),'AADITH / SELECTED WORK',font=F(21),fill=(206,222,201))
d.text((55,135),'Good ideas.',font=F(68),fill=(247,244,222))
d.text((55,212),'Made real.',font=F(68),fill=(247,244,222))
d.rounded_rectangle((58,368,424,441),radius=35,fill=(227,242,120))
d.text((89,389),'Explore my work  →',font=F(26),fill=(26,48,26))
d.text((60,512),'DESIGN · CODE · CURIOSITY',font=F(16),fill=(173,195,160))
d.rounded_rectangle((654,115,928,430),radius=10,fill=(241,237,218))
d.ellipse((704,172,878,346),fill=(218,72,43))
d.rounded_rectangle((741,151,800,388),radius=25,fill=(228,189,55))
d.text((702,453),'LET’S MAKE THINGS.',font=F(19),fill=(230,233,209))
im.save(p/'monitor-idle.png',optimize=True)
# Silver label deliberately has no invented nutrition text or brand claims.
im=Image.new('RGB',(768,768),(211,212,208));d=ImageDraw.Draw(im)
for x in range(768):
 c=round(213+11*math.sin(x/767*math.pi*2));d.line((x,0,x,768),fill=(c,c,min(255,c+1)))
for x in (30,398):
 d.text((x,146),'Diet',font=F(84,False),fill=(98,94,89))
 d.text((x-12,264),'Coke',font=F(125),fill=(191,32,29))
 d.line((x+15,461,x+257,421),fill=(191,32,29),width=8)
 d.text((x+21,527),'NO SUGAR',font=F(19),fill=(80,81,76))
im.save(p/'can-label.jpg',quality=92)
im=Image.new('RGBA',(128,128),(0,0,0,0));d=ImageDraw.Draw(im)
for y in range(-128,256,12):
 d.line((0,y,128,y+128),fill=(70,68,57,240),width=2)
 d.line((0,y,128,y-128),fill=(102,98,81,210),width=2)
im.save(p/'chair-mesh.png',optimize=True)
im=Image.new('RGB',(640,800),(235,227,207)); d=ImageDraw.Draw(im)
d.text((49,44),'A FEW THINGS',font=F(28),fill=(43,64,49))
d.text((48,93),'ABOUT ME',font=F(51),fill=(43,64,49))
d.rounded_rectangle((48,179,589,598),radius=7,fill=(155,177,143))
d.ellipse((310,230,491,411),fill=(234,200,148))
d.polygon([(49,551),(225,321),(430,598),(49,598)],fill=(47,78,60))
d.polygon([(293,598),(454,383),(589,547),(589,598)],fill=(90,122,84))
d.text((51,650),'Design. Build. Explore.',font=F(29,False),fill=(43,64,49))
d.text((51,718),'A SMALL WINDOW INTO MY WORLD',font=F(15),fill=(97,99,76))
im.save(p/'about-card.png',optimize=True)
im=Image.new('RGB',(768,512),(243,233,211)); d=ImageDraw.Draw(im)
d.text((44,42),'LET’S TALK',font=F(72),fill=(167,49,29))
d.line((44,155,717,155),fill=(172,74,48),width=2)
d.text((46,222),'Have something in mind?',font=F(31,False),fill=(68,76,53))
d.text((46,332),'CONTACT  ↗',font=F(49),fill=(35,68,51))
im.save(p/'contact-card.png',optimize=True)
'''
try:
    subprocess.run(['/opt/homebrew/bin/python3', '-c', TEXTURE_CODE, str(TEX)], check=True)
except (FileNotFoundError, subprocess.CalledProcessError):
    subprocess.run(['python3', '-c', TEXTURE_CODE, str(TEX)], check=True)

def B(v): return Vector((v[0], -v[2], v[1]))
def mat(name, color, rough=.5, metal=0, emission=None):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    if emission:
        p.inputs['Emission Color'].default_value=(*emission[0],1)
        p.inputs['Emission Strength'].default_value=emission[1]
    return m

def texmat(name, filename, rough=.6, metal=0, alpha=False, emission=0):
    m=mat(name,(1,1,1),rough,metal)
    p=m.node_tree.nodes.get('Principled BSDF');t=m.node_tree.nodes.new('ShaderNodeTexImage')
    t.image=bpy.data.images.load(str(TEX/filename),check_existing=True)
    m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
    if emission:
        m.node_tree.links.new(t.outputs['Color'],p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value=emission
    if alpha:
        m.node_tree.links.new(t.outputs['Alpha'],p.inputs['Alpha'])
        m.surface_render_method='DITHERED'
    return m

M={
 'white':mat('Warm powder-coated white',(0.82,.805,.755),.52),
 'edge':mat('Porcelain edges',(.94,.925,.875),.34),
 'ivory':mat('Uncoated paper',(.83,.792,.668),.93),
 'wall':mat('Limewashed plaster',(.57,.515,.408),.97),
 'floor':mat('Warm limestone',(.72,.675,.558),.79),
 'grout':mat('Tile grout',(.48,.45,.374),.97),
 'red':mat('Lamp enamel vermilion',(.60,.036,.018),.24,.19),
 'rededge':mat('Lamp edge red',(.31,.018,.01),.32,.25),
 'yellow':mat('Figma ochre',(.96,.596,.024),.42),
 'dark':mat('Soft charcoal plastic',(.021,.026,.023),.45),
 'black':mat('Matte black rubber',(.008,.012,.010),.84),
 'green':mat('Forest green',(.025,.21,.108),.42),
 'leaf':mat('Leaf jade',(.092,.285,.128),.51),
 'leaflight':mat('Leaf sage',(.235,.395,.195),.6),
 'leafdark':mat('Leaf shaded',(.041,.159,.072),.63),
 'silver':mat('Brushed aluminium',(.66,.69,.68),.3,.78),
 'gold':mat('Satin brass',(.61,.351,.068),.29,.67),
 'wood':mat('Walnut',(.185,.095,.033),.68),
 'soil':mat('Potting soil',(.043,.032,.017),.99),
 'mesh':mat('Chair woven frame',(.13,.13,.097),.78),
 'sage':mat('Sage green hardcover',(.254,.32,.236),.76),
 'blue':mat('Washed blue hardcover',(.137,.224,.255),.77),
 'terracotta':mat('Terracotta clay',(.493,.158,.076),.83),
 'pink':mat('Dusty pink',(.623,.30,.26),.66),
 'cream':mat('Warm cream accents',(.88,.782,.5),.62),
 'bulb':mat('Warm lamp bulb',(.97,.704,.332),.28,0,((1,.72,.35),2.5)),
 'glass':mat('Window glass night',(.012,.025,.033),.18,.20,((.008,.018,.029),.13)),
 'city':mat('Distant warm windows',(.85,.64,.34),.5,0,((1,.73,.41),2.0)),
 'peg':texmat('Pegboard printed recesses','pegboard.png',.88),
 'screen':texmat('Monitor idle display','monitor-idle.png',.35,0,False,.5),
 'can':texmat('Diet Coke aluminium label','can-label.jpg',.27,.45),
 'chairmesh':texmat('Chair mesh weave','chair-mesh.png',.9,0,True),
 'about':texmat('About printed card','about-card.png',.93),
 'contact':texmat('Contact printed card','contact-card.png',.92),
}

def parent(obj,g):
    if g:
        obj.parent=g;obj.matrix_parent_inverse=g.matrix_world.inverted()
    return obj
def finish(obj,name,material=None,g=None,smooth=False,bevel=0):
    obj.name=name
    if material: obj.data.materials.append(M[material] if isinstance(material,str) else material)
    if bevel:
        mod=obj.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=3
        mod=obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');mod.keep_sharp=True
    if smooth and hasattr(obj.data,'polygons'):
        for p in obj.data.polygons:p.use_smooth=True
    parent(obj,g);return obj
def group(name,pos):
    obj=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(obj)
    obj.location=B(pos);bpy.context.view_layer.update()
    obj['interactive']=True;return obj
def box(name,pos,size,material='white',bevel=.015,g=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=B(pos))
    obj=bpy.context.object;obj.dimensions=(size[0],size[2],size[1])
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(obj,name,material,g,False,bevel)
def sphere(name,pos,size,material='white',g=None,segments=20,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=B(pos))
    obj=bpy.context.object;obj.scale=(size[0],size[2],size[1])
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(obj,name,material,g,True)
def cyl(name,pos,radius,height,material='white',g=None,vertices=32,axis=(0,1,0),bevel=.005):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=height,location=B(pos))
    obj=bpy.context.object
    obj.rotation_mode='QUATERNION';obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(B(axis).normalized())
    return finish(obj,name,material,g,True,bevel)
def rod(name,a,b,radius,material='dark',g=None,vertices=12):
    mid=(Vector(a)+Vector(b))/2;delta=Vector(b)-Vector(a)
    return cyl(name,mid,radius,delta.length,material,g,vertices,delta,.002)
def curve(name,points,radius,material='dark',g=None):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=10
    c.bevel_depth=radius;c.bevel_resolution=2
    s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):
        p.co=B(co);p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(obj)
    return finish(obj,name,material,g)
def ring(name,pos,radius,tube,material='silver',g=None,axis=(0,1,0),segments=32):
    bpy.ops.mesh.primitive_torus_add(major_segments=segments,minor_segments=8,location=B(pos),major_radius=radius,minor_radius=tube)
    obj=bpy.context.object;obj.rotation_mode='QUATERNION';obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(B(axis).normalized())
    return finish(obj,name,material,g,True)
def lathe(name,pos,profile,material='white',g=None,segments=32):
    verts=[];faces=[]
    for height,rad in profile:
        for i in range(segments):
            a=2*math.pi*i/segments;verts.append(B((pos[0]+rad*math.cos(a),pos[1]+height,pos[2]+rad*math.sin(a))))
    for j in range(len(profile)-1):
        for i in range(segments):faces.append((j*segments+i,(j+1)*segments+i,(j+1)*segments+(i+1)%segments,j*segments+(i+1)%segments))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    return finish(obj,name,material,g,True)
def front(name,pos,width,height,material,g=None):
    vertices=[B((pos[0]+x*width,pos[1]+y*height,pos[2])) for x,y in [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],[(0,1,2,3)]);mesh.update()
    uv=mesh.uv_layers.new(name='UVMap')
    for loop,coord in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=coord
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    return finish(obj,name,material,g)
def top(name,pos,width,depth,material,g=None):
    vertices=[B((pos[0]+x*width,pos[1],pos[2]+z*depth)) for x,z in [(-.5,.5),(.5,.5),(.5,-.5),(-.5,-.5)]]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],[(0,1,2,3)]);mesh.update()
    uv=mesh.uv_layers.new(name='UVMap')
    for loop,coord in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=coord
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    return finish(obj,name,material,g)
fontpath='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT=bpy.data.fonts.load(fontpath) if Path(fontpath).exists() else None
def text3(name,body,pos,size,material='dark',g=None,align='CENTER',rotation=0):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x=align;cu.align_y='CENTER';cu.extrude=.0003;cu.bevel_depth=0;cu.resolution_u=3
    if FONT:cu.font=FONT
    obj=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(obj);obj.location=B(pos)
    obj.rotation_euler=(math.pi/2,0,rotation)
    return finish(obj,name,material,g)
def polygon_slab(name,outline,y,height,material='white',g=None,bevel=.02):
    n=len(outline);verts=[B((x,y+dy,z)) for dy in [-height/2,height/2] for x,z in outline]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    faces=[tuple(reversed(face)) for face in faces]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    return finish(ob,name,material,g,False,bevel)

# Architecture: two perpendicular walls meet behind the central monitor. The
# bisector of that physical 90-degree room corner points toward the visitor.
floor_outline=[(0,-2.68),(3.32,.64),(3.32,2.36),(-3.32,2.36),(-3.32,.64)]
polygon_slab('Room floor',floor_outline,-.10,.17,'floor',bevel=.035)
for sign in [-1,1]:
    ob=box('Left corner wall' if sign<0 else 'Right corner wall',(sign*1.585,2.28,-.965),(4.483,4.6,.15),'wall',.015)
    ob.rotation_euler.z=math.radians(-sign*45)
    ob=box('Corner wall baseboard',(sign*1.542,.14,-.922),(4.40,.18,.065),'white',.007)
    ob.rotation_euler.z=math.radians(-sign*45)
for x in [-2.8,-1.7,-.6,.5,1.6,2.7]:
    zmin=abs(x)-2.66;zmax=2.33
    box('Floor tile seam',(x,-.012,(zmin+zmax)/2),(.005,.003,zmax-zmin),'grout',0)
for z in [-1.5,-.4,.7,1.8]:
    halfwidth=min(3.30,z+2.65)
    box('Floor tile seam',(0,-.012,z),(halfwidth*2,.003,.005),'grout',0)

# Desk with a shallow curved front cutout and substantial shelf joinery.
outline=[(0,-2.34),(2.43,.09),(1.68,.89),(1.40,.98),(1.06,.93),(.76,.84),(.39,.78),(0,.76),(-.39,.78),(-.76,.84),(-1.06,.93),(-1.40,.98),(-1.68,.89),(-2.43,.09)]
polygon_slab('Corner desk sculpted top',outline,1.31,.105,'edge',bevel=.028)
for sign in [-1,1]:
    ob=box('Desk angled side panel',(sign*2.02,.64,.49),(.10,1.25,1.085),'white',.02)
    ob.rotation_euler.z=math.radians(-sign*45)
    ob=box('Desk angled foot',(sign*2.02,.04,.49),(.16,.07,1.11),'edge',.018)
    ob.rotation_euler.z=math.radians(-sign*45)
    ob=box('Desk corner back brace',(sign*1.11,.95,-1.06),(3.14,.34,.065),'white',.015)
    ob.rotation_euler.z=math.radians(-sign*45)
wing_snapshot=set(bpy.context.scene.objects)
for x in [-1.60,1.60]:
    for sx in [-.57,.57]:box('Shelf vertical',(x+sx,2.22,-.72),(.083,1.74,.65),'edge',.012)
    for h in [1.41,2.01,2.58,3.08]:box('Shelf horizontal',(x,h,-.72),(1.22,.073,.68),'edge',.012)
    # Subtly inset lower backing strengthens silhouettes and contact shadows.
    box('Shelf lower back',(x,1.71,-1.045),(1.13,.57,.032),'white',.008)
for ob in set(bpy.context.scene.objects)-wing_snapshot:
    (WING_LEFT if ob.location.x<0 else WING_RIGHT).add(ob)
box('Monitor overhead bridge',(0,2.92,-.92),(1.35,.09,.45),'edge',.016)
box('Bridge short riser left',(-.60,2.78,-1.04),(.055,.23,.28),'white',.008)
box('Bridge short riser right',(.60,2.78,-1.04),(.055,.23,.28),'white',.008)

# Window, night glass and pale wooden mullions.
gw=group('window',(1.49,3.76,-1.29))
WING_RIGHT.add(gw)
box('Window deep recess',(1.46,3.65,-1.295),(2.12,1.60,.07),'dark',.009,gw)
glass=front('window_glass',(1.46,3.65,-1.247),1.93,1.43,'glass',gw)
for x in [.42,2.50]:box('Window outer stile',(x,3.66,-1.17),(.10,1.7,.16),'white',.018,gw)
for y in [2.85,4.47]:box('Window outer rail',(1.46,y,-1.16),(2.20,.10,.19),'white',.015,gw)
for x in [1.105,1.805]:box('Window vertical mullion',(x,3.66,-1.13),(.045,1.57,.15),'edge',.009,gw)
for y in [3.35,3.98]:box('Window horizontal mullion',(1.46,y,-1.115),(2.06,.039,.16),'edge',.007,gw)
box('Window sill',(1.46,2.82,-1.10),(2.28,.065,.32),'edge',.012,gw)
for i in range(22):
    x=random.uniform(.54,2.37);y=random.uniform(2.97,3.82)
    box('Distant city light',(x,y,-1.238),(.009,.013,.002),'city',.001,gw)
box('Window latch',(1.42,3.65,-1.01),(.045,.13,.034),'silver',.01,gw)

# Left pegboard with printed slots, overlapping pinned papers and accessories.
wing_snapshot=set(bpy.context.scene.objects)
box('Pegboard rounded backing',(-1.55,3.87,-1.23),(2.04,1.20,.075),'edge',.055)
front('Pegboard slots',(-1.55,3.87,-1.185),1.94,1.10,'peg')
for x,y in [(-2.45,3.39),(-.65,3.39),(-2.45,4.33),(-.65,4.33)]:
    cyl('Pegboard silver screw',(x,y,-1.175),.018,.009,'silver',vertices=12,axis=(0,0,1))
ga=group('about',(-1.85,3.89,-1.03))
box('About card stock',(-1.85,3.89,-1.09),(.52,.65,.012),'ivory',.005,ga)
front('About card illustration',(-1.85,3.89,-1.080),.51,.64,'about',ga)
cyl('About card pin',(-1.85,4.19,-1.06),.025,.025,'red',ga,16,(0,0,1))
gc=group('contact',(-1.075,3.65,-1.0))
box('Contact card paper',(-1.075,3.65,-1.08),(.62,.41,.012),'ivory',.006,gc)
front('Contact card print',(-1.075,3.65,-1.069),.61,.40,'contact',gc)
cyl('Contact card brass pin',(-1.075,3.84,-1.045),.022,.028,'gold',gc,16,(0,0,1))
box('Pegboard postcard red',(-1.21,4.18,-1.12),(.45,.30,.012),'red',.002)
text3('Postcard typography','MAKE',(-1.21,4.205,-1.108),.08,'cream')
text3('Postcard typography','THINGS.',(-1.21,4.115,-1.108),.062,'cream')
box('Cream clipped note',(-2.38,3.65,-1.135),(.24,.38,.013),'ivory',.004)
for h in [3.77,3.70,3.64,3.58]:box('Pencil note lines',(-2.38,h,-1.124),(.16,.005,.003),'sage',0)
box('Binder clip',(-2.38,3.85,-1.097),(.075,.035,.044),'dark',.007)
ring('Binder clip handle',(-2.38,3.89,-1.087),.023,.003,'silver',axis=(0,0,1),segments=16)
box('Pegboard shallow tray',(-1.56,3.325,-1.00),(1.42,.07,.32),'white',.023)
box('Tray front lip',(-1.56,3.355,-.843),(1.42,.115,.034),'edge',.01)
# Hanging headphones with padded ear cups.
curve('Headphone arch',[(-2.41,4.17,-1.035),(-2.44,4.4,-1.00),(-2.15,4.47,-1.00),(-2.03,4.23,-1.00)],.026,'dark')
for x in [-2.405,-2.04]:
    sphere('Headphone cushion',(x,4.15,-1.005),(.075,.12,.06),'black')
    sphere('Headphone ear shell',(x,4.16,-.985),(.060,.105,.059),'dark')
rod('Headphone hook',(-2.20,4.41,-1.17),(-2.20,4.41,-.96),.012,'silver')
# Pencil cup and individually modeled colored stationery.
lathe('Pegboard pencil cup',(-.73,3.29,-.94),[(0,.095),(.015,.106),(.24,.11),(.25,.11),(.25,.098),(.02,.08)],'white')
for i in range(7):
    x=-.79+(i%3)*.05;z=-.99+(i//3)*.042
    rod('Colored pencil',(x,3.36,z),(x+random.uniform(-.045,.045),3.68+random.uniform(0,.10),z+.01),.009,['red','yellow','green','blue'][i%4])
WING_LEFT.update(set(bpy.context.scene.objects)-wing_snapshot)

# Monitor: face plane remains separate so Three.js can replace only its texture.
gm=group('monitor',(0,2.12,-.40))
box('Monitor outer housing',(0,2.12,-.406),(1.91,1.15,.115),'white',.035,gm)
box('Monitor black bezel',(0,2.12,-.342),(1.80,1.055,.026),'dark',.012,gm)
front('monitor_screen',(0,2.12,-.325),1.72,.98,'screen',gm)
box('Monitor lower silver edge',(0,1.583,-.335),(1.78,.048,.021),'silver',.006,gm)
cyl('Monitor power LED',(.81,1.584,-.319),.005,.005,'leaflight',gm,12,(0,0,1))
box('Monitor neck',(0,1.58,-.58),(.16,.40,.10),'silver',.023,gm)
box('Monitor foot',(0,1.377,-.47),(.66,.035,.38),'silver',.024,gm)
text3('Monitor bezel mark','DELL',(0,1.584,-.316),.022,'dark',gm)
curve('Monitor power cable',[(0,1.64,-.49),(-.40,1.43,-.54),(-.65,1.42,-.23),(-.52,1.367,-.1),(-.39,1.367,-.25)],.009,'black')
curve('Loose controller cable',[(-.94,1.38,.02),(-1.03,1.37,-.21),(-.88,1.37,-.35),(-.67,1.37,-.25),(-.81,1.37,-.07)],.006,'dark')

# Console beside cables under the screen, including a perforated dark vent.
box('Xbox Series S body',(.13,1.454,-.30),(.78,.145,.49),'edge',.028)
cyl('Console vent',(.18,1.530,-.29),.191,.007,'black',vertices=48,bevel=.002)
for j in range(-5,6):
    for i in range(-5,6):
        if i*i+j*j<28:cyl('Vent inset',(.18+i*.029,1.535,-.29+j*.029),.007,.002,'dark',vertices=8,bevel=0)
cyl('Console power button',(.439,1.456,-.046),.013,.006,'silver',vertices=16,axis=(0,0,1))
box('Console USB port',(-.17,1.45,-.049),(.039,.015,.006),'dark',.002)

# Sticker-covered closed laptop, close to the photo's arrangement.
gl=group('laptop',(-.07,1.411,.46))
box('Laptop lower shell',(-.07,1.397,.46),(1.17,.055,.76),'silver',.037,gl)
box('Laptop dark lid',(-.07,1.428,.46),(1.155,.021,.75),'dark',.027,gl)
if (TEX/'laptop-stickers.png').exists():
    # The PNG stays as source artwork. Its opaque albedo needs only a small JPEG
    # at runtime, avoiding a 1.5 MB lossless texture inside every GLB download.
    subprocess.run(['/opt/homebrew/bin/python3','-c','from PIL import Image; import sys; Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2],quality=91,optimize=True)',str(TEX/'laptop-stickers.png'),str(TEX/'laptop-stickers.jpg')],check=True)
sticker_file=next((p.name for p in [TEX/'laptop-stickers.jpg',TEX/'laptop-stickers.png',TEX/'laptop-stickers.webp'] if p.exists()),None)
if sticker_file:
    if sticker_file.endswith('.webp'):
        subprocess.run(['/opt/homebrew/bin/python3','-c','from PIL import Image; import sys; Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2])',str(TEX/sticker_file),str(TEX/'laptop-stickers.png')],check=True)
        sticker_file='laptop-stickers.png'
    M['stickers']=texmat('Laptop sticker collage',sticker_file,.58)
    top('Laptop sticker printed lid',(-.07,1.440,.46),1.112,.705,'stickers',gl)
else:
    # This fallback only runs before the independently authored texture arrives.
    for row in range(5):
        for col in range(8):
            x=-.55+col*.137+random.uniform(-.01,.01);z=.19+row*.13
            box('Diecut sticker white border',(x,1.441,z),(.103,.002,.082),'ivory',.016,gl)
            box('Colored sticker',(x,1.443,z),(.086,.002,.065),['red','green','yellow','blue','pink'][random.randrange(5)],.01,gl)
for x in [-.39,.28]:box('Laptop hinge',(x,1.421,.085),(.22,.033,.031),'dark',.012,gl)
for x in [-.576,-.546,-.516]:box('Laptop side port',(x,1.395,.842),(.025,.009,.003),'dark',.001,gl)
for name,pos,material,label in [('sticker_1',(-.34,1.447,.59),'yellow','!'),('sticker_2',(.24,1.447,.29),'red','*')]:
    gs=group(name,pos);gs['easterEgg']=True
    cyl(name+' diecut',pos,.054,.003,'ivory',gs,24,bevel=.001)
    cyl(name+' ink',(pos[0],pos[1]+.002,pos[2]),.046,.003,material,gs,24,bevel=.001)
    # Small geometrical icon, keeping personal meaning in editable content.
    box(name+' icon',(pos[0],pos[1]+.005,pos[2]),(.015,.002,.053),'dark',.003,gs)

def controller(name,pos,material='white',interactive=False,scale=1):
    g=group(name,pos) if interactive else None;x,y,z=pos
    outline=[(-.19,-.14),(.19,-.14),(.27,-.07),(.31,.14),(.25,.19),(.18,.16),(.10,.058),(-.10,.058),(-.18,.16),(-.25,.19),(-.31,.14),(-.27,-.07)]
    polygon_slab(name+' sculpted shell',[(x+u*scale,z+v*scale) for u,v in outline],y,.085*scale,material,g,.045*scale)
    for dx,dz in [(-.13,-.015),(.083,.067)]:
        cyl(name+' stick boot',(x+dx*scale,y+.052*scale,z+dz*scale),.046*scale,.018*scale,'black',g,24)
        cyl(name+' thumbstick',(x+dx*scale,y+.067*scale,z+dz*scale),.032*scale,.026*scale,'dark',g,24)
        ring(name+' stick rim',(x+dx*scale,y+.082*scale,z+dz*scale),.026*scale,.003*scale,'mesh',g,segments=20)
    for dx,dz,ma in [(.19,-.045,'yellow'),(.225,-.005,'red'),(.15,-.005,'blue'),(.19,.036,'green')]:
        cyl(name+' face button',(x+dx*scale,y+.052*scale,z+dz*scale),.017*scale,.018*scale,ma,g,16)
    box(name+' dpad vertical',(x-.067*scale,y+.054*scale,z+.063*scale),(.021*scale,.014*scale,.075*scale),'dark',.005,g)
    box(name+' dpad horizontal',(x-.067*scale,y+.054*scale,z+.063*scale),(.075*scale,.014*scale,.021*scale),'dark',.005,g)
    cyl(name+' home button',(x,y+.053*scale,z-.06*scale),.020*scale,.009*scale,'silver',g,16)
    for dx in [-.17,.17]:box(name+' shoulder trigger',(x+dx*scale,y+.028*scale,z-.143*scale),(.12*scale,.051*scale,.045*scale),'dark',.014,g)
    return g
controller('controller',(-.94,1.420,.50),'edge',True,.87)
controller('Black controller',(.91,1.405,-.10),'dark',False,.74)

# Soda can: rolled aluminium rims, shoulder, pull tab and a wrapped label.
gcan=group('can',(.94,1.40,.60))
lathe('Can spun body',(.94,1.372,.60),[(0,.074),(.011,.081),(.032,.091),(.310,.091),(.331,.083),(.35,.078)],'silver',gcan,48)
body=cyl('Can label cylinder',(.94,1.548,.60),.0912,.27,'can',gcan,48,bevel=0)
# Cylinder side UV from Blender is adequate for the wrapped label.
for y in [1.381,1.714]:ring('Can rolled aluminium rim',(.94,y,.60),.078,.006,'silver',gcan,segments=40)
cyl('Can lid',(.94,1.714,.60),.076,.006,'silver',gcan,40,bevel=0)
sphere('Can opening',(.94,1.718,.623),(.025,.002,.038),'dark',gcan,16,8)
ring('Can pull tab',(.94,1.723,.573),.019,.005,'silver',gcan,segments=20)
cyl('Can tab rivet',(.94,1.725,.593),.006,.004,'silver',gcan,12,bevel=0)

# Shelf books. Readable, deliberately non-biographical cover labels.
gb=group('books',(-1.55,3.17,-.69))
WING_LEFT.add(gb)
book_specs=[(-1.96,.13,.48,'red','FORM'),(-1.80,.15,.55,'sage','NOTES'),(-1.62,.17,.52,'ivory','DESIGN'),(-1.43,.14,.44,'blue','IDEAS'),(-1.26,.15,.57,'terracotta','JOURNAL')]
for x,w,h,ma,label in book_specs:
    box('Book pages',(x,3.12+h/2,-.74),(w-.016,h-.022,.33),'ivory',.008,gb)
    for sx in [-1,1]:
        cover_parent=gb
        if x==-1.96 and sx==-1:
            cover_parent=group('books_cover',(x+sx*w/2,3.12+h/2,-.563))
            parent(cover_parent,gb)
        box('Cloth book cover',(x+sx*w/2,3.12+h/2,-.75),(.011,h,.365),ma,.004,cover_parent)
    box('Book rounded spine',(x,3.12+h/2,-.555),(w,h,.018),ma,.01,gb)
    text3('Book spine '+label,label,(x,3.12+h*.53,-.540),min(.029,w*.26),'cream' if ma!='ivory' else 'dark',gb)
    for y in [3.17,3.12+h-.047]:box('Book spine gilding',(x,y,-.539),(w*.73,.007,.002),'gold',.001,gb)
    for j in range(5):box('Fine page edges',(x,3.16+j*(h-.08)/5,-.563),(w-.028,.002,.004),'cream',0,gb)
# A relaxed pile of journals on the lower shelf.
wing_snapshot=set(bpy.context.scene.objects)
for i,ma in enumerate(['terracotta','ivory','sage']):
    y=2.072+i*.061
    box('Stacked notebook pages',(1.68,y,-.64),(.62,.041,.39),'ivory',.005)
    for dy in [-.025,.025]:box('Notebook cover',(1.68,y+dy,-.64),(.65,.008,.41),ma,.005)
box('Notebook ribbon',(1.73,2.01,-.407),(.024,.07,.004),'red',.003)
WING_RIGHT.update(set(bpy.context.scene.objects)-wing_snapshot)

# Figma yellow box with separate lid pivot for the runtime opening motion.
gf=group('figma',(-1.61,2.69,-.62))
WING_LEFT.add(gf)
box('Figma box base',(-1.61,2.732,-.67),(.62,.25,.43),'yellow',.026,gf)
lid=group('figma_lid',(-1.61,2.861,-.85));parent(lid,gf)
box('Figma box lid',(-1.61,2.864,-.66),(.65,.045,.45),'yellow',.02,lid)
text3('Figma box label','Figma',(-1.61,2.75,-.450),.074,'dark',gf)
for i,(dx,dy,ma) in enumerate([(-.033,.038,'red'),(.022,.038,'terracotta'),(-.033,-.012,'pink'),(.022,-.012,'blue'),(-.033,-.062,'green')]):
    sphere('Figma symbol',(-1.835+dx,2.758+dy,-.447),(.023,.024,.003),ma,gf,12,8)

# Three unlabelled trophies: content comes from the separate editable data file.
for i,(x,h) in enumerate([(.99,.41),(1.46,.56),(1.94,.39)],1):
    gt=group('trophy_'+str(i),(x,3.13,-.65))
    WING_RIGHT.add(gt)
    box('Trophy walnut plinth',(x,3.135,-.72),(.24,.075,.23),'wood',.019,gt)
    box('Blank brass plaque',(x,3.143,-.601),(.13,.037,.005),'gold',.004,gt)
    cyl('Trophy stem',(x,3.22+h*.26,-.72),.025,h*.45,'gold',gt,20)
    lathe('Trophy cup',(x,3.20+h*.48,-.72),[(0,.027),(.035,.055),(.10,.11),(.18,.139),(.19,.139),(.19,.125),(.10,.09),(.037,.029)],'gold',gt,28)
    for sign in [-1,1]:
        curve('Trophy curved handle',[(x+sign*.13,3.37+h*.3,-.72),(x+sign*.205,3.39+h*.3,-.72),(x+sign*.198,3.28+h*.3,-.72),(x+sign*.08,3.27+h*.3,-.72)],.010,'gold',gt)

# Plants: pots with real rims, low-poly curved leaves and branching silhouettes.
def leaf(name,start,end,width,material='leaf',g=None,bend=.04):
    a=Vector(start);b=Vector(end);d=b-a
    sideways=Vector((d.z,0,-d.x)).normalized() if abs(d.x)+abs(d.z)>.001 else Vector((1,0,0))
    verts=[];n=7
    for j in range(n):
        t=j/(n-1);center=a+d*t+Vector((0,bend*math.sin(t*math.pi),0))
        wid=width*(math.sin(t*math.pi)**.9)
        verts.extend([B(center-sideways*wid),B(center+Vector((0,.018*math.sin(t*math.pi),0))),B(center+sideways*wid)])
    faces=[]
    for j in range(n-1):
        for k in range(2):faces.append((j*3+k,j*3+k+1,(j+1)*3+k+1,(j+1)*3+k))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    ob=finish(ob,name,material,g,True);sol=ob.modifiers.new('Leaf thickness','SOLIDIFY');sol.thickness=.0015
    return ob
def plant(name,pos,scale=1,potmat='white',succulent=False):
    x,y,z=pos;g=group(name,pos)
    profile=[(0,.086*scale),(.012*scale,.094*scale),(.17*scale,.121*scale),(.19*scale,.12*scale),(.19*scale,.106*scale),(.155*scale,.103*scale)]
    lathe(name+' ceramic pot',pos,profile,potmat,g,28)
    cyl(name+' soil',(x,y+.165*scale,z),.105*scale,.012,'soil',g,24,bevel=0)
    for i in range(13 if succulent else 9):
        a=i*2.399;h=(.10+.16*(i%3)/2)*scale
        rad=(.10+.055*(i%3))*scale
        start=(x,y+.172*scale,z);end=(x+math.cos(a)*rad,y+.17*scale+h,z+math.sin(a)*rad)
        if not succulent:
            tip=(x+math.cos(a)*rad*1.10,y+.42*scale+(i%3)*.11*scale,z+math.sin(a)*rad*1.10)
            rod(name+' stem',start,tip,.003*scale,'leafdark',g,8)
            start=(tip[0]*.0+x*.0 + (x+tip[0])/2,(y+.17*scale+tip[1])/2,(z+tip[2])/2)
            end=(tip[0]+math.cos(a)*.11*scale,tip[1],tip[2]+math.sin(a)*.11*scale)
        leaf(name+' leaf',start,end,.040*scale if succulent else .065*scale,['leaf','leaflight','leafdark'][i%3],g,.02*scale)
    return g
WING_LEFT.add(plant('plant_1',(-1.94,2.05,-.65),.91,'white',True))
WING_LEFT.add(plant('Small aloe',(-1.56,2.05,-.71),.85,'white',True))
WING_LEFT.add(plant('Tiny jade plant',(-1.20,2.05,-.65),.72,'white',True))
WING_RIGHT.add(plant('plant_2',(2.08,3.12,-.75),1.02,'yellow',False))
# Signature glossy green cactus/vase on the top bridge.
lathe('Green sculptural vase',(.47,2.98,-.84),[(0,.10),(.025,.13),(.34,.13),(.52,.10),(.58,.0)],'green',segments=32)
curve('Cactus left arm',[(.38,3.21,-.84),(.21,3.26,-.84),(.19,3.53,-.84)],.053,'green')
curve('Cactus right arm',[(.56,3.31,-.84),(.68,3.38,-.84),(.69,3.58,-.84)],.043,'green')

# Speaker soundbar with perforations consolidated during export.
gs=group('speaker',(-.28,3.07,-.67))
box('Speaker fabric body',(-.28,3.06,-.73),(.95,.21,.25),'dark',.065,gs)
box('Speaker grille',(-.28,3.06,-.596),(.84,.15,.007),'black',.035,gs)
for i in range(24):
    for j in range(4):cyl('Speaker perforation',(-.662+i*.033,3.012+j*.03,-.590),.006,.003,'mesh',gs,8,(0,0,1),0)
box('Speaker indicator',(.067,3.063,-.585),(.023,.004,.003),'cream',.001,gs)
text3('Speaker brandless mark','SOUND',(-.57,3.03,-.582),.015,'silver',gs)
curve('Speaker cable',[(-.65,3.02,-.82),(-.86,2.97,-.90),(-.80,2.85,-.90),(-.76,2.76,-1.01)],.006,'black')

# Small shelf collectibles, a framed print, and stationery on the desktop.
gtoy=group('toy',(1.36,2.66,-.66))
WING_RIGHT.add(gtoy)
box('Tiny robot torso',(1.36,2.69,-.68),(.14,.17,.09),'sage',.019,gtoy)
box('Tiny robot head',(1.36,2.84,-.68),(.16,.13,.10),'cream',.022,gtoy)
for dx in [-.043,.043]:
    cyl('Robot eye',(1.36+dx,2.86,-.62),.016,.005,'dark',gtoy,16,(0,0,1))
    rod('Robot leg',(1.36+dx,2.62,-.68),(1.36+dx,2.60,-.68),.023,'dark',gtoy)
for s in [-1,1]:rod('Robot arm',(1.36+s*.074,2.73,-.68),(1.36+s*.125,2.69,-.68),.016,'terracotta',gtoy)
cyl('Robot aerial',(1.36,2.955,-.68),.009,.085,'silver',gtoy,12)
sphere('Robot aerial tip',(1.36,3.00,-.68),(.021,.021,.021),'red',gtoy,12,8)
WING_RIGHT.add(box('Small photo frame',(1.91,2.745,-.71),(.27,.28,.04),'yellow',.016))
WING_RIGHT.add(front('Small abstract print',(1.91,2.745,-.685),.22,.23,'blue'))
WING_RIGHT.add(sphere('Print circle',(1.91,2.76,-.68),(.071,.071,.002),'cream',segments=16,rings=8))
# Handheld console with screen and colored buttons, left desk edge.
box('Mini handheld body',(-1.58,1.412,.31),(.25,.07,.32),'dark',.019)
top('Mini handheld screen',(-1.58,1.451,.28),.17,.145,'green')
for x in [-1.65,-1.61]:cyl('Handheld button',(x,1.455,.409),.014,.008,'red',vertices=12)
box('Handheld dpad',(-1.5,1.453,.40),(.04,.006,.015),'silver',.003)
gp=group('pencil',(1.48,1.38,.50))
rod('Desktop pencil',(1.32,1.38,.54),(1.72,1.38,.37),.011,'yellow',gp,6)
rod('Pencil graphite',(1.72,1.38,.37),(1.76,1.38,.354),.005,'dark',gp,8)
rod('Pencil eraser',(1.285,1.38,.555),(1.32,1.38,.54),.012,'pink',gp,12)
lathe('Desktop pen holder',(1.67,1.367,.02),[(0,.091),(.018,.103),(.23,.098),(.245,.099),(.245,.083),(.02,.08)],'mesh',segments=24)
for i in range(4):rod('Desktop pen',(1.61+i*.034,1.39,.02),(1.60+i*.043,1.77+(i%2)*.04,.025),.009,['silver','dark','red','cream'][i])
box('Desk little closed notebook',(-1.57,1.394,.69),(.33,.037,.30),'dark',.015)
text3('Notebook edge mark','IDEAS',(-1.57,1.396,.849),.02,'gold')

# Mesh chair moved left, preserving the laptop/monitor approach and tap targets.
gch=group('chair',(-1.63,0,1.62))
cx=-1.63;cz=1.62
cyl('Chair gas cylinder',(cx,.47,cz),.038,.72,'silver',gch,24)
cyl('Chair piston sleeve',(cx,.27,cz),.061,.30,'dark',gch,24)
for i in range(5):
    a=i*math.pi*2/5
    end=(cx+math.cos(a)*.50,.11,cz+math.sin(a)*.50)
    rod('Chair base spoke',(cx,.22,cz),end,.027,'mesh',gch)
    for side in [-1,1]:cyl('Chair caster',(end[0]+side*.022,.075,end[2]),.049,.035,'dark',gch,16,(1,0,0))
box('Chair seat cushion',(cx,.86,cz),(.69,.13,.66),'mesh',.095,gch)
box('Chair underseat',(cx,.79,cz),(.43,.061,.37),'dark',.035,gch)
# Forward-facing open mesh back, with curved uprights and the lumbar support.
for dx in [-.32,.32]:
    curve('Chair back frame',[(cx+dx,.90,cz+.24),(cx+dx*1.10,1.18,cz+.36),(cx+dx*1.05,1.65,cz+.35)],.027,'mesh',gch)
curve('Chair back upper frame',[(cx-.33,1.65,cz+.35),(cx,1.69,cz+.39),(cx+.33,1.65,cz+.35)],.029,'mesh',gch)
curve('Chair back lower frame',[(cx-.32,1.07,cz+.32),(cx,1.03,cz+.36),(cx+.32,1.07,cz+.32)],.025,'mesh',gch)
chairface=front('Chair breathable mesh',(cx,1.355,cz+.36),.62,.55,'chairmesh',gch)
uv=chairface.data.uv_layers.active
for l in uv.data:l.uv=(l.uv.x*7,l.uv.y*6)
# A low-cost crossed lattice keeps the fabric readable when alpha texture detail
# is below one pixel. It shares the chair material and becomes one draw call.
for slope in [-1,1]:
    for i in range(-20,21):
        offset=i*.022
        lo=max(-.31,(-.275-offset) if slope==1 else (offset-.275))
        hi=min(.31,(.275-offset) if slope==1 else (offset+.275))
        if hi>lo:
            rod('Chair woven diagonal',(cx+lo,1.355+slope*lo+offset,cz+.361),(cx+hi,1.355+slope*hi+offset,cz+.361),.0017,'mesh',gch,6)
curve('Chair lumbar support',[(cx-.27,1.145,cz+.39),(cx,1.11,cz+.43),(cx+.27,1.145,cz+.39)],.041,'mesh',gch)
for sign in [-1,1]:
    rod('Chair armrest stem',(cx+sign*.31,.82,cz),(cx+sign*.43,1.12,cz),.024,'silver',gch)
    box('Chair soft armrest',(cx+sign*.42,1.14,cz+.005),(.11,.055,.36),'mesh',.035,gch)
# Small offset turn gives the chair a casual, lived-in position.
gch.rotation_euler.z=math.radians(-18)

# Distinctive three-head red lamp. Heads keep their own local hinge pivots.
lx=2.63;lz=.31
lathe('Lamp weighted foot',(lx,0,lz),[(0,.36),(.028,.41),(.085,.405),(.14,.33),(.17,.11)],'red',segments=48)
ring('Lamp base dark seam',(lx,.031,lz),.397,.011,'rededge',segments=48)
cyl('Lamp pole',(lx,1.99,lz),.036,3.76,'rededge',vertices=24)
cyl('Lamp stem highlight',(lx+.012,1.99,lz-.016),.010,3.69,'red',vertices=16)
for i,(y,dx,dz) in enumerate([(3.69,-.36,-.035),(2.68,-.25,.17),(1.79,-.15,.30)],1):
    pivot=(lx+dx,y,lz+dz)
    rod('Lamp articulated arm',(lx,y-.09,lz),pivot,.025,'rededge')
    ring('Lamp clamp',(lx,y-.09,lz),.045,.013,'red',axis=(0,1,0),segments=24)
    g=group('lamp_'+str(i),pivot)
    # Bell shape made along a vertical axis, then rotated around its pivot.
    shade=lathe('Lamp '+str(i)+' bell',pivot,[(0,.066),(.04,.082),(.16,.14),(.32,.24),(.37,.255),(.387,.25),(.387,.232),(.31,.223),(.15,.125),(.035,.057)],'red',g,40)
    inner=lathe('Lamp '+str(i)+' cream lining',pivot,[(.055,.07),(.16,.128),(.313,.221),(.378,.233)],'cream',g,40)
    bulb_material=M['bulb'].copy();bulb_material.name='Warm lamp bulb '+str(i)
    bulb=sphere('lamp_bulb_'+str(i),(pivot[0],pivot[1]+.26,pivot[2]),(.065,.09,.065),bulb_material,g,20,12)
    ring('Lamp '+str(i)+' rolled rim',(pivot[0],pivot[1]+.38,pivot[2]),.245,.009,'rededge',g,segments=40)
    box('Lamp switch',(pivot[0],pivot[1]-.018,pivot[2]),(.036,.048,.041),'dark',.01,g)
    # Y-up local lamp axis points down and into the workspace.
    direction=Vector((-.57,-.72,.32)).normalized()
    g.rotation_mode='QUATERNION';g.rotation_quaternion=B((0,1,0)).rotation_difference(B(direction))
curve('Lamp power cord',[(lx,.17,lz),(2.86,.06,.29),(2.95,.026,.79),(2.57,.025,1.0),(2.28,.027,.64),(2.24,.03,-.33)],.012,'black')

# Place each furnished shelf wing against its own wall of the room corner. The
# authoring coordinates above remain convenient for editing individual objects;
# these parent transforms make the physical corner explicit in the exported asset.
for name,members,oldx,newx,angle in [
    ('workspace_left_wing',WING_LEFT,-1.60,-1.28,45),
    ('workspace_right_wing',WING_RIGHT,1.60,1.28,-45),
]:
    wing=group(name,(oldx,0,-.72));wing['interactive']=False
    for ob in members:
        if ob.parent is None:parent(ob,wing)
    wing.location=B((newx,0,-.48))
    wing.rotation_euler.z=math.radians(angle)
bpy.context.view_layer.update()

# Mesh consolidation minimizes draw calls while preserving object pivots and the
# three replaceable planes. Curves and fonts become regular glTF mesh geometry.
preserve={'monitor_screen','window_glass','Chair breathable mesh'}
for ob in list(bpy.context.scene.objects):
    if ob.type in {'CURVE','FONT'}:
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
        bpy.ops.object.convert(target='MESH')
for ob in list(bpy.context.scene.objects):
    if ob.type=='MESH':
        bpy.context.view_layer.objects.active=ob
        for mod in list(ob.modifiers):
            try:bpy.ops.object.modifier_apply(modifier=mod.name)
            except RuntimeError:pass
# Join material groups only within the same immediate parent, retaining hierarchy.
buckets={}
for ob in list(bpy.context.scene.objects):
    if ob.type!='MESH' or ob.name in preserve:continue
    key=(ob.parent.name if ob.parent else '_static',ob.data.materials[0].name if ob.data.materials else '_none')
    buckets.setdefault(key,[]).append(ob)
for (root,material),objects in buckets.items():
    if len(objects)<2:continue
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:ob.select_set(True)
    active=objects[0];bpy.context.view_layer.objects.active=active
    bpy.ops.object.join();active.name=f'{root} · {material}'

# No AO or lighting is baked into this first pass. Runtime supplies shadows;
# the Cycles preview below is only a composition/material QA render.
# Geometry and materials remain independently editable in the saved .blend.
bpy.context.view_layer.update()
mesh_objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in mesh_objects)
print('Workspace geometry:',len(mesh_objects),'meshes;',triangles,'triangles')

# Exclude preview cameras and lights from the GLB, use website lighting instead.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(OUT/'workspace.glb'),export_format='GLB',use_selection=True,
    export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,
    export_materials='EXPORT',export_texcoords=True,export_normals=True,
    export_image_format='AUTO',export_unused_images=False)

# Editorial, eye-level three-quarter preview close to the website composition.
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.world.color=(.25,.25,.25)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.36,.37,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.48
def area(name,pos,target,power,color,size):
    bpy.ops.object.light_add(type='AREA',location=B(pos));light=bpy.context.object;light.name=name
    light.data.energy=power;light.data.color=color;light.data.shape='DISK';light.data.size=size
    light.rotation_euler=(B(target)-light.location).to_track_quat('-Z','Y').to_euler()
area('Warm overhead softbox',(-1.5,5.2,2.2),(0,1.5,0),580,(1,.79,.53),4.0)
area('Front fill',(1,4.3,5),(0,2,0),260,(.84,.91,1),4)
area('Monitor bounce',(0,2.0,-.22),(0,1.4,.7),18,(.78,.89,.60),1.2)
for y in [1.72,2.66,3.65]:
    area('Red lamp practical',(2.29,y,.45),(0,y-.3,-.35),42,(1,.69,.33),.42)
bpy.ops.object.camera_add(location=B((3.6,4.6,8.6)))
camera=bpy.context.object;camera.name='Workspace overview camera'
camera.rotation_euler=(B((0,2.2,-.30))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=7.55;camera.data.lens=44
scene.camera=camera
scene.render.resolution_x=1500;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ART/'workspace-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'workspace.blend'))
if '--render' in sys.argv:bpy.ops.render.render(write_still=True)
manifest={
 'file':'/models/workspace.glb','triangles':triangles,'meshCount':len(mesh_objects),
 'bytes':(OUT/'workspace.glb').stat().st_size,
 'coordinateSystem':'Y up, Z toward visitor; Blender source uses X, -Z, Y',
 'screen':{'name':'monitor_screen','center':[0,2.12,-.325],'width':1.72,'height':.98},
 'interactiveRoots':{o.name:[round(v,4) for v in (o.matrix_world.translation.x,o.matrix_world.translation.z,-o.matrix_world.translation.y)] for o in scene.objects if o.type=='EMPTY' and o.get('interactive')},
 'corner':{'angleDegrees':90,'rearApex':[0,0,-2.55],'deskRearApex':[0,1.31,-2.34],'leftShelfYawDegrees':45,'rightShelfYawDegrees':-45},
}
(OUT/'workspace.manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
