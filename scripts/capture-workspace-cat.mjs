import { chromium } from '@playwright/test';
import { writeFile } from 'node:fs/promises';
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1, recordVideo: { dir: 'artifacts/workspace/cat/video', size: { width: 1440, height: 1000 } } });
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',msg=>{if(msg.type()==='warning'||msg.type()==='error')console.log(msg.text());});
await page.goto('http://127.0.0.1:4322/');
await page.addStyleTag({content:'astro-dev-toolbar { display:none !important; }'});
await page.waitForFunction(()=>document.querySelector('#desk-canvas')?.dataset.catReady==='true',{},{timeout:60000});
const states=[];
for(let i=0;i<75;i++) {
  const data=await page.locator('#desk-canvas').evaluate(n=>({...n.dataset}));
  if(states.at(-1)?.state!==data.catState){states.push({state:data.catState,position:data.catPosition,cycle:data.catCycle});console.log(states.at(-1));}
  if(['looking-around','wandering'].includes(data.catState)&&!states.at(-1).captured){
    await page.screenshot({path:`artifacts/workspace/cat/browser-${data.catState}.png`});states.at(-1).captured=true;
  }
  await page.waitForTimeout(1000);
}
await writeFile('artifacts/workspace/cat/browser-report.json',JSON.stringify({states,errors},null,2));
await page.close();await browser.close();
