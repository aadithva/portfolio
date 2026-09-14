import { test, expect, type Page } from '@playwright/test';

async function ready(page: Page) {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await expect(page.locator('#desk-stage')).toHaveAttribute('data-ready', 'true');
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-camera-navigation', 'enabled');
}

async function camera(page: Page) {
  return page.locator('#desk-canvas').evaluate(element => {
    const { cameraYaw, cameraPitch, cameraZoom, cameraDragging, cameraModified } = (element as HTMLElement).dataset;
    return { yaw: Number(cameraYaw), pitch: Number(cameraPitch), zoom: Number(cameraZoom), dragging: cameraDragging, modified: cameraModified };
  });
}

test('camera: dragging a content hotspot rotates the room without opening it, then a tap still opens it', async ({ page }) => {
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  await ready(page);
  const monitor = page.locator('[data-object=monitor]');
  const box = await monitor.boundingBox(); if (!box) throw new Error('Monitor hotspot missing');
  const x = box.x + box.width / 2, y = box.y + box.height / 2;
  await page.mouse.move(x, y); await page.mouse.down();
  await page.mouse.move(x + 115, y + 34, { steps: 8 });
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-camera-dragging', 'true');
  await page.mouse.up();
  // The compatibility-click guard belongs to the scene, not its toolbar.
  // A deliberate zoom button click immediately after releasing a drag works.
  const zoomBefore = (await camera(page)).zoom;
  await page.locator('#desk-zoom-in').click();
  await expect.poll(async () => (await camera(page)).zoom).toBeGreaterThan(zoomBefore + .05);
  await expect(page.locator('#computer-desktop')).not.toBeVisible();
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect.poll(async () => Math.abs((await camera(page)).yaw)).toBeGreaterThan(.12);
  expect((await camera(page)).dragging).toBe('false');
  await monitor.click();
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-phase', 'ready');
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-camera-navigation', 'disabled');
  await page.keyboard.press('Escape');
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-camera-modified', 'false');
  expect(errors).toEqual([]);
});

test('camera: orbit and zoom are bounded, reset and guided views restore their authored framing', async ({ page }) => {
  await ready(page);
  const stage = await page.locator('#desk-stage').boundingBox(); if (!stage) throw new Error('Desk stage missing');
  const x = stage.x + stage.width * .2, y = stage.y + stage.height * .22;
  await page.mouse.move(x, y); await page.mouse.down();
  await page.mouse.move(x + stage.width * .6, y + stage.height * .62, { steps: 12 }); await page.mouse.up();
  const rotated = await camera(page);
  expect(Math.abs(rotated.yaw)).toBeCloseTo(22 * Math.PI / 180, 4);
  expect(Math.abs(rotated.pitch)).toBeCloseTo(10 * Math.PI / 180, 4);
  await page.mouse.move(stage.x + stage.width / 2, stage.y + 22);
  for (let index = 0; index < 12; index++) await page.mouse.wheel(0, -100);
  await expect.poll(async () => (await camera(page)).zoom).toBeCloseTo(1 / .76, 4);
  for (let index = 0; index < 12; index++) await page.mouse.wheel(0, 100);
  await expect.poll(async () => (await camera(page)).zoom).toBeCloseTo(1 / 1.08, 4);
  await page.locator('[data-room-view=desk-detail]').click();
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-view', 'desk-detail');
  await expect.poll(async () => (await camera(page)).zoom).toBe(1);
  expect((await camera(page)).yaw).toBe(0);
  await page.locator('#desk-reset').click();
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-view', 'overview');
  expect((await camera(page)).modified).toBe('false');
});

test('camera: touch drag, pinch and cancellation preserve taps and page navigation', async ({ browser }) => {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const page = await context.newPage(); await ready(page);
  const client = await context.newCDPSession(page);
  const stage = await page.locator('#desk-stage').boundingBox(); if (!stage) throw new Error('Desk stage missing');
  const x = stage.x + stage.width / 2, y = stage.y + stage.height * .3;
  const point = (id: number, px: number, py: number) => ({ id, x: px, y: py, radiusX: 2, radiusY: 2, force: 1 });
  await client.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [point(1, x, y)] });
  await client.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [point(1, x + 70, y + 25)] });
  await client.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await expect.poll(async () => Math.abs((await camera(page)).yaw)).toBeGreaterThan(.1);
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await client.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [point(1, x - 38, y), point(2, x + 38, y)] });
  await client.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [point(1, x - 68, y), point(2, x + 68, y)] });
  await expect.poll(async () => (await camera(page)).zoom).toBeGreaterThan(1.15);
  await client.send('Input.dispatchTouchEvent', { type: 'touchCancel', touchPoints: [] });
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-camera-dragging', 'false');
  await page.locator('#desk-reset').tap();
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-camera-modified', 'false');
  await page.locator('[data-object=monitor]').tap();
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-phase', 'ready');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await context.close();
});

test('camera: keyboard zoom and recenter controls expose their bounds', async ({ page }) => {
  await ready(page);
  const zoomIn = page.getByRole('button', { name: 'Zoom in on the desk' });
  const zoomOut = page.getByRole('button', { name: 'Zoom out from the desk' });
  const recenter = page.getByRole('button', { name: 'Recenter this view' });
  await zoomIn.focus(); await page.keyboard.press('Enter');
  await expect.poll(async () => (await camera(page)).zoom).toBeGreaterThan(1.05);
  await expect(recenter).toBeEnabled();
  for (let index = 0; index < 5; index++) {
    if (await zoomIn.isEnabled()) { await zoomIn.focus(); await page.keyboard.press('Enter'); }
  }
  await expect(zoomIn).toBeDisabled(); await expect(zoomOut).toBeEnabled();
  await recenter.focus(); await page.keyboard.press('Enter');
  await expect.poll(async () => (await camera(page)).zoom).toBe(1);
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-camera-modified', 'false');
  await page.locator('[data-object=monitor]').focus(); await page.keyboard.press('Enter');
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-phase', 'ready');
  await expect(page.locator('#desk-camera-controls')).not.toBeVisible();
});
