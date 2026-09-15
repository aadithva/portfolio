import { chromium } from '@playwright/test';
const browser=await chromium.launch({channel:'chrome',headless:true});
const page=await browser.newPage({viewport:{width:1000,height:850}});
page.on('pageerror',error=>console.error(error));
page.on('console',msg=>console.log(msg.text()));
await page.route('**/cat-review',route=>route.fulfill({contentType:'text/html',body:`
<style>body{margin:0;background:#383c40}canvas{display:block}</style>
<script type="importmap">{"imports":{"three":"/node_modules/three/build/three.module.js"}}</script>
<script type="module">
import * as T from 'three';
import {GLTFLoader} from '/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {makeCatCoatMatte} from '/src/lib/workspace/cat-fur.ts';
const renderer=new T.WebGLRenderer({antialias:true});renderer.setSize(1000,850);renderer.setPixelRatio(1);renderer.setClearColor(0x383c40);renderer.toneMapping=T.AgXToneMapping;document.body.append(renderer.domElement);
const scene=new T.Scene();const camera=new T.PerspectiveCamera(36,1000/850,.1,100);camera.position.set(12,7,18);camera.lookAt(0,1,0);
scene.add(new T.HemisphereLight(0xffffff,0xb8aa9a,2));const key=new T.DirectionalLight(0xffeddd,3);key.position.set(4,10,9);scene.add(key);
const gltf=await new GLTFLoader().loadAsync('/models/workspace-cat.glb?v=5');scene.add(gltf.scene);
makeCatCoatMatte(gltf.scene);
gltf.scene.traverse(o=>{if(!o.isMesh)return;o.frustumCulled=false;for(const m of Array.isArray(o.material)?o.material:[o.material])if(m.name==='Calico layered fur'){m.transparent=false;m.alphaTest=.12;m.alphaToCoverage=true;m.side=T.DoubleSide;}});
const mixer=new T.AnimationMixer(gltf.scene);
window.pose=(name,time)=>{mixer.stopAllAction();mixer.clipAction(gltf.animations.find(a=>a.name===name)).play();mixer.setTime(time);renderer.render(scene,camera);};
window.pose('Idle',0);window.ready=true;
</script>`}));
await page.goto('http://127.0.0.1:4322/cat-review');
await page.waitForFunction(()=>window.ready);
for(const [name,clip,time] of [['matte-coat','Idle',0],['walking','Walk',.4]]){
  await page.evaluate(([clip,time])=>window.pose(clip,time),[clip,time]);
  await page.screenshot({path:`artifacts/workspace/cat/review-${name}.png`});
}
await browser.close();
