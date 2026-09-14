import { chromium } from '@playwright/test';
import { writeFile } from 'node:fs/promises';
const output='artifacts/workspace/shelf-fit';
const browser=await chromium.launch({channel:'chrome',headless:true});
const report=[];
for (const [name,width,height] of [['desktop',1440,900],['mobile',390,844]]) {
 const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:width<761?2:1,isMobile:width<761,hasTouch:width<761,reducedMotion:'reduce'});
 const page=await context.newPage();const errors=[];const models=[];
 page.on('pageerror',error=>errors.push(error.message));
 page.on('response',response=>{if(response.url().includes('workspace-saved.glb'))models.push({url:response.url(),status:response.status()});});
 await page.goto('http://localhost:4323/',{waitUntil:'networkidle'});
 await page.waitForFunction(()=>document.querySelector('#desk-stage')?.dataset.ready==='true');
 await page.mouse.move(0,0);
 for(const view of ['overview','desk-detail','shelf-detail']) {
  await page.locator('[data-room-view="'+view+'"]').click();
  await page.waitForFunction(view=>document.querySelector('#desk-canvas')?.dataset.view===view,view);
  await page.mouse.move(0,0);
  await page.screenshot({path:output+'/'+name+'-'+view+'.png'});
 }
 await page.locator('[data-object="monitor"]').click();
 await page.waitForFunction(()=>document.querySelector('#computer-desktop')?.open&&document.querySelector('#computer-desktop')?.dataset.phase==='ready');
 await page.screenshot({path:output+'/'+name+'-computer.png'});
 await page.locator('#computer-exit').click();
 await page.waitForFunction(()=>!document.querySelector('#computer-desktop')?.open);
 report.push({name,errors,models,canvas:await page.locator('#desk-canvas').evaluate(n=>({...n.dataset})),scrollWidth:await page.evaluate(()=>document.documentElement.scrollWidth),width});
 await context.close();
}
await browser.close();await writeFile(output+'/browser-qa.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
