import { chromium } from '@playwright/test';
const browser = await chromium.launch({channel:'chrome',headless:true});
for (const [name,width,height] of [['laptop',1280,800],['mobile',390,844],['desktop',1440,1000]]) {
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.WORKSPACE_URL||'http://127.0.0.1:4322/',{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.querySelector('#desk-stage')?.dataset.ready==='true');
  await page.waitForTimeout(1400);
  await page.screenshot({path:`artifacts/workspace/${name}.png`});
  console.log(name,await page.locator('#desk-canvas').evaluate(n=>n.dataset),errors);
  await page.locator('.ws-nav [data-open-section="work"]').click();
  await page.locator('#desk-content').waitFor({state:'visible'});
  await page.waitForTimeout(400);
  await page.screenshot({path:`artifacts/workspace/${name}-work.png`});
  await page.close();
}
await browser.close();
