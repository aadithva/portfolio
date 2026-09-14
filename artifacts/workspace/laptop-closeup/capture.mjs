import {chromium} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
const output='artifacts/workspace/laptop-closeup';const b=await chromium.launch({channel:'chrome',headless:true});const report=[];
for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]){
 const context=await b.newContext({viewport:{width,height},deviceScaleFactor:name==='mobile'?2:1,isMobile:name==='mobile',hasTouch:name==='mobile',reducedMotion:'reduce'});const p=await context.newPage();const errors=[];const models=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.url().includes('workspace-saved.glb'))models.push({url:r.url(),status:r.status()})});
 await p.goto('http://localhost:4323/',{waitUntil:'networkidle'});await p.waitForFunction(()=>document.querySelector('#desk-stage')?.dataset.ready==='true');
 await p.locator('[data-room-view=desk-detail]').click();await p.waitForFunction(()=>document.querySelector('#desk-canvas')?.dataset.view==='desk-detail');await p.mouse.move(0,0);
 await p.screenshot({path:output+'/'+name+'-desk.png'});
 await p.locator('[data-object=laptop]').click();await p.locator('[data-content-section=experiments]').waitFor({state:'visible'});
 await p.keyboard.press('Escape');await p.waitForFunction(()=>document.querySelector('#desk-stage')?.dataset.state==='idle');
 await p.locator('[data-object=controller]').click();await p.locator('[data-sticker-start]').click();
 await p.waitForFunction(()=>document.querySelector('#desk-canvas')?.dataset.view==='experiments');
 await p.locator('[data-object=sticker_1]').click();await p.locator('[data-object=sticker_2]').click();
 const found=await p.locator('#desk-toast').innerText();if(!found.includes('Both stickers found'))throw new Error('Photographed sticker targets failed: '+found);
 await p.mouse.move(0,0);await p.screenshot({path:output+'/'+name+'-laptop.png'});
 report.push({name,errors,models,found,stats:await p.locator('#desk-canvas').evaluate(n=>({...n.dataset})),overflow:await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)});
 await context.close();
}
await b.close();await writeFile(output+'/browser-qa.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
