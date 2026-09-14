import {chromium} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
const browser=await chromium.launch({channel:'chrome',headless:true});const report=[];
for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]) {
 const context=await browser.newContext({viewport:{width,height},isMobile:name==='mobile',hasTouch:name==='mobile',deviceScaleFactor:name==='mobile'?2:1});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto((process.env.PAPER_URL||'http://localhost:4322/')+'#desk-achievements');
 await page.locator('#desk-content[data-paper=source]').waitFor();
 let frame=await(await page.locator('#desk-paper-preview iframe').elementHandle()).contentFrame();
 await frame.waitForFunction(()=>window.__sheet?.state().intro>.97&&window.__paperPortfolio?.state().section==='achievements');
 await page.screenshot({path:`artifacts/workspace/paper-l2/${name}-achievements.png`});
 const achievements=await frame.evaluate(()=>window.__paperPortfolio.state());
 await page.locator('#desk-back').click();
 await page.locator('.ws-nav [data-open-section=work]').click();
 await page.locator('#desk-content[data-paper=source]').waitFor();
 frame=await(await page.locator('#desk-paper-preview iframe').elementHandle()).contentFrame();
 await frame.waitForFunction(()=>window.__sheet?.state().intro>.97&&window.__paperPortfolio?.state().section==='work');
 await page.screenshot({path:`artifacts/workspace/paper-l2/${name}-work.png`});
 const work=await frame.evaluate(()=>window.__paperPortfolio.state());
 report.push({name,errors,achievements,work,overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)});
 await context.close();
}
await browser.close();await writeFile('artifacts/workspace/paper-l2/capture.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
