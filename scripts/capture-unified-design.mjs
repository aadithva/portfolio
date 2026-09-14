import { chromium } from '@playwright/test';
import { mkdir, rename, writeFile } from 'node:fs/promises';

const base = process.env.WORKSPACE_URL || 'http://127.0.0.1:4323';
const output = 'artifacts/workspace/unified';
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const report = [];
for (const [name, width, height] of [['desktop', 1440, 900], ['laptop', 1280, 800], ['mobile', 390, 844], ['small-mobile', 320, 740]]) {
  const context = await browser.newContext({
    viewport: { width, height }, deviceScaleFactor: name === 'mobile' ? 2 : 1,
    isMobile: width < 761, hasTouch: width < 761,
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(base, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => document.querySelector('#desk-stage')?.dataset.ready === 'true');
  await page.mouse.move(0, 0);
  await page.screenshot({ path: output + '/' + name + '-room.png' });
  const stats = await page.locator('#desk-canvas').evaluate(node => ({ ...node.dataset }));
  for (const view of ['desk-detail', 'shelf-detail']) {
    await page.locator('[data-room-view="' + view + '"]').click();
    await page.waitForFunction(view => document.querySelector('#desk-canvas')?.dataset.view === view, view);
    await page.screenshot({ path: output + '/' + name + '-' + view + '.png' });
  }
  await page.locator('.ws-intro [data-open-computer]').click();
  await page.locator('#computer-desktop').waitFor({ state: 'visible' });
  await page.locator('#computer-desktop img').evaluateAll(images => Promise.all(images.map(image => image.decode())));
  await page.mouse.move(0, 0);
  await page.screenshot({ path: output + '/' + name + '-computer.png' });
  await page.locator('#computer-app-work').click();
  await page.locator('#desk-content').waitFor({ state: 'visible' });
  await page.waitForFunction(() => {
    const viewport = document.querySelector('#desk-content-scroll').getBoundingClientRect();
    return [...document.querySelectorAll('[data-content-section="work"] img')].filter(image => {
      const rect = image.getBoundingClientRect();
      return rect.top < viewport.bottom && rect.bottom > viewport.top;
    }).every(image => image.complete && image.naturalWidth > 0);
  });
  await page.screenshot({ path: output + '/' + name + '-window.png' });
  await page.keyboard.press('Escape');
  await page.locator('#computer-exit').click();
  await page.goto(base + '/work', { waitUntil: 'networkidle' });
  await page.screenshot({ path: output + '/' + name + '-work-index.png' });
  const nav = await page.locator('.nav a').evaluateAll(nodes => nodes.map(node => ({ text: node.textContent.trim(), href: node.getAttribute('href'), height: node.getBoundingClientRect().height })));
  report.push({ name, width, height, errors, stats, nav, scrollWidth: await page.evaluate(() => document.documentElement.scrollWidth) });
  await context.close();
}
// Record the actual camera, computer, and window flow at desktop dimensions.
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, recordVideo: { dir: output, size: { width: 1440, height: 900 } } });
const page = await context.newPage();
await page.goto(base, { waitUntil: 'networkidle' });
await page.waitForFunction(() => document.querySelector('#desk-stage')?.dataset.ready === 'true');
await page.waitForTimeout(1700);
await page.locator('[data-room-view="desk-detail"]').click();
await page.waitForTimeout(1200);
await page.locator('[data-room-view="shelf-detail"]').click();
await page.waitForTimeout(1200);
await page.locator('[data-room-view="overview"]').click();
await page.waitForTimeout(1100);
await page.locator('[data-object="monitor"]').click();
await page.waitForFunction(() => document.querySelector('#computer-desktop')?.open && document.querySelector('#computer-desktop')?.dataset.phase === 'ready');
await page.waitForTimeout(700);
await page.locator('#computer-app-work').click();
await page.locator('#desk-content').waitFor({ state: 'visible' });
await page.waitForTimeout(1400);
await page.keyboard.press('Escape');
await page.waitForTimeout(400);
await page.locator('#computer-exit').click();
await page.waitForTimeout(1200);
const video = page.video();
await context.close();
if (video) await rename(await video.path(), output + '/room-computer-work.webm');
await writeFile(output + '/qa.json', JSON.stringify(report, null, 2) + '\n');
await browser.close();
console.log(JSON.stringify(report.map(({name, errors, stats, scrollWidth}) => ({name, errors, stats, scrollWidth})), null, 2));
