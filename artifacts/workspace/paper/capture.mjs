import {chromium} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
const output='artifacts/workspace/paper';const browser=await chromium.launch({channel:'chrome',headless:true});const report=[];
for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]){
 const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:name==='mobile'?2:1,isMobile:name==='mobile',hasTouch:name==='mobile',recordVideo:name==='desktop'?{dir:output,size:{width,height}}:undefined});
 const page=await context.newPage();let errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.goto('http://localhost:4323/#desk-design',{waitUntil:'networkidle'});
 await page.waitForFunction(()=>document.querySelector('#desk-content')?.dataset.paper==='webgl');
 await page.mouse.move(0,0);await page.waitForFunction(()=>document.querySelector('#desk-content')?.dataset.paperRendering==='idle');
 await page.screenshot({path:output+'/'+name+'-rest.png'});
 if(name==='desktop'){
  const box=await page.locator('.ws-dialog-bar').boundingBox();const x=box.x+box.width*.5,y=box.y+30;
  await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+140,y+70,{steps:20});await page.waitForTimeout(200);
  await page.screenshot({path:output+'/desktop-bend.png'});await page.mouse.up();await page.mouse.move(0,0);
  await page.waitForFunction(()=>document.querySelector('#desk-content')?.dataset.paperRendering==='idle');
 }
 const metrics=await page.locator('#desk-content').evaluate(e=>({attributes:{...e.dataset},dialogWidth:e.clientWidth,sheetWidth:document.querySelector('#desk-paper').clientWidth,scrollWidth:document.querySelector('#desk-content-scroll').scrollWidth,clientWidth:document.querySelector('#desk-content-scroll').clientWidth,canvasSize:[document.querySelector('#desk-paper-canvas').width,document.querySelector('#desk-paper-canvas').height]}));
 report.push({name,errors,metrics});await context.close();
}
await browser.close();await writeFile(output+'/visual-qa.json',JSON.stringify(report,null,2));console.log(report);
