import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { DeskCameraOrbit } from './camera-orbit';
import { WorkspaceCat } from './cat';
import savedLighting from '../../../public/models/workspace-saved.manifest.json';
import { assetUrl, views, mobileViews, scenePalette, presentationLighting, viewObjects, objectBindings, motionDuration, idleDelay, cursorFraming, type ViewId } from './config';

export type MonitorProject = { title: string; image: string | null; href: string; category: string; year: string; description: string };
export type ScreenRect = { left: number; top: number; width: number; height: number };
export type CameraNavigationState = { enabled: boolean; dragging: boolean; modified: boolean; canZoomIn: boolean; canZoomOut: boolean; zoom: number };
type CameraPointer = { x: number; y: number; startX: number; startY: number; capture: HTMLElement; hotspot: HTMLButtonElement | null };
type SceneOptions = {
  mount: HTMLElement; hotspots: HTMLElement; reducedMotion: boolean;
  projects: MonitorProject[];
  onProgress: (progress: number, detail: string) => void;
  onReady: () => void; onError: (message: string) => void;
  onObject: (name: string, source?: HTMLElement) => void;
  onMeow: () => void;
  onHover: (label: string | null, x: number, y: number) => void;
};
type Selection = { object: THREE.Object3D; initial: THREE.Vector3; rotation: THREE.Euler; anchor: THREE.Vector3; button: HTMLButtonElement; impulse: number; hover: number; };
type Transition = { start: number; duration: number; from: THREE.Vector3; to: THREE.Vector3; targetFrom: THREE.Vector3; targetTo: THREE.Vector3; fovFrom: number; fovTo: number; resolve: (finished: boolean) => void; };

export class DeskScene {
  private scene = new THREE.Scene();
  private camera = new THREE.PerspectiveCamera(37, 1, .1, 60);
  private renderer: THREE.WebGLRenderer;
  private raycaster = new THREE.Raycaster();
  private pointer = new THREE.Vector2();
  private cursor = new THREE.Vector2();
  private parallax = new THREE.Vector2();
  private framingOffset = new THREE.Vector3();
  private framedTarget = new THREE.Vector3();
  private baseCamera = new THREE.Vector3();
  private target = new THREE.Vector3(0, 2.05, 0);
  private selected = new Map<string, Selection>();
  private hoverName: string | null = null;
  private model?: THREE.Group;
  private transition?: Transition;
  private view: ViewId = 'overview';
  private enabled = true;
  private disposed = false;
  private ready = false;
  private isDay = false;
  private raf = 0;
  private lastFrame = 0;
  private lastActivity = performance.now();
  private idle = false;
  private lastSlide = 0;
  private slide = 0;
  private reduced: boolean;
  private lowPower: boolean;
  private frameSamples: number[] = [];
  private resized: ResizeObserver;
  private screenCanvas = document.createElement('canvas');
  private screenTexture: THREE.CanvasTexture;
  private screenMaterial: THREE.MeshBasicMaterial;
  private screenMesh?: THREE.Mesh;
  private computerMode = false;
  private environment: THREE.WebGLRenderTarget;
  private hemi: THREE.HemisphereLight;
  private key: THREE.DirectionalLight;
  private fill: THREE.DirectionalLight;
  private lampLights: THREE.PointLight[] = [];
  private lamps = [true, true, true];
  private abort = new AbortController();
  private timeout?: ReturnType<typeof setTimeout>;
  private orbit = new DeskCameraOrbit();
  private cameraPointers = new Map<number, CameraPointer>();
  private cameraDragging = false;
  private cameraGestureMoved = false;
  private pinchDistance = 0;
  private suppressClickUntil = 0;
  private viewport = { width: 1, height: 1 };
  private idleTimer?: ReturnType<typeof setTimeout>;
  private hunting = false;
  private hinges = new Map<string, { object: THREE.Object3D; base: THREE.Euler; position: THREE.Vector3; amount: number }>();
  private zero = new THREE.Vector2();
  private focusTargets = new Map<ViewId, THREE.Vector3>();
  private bakedMaps = new Map<string, THREE.Texture>();
  private authoredLights: THREE.Light[] = [];
  private cat?: WorkspaceCat;

  constructor(private options: SceneOptions) {
    this.reduced = options.reducedMotion;
    this.lowPower = window.innerWidth < 761 || navigator.hardwareConcurrency <= 4 || (navigator as Navigator & {deviceMemory?: number}).deviceMemory! <= 4;
    this.renderer = new THREE.WebGLRenderer({ antialias: !this.lowPower, alpha: true, powerPreference: 'low-power' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, this.lowPower ? 1.35 : 1.7));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.AgXToneMapping;
    this.renderer.toneMappingExposure = 1;
    // Mobile keeps the exported indirect lighting and avoids three extra shadow renders.
    this.renderer.shadowMap.enabled = !this.lowPower;
    options.mount.dataset.realtimeShadows = String(!this.lowPower);
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.shadowMap.autoUpdate = false;
    this.renderer.setClearColor(0x000000, 0);
    options.mount.append(this.renderer.domElement);
    const pmrem = new THREE.PMREMGenerator(this.renderer), room = new RoomEnvironment();
    this.environment = pmrem.fromScene(room, .06);
    this.scene.environment = this.environment.texture;
    this.scene.environmentIntensity = presentationLighting.night.environment;
    room.dispose(); pmrem.dispose();
    this.hemi = new THREE.HemisphereLight(0xffecd0, 0x908475, presentationLighting.night.hemisphere);
    this.scene.add(this.hemi);
    this.key = new THREE.DirectionalLight(0xffe0b0, 3.5);
    this.key.position.set(-3, 7, 5);
    this.key.castShadow = !this.lowPower;
    this.key.shadow.mapSize.set(this.lowPower ? 1024 : 2048, this.lowPower ? 1024 : 2048);
    Object.assign(this.key.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: .5, far: 18 });
    this.key.shadow.normalBias = .025;
    this.key.shadow.bias = -.00015;
    this.key.shadow.radius = 3;
    this.scene.add(this.key);
    this.fill = new THREE.DirectionalLight(0xb1c6ea, .6);
    this.fill.position.set(4, 4, -2); this.scene.add(this.fill);
    [[2.6,3.4,.7],[2.6,2.6,.7],[2.6,1.65,.7]].forEach(p => {
      const light = new THREE.PointLight(0xffb45d, 2.5, 3.5, 2); light.position.set(p[0],p[1],p[2]); this.lampLights.push(light); this.scene.add(light);
    });
    this.installSavedLighting();
    this.screenCanvas.width = 1024; this.screenCanvas.height = 576;
    this.screenTexture = new THREE.CanvasTexture(this.screenCanvas);
    this.screenTexture.colorSpace = THREE.SRGBColorSpace;
    this.screenTexture.flipY = false;
    this.screenMaterial = new THREE.MeshBasicMaterial({ map: this.screenTexture, toneMapped: false });
    this.drawScreen();
    // Font loading does not hold up the room's first render.
    void document.fonts.load('500 48px "IBM Plex Sans"').then(() => {
      if (!this.disposed) { this.drawScreen(); this.wake(); }
    }).catch(() => { /* The system sans fallback keeps the screen readable. */ });
    options.mount.dataset.view = this.view;
    options.mount.dataset.computerMode = 'false';
    this.publishCameraState();
    this.resized = new ResizeObserver(() => this.resize()); this.resized.observe(options.mount);
    this.resize();
    this.events();
  }

  async load() {
    const loader = new GLTFLoader();
    this.timeout = setTimeout(() => { if (!this.ready) this.options.onError('The room is taking longer than expected. You can keep browsing every section while it loads.'); }, 25000);
    try {
      this.options.onProgress(3, 'Loading the Blender scene.');
      const gltf = await loader.loadAsync(assetUrl, progress => {
        if (this.disposed) return;
        const fraction = progress.total > 0 ? progress.loaded / progress.total : Math.min(progress.loaded / 6000000, .94);
        this.options.onProgress(Math.min(92, Math.round(5 + fraction * 87)), 'Unpacking the desk, textures, and shelf objects.');
      });
      if (this.disposed) { this.disposeModel(gltf.scene); return; }
      this.model = gltf.scene;
      const atlasNames = new Set<string>();
      this.model.traverse(object => {if(object.userData.bakedAtlas)atlasNames.add(object.userData.bakedAtlas);});
      const textureLoader = new THREE.TextureLoader();
      await Promise.all([...atlasNames].map(async name => {
        const texture = await textureLoader.loadAsync(`/textures/workspace/saved-bake/${name}-indirect.webp?v=${savedLighting.revision}`);
        texture.colorSpace = THREE.NoColorSpace;
        texture.flipY = false;
        texture.channel = 1;
        texture.anisotropy = Math.min(8,this.renderer.capabilities.getMaxAnisotropy());
        this.bakedMaps.set(name,texture);
      }));
      let geometryTriangles = 0;
      this.model.traverse(object => {
        const mesh = object as THREE.Mesh;
        if (mesh.isMesh) {
          geometryTriangles += (mesh.geometry.index?.count ?? mesh.geometry.attributes.position.count) / 3;
          mesh.castShadow = true; mesh.receiveShadow = true;
          if (mesh.userData.interactionOnly) {
            // Photographed stickers provide the appearance; named meshes keep
            // their bounds/raycast targets without drawing extra discs on top.
            mesh.visible = false; mesh.castShadow = false; mesh.receiveShadow = false;
          }
          if(mesh.userData.bakedAtlas && mesh.userData.bakedUV===0 && !mesh.geometry.getAttribute('uv1')) {
            mesh.geometry.setAttribute('uv1',mesh.geometry.getAttribute('uv').clone());
          }
          const materials=Array.isArray(mesh.material)?mesh.material:[mesh.material];
          for(const material of materials) {
            const surface=material as THREE.MeshStandardMaterial;
            if(surface.map)surface.map.anisotropy=Math.min(surface.name==='Laptop sticker collage'?16:8,this.renderer.capabilities.getMaxAnisotropy());
            if(surface.name==='Certificate · Anti-reflection glazing') {
              mesh.castShadow=false;mesh.receiveShadow=false;surface.depthWrite=false;
            }
            // Detail normals keep their own UV channel; the bake atlas can now
            // follow it on UV2 rather than always occupying UV1.
            const atlasName=mesh.userData.bakedAtlas;
            const atlasChannel=mesh.userData.bakedUV===0?1:(mesh.userData.bakedUV??1);
            const atlasKey=`${atlasName}:${atlasChannel}`;
            let lightMap=this.bakedMaps.get(atlasKey);
            if(!lightMap && this.bakedMaps.has(atlasName)) {
              lightMap=this.bakedMaps.get(atlasName)!.clone();
              lightMap.channel=atlasChannel;this.bakedMaps.set(atlasKey,lightMap);
            }
            if(lightMap){surface.lightMap=lightMap;surface.lightMapIntensity=presentationLighting.indirect;surface.needsUpdate=true;}
          }
          if (/monitor_screen/.test(mesh.name)) { mesh.material = this.screenMaterial; this.screenMesh = mesh; }
        }
      });
      this.options.mount.dataset.geometryTriangles = String(geometryTriangles);
      this.scene.add(this.model);
      this.model.updateMatrixWorld(true);
      const chair=this.model.getObjectByName('chair');
      if(chair){
        // Keep the measured cushion point local while opening the seat toward the room.
        chair.userData.catSeatLocal=chair.worldToLocal(new THREE.Vector3(-.36,.767,-.31)).toArray();
        chair.rotation.y-=THREE.MathUtils.degToRad(18);
        chair.updateMatrixWorld(true);
      }
      for (const [name, binding] of Object.entries(objectBindings)) {
        const object = this.model.getObjectByName(name);
        if (!object) continue;
        const bounds = new THREE.Box3().setFromObject(object, true), center = bounds.getCenter(new THREE.Vector3());
        const button = document.createElement('button');
        button.className = 'ws-hotspot'; button.dataset.object = name; button.ariaLabel = binding.label;
        button.dataset.kind = binding.section ? 'content' : 'playful';
        if (binding.action === 'sticker') button.dataset.sticker = 'true';
        button.title = binding.label;
        const label = document.createElement('span'); label.textContent = binding.label; button.append(label);
        if (name === 'monitor') {
          button.dataset.primary = 'true';
          const screen=this.model.getObjectByName('monitor_screen');
          if(screen){const bounds=new THREE.Box3().setFromObject(screen, true);bounds.getCenter(center);const size=bounds.getSize(new THREE.Vector3());center.x+=size.x*.36;center.y-=size.y*.26;center.z+=.015;}
        }
        button.addEventListener('click', () => this.activate(name, button), { signal: this.abort.signal });
        button.addEventListener('focus', () => { this.hoverName = name; this.wake(); }, { signal: this.abort.signal });
        button.addEventListener('blur', () => { this.hoverName = null; this.wake(); }, { signal: this.abort.signal });
        this.options.hotspots.append(button);
        this.selected.set(name, { object, initial: object.position.clone(), rotation: object.rotation.clone(), anchor: object.worldToLocal(center), button, impulse: -Infinity, hover: 0 });
      }
      for (const name of ['figma_lid', 'books_cover']) {
        const object = this.model.getObjectByName(name);
        if (object) this.hinges.set(name, { object, base: object.rotation.clone(), position: object.position.clone(), amount: 0 });
      }
      for(const [view,name] of Object.entries(viewObjects)) {
        const object=this.model.getObjectByName(name);
        if(object)this.focusTargets.set(view as ViewId,new THREE.Box3().setFromObject(object, true).getCenter(new THREE.Vector3()));
      }
      const screen=this.model.getObjectByName('monitor_screen');
      if(screen)this.focusTargets.set('work',new THREE.Box3().setFromObject(screen, true).getCenter(new THREE.Vector3()));
      this.lampLights.forEach((light,index)=>{const lamp=this.model?.getObjectByName(`lamp_${index+1}`);if(lamp)light.position.copy(lamp.getWorldPosition(new THREE.Vector3())).add(new THREE.Vector3(-.25,-.1,.1));});
      const lampPositions=[1,2,3].map(index=>this.model!.getObjectByName(`lamp_${index}`)?.getWorldPosition(new THREE.Vector3()));
      for(const light of this.authoredLights) {
        if(!light.name.startsWith('Red lamp practical'))continue;
        const rootName=light.userData.lampRoot as string | undefined;
        const root=rootName?this.model.getObjectByName(rootName):undefined;
        if(root && rootName) {
          light.userData.lampIndex=Number(rootName.split('_')[1])-1;
          // Keep both emitter and aim point on the physical shade, including
          // its hover/click motion. attach preserves their exported world pose.
          root.attach(light);
          if(light instanceof THREE.SpotLight)root.attach(light.target);
          continue;
        }
        let nearest=0,distance=Infinity;
        lampPositions.forEach((position,index)=>{if(position && position.distanceToSquared(light.position)<distance){nearest=index;distance=position.distanceToSquared(light.position);}});
        light.userData.lampIndex=nearest;
      }
      this.ready = true;
      this.publishCameraState();
      clearTimeout(this.timeout);
      this.renderer.shadowMap.needsUpdate = true;
      this.options.onProgress(97, 'Finding the light.');
      // Compile shaders before removing the loading state.
      await this.renderer.compileAsync(this.scene, this.camera);
      if (this.disposed) return;
      this.options.onProgress(100, 'Your desk is ready.');
      this.options.onReady();
      // The room is usable before the separately skinned companion loads.
      void WorkspaceCat.load(this.scene, this.model, this.options.mount, this.options.onMeow).then(cat => {
        if(this.disposed){cat.dispose();return;}
        this.cat=cat;cat.setReducedMotion(this.reduced);this.renderer.shadowMap.needsUpdate=true;this.wake();
      }).catch(error=>{
        if(!this.disposed){this.options.mount.dataset.catReady='false';console.warn('Workspace cat could not load',error);}
      });
      this.resize();
      if (!this.reduced && this.view === 'overview') {
        this.baseCamera.add(new THREE.Vector3(.15,.18,.65));
        this.camera.position.copy(this.baseCamera);
        void this.toView('overview', 1100);
      }
      this.wake();
    } catch (error) {
      clearTimeout(this.timeout);
      if (!this.disposed) { console.error('Desk scene failed to load', error); this.options.onError('The 3D room could not load. The navigation and all portfolio pages still work.'); }
    }
  }

  private installSavedLighting() {
    RectAreaLightUniformsLib.init();
    this.key.visible=false;
    this.fill.visible=false;
    this.lampLights.forEach(light=>light.visible=false);
    for(const source of savedLighting.lights) {
      const color=new THREE.Color().setRGB(source.color[0],source.color[1],source.color[2],THREE.LinearSRGBColorSpace);
      let light: THREE.Light;
      if(source.type==='AREA') {
        const width=Math.max(.05,source.size),height=Math.max(.05,source.sizeY);
        light=new THREE.RectAreaLight(color,source.energy/(width*height*Math.PI),width,height);
      } else if(source.type==='SPOT') {
        const spot=new THREE.SpotLight(color,source.energy,12,source.angle/2,Math.max(.6,source.blend),2);
        spot.castShadow=!this.lowPower;
        spot.shadow.mapSize.set(this.lowPower?512:1024,this.lowPower?512:1024);
        spot.shadow.bias=-.0001;spot.shadow.normalBias=.012;
        spot.target.position.fromArray(source.position).add(new THREE.Vector3(...source.direction));
        this.scene.add(spot.target);light=spot;
      } else {
        light=new THREE.PointLight(color,source.energy,12,2);
      }
      light.position.fromArray(source.position);
      light.name=source.name;
      light.userData.lampRoot='lampRoot' in source?source.lampRoot:undefined;
      light.lookAt(light.position.clone().add(new THREE.Vector3(...source.direction)));
      light.userData.authoredIntensity=light.intensity;
      const presentationScale = source.name==='Monitor bounce' ? presentationLighting.monitor
        : source.name==='Desk ceiling warm fill' ? presentationLighting.ceiling
        : source.type==='AREA' ? presentationLighting.areaFill : presentationLighting.practicals;
      light.userData.presentationIntensity=light.intensity*presentationScale;
      light.intensity=light.userData.presentationIntensity;
      this.authoredLights.push(light);this.scene.add(light);
    }
    this.renderer.toneMappingExposure=Math.pow(2,savedLighting.exposure)*presentationLighting.exposure;
  }

  private events() {
    const signal = this.abort.signal, canvas = this.renderer.domElement;
    const stage = this.options.mount.parentElement!;
    this.cameraEvents(stage, signal);
    stage.addEventListener('pointermove', event => {
      if(event.pointerType==='touch'||!this.enabled||this.view!=='overview'||this.cameraPointers.size||this.orbit.modified)return;
      const rect=stage.getBoundingClientRect();
      const x=THREE.MathUtils.clamp((event.clientX-rect.left)/rect.width*2-1,-1,1);
      const y=THREE.MathUtils.clamp(1-(event.clientY-rect.top)/rect.height*2,-1,1);
      // A small neutral zone keeps the primary monitor interaction steady.
      const response=(value:number)=>Math.sign(value)*Math.pow(Math.max(0,(Math.abs(value)-.12)/.88),1.25);
      this.cursor.set(response(x),response(y));this.activity();
    },{signal});
    stage.addEventListener('pointerleave',()=>{this.cursor.set(0,0);this.wake();},{signal});
    canvas.addEventListener('pointermove', event => {
      this.activity();
      if (this.cameraPointers.size) return;
      const rect = canvas.getBoundingClientRect();
      this.pointer.set((event.clientX-rect.left)/rect.width*2-1, -((event.clientY-rect.top)/rect.height)*2+1);
      if (!this.enabled || !this.model) return;
      this.raycaster.setFromCamera(this.pointer, this.camera);
      const hits = this.raycaster.intersectObject(this.model, true);
      let name: string | null = null;
      if (hits[0]) { let node: THREE.Object3D | null = hits[0].object; while(node) { if (this.selected.has(node.name)) { name = node.name; break; } node=node.parent; } }
      this.hoverName = name;
      canvas.style.cursor = name ? 'pointer' : this.canNavigateCamera() ? 'grab' : 'default';
      this.options.onHover(name ? objectBindings[name].label : null, event.clientX-rect.left, event.clientY-rect.top);
      this.wake();
    }, { signal });
    canvas.addEventListener('pointerleave', () => { this.hoverName = null; this.options.onHover(null,0,0); this.wake(); }, { signal });
    canvas.addEventListener('webglcontextlost', event => { event.preventDefault(); this.options.onError('Your browser paused 3D rendering. The portfolio is still available through the navigation.'); }, { signal });
    canvas.addEventListener('webglcontextrestored', () => location.reload(), { signal });
    document.addEventListener('visibilitychange', () => { if(document.hidden) { this.clearCameraGesture();cancelAnimationFrame(this.raf);this.raf=0; } else this.wake(); }, { signal });
  }

  private canNavigateCamera() { return this.ready && this.enabled && !this.computerMode && this.view !== 'computer' && !this.transition && !this.disposed; }

  getNavigationState(): CameraNavigationState {
    const enabled = this.canNavigateCamera();
    return { enabled, dragging: this.cameraDragging, modified: this.orbit.modified,
      canZoomIn: enabled && this.orbit.canZoomIn, canZoomOut: enabled && this.orbit.canZoomOut, zoom: this.orbit.zoom };
  }

  private publishCameraState() {
    const state = this.getNavigationState(), mount = this.options.mount;
    mount.dataset.cameraNavigation = state.enabled ? 'enabled' : 'disabled';
    mount.dataset.cameraDragging = String(state.dragging);
    mount.dataset.cameraModified = String(state.modified);
    mount.dispatchEvent(new CustomEvent<CameraNavigationState>('desk-camera-change', { detail: state, bubbles: true }));
    this.renderer.domElement.style.cursor = state.dragging ? 'grabbing' : this.hoverName ? 'pointer' : state.enabled ? 'grab' : 'default';
  }

  /** Positive values zoom in. Also used by the keyboard-accessible toolbar. */
  zoomBy(direction: number) {
    if (!this.canNavigateCamera() || !Number.isFinite(direction)) return;
    this.orbit.zoomBy(Math.exp(-THREE.MathUtils.clamp(direction, -4, 4) * .09));
    this.cursor.set(0, 0); this.hoverName = null; this.options.onHover(null, 0, 0);
    this.publishCameraState(); this.activity();
  }

  resetCamera() {
    if (!this.canNavigateCamera()) return Promise.resolve(false);
    return this.toView(this.view);
  }

  private clearCameraGesture() {
    // Delete pointers before releasing capture: lostpointercapture can arrive
    // synchronously and must not leave another stale drag behind.
    const pointers = [...this.cameraPointers.entries()];
    if (pointers.length) this.suppressClickUntil = performance.now() + 400;
    this.cameraPointers.clear();
    for (const [id, pointer] of pointers) {
      if (pointer.capture.hasPointerCapture(id)) pointer.capture.releasePointerCapture(id);
    }
    this.cameraDragging = false; this.cameraGestureMoved = false; this.pinchDistance = 0;
    this.publishCameraState();
  }

  private cameraEvents(stage: HTMLElement, signal: AbortSignal) {
    const canvas = this.renderer.domElement;
    const eligibleTarget = (event: Event) => event.target === canvas || event.target instanceof Element && !!event.target.closest('.ws-hotspot');
    const pinchLength = () => {
      const [a, b] = [...this.cameraPointers.values()];
      return a && b ? Math.hypot(a.x - b.x, a.y - b.y) : 0;
    };
    stage.addEventListener('pointerdown', event => {
      if (!this.canNavigateCamera() || !eligibleTarget(event) || event.button !== 0 || this.cameraPointers.size >= 2) return;
      const capture = event.target instanceof HTMLElement ? event.target : canvas;
      const hotspot = capture.closest<HTMLButtonElement>('.ws-hotspot');
      if (!this.cameraPointers.size) { this.cameraGestureMoved = false; this.suppressClickUntil = 0; }
      this.cameraPointers.set(event.pointerId, { x: event.clientX, y: event.clientY, startX: event.clientX, startY: event.clientY, capture, hotspot });
      capture.setPointerCapture(event.pointerId);
      this.cursor.set(0, 0); this.hoverName = null; this.options.onHover(null, 0, 0);
      if (this.cameraPointers.size === 2) {
        this.pinchDistance = pinchLength(); this.cameraDragging = true; this.cameraGestureMoved = true;
      }
      this.publishCameraState(); this.activity();
    }, { signal });
    stage.addEventListener('pointermove', event => {
      const pointer = this.cameraPointers.get(event.pointerId);
      if (!pointer || !this.canNavigateCamera()) return;
      const dx = event.clientX - pointer.x, dy = event.clientY - pointer.y;
      pointer.x = event.clientX; pointer.y = event.clientY;
      if (this.cameraPointers.size === 2) {
        const distance = pinchLength();
        if (distance > 8 && this.pinchDistance > 8) this.orbit.zoomBy(this.pinchDistance / distance);
        this.pinchDistance = distance;
      } else {
        if (!this.cameraDragging && Math.hypot(pointer.x - pointer.startX, pointer.y - pointer.startY) < 6) return;
        const scale = 1.3 / Math.max(300, Math.min(this.viewport.width, this.viewport.height));
        this.orbit.rotate(-dx * scale, -dy * scale);
      }
      this.cameraDragging = true; this.cameraGestureMoved = true;
      event.preventDefault(); this.publishCameraState(); this.activity();
    }, { signal, passive: false });
    stage.addEventListener('pointerup', event => {
      const pointer = this.cameraPointers.get(event.pointerId);
      if (!pointer) return;
      const moved = this.cameraGestureMoved || Math.hypot(event.clientX - pointer.startX, event.clientY - pointer.startY) >= 6;
      this.cameraPointers.delete(event.pointerId);
      if (pointer.capture.hasPointerCapture(event.pointerId)) pointer.capture.releasePointerCapture(event.pointerId);
      if (moved) this.suppressClickUntil = performance.now() + 400;
      // Hotspots keep their native click and keyboard activation. Raycast only
      // taps that began on the canvas, after ruling out drag and pinch gestures.
      if (!moved && !pointer.hotspot && this.canNavigateCamera()) this.activateAt(event.clientX, event.clientY);
      if (!this.cameraPointers.size) {
        this.cameraDragging = false; this.cameraGestureMoved = false; this.pinchDistance = 0;
      } else {
        for (const remaining of this.cameraPointers.values()) { remaining.startX = remaining.x; remaining.startY = remaining.y; }
      }
      this.publishCameraState(); this.activity();
    }, { signal });
    const cancel = (event: PointerEvent) => {
      if (!this.cameraPointers.has(event.pointerId)) return;
      this.suppressClickUntil = performance.now() + 400; this.clearCameraGesture(); this.activity();
    };
    stage.addEventListener('pointercancel', cancel, { signal });
    stage.addEventListener('lostpointercapture', cancel, { signal });
    stage.addEventListener('click', event => {
      // Mouse/touch compatibility clicks after a captured drag must not open a
      // portfolio section. Keyboard clicks have detail=0 and stay untouched.
      if (event.detail > 0 && eligibleTarget(event) && performance.now() < this.suppressClickUntil) { event.preventDefault(); event.stopImmediatePropagation(); }
    }, { signal, capture: true });
    stage.addEventListener('wheel', event => {
      if (!this.canNavigateCamera() || !eligibleTarget(event) || event.ctrlKey || event.metaKey) return;
      const unit = event.deltaMode === WheelEvent.DOM_DELTA_LINE ? 16 : event.deltaMode === WheelEvent.DOM_DELTA_PAGE ? this.viewport.height : 1;
      const delta = THREE.MathUtils.clamp(event.deltaY * unit, -120, 120);
      if (!delta || delta < 0 && !this.orbit.canZoomIn || delta > 0 && !this.orbit.canZoomOut) return;
      event.preventDefault(); this.zoomBy(-delta / 90);
    }, { signal, passive: false });
    window.addEventListener('blur', () => this.clearCameraGesture(), { signal });
  }

  private activateAt(x: number, y: number) {
    if (!this.model) return;
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.pointer.set((x - rect.left) / rect.width * 2 - 1, -((y - rect.top) / rect.height) * 2 + 1);
    this.raycaster.setFromCamera(this.pointer, this.camera);
    const hit = this.raycaster.intersectObject(this.model, true)[0];
    let node: THREE.Object3D | null = hit?.object ?? null;
    while (node) {
      const selected = this.selected.get(node.name);
      if (selected) { this.activate(node.name, selected.button); break; }
      node = node.parent;
    }
  }

  private activate(name: string, source: HTMLElement) {
    if (!this.enabled) return;
    this.pulse(name); this.options.onHover(null,0,0); this.options.onObject(name,source);
  }
  pulse(name: string) { const entry=this.selected.get(name); if(entry && performance.now()-entry.impulse>700) entry.impulse=performance.now(); this.activity(); }
  activity() { this.lastActivity=performance.now(); clearTimeout(this.idleTimer); if(this.idle) {this.idle=false;this.drawScreen();} this.wake(); }
  setEnabled(enabled: boolean) { this.enabled=enabled; this.options.hotspots.inert=!enabled; this.hoverName=null; this.clearCameraGesture(); this.options.onHover(null,0,0); this.wake(); }
  setReducedMotion(reduced: boolean) { this.reduced=reduced; if(reduced)this.skipTransition(); this.wake(); }
  setHunt(value: boolean) { this.hunting = value; for (const [name, entry] of this.selected) if(name.startsWith('sticker_'))entry.button.dataset.hunt=String(value); this.wake(); }

  setComputerMode(active: boolean) {
    this.computerMode = active;
    if (active) this.clearCameraGesture();
    this.publishCameraState();
    this.options.mount.dataset.computerMode = String(active);
    this.idle = false;
    this.lastActivity = performance.now();
    clearTimeout(this.idleTimer);
    // Keep the glass still while it becomes the HTML desktop's entry point.
    const monitor = this.selected.get('monitor');
    if (active && monitor) {
      monitor.impulse = -Infinity; monitor.hover = 0;
      monitor.object.position.copy(monitor.initial);
      monitor.object.rotation.copy(monitor.rotation);
      monitor.object.updateWorldMatrix(true, true);
    }
    this.drawScreen();
    this.wake();
  }

  /** Unclamped screen bounds in browser viewport CSS pixels, suitable for a fixed HTML portal. */
  getScreenRect(): ScreenRect | null {
    const screen = this.screenGeometry();
    if (!screen || !this.ready || this.disposed) return null;
    this.camera.updateMatrixWorld(true);
    const projected = screen.corners.map(corner => corner.clone().project(this.camera));
    // A portal cannot represent a screen crossing the camera's near plane.
    if (projected.some(point => !Number.isFinite(point.x) || !Number.isFinite(point.y) || point.z < -1 || point.z > 1)) return null;
    const rect = this.renderer.domElement.getBoundingClientRect();
    if (!rect.width || !rect.height) return null;
    const left = Math.min(...projected.map(point => point.x));
    const right = Math.max(...projected.map(point => point.x));
    const top = Math.max(...projected.map(point => point.y));
    const bottom = Math.min(...projected.map(point => point.y));
    return {
      left: rect.left + (left + 1) * rect.width / 2,
      top: rect.top + (1 - top) * rect.height / 2,
      width: (right - left) * rect.width / 2,
      height: (top - bottom) * rect.height / 2,
    };
  }

  private screenGeometry() {
    const mesh = this.screenMesh;
    if (!mesh) return null;
    const positions = mesh.geometry.getAttribute('position');
    if (!positions || positions.count < 3) return null;
    mesh.updateWorldMatrix(true, false);
    // Project the actual screen vertices, rather than an axis-aligned world box.
    const corners = Array.from({ length: positions.count }, (_, index) =>
      new THREE.Vector3().fromBufferAttribute(positions, index).applyMatrix4(mesh.matrixWorld));
    const center = new THREE.Box3().setFromPoints(corners).getCenter(new THREE.Vector3());
    const normals = mesh.geometry.getAttribute('normal');
    const normal = new THREE.Vector3();
    if (normals) {
      for (let index = 0; index < normals.count; index++) normal.add(new THREE.Vector3().fromBufferAttribute(normals, index));
      normal.applyNormalMatrix(new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld));
    } else {
      for (let index = 2; index < corners.length && normal.lengthSq() < 1e-12; index++) {
        normal.crossVectors(corners[1].clone().sub(corners[0]), corners[index].clone().sub(corners[0]));
      }
      normal.normalize();
    }
    if (normal.lengthSq() < 1e-12) return null;
    // Some exports reverse winding. Always approach from the room side.
    if (normal.dot(new THREE.Vector3(...views.overview.position).sub(center)) < 0) normal.negate();
    return { corners, center, normal };
  }

  toView(view: ViewId, duration = motionDuration): Promise<boolean> {
    this.transition?.resolve(false); this.transition=undefined;
    this.clearCameraGesture();
    // Start object transitions at the currently visible framing, not the neutral pose.
    this.baseCamera.copy(this.camera.position);
    this.target.add(this.framingOffset);
    this.orbit.reset();
    this.parallax.set(0,0);this.cursor.set(0,0);this.framingOffset.set(0,0,0);
    this.view=view;
    this.options.mount.dataset.view=view;
    const next=this.cameraView(view);
    if(this.reduced || duration===0) {
      this.baseCamera.fromArray(next.position);this.target.fromArray(next.target);this.camera.fov=next.fov;this.camera.updateProjectionMatrix();this.camera.position.copy(this.baseCamera);this.camera.lookAt(this.target);this.publishCameraState();this.wake();return Promise.resolve(true);
    }
    return new Promise(resolve => {
      this.transition={start:performance.now(),duration,from:this.baseCamera.clone(),to:new THREE.Vector3(...next.position),targetFrom:this.target.clone(),targetTo:new THREE.Vector3(...next.target),fovFrom:this.camera.fov,fovTo:next.fov,resolve};this.publishCameraState();this.wake();
    });
  }
  skipTransition() {
    const transition=this.transition;if(!transition)return;
    this.baseCamera.copy(transition.to);this.target.copy(transition.targetTo);this.camera.fov=transition.fovTo;this.camera.updateProjectionMatrix();this.camera.position.copy(this.baseCamera);this.camera.lookAt(this.target);this.transition=undefined;transition.resolve(true);this.publishCameraState();this.wake();
  }
  private cameraView(view: ViewId) {
    if (view === 'computer') {
      const screen = this.screenGeometry();
      if (screen) {
        const { center, normal, corners } = screen;
        const right = new THREE.Vector3().crossVectors(this.camera.up, normal).normalize();
        if (right.lengthSq() < 1e-12) right.set(1, 0, 0);
        const up = new THREE.Vector3().crossVectors(normal, right).normalize();
        const halfWidth = Math.max(...corners.map(corner => Math.abs(corner.clone().sub(center).dot(right))));
        const halfHeight = Math.max(...corners.map(corner => Math.abs(corner.clone().sub(center).dot(up))));
        const tangent = Math.tan(THREE.MathUtils.degToRad(views.computer.fov / 2));
        // Cover the viewport with a little overscan, while staying in front of the glass.
        // Portrait devices crop the sides for the final handoff to the responsive HTML desktop.
        const distance = Math.max(this.camera.near + .025, .985 * Math.min(
          halfHeight / tangent,
          halfWidth / (tangent * this.viewport.width / this.viewport.height),
        ));
        return { position: center.clone().addScaledVector(normal, distance).toArray(), target: center.toArray(), fov: views.computer.fov };
      }
      return views.computer;
    }
    // Content stays usable before the separately sourced bicycle is installed.
    const guided = view==='expeditions' && !this.focusTargets.has(view) ? 'overview' : view;
    if(guided==='overview' || guided==='desk-detail' || guided==='shelf-detail') {
      const composition = window.innerWidth <= 760 ? mobileViews[guided] ?? views[guided] : views[guided];
      const target=new THREE.Vector3(...composition.target);
      const offset=new THREE.Vector3(...composition.position).sub(target);
      const aspect=this.viewport.width/this.viewport.height;
      // Narrow windows retain usable tap targets without cutting off both shelf wings.
      offset.multiplyScalar(Math.max(1,(window.innerWidth<=760?.72:1.18)/aspect));
      return {position:target.clone().add(offset).toArray(),target:composition.target,fov:composition.fov};
    }
    const focus=this.focusTargets.get(view);
    if(focus){const offset=new THREE.Vector3(...views[view].position).sub(new THREE.Vector3(...views[view].target));if(view==='expeditions'||view==='achievements')offset.multiplyScalar(Math.max(1,.62/(this.viewport.width/this.viewport.height)));return {position:focus.clone().add(offset).toArray(),target:focus.toArray(),fov:views[view].fov};}
    return views[view];
  }
  private resize() {
    const {width,height}=this.options.mount.getBoundingClientRect();if(!width||!height)return;
    this.viewport = { width, height };
    this.renderer.setSize(width,height,false);this.camera.aspect=width/height;
    if(!this.transition) { const view=this.cameraView(this.view);this.baseCamera.fromArray(view.position);this.target.fromArray(view.target);this.camera.fov=view.fov; }
    else if(this.view==='computer') { const view=this.cameraView('computer');this.transition.to.fromArray(view.position);this.transition.targetTo.fromArray(view.target);this.transition.fovTo=view.fov; }
    this.camera.updateProjectionMatrix();this.wake();
  }

  setDay(day: boolean) {
    this.isDay=day;
    const lighting=day?presentationLighting.day:presentationLighting.night;
    this.hemi.color.set(day?0xe8f2ff:0xffecd0);this.hemi.intensity=lighting.hemisphere;
    this.key.color.set(day?0xfff2d8:0xffd39b);this.key.intensity=day?2.8:1.25;
    this.fill.intensity=day?.55:.16;
    this.authoredLights.forEach(light=>{const index=light.userData.lampIndex;light.intensity=light.userData.presentationIntensity*(index===undefined||this.lamps[index]?1:0)*(day?.65:1);});
    this.key.visible=day;
    this.scene.environmentIntensity=lighting.environment;
    this.model?.traverse(object=>{
      const mesh=object as THREE.Mesh;
      if(mesh.isMesh && /window_glass/.test(mesh.name)) {
        const material=(mesh.material as THREE.MeshStandardMaterial);
        material.color.set(day?0xa3c7d0:0x101e32);
        material.emissive?.set(day?0x829c9e:0x0b1525);
        material.emissiveIntensity=day?.35:.16;
      }
      if(/night_(star|city)|Distant[ _]warm[ _]windows/.test(object.name))object.visible=!day;
    });
    this.screenMaterial.color.setScalar(day?.78:1);this.drawScreen();this.renderer.shadowMap.needsUpdate=true;this.wake();
  }
  toggleLamp(index: number) {
    this.lamps[index]=!this.lamps[index];this.lampLights[index].intensity=this.lamps[index]?2.5:0;
    this.authoredLights.forEach(light=>{if(light.userData.lampIndex===index)light.intensity=this.lamps[index]?light.userData.presentationIntensity*(this.isDay?.65:1):0;});
    const root=this.selected.get(`lamp_${index+1}`)?.object;
    root?.traverse(object=>{const mesh=object as THREE.Mesh;if(mesh.isMesh&&/bulb|diffuser/.test(mesh.name)){ const m=mesh.material as THREE.MeshStandardMaterial;m.emissiveIntensity=this.lamps[index]?2:0;m.color?.set(this.lamps[index]?0xffdda0:0xaaa090); }});
    this.wake();return this.lamps[index];
  }
  private drawScreen() {
    const ctx = this.screenCanvas.getContext('2d')!;
    const palette = scenePalette;
    const sans = '"IBM Plex Sans", Arial, sans-serif';
    const mono = '"IBM Plex Mono", monospace';
    ctx.textAlign = 'left';
    ctx.fillStyle = palette.background; ctx.fillRect(0, 0, 1024, 576);
    ctx.fillStyle = palette.panel; ctx.fillRect(0, 0, 1024, 72);
    ctx.fillStyle = palette.muted; ctx.font = `18px ${mono}`;
    ctx.fillText('PERSONAL COMPUTER', 64, 45);
    ctx.fillStyle = palette.red; ctx.beginPath(); ctx.arc(943, 37, 7, 0, Math.PI * 2); ctx.fill();

    ctx.fillStyle = palette.ivory; ctx.font = `500 78px ${sans}`;
    ctx.fillText('Aadith’s', 64, 180); ctx.fillText('desktop.', 64, 259);
    ctx.fillStyle = palette.muted; ctx.font = `25px ${sans}`;
    ctx.fillText('Selected work and things in progress.', 67, 312);
    ctx.fillStyle = palette.red; ctx.beginPath(); ctx.roundRect(64, 364, 325, 66, 5); ctx.fill();
    ctx.fillStyle = palette.background; ctx.font = `500 25px ${sans}`;
    ctx.fillText(this.computerMode ? 'Opening desktop' : 'Enter desktop', 88, 406);
    ctx.strokeStyle = palette.background; ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.moveTo(342, 405); ctx.lineTo(355, 392); ctx.moveTo(342, 392); ctx.lineTo(355, 392); ctx.lineTo(355, 405); ctx.stroke();

    // A single folder preview echoes the HTML desktop without adding a second UI system.
    ctx.fillStyle = palette.raised; ctx.beginPath(); ctx.roundRect(614, 127, 326, 310, 8); ctx.fill();
    ctx.strokeStyle = palette.muted; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.roundRect(703, 155, 98, 118, 3); ctx.stroke();
    ctx.beginPath(); ctx.roundRect(744, 169, 102, 116, 3); ctx.stroke();
    ctx.fillStyle = palette.red;
    ctx.beginPath(); ctx.moveTo(672, 208); ctx.lineTo(672, 190); ctx.quadraticCurveTo(672, 182, 680, 182);
    ctx.lineTo(735, 182); ctx.lineTo(754, 208); ctx.lineTo(865, 208); ctx.quadraticCurveTo(873, 208, 873, 216);
    ctx.lineTo(873, 321); ctx.quadraticCurveTo(873, 329, 865, 329); ctx.lineTo(680, 329); ctx.quadraticCurveTo(672, 329, 672, 321); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = palette.brightRed; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(684, 222); ctx.lineTo(861, 222); ctx.stroke();
    const project = this.idle && !this.computerMode && this.options.projects.length
      ? this.options.projects[this.slide % this.options.projects.length] : undefined;
    ctx.fillStyle = palette.ivory; ctx.font = `500 27px ${sans}`;
    let title = project?.title ?? 'Selected work';
    if (ctx.measureText(title).width > 270) {
      while (ctx.measureText(`${title}…`).width > 270) title = title.slice(0, -1);
      title += '…';
    }
    ctx.fillText(title, 642, 382);
    ctx.fillStyle = palette.muted; ctx.font = `17px ${mono}`; ctx.fillText('PROJECTS / WRITING / LAB', 642, 410);

    ctx.fillStyle = palette.panel; ctx.fillRect(0, 491, 1024, 85);
    ctx.fillStyle = palette.muted; ctx.font = `18px ${mono}`;
    ctx.fillText(this.computerMode ? 'MAKE YOURSELF AT HOME' : 'A FEW FOLDERS. A LOT TO EXPLORE.', 64, 539);
    ctx.textAlign = 'right'; ctx.fillStyle = palette.ivory; ctx.fillText(this.computerMode ? 'READY' : 'OPEN ↗', 946, 539); ctx.textAlign = 'left';
    if (this.screenTexture) this.screenTexture.needsUpdate = true;
  }

  private wake() { if(!this.raf&&!this.disposed&&!document.hidden)this.raf=requestAnimationFrame(time=>this.frame(time)); }
  private frame(now: number) {
    this.raf=0;if(this.disposed||document.hidden)return;
    const frameDelta=now-this.lastFrame;
    if(this.lowPower&&frameDelta<31){this.wake();return;}
    const dt=Math.min(frameDelta/1000,.08)||.016;this.lastFrame=now;
    if(this.transition){const t=this.transition,p=Math.min((now-t.start)/t.duration,1),e=p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2;this.baseCamera.lerpVectors(t.from,t.to,e);this.target.lerpVectors(t.targetFrom,t.targetTo,e);this.camera.fov=THREE.MathUtils.lerp(t.fovFrom,t.fovTo,e);this.camera.updateProjectionMatrix();if(p===1){this.transition=undefined;t.resolve(true);this.publishCameraState();}}
    const orbitMoving = this.orbit.step(dt, this.reduced || this.cameraDragging);
    const parallaxAllowed=!this.reduced&&this.view==='overview'&&this.enabled&&!this.transition&&!this.cameraPointers.size&&!this.orbit.modified;
    this.parallax.lerp(parallaxAllowed?this.cursor:this.zero,1-Math.exp(-dt*cursorFraming.damping));
    this.framingOffset.set(this.parallax.x*cursorFraming.horizontal,this.parallax.y*(this.parallax.y>0?cursorFraming.up:cursorFraming.down),0);
    this.camera.position.copy(this.baseCamera);
    if (!this.transition && this.view !== 'computer') this.orbit.apply(this.camera.position, this.target);
    this.camera.position.add(this.framingOffset);
    this.framedTarget.copy(this.target).add(this.framingOffset);
    this.camera.lookAt(this.framedTarget);
    this.options.mount.dataset.cameraTargetY=this.framedTarget.y.toFixed(3);
    this.options.mount.dataset.cameraYaw=this.orbit.yaw.toFixed(5);
    this.options.mount.dataset.cameraPitch=this.orbit.pitch.toFixed(5);
    this.options.mount.dataset.cameraZoom=(1 / this.orbit.distance).toFixed(5);
    let moving=false;
    for (const [name, hinge] of this.hinges) {
      const destination = name === 'figma_lid' ? this.view === 'design' : this.view === 'writing';
      const next = destination ? 1 : 0;
      hinge.amount = this.reduced ? next : THREE.MathUtils.lerp(hinge.amount, next, 1 - Math.exp(-dt * 7));
      hinge.object.rotation.copy(hinge.base);
      hinge.object.position.copy(hinge.position);
      if(hinge.object.userData.openingMotion === 'lift') {
        hinge.object.position.y += Math.min(1, hinge.amount / .65) * (hinge.object.userData.openingDistance ?? .17);
        const reveal = THREE.MathUtils.smoothstep(hinge.amount, .68, 1);
        hinge.object.position.z += reveal * (hinge.object.userData.openingForward ?? 0);
      }
      else if(name === 'figma_lid')hinge.object.rotation.x -= hinge.amount * .85;
      else hinge.object.rotation.y -= hinge.amount * .7;
      if(Math.abs(hinge.amount-next)>.002)moving=true;
    }
    const {width,height}=this.viewport;
    for(const [name,s] of this.selected){
      const binding=objectBindings[name],desired=this.hoverName===name&&this.enabled?1:0;
      s.hover=THREE.MathUtils.lerp(s.hover,desired,1-Math.exp(-dt*11));
      const elapsed=(now-s.impulse)/1000,impulse=elapsed<1.5?Math.sin(elapsed*12)*Math.exp(-elapsed*3.7):0;
      const still=this.reduced || (name==='monitor' && (this.computerMode || this.view==='computer'));
      const h=still?0:s.hover,p=still?0:impulse;
      s.object.position.copy(s.initial);s.object.rotation.copy(s.rotation);
      if(binding.motion==='book'){s.object.position.z+=h*.065;s.object.rotation.y+=p*.075;}
      else if(binding.motion==='paper'){s.object.position.z+=h*.02;s.object.rotation.x+=h*.025+p*.035;}
      else if(binding.motion==='metal'){s.object.rotation.z+=h*.026+p*.09;}
      else if(binding.motion==='plant'){s.object.rotation.z+=p*.08;s.object.rotation.x+=p*.035;}
      else if(binding.motion==='chair'){s.object.rotation.y+=p*.28;}
      else if(binding.motion==='lid'){s.object.position.y+=h*.014;s.object.rotation.x+=p*.07;}
      else{s.object.position.y+=h*.01+Math.max(0,p)*.045;s.object.rotation.z+=p*.025;}
      if(Math.abs(p)>.001||Math.abs(s.hover-desired)>.01)moving=true;
      s.object.updateWorldMatrix(true,false);
      const world=s.anchor.clone().applyMatrix4(s.object.matrixWorld),screen=world.clone().project(this.camera);
      s.button.style.left=`${(screen.x*.5+.5)*width}px`;s.button.style.top=`${(-screen.y*.5+.5)*height}px`;
      s.button.hidden=(this.hunting && name==='laptop')||screen.z>1||screen.z< -1||Math.abs(screen.x)>1.08||Math.abs(screen.y)>1.08;
    }
    this.cat?.setReducedMotion(this.reduced);
    const catMoving=this.cat?.update(dt,this.enabled&&!this.computerMode&&this.view!=='computer')??false;
    this.cat?.project(this.camera,width,height);
    if(moving||catMoving)this.renderer.shadowMap.needsUpdate=true;
    if(!this.computerMode&&this.view!=='computer'&&!this.reduced&&this.enabled&&now-this.lastActivity>idleDelay){if(!this.idle||now-this.lastSlide>6500){this.idle=true;this.lastSlide=now;this.slide++;this.drawScreen();}}
    this.renderer.render(this.scene,this.camera);
    // Exposed read-only metrics make QA possible without adding a visitor-facing debug UI.
    this.options.mount.dataset.drawCalls=String(this.renderer.info.render.calls);this.options.mount.dataset.triangles=String(this.renderer.info.render.triangles);this.options.mount.dataset.pixelRatio=String(this.renderer.getPixelRatio());
    if(this.ready&&frameDelta>0&&frameDelta<150){this.frameSamples.push(frameDelta);if(this.frameSamples.length===100){const average=this.frameSamples.reduce((a,b)=>a+b,0)/100;if(average>38&&!this.lowPower){this.lowPower=true;this.renderer.setPixelRatio(1.2);this.renderer.shadowMap.enabled=false;this.options.mount.dataset.realtimeShadows='false';}this.frameSamples=[];}}
    if(this.transition||moving||catMoving||orbitMoving||this.parallax.distanceTo(parallaxAllowed?this.cursor:this.zero)>.001)this.wake();
    else this.scheduleIdle();
  }
  private scheduleIdle() {
    clearTimeout(this.idleTimer);
    if(this.computerMode || this.view==='computer' || this.reduced || !this.enabled || !this.ready || this.disposed || document.hidden)return;
    const delay=this.idle ? Math.max(100,6500-(performance.now()-this.lastSlide)) : Math.max(100,idleDelay-(performance.now()-this.lastActivity));
    this.idleTimer=setTimeout(()=>this.wake(),delay);
  }
  private disposeModel(root: THREE.Object3D) { const materials=new Set<THREE.Material>();root.traverse(object=>{const mesh=object as THREE.Mesh;if(!mesh.isMesh)return;mesh.geometry.dispose();(Array.isArray(mesh.material)?mesh.material:[mesh.material]).forEach(m=>materials.add(m));});materials.forEach(m=>{for(const value of Object.values(m)){if(value instanceof THREE.Texture)value.dispose();}m.dispose();}); }
  dispose(){this.disposed=true;this.clearCameraGesture();cancelAnimationFrame(this.raf);clearTimeout(this.timeout);clearTimeout(this.idleTimer);this.abort.abort();this.resized.disconnect();this.transition?.resolve(false);this.cat?.dispose();if(this.model)this.disposeModel(this.model);this.screenTexture.dispose();this.screenMaterial.dispose();this.environment.dispose();this.renderer.dispose();this.renderer.domElement.remove();this.options.hotspots.replaceChildren();}
}
