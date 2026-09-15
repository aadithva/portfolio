import {chromium} from '@playwright/test';
const browser=await chromium.launch({channel:'chrome',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
await page.emulateMedia({reducedMotion:'reduce'});
await page.goto('http://127.0.0.1:4322/');
await page.waitForFunction(()=>document.querySelector('#desk-stage')?.dataset.ready==='true');
await page.screenshot({path:'artifacts/workspace/floral-mat/overview.png'});
for(const [name,dx,dy] of [['left',-1100,-700],['right',1100,700]]) {
 await page.locator('#desk-reset').click();
 await page.mouse.move(600,350); await page.mouse.down(); await page.mouse.move(600+dx,350+dy,{steps:10}); await page.mouse.up();
 await page.mouse.move(700,200);for(let i=0;i<8;i++)await page.mouse.wheel(0,100);
 await page.waitForTimeout(500);
 await page.screenshot({path:`artifacts/workspace/floral-mat/${name}.png`});
}
await browser.close();
