import {chromium} from '@playwright/test';
import {writeFileSync} from 'node:fs';

const browser=await chromium.launch({channel:'chrome',headless:true});
const results=[];
try {
  for(const [name,width,height] of [['desktop',1440,1000],['laptop',1280,800],['mobile',390,844]]) {
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.goto('http://127.0.0.1:4321/');
    await page.waitForFunction(()=>document.querySelector('#desk-stage')?.dataset.ready==='true');
    await page.waitForTimeout(500);
    await page.screenshot({path:`artifacts/workspace/bicycle-lamp-clearance/${name}.png`});
    if(name==='desktop') {
      await page.locator('#desk-day').click();
      await page.waitForTimeout(200);
      await page.screenshot({path:'artifacts/workspace/bicycle-lamp-clearance/day.png'});
      await page.locator('#desk-day').click();
    }
    const bicycle=page.locator('[data-object=bicycle]');
    const trigger=name==='mobile'?page.locator('.ws-nav [data-open-section=expeditions]'):bicycle;
    await trigger.focus();
    await page.keyboard.press('Enter');
    await page.locator('#desk-content').waitFor({state:'visible'});
    await page.keyboard.press('Escape');
    await page.waitForTimeout(150);
    results.push({viewport:name,errors,focusReturned:await trigger.evaluate(el=>el===document.activeElement)});
    await page.close();
  }
} finally {
  await browser.close();
}
writeFileSync('artifacts/workspace/bicycle-lamp-clearance/browser-check.json',JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify(results,null,2));
if(results.some(result=>result.errors.length||!result.focusReturned))process.exitCode=1;
