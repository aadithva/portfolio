import { test, expect } from '@playwright/test';

test('cat stays on the floor, meows on click, and returns from the opposite side', async ({ page }) => {
  test.setTimeout(110000);
  const errors: string[] = [];page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await page.addStyleTag({content:'astro-dev-toolbar { display:none !important; }'});
  const canvas=page.locator('#desk-canvas');
  await expect(canvas).toHaveAttribute('data-cat-ready','true',{timeout:30000});
  await page.evaluate(()=>{
    const canvas=document.querySelector('#desk-canvas')!;
    (window as any).__catStates=[];
    new MutationObserver(()=>{
      const data=(canvas as HTMLElement).dataset;
      (window as any).__catStates.push(data.catState);
    }).observe(canvas,{attributes:true,attributeFilter:['data-cat-state']});
  });
  await expect(canvas).toHaveAttribute('data-cat-direction','right-to-left');
  await expect(canvas).toHaveAttribute('data-cat-state','looking-around',{timeout:35000});
  await page.locator('.ws-cat-hit').click();
  await expect(canvas).toHaveAttribute('data-cat-meows','1');
  expect(Number((await canvas.getAttribute('data-cat-position'))!.split(',')[1])).toBeLessThan(.03);
  await page.screenshot({path:'artifacts/workspace/cat/verified-wandering.png'});
  await expect(canvas).toHaveAttribute('data-cat-state','outside',{timeout:40000});
  await expect(canvas).toHaveAttribute('data-cat-cycle','1',{timeout:16000});
  const states=await page.evaluate(()=>(window as any).__catStates as string[]);
  expect(states.some(state=>state.includes('desk'))).toBe(false);
  expect(states.some(state=>state.includes('chair')||state.includes('jump'))).toBe(false);
  await expect(canvas).toHaveAttribute('data-cat-direction','left-to-right');
  expect(errors).toEqual([]);
});

test('mobile reduced motion rests on floor and supports keyboard meow',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto('/');
  await page.addStyleTag({content:'astro-dev-toolbar { display:none !important; }'});
  const canvas=page.locator('#desk-canvas');
  await expect(canvas).toHaveAttribute('data-cat-state','resting-reduced-motion',{timeout:30000});
  const before=await canvas.getAttribute('data-cat-position');
  await page.waitForTimeout(1200);
  expect(await canvas.getAttribute('data-cat-position')).toBe(before);
  await page.locator('.ws-cat-hit').focus();await page.locator('.ws-cat-hit').press('Enter');
  await expect(canvas).toHaveAttribute('data-cat-meows','1');
  await page.locator('#desk-day').click();
  await page.screenshot({path:'artifacts/workspace/cat/verified-mobile-day.png'});
  await page.emulateMedia({reducedMotion:'no-preference'});
  await expect(canvas).toHaveAttribute('data-cat-state','entering');
});

test('opening portfolio content pauses the companion clock',async({page})=>{
  await page.goto('/');
  const canvas=page.locator('#desk-canvas');
  await expect(canvas).toHaveAttribute('data-cat-ready','true',{timeout:30000});
  await page.locator('.ws-nav [data-open-section="about"]').click();
  await expect(page.locator('#desk-content')).toBeVisible();
  const before=await canvas.getAttribute('data-cat-position');
  await page.waitForTimeout(1200);
  expect(await canvas.getAttribute('data-cat-position')).toBe(before);
  await page.locator('#desk-close').click();
  await expect.poll(()=>canvas.getAttribute('data-cat-position')).not.toBe(before);
});

test('cat failure does not prevent room and navigation from loading',async({page})=>{
  await page.route('**/models/workspace-cat.glb*',route=>route.abort());
  await page.goto('/');
  await expect(page.locator('#desk-stage')).toHaveAttribute('data-ready','true',{timeout:30000});
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-cat-ready','false');
  await expect(page.locator('#desk-failure')).toBeHidden();
  await page.locator('#desk-guide').click();
  await expect(page.locator('#desk-guide-panel a[href="https://blendswap.com/blend/18519"]')).toBeVisible();
});
