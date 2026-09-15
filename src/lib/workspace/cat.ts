import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { makeCatCoatMatte } from './cat-fur';

type Point = [number, number, number];
type Step = { name: string; seconds: number; to?: Point; hidden?: boolean };
const right: Point = [5.8, -.011, 2.2];
const left: Point = [-5.8, -.011, 2.2];

/** Floor-only paths stay in front of the chair casters and balcony plant. */
export class WorkspaceCat {
  readonly root = new THREE.Group();
  private mixer: THREE.AnimationMixer;
  private actions = new Map<string, THREE.AnimationAction>();
  private action?: THREE.AnimationAction;
  private steps: Step[] = [];
  private index = 0;
  private elapsed = 0;
  private from = new THREE.Vector3();
  private destination = new THREE.Vector3();
  private yaw = -Math.PI / 2;
  private initialYaw = this.yaw;
  private cycle = 0;
  private reduced = false;
  private disposed = false;
  private pause = 0;
  private shadow: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
  private shadowTexture: THREE.CanvasTexture;
  readonly button: HTMLButtonElement;
  private center = new THREE.Vector3();
  private head = new THREE.Vector3();

  static async load(scene: THREE.Scene, _room: THREE.Group, mount: HTMLElement, onMeow: () => void) {
    const gltf=await new GLTFLoader().loadAsync('/models/workspace-cat.glb?v=5');
    if(!['Idle','Walk'].every(name=>gltf.animations.some(clip=>clip.name===name))){
      disposeObject(gltf.scene);throw new Error('Cat requires Idle and Walk clips');
    }
    return new WorkspaceCat(scene,mount,gltf.scene,gltf.animations,onMeow);
  }

  private constructor(private scene: THREE.Scene, private mount: HTMLElement, model: THREE.Group, clips: THREE.AnimationClip[], onMeow: () => void) {
    this.root.name='JonasDichelle calico cat';
    model.scale.setScalar(.072);model.position.y=2.88*.072;
    this.root.add(model);makeCatCoatMatte(model);
    model.traverse(object=>{
      const mesh=object as THREE.Mesh;if(!mesh.isMesh)return;
      mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=false;
    });
    this.mixer=new THREE.AnimationMixer(model);
    clips.forEach(clip=>this.actions.set(clip.name,this.mixer.clipAction(clip)));
    const canvas=document.createElement('canvas');canvas.width=canvas.height=64;
    const ctx=canvas.getContext('2d')!;
    const gradient=ctx.createRadialGradient(32,32,2,32,32,31);
    gradient.addColorStop(0,'rgba(0,0,0,.25)');gradient.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=gradient;ctx.fillRect(0,0,64,64);
    this.shadowTexture=new THREE.CanvasTexture(canvas);
    this.shadow=new THREE.Mesh(new THREE.PlaneGeometry(.42,.66),new THREE.MeshBasicMaterial({map:this.shadowTexture,transparent:true,depthWrite:false,toneMapped:false}));
    this.shadow.rotation.x=-Math.PI/2;scene.add(this.root,this.shadow);
    this.button=document.createElement('button');
    this.button.className='ws-cat-hit';this.button.dataset.cat='true';
    this.button.ariaLabel='Pet the cat. Hear a meow.';this.button.title='Pet the cat';
    this.button.addEventListener('click',()=>{this.pause=.9;onMeow();});
    mount.parentElement!.append(this.button);
    this.root.position.fromArray(right);this.buildRoutine();this.begin();
    mount.dataset.catReady='true';
  }

  private buildRoutine() {
    const direction=this.cycle%2===0?-1:1;
    const points: Point[]=[[1.25,-.011,1.0],[.35,-.011,.78],[-.65,-.011,.92],[-1.65,-.011,1.15]];
    if(direction===1)points.reverse();
    this.steps=[];
    let previous=new THREE.Vector3(...(direction===-1?right:left));
    for(const [i,to] of [...points,direction===-1?left:right].entries()){
      const target=new THREE.Vector3(...to);
      this.steps.push({name:i===0?'entering':i===points.length?'leaving':'wandering',seconds:previous.distanceTo(target)/.46,to});
      if(i===1||i===2)this.steps.push({name:'looking-around',seconds:2+Math.random()*3});
      previous=target;
    }
    this.steps.push({name:'outside',seconds:5+Math.random()*7,hidden:true});this.index=0;
    this.mount.dataset.catDirection=direction===-1?'right-to-left':'left-to-right';
  }

  private play(name: string) {
    const next=this.actions.get(name)!;if(next===this.action)return;
    next.reset().setEffectiveWeight(1).setEffectiveTimeScale(name==='Walk'?.87:1).setLoop(THREE.LoopRepeat,Infinity).play();
    this.action?.crossFadeTo(next,.22,false);this.action=next;
  }

  private begin() {
    const step=this.steps[this.index];this.elapsed=0;this.from.copy(this.root.position);this.initialYaw=this.yaw;
    if(step.to){this.destination.fromArray(step.to);this.yaw=Math.atan2(this.destination.x-this.from.x,this.destination.z-this.from.z);}
    this.root.visible=!step.hidden;this.play(step.to?'Walk':'Idle');
    this.mount.dataset.catState=step.name;this.mount.dataset.catCycle=String(this.cycle);
  }

  setReducedMotion(reduced: boolean) {
    if(reduced===this.reduced)return;this.reduced=reduced;
    if(reduced){
      this.root.visible=true;this.root.position.set(.35,-.011,.78);this.play('Idle');
      this.mixer.stopAllAction();this.action=undefined;this.play('Idle');this.mixer.update(0);
      this.mount.dataset.catState='resting-reduced-motion';
    }else{this.root.position.fromArray(this.cycle%2===0?right:left);this.buildRoutine();this.begin();}
  }

  update(dt: number, active: boolean) {
    if(this.disposed)return false;
    if(active&&!this.reduced){
      if(this.pause>0){this.pause=Math.max(0,this.pause-dt);this.play('Idle');}
      else{
        const step=this.steps[this.index];this.play(step.to?'Walk':'Idle');this.elapsed+=dt;
        if(step.to)this.root.position.lerpVectors(this.from,this.destination,Math.min(1,this.elapsed/step.seconds));
        if(this.elapsed>=step.seconds){this.index++;if(this.index===this.steps.length){this.cycle++;this.buildRoutine();}this.begin();}
      }
      this.mixer.update(dt);
    }
    const difference=Math.atan2(Math.sin(this.yaw-this.initialYaw),Math.cos(this.yaw-this.initialYaw));
    this.root.rotation.y=this.initialYaw+difference*THREE.MathUtils.smoothstep(this.elapsed,0,.5);
    this.shadow.visible=this.root.visible;this.shadow.position.copy(this.root.position);this.shadow.position.y+=.006;this.shadow.rotation.z=-this.yaw;
    this.button.disabled=!active;
    this.mount.dataset.catPosition=this.root.position.toArray().map(n=>n.toFixed(3)).join(',');
    return active&&!this.reduced;
  }

  project(camera: THREE.Camera, width: number, height: number) {
    // Two small targets along the body cover the clickable silhouette without
    // taking over the floor or nearby furniture. A native button supports touch and keyboard.
    this.center.set(0,.26,0);this.root.localToWorld(this.center);this.center.project(camera);
    this.head.set(0,.4,.23);this.root.localToWorld(this.head);this.head.project(camera);
    const x=(this.center.x*.5+.5)*width,y=(-this.center.y*.5+.5)*height;
    this.button.hidden=!this.root.visible||this.center.z>1||Math.abs(this.center.x)>1.03||Math.abs(this.center.y)>1.03;
    this.button.style.left=`${x}px`;this.button.style.top=`${y}px`;
    this.button.style.width=`${Math.max(44,Math.min(100,Math.abs(this.head.x-this.center.x)*width+30))}px`;
    this.button.style.height='54px';
  }

  dispose(){
    this.disposed=true;this.button.remove();this.mixer.stopAllAction();this.mixer.uncacheRoot(this.mixer.getRoot());
    this.scene.remove(this.root,this.shadow);disposeObject(this.root);this.shadow.geometry.dispose();this.shadow.material.dispose();this.shadowTexture.dispose();
  }
}

function disposeObject(root: THREE.Object3D) {
  const materials=new Set<THREE.Material>(),textures=new Set<THREE.Texture>(),skeletons=new Set<THREE.Skeleton>();
  root.traverse(object=>{const mesh=object as THREE.SkinnedMesh;if(!mesh.isMesh)return;mesh.geometry.dispose();if(mesh.isSkinnedMesh)skeletons.add(mesh.skeleton);for(const material of Array.isArray(mesh.material)?mesh.material:[mesh.material])materials.add(material);});
  for(const material of materials){for(const value of Object.values(material))if(value instanceof THREE.Texture)textures.add(value);material.dispose();}
  textures.forEach(texture=>texture.dispose());skeletons.forEach(skeleton=>skeleton.dispose());
}
