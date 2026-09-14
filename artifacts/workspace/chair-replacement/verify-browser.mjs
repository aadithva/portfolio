import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
const root='/Users/aadith/Projects/Portfolio/Website';
const out=`${root}/artifacts/workspace/chair-replacement`;
const browser=await chromium.launch({channel:'chrome',headless:true});
const results=[];
try {
  for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]) {
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1,hasTouch:name==='mobile'});
    const errors=[],requests=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('response',response=>{
      if(response.url().includes('workspace-saved.glb')||response.url().includes('saved-bake')) requests.push({url:response.url(),status:response.status()});
    });
    await page.goto(process.env.WORKSPACE_URL||'http://127.0.0.1:4322/',{waitUntil:'networkidle'});
    await page.waitForFunction(()=>document.querySelector('#desk-stage')?.dataset.ready==='true',{},{timeout:45000});
    await page.waitForTimeout(1500);
    await page.screenshot({path:`${out}/browser-${name}.png`});
    const chair=page.getByRole('button',{name:'Take a spin',exact:true});
    await chair.waitFor({state:'attached'});
    const box=await chair.boundingBox();
    let interacted=false;
    if(box) {
      await chair.scrollIntoViewIfNeeded();
      // Touch intentionally raycasts through the canvas; the DOM hotspot is
      // the keyboard alternative and has pointer-events disabled on mobile.
      if(name==='mobile') await page.touchscreen.tap(Math.max(5,Math.min(width-5,box.x+box.width/2)),box.y+box.height/2);
      else { await chair.focus(); await page.keyboard.press('Enter'); }
      await page.waitForTimeout(150);
      const moved=await chair.boundingBox();
      interacted=!!moved && (Math.abs(moved.x-box.x)>.01 || Math.abs(moved.y-box.y)>.01);
      await page.screenshot({path:`${out}/browser-${name}-swivel.png`});
    }
    const data=await page.locator('#desk-canvas').evaluate(n=>({...n.dataset}));
    results.push({name,errors,requests,data,chairAccessible:await chair.count()===1,chairInteraction:interacted,chairBounds:box});
    await page.close();
  }
} finally { await browser.close(); }
await fs.writeFile(`${out}/browser-check.json`,JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify(results,null,2));
if(results.some(result=>result.errors.length||!result.chairAccessible||!result.chairInteraction||result.requests.some(r=>r.status!==200))) process.exitCode=1;
