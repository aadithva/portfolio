import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {chromium} from '@playwright/test';
const data=readFileSync('public/models/workspace-saved.glb');
const gltf=JSON.parse(data.subarray(20,20+data.readUInt32LE(12)).toString());
const names=['Lamp enamel vermilion','Lamp edge red','rama','wheel.orange','wheel.black','Warm powder-coated white','Limewashed plaster'];
const materials=names.map(name=>{
  const m=gltf.materials.find(m=>m.name===name);assert(m,`Missing ${name}`);
  assert(m.normalTexture,`Missing normal map: ${name}`);
  assert(m.pbrMetallicRoughness.metallicRoughnessTexture,`Missing roughness map: ${name}`);
  if(['rama','wheel.orange','wheel.black'].includes(name)) {
    const rgb=m.pbrMetallicRoughness.baseColorFactor.slice(0,3);
    assert(Math.max(...rgb)<.02&&Math.max(...rgb)-Math.min(...rgb)<.0001,`${name} must be neutral black`);
  }
  return {name,normal:m.normalTexture,roughness:m.pbrMetallicRoughness.metallicRoughnessTexture,color:m.pbrMetallicRoughness.baseColorFactor};
});
for(const node of gltf.nodes) {
  if(node.mesh===undefined||node.extras?.bakedUV===undefined)continue;
  for(const primitive of gltf.meshes[node.mesh].primitives)assert(primitive.attributes[`TEXCOORD_${node.extras.bakedUV}`]!==undefined,`Missing lightmap UV: ${node.name}`);
}
const browser=await chromium.launch({channel:'chrome',headless:true});
const results=[];
try {
  for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]) {
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.goto('http://127.0.0.1:4321/');
    await page.waitForFunction(()=>document.querySelector('#desk-stage')?.dataset.ready==='true');
    await page.waitForTimeout(500);
    await page.screenshot({path:`artifacts/workspace/matte-materials/${name}-night.png`});
    await page.locator('#desk-day').focus();
    await page.keyboard.press('Enter');
    await page.waitForTimeout(300);
    await page.screenshot({path:`artifacts/workspace/matte-materials/${name}-day.png`});
    results.push({name,errors,metrics:await page.locator('#desk-canvas').evaluate(el=>({...el.dataset}))});
    await page.close();
  }
}finally{await browser.close();}
writeFileSync('artifacts/workspace/matte-materials/verification.json',JSON.stringify({materials,results},null,2)+'\n');
console.log(JSON.stringify({materials,results},null,2));
assert(results.every(r=>r.errors.length===0),'Browser errors');
