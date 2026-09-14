import {chromium} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
const browser=await chromium.launch({channel:'chrome',headless:true});const report=[];
for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]) {
 const context=await browser.newContext({viewport:{width,height},isMobile:name==='mobile',hasTouch:name==='mobile',deviceScaleFactor:name==='mobile'?2:1,reducedMotion:'reduce'});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://localhost:4322/');
 const hotspot=page.locator('[data-object=certificate_iitg]');await hotspot.waitFor({timeout:60000});
 await page.waitForTimeout(1800);
 const visibility=await hotspot.evaluate(e=>({rect:e.getBoundingClientRect().toJSON(),visibility:getComputedStyle(e).visibility,aria:e.getAttribute('aria-label'),style:e.getAttribute('style')}));
 await page.screenshot({path:`artifacts/workspace/certificate-frame/${name}-overview.png`});
 report.push({name,errors,visibility});await context.close();
}
await browser.close();await writeFile('artifacts/workspace/certificate-frame/browser.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
