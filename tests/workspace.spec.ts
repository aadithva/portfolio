import { test, expect } from '@playwright/test';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

const originalPaperHash='8ec1b71c0dbcafbadf908100ae2a08045d0a1087c00a09d28245ef19366c7353';

async function paperFrame(page: import('@playwright/test').Page) {
  const iframe=page.locator('#desk-paper-preview iframe');
  let readyFrame: import('@playwright/test').Frame | undefined;
  // The authored component can replace its iframe as visibility changes. Resolve
  // the current frame on each poll instead of keeping a detached booting frame.
  await expect.poll(async()=>{
    let frame: import('@playwright/test').Frame | null | undefined;
    try {
      if(!await iframe.isVisible())return false;
      frame=await(await iframe.elementHandle())?.contentFrame();
      if(!frame)return false;
      const ready=await frame.evaluate(()=>{
        const sheet=(window as unknown as {__sheet?:{state:()=>{intro:number}}}).__sheet;
        const content=(window as unknown as {__paperPortfolio?:{state:()=>{section:string;renderedText:string}}}).__paperPortfolio;
        return !!sheet&&sheet.state().intro>.9&&!!content?.state().section&&!!content.state().renderedText;
      });
      if(ready)readyFrame=frame;
      return ready;
    } catch(error) {
      if(frame?.isDetached()||(error instanceof Error&&error.message.includes('Element is not attached to the DOM')))return false;
      throw error;
    }
  },{message:'The active ThreeUI source should finish its arrival',intervals:[100,200,300]}).toBe(true);
  return readyFrame!;
}

async function paperState(frame: import('@playwright/test').Frame) {
  return frame.evaluate(()=>{
    const sheet=(window as unknown as {__sheet:{
      state:()=>{intro:number;dragYaw:number;dragPitch:number;hover:number;quad:number[][]};
      uni:{uTime:{value:number}};
    }}).__sheet;
    return {...sheet.state(),time:sheet.uni.uTime.value};
  });
}

type PaperContentState = {
  section:string;page:number;pageCount:number;title:string;renderedText:string;
  artwork:{src:string;alt:string;loaded:boolean}|null;
  links:{label:string;href?:string;actionId?:string;x:number;y:number;width:number;height:number}[];
};

async function paperContent(frame: import('@playwright/test').Frame):Promise<PaperContentState> {
  return frame.evaluate(()=>(window as unknown as {__paperPortfolio:{state:()=>PaperContentState}}).__paperPortfolio.state());
}

async function expectRideMedalPaper(page: import('@playwright/test').Page) {
  await expect(page.locator('#desk-content')).toHaveAttribute('data-achievement','ride-for-unity');
  await expect(page.locator('#desk-dialog-title')).toHaveText('Ride for Unity medal');
  const frame=await paperFrame(page);
  await expect.poll(async()=>(await paperContent(frame)).section).toBe('achievements:ride-for-unity');
  const content=await paperContent(frame);
  expect(content.title).toBe('Ride for Unity medal');
  expect(content.renderedText).toContain('Ride for Unity');
  expect(content.renderedText).not.toMatch(/IIT Guwahati|Bachelor of Design|Microsoft|Owly/);
  expect(content.artwork).toBeNull();
  return frame;
}

async function paperLink(page: import('@playwright/test').Page,match:{href?:string;label?:string},tap=false) {
  const frame=await paperFrame(page);
  let content=await paperContent(frame);
  for(let count=0;count<content.pageCount;count++) {
    const link=content.links.find(link=>match.href?link.href===match.href:link.label===match.label);
    if(link) {
      // Hit the rendered paper at the projected texture coordinates. This must
      // exercise the actual UV hit test, never the hidden HTML action directly.
      const point=await frame.evaluate(link=>{
        const sheet=(window as unknown as {__sheet:{point:(u:number,v:number)=>{x:number;y:number}}}).__sheet;
        return sheet.point((link.x+link.width/2)/1400,1-(link.y+link.height/2)/1932);
      },link);
      const box=await page.locator('#desk-paper-preview iframe').boundingBox();
      if(!box)throw new Error('The content paper has no bounds');
      const x=box.x+(point.x+1)*box.width/2,y=box.y+(1-point.y)*box.height/2;
      if(tap)await page.touchscreen.tap(x,y);else await page.mouse.click(x,y);
      return;
    }
    const next=page.locator('#desk-paper-next');
    if(await next.isDisabled())break;
    const previous=content.page;
    await next.click();
    await expect.poll(async()=>(await paperContent(frame)).page).not.toBe(previous);
    content=await paperContent(frame);
  }
  throw new Error(`No visible paper link matches ${JSON.stringify(match)}`);
}

async function expectPaperFits(page: import('@playwright/test').Page) {
  const frame=await paperFrame(page);
  const box=await page.locator('#desk-paper-preview iframe').boundingBox();
  const viewport=page.viewportSize();
  if(!box||!viewport)throw new Error('Paper viewport is missing');
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x+box.width).toBeLessThanOrEqual(viewport.width);
  expect(box.y).toBeGreaterThanOrEqual(0);
  expect(box.y+box.height).toBeLessThanOrEqual(viewport.height);
  expect(await frame.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  for(const [x,y] of (await paperState(frame)).quad) {
    expect(x).toBeGreaterThanOrEqual(0);expect(x).toBeLessThanOrEqual(box.width);
    expect(y).toBeGreaterThanOrEqual(0);expect(y).toBeLessThanOrEqual(box.height);
  }
}

async function expectPlainContent(page: import('@playwright/test').Page,section:string) {
  const dialog=page.locator('#desk-content'),scroll=page.locator('#desk-content-scroll');
  await expect(dialog).toBeVisible();
  await expect(dialog).toHaveAttribute('data-content-view','standard');
  await expect(dialog).not.toHaveAttribute('data-paper',/./);
  await expect(dialog).not.toHaveAttribute('data-paper-view',/./);
  await expect(page.locator(`[data-content-section=${section}]`)).toBeVisible();
  await expect(page.locator('#desk-paper-preview iframe')).toHaveCount(0);
  await expect(page.locator('#desk-paper-reader')).not.toBeVisible();
  await expect(page.locator('.ws-paper-paging')).not.toBeVisible();
  await expect(scroll).toHaveCSS('clip-path','none');
  expect(await scroll.evaluate(element=>element.clientWidth>1&&element.scrollWidth<=element.clientWidth+1)).toBe(true);
}

async function ready(page: import('@playwright/test').Page) {
  await page.goto('/');
  await expect(page.locator('#desk-stage')).toHaveAttribute('data-ready','true');
  if(await page.locator('#desk-skip').isVisible())await page.locator('#desk-skip').click();
}

test('design: guided views survive rapid changes, monitor entry, Escape and reset', async ({page}) => {
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  await ready(page);
  const stage=page.locator('#desk-stage'),canvas=page.locator('#desk-canvas');
  const view=(id:string)=>page.locator(`[data-room-view="${id}"]`);
  for(const id of ['desk-detail','shelf-detail','desk-detail']) {
    await view(id).click();
    await expect(view(id)).toHaveAttribute('aria-pressed','true');
    await expect(page.locator('[data-room-view][aria-pressed=true]')).toHaveCount(1);
    await expect(canvas).toHaveAttribute('data-view',id);
  }
  await page.locator('[data-object=monitor]').click();
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-phase','ready');
  await expect(canvas).toHaveAttribute('data-view','computer');
  await page.keyboard.press('Escape');
  await expect(stage).toHaveAttribute('data-state','idle');
  await expect(canvas).toHaveAttribute('data-view','overview');
  await expect(view('overview')).toHaveAttribute('aria-pressed','true');
  await expect(page.locator('[data-object=monitor]')).toBeFocused();

  await view('shelf-detail').click();
  await expect(stage).toHaveAttribute('data-state','guided');
  await page.keyboard.press('Escape');
  await expect(stage).toHaveAttribute('data-state','idle');
  await expect(canvas).toHaveAttribute('data-view','overview');
  await expect(view('overview')).toHaveAttribute('aria-pressed','true');
  await view('desk-detail').click();
  await page.locator('#desk-reset').click();
  await expect(stage).toHaveAttribute('data-state','idle');
  await expect(canvas).toHaveAttribute('data-view','overview');
  await expect(page.locator('[data-room-view][aria-pressed=true]')).toHaveCount(1);
  expect(errors).toEqual([]);
});

test('design: room, computer, content windows and Work retain one shared palette', async ({page}) => {
  await page.emulateMedia({reducedMotion:'reduce'});await ready(page);
  const appearance=(selector:string)=>page.locator(selector).evaluate(element=>{
    const style=getComputedStyle(element);
    return {background:style.backgroundColor,ink:style.color,font:style.fontFamily};
  });
  const room=await appearance('body');
  const panel=(await appearance('.ws-nav')).background;
  const accent=(await appearance('[data-room-view=overview] span')).ink;
  await page.locator('[data-object=monitor]').click();
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-phase','ready');
  expect(await appearance('#computer-desktop')).toEqual(room);
  expect((await appearance('.computer-owner-mark')).ink).toBe(accent);
  await page.locator('#computer-app-work').click();
  await expect(page.locator('[data-content-section=work]')).toBeVisible();
  const contentWindow=await appearance('#desk-content');
  // The ordinary HTML window retains the room's panel color.
  const paperColor=await page.locator('#desk-paper').evaluate(element=>{
    const probe=document.createElement('span');
    probe.style.cssText='position:absolute;visibility:hidden;color:var(--paper-color)';
    element.append(probe);const color=getComputedStyle(probe).color;probe.remove();return color;
  });
  expect(paperColor).toBe(panel);
  expect(contentWindow.ink).toBe(room.ink);
  expect((await appearance('[data-content-section=work] .wc-eyebrow')).ink).toBe(accent);
  await page.goto('/work');
  await expect(page.locator('main .page-header__title')).toHaveText('Work');
  expect(await appearance('body')).toEqual(room);
});

test('paper: achievements use the authored sheet above the desk, with hover and drag',async({page})=>{
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  await ready(page);
  const achievements=page.locator('.ws-nav [data-open-section=achievements]');
  await achievements.focus();await page.keyboard.press('Enter');
  const dialog=page.locator('#desk-content');
  await expect(dialog).toHaveAttribute('data-paper','source');
  await expect(dialog).toHaveAttribute('data-paper-view','sheet');
  const frame=await paperFrame(page),iframe=page.locator('#desk-paper-preview iframe');
  const canonical=readFileSync('vendor/threeui/src/shaders/3d-paper/sources/3d-paper.html','utf8');
  expect(createHash('sha256').update(canonical).digest('hex')).toBe(originalPaperHash);
  const source=await iframe.getAttribute('srcdoc');
  // The unmodified authored shader is retained; only portfolio integration and
  // content differ from the registered certificate's complete document hash.
  const wave=canonical.match(/const WAVE = `([\s\S]*?)`;/)?.[1];
  expect(wave).toBeTruthy();expect(source).toContain(wave!);
  expect(await frame.evaluate(()=>(window as unknown as {THREE:{REVISION:string}}).THREE.REVISION)).toBe('149');
  const content=await paperContent(frame);
  expect(content.section).toBe('achievements');
  expect(content.renderedText).toContain('Bachelor of Design · IIT Guwahati');
  await expect.poll(async()=>(await paperContent(frame)).artwork?.loaded).toBe(true);
  expect((await paperContent(frame)).artwork?.src).toMatch(/\/textures\/workspace\/iitg-degree\.jpg$/);
  expect((await paperContent(frame)).artwork?.alt).toBe('Bachelor of Design · IIT Guwahati');
  expect(content.renderedText).not.toMatch(/Nocturne|Studio of the Week|Ilya Marchetti|Dara Okonkwo/);
  await expect(frame.locator('#bg h1')).not.toHaveText(/NOCTURNE/i);
  await expect(frame.locator('#bg')).not.toBeVisible();
  await expect(frame.locator('body')).toHaveCSS('background-color','rgba(0, 0, 0, 0)');
  // Chromium paints an opaque iframe canvas if its document color scheme does
  // not match the host, even when both CSS backgrounds are transparent.
  await expect(iframe).toHaveCSS('color-scheme','dark');
  await expect(frame.locator('html')).toHaveCSS('color-scheme','dark');
  expect(await frame.evaluate(()=>{
    const sheet=(window as unknown as {__sheet:{renderer:{getClearAlpha:()=>number;getContext:()=>WebGLRenderingContext};scene:{background:unknown}}}).__sheet;
    return {clearAlpha:sheet.renderer.getClearAlpha(),alpha:sheet.renderer.getContext().getContextAttributes()?.alpha,background:sheet.scene.background};
  })).toEqual({clearAlpha:0,alpha:true,background:null});
  await expect(dialog).toHaveCSS('background-color','rgba(0, 0, 0, 0)');
  await expect(page.locator('#desk-canvas')).toBeVisible();
  await expect(page.locator('.ws-intro')).not.toBeVisible();
  await expect(page.locator('#desk-paper-expand')).toHaveCount(0);
  // The paper occupies the L2 viewport. The accessible HTML copy has no visible
  // side-column footprint until a visitor explicitly opens the reader.
  const box=await iframe.boundingBox(),dialogBox=await dialog.boundingBox();
  if(!box||!dialogBox)throw new Error('Content paper bounds are missing');
  expect(box.width).toBeGreaterThan(dialogBox.width*.85);
  expect(await page.locator('#desk-content-scroll').evaluate(element=>{
    const style=getComputedStyle(element),bounds=element.getBoundingClientRect();
    return style.clipPath!=='none'||bounds.width<=1||style.display==='none';
  })).toBe(true);
  const initial=await paperState(frame);
  const x=box.x+initial.quad.reduce((sum,point)=>sum+point[0],0)/4;
  const y=box.y+initial.quad.reduce((sum,point)=>sum+point[1],0)/4;
  await page.mouse.move(x,y);
  await expect.poll(async()=>(await paperState(frame)).hover).toBeGreaterThan(.4);
  await page.mouse.down();await page.mouse.move(x+70,y-16,{steps:8});
  await expect.poll(async()=>Math.abs((await paperState(frame)).dragYaw-initial.dragYaw)).toBeGreaterThan(.15);
  await page.mouse.up();
  expect((await paperContent(frame)).renderedText).toBe(content.renderedText);
  await expect(page).toHaveURL(/#desk-achievements$/);
  // A drag over printed content must not accidentally follow a paper link.
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();await expect(iframe).toHaveCount(0);
  await expect(achievements).toBeFocused();expect(errors).toEqual([]);
});

test('paper: achievement pages, text reading mode, and the printed timeline link remain usable',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.route('**/models/workspace-saved.glb*',route=>route.abort());
  await page.goto('/');await expect(page.locator('#desk-failure')).toBeVisible();
  const achievements=page.locator('.ws-nav [data-open-section=achievements]');
  await achievements.focus();await page.keyboard.press('Enter');
  const dialog=page.locator('#desk-content'),scroll=page.locator('#desk-content-scroll');
  await expect(dialog).toBeVisible();await expect(page.locator('#desk-back')).toBeFocused();
  const frame=await paperFrame(page),first=await paperContent(frame);
  expect(first.section).toBe('achievements');expect(first.pageCount).toBeGreaterThanOrEqual(3);
  expect(first.renderedText).toContain('Bachelor of Design · IIT Guwahati');
  await expect.poll(async()=>(await paperContent(frame)).artwork?.loaded).toBe(true);
  await page.locator('#desk-paper-next').focus();await page.keyboard.press('Enter');
  await expect.poll(async()=>(await paperContent(frame)).page).toBe(first.page+1);
  expect((await paperContent(frame)).renderedText).not.toBe(first.renderedText);
  expect((await paperContent(frame)).renderedText).toContain('A few milestones.');
  expect((await paperContent(frame)).artwork).toBeNull();
  await page.locator('#desk-paper-prev').click();
  await expect.poll(async()=>(await paperContent(frame)).page).toBe(first.page);
  const timeline=page.locator('[data-content-section=achievements] a[href="/about"]');
  await timeline.focus();
  await expect(dialog).toHaveAttribute('data-paper-view','reader');
  await expect(timeline).toBeFocused();await expect(timeline).toBeInViewport();
  expect(frame.isDetached()).toBe(true);
  await expect(page.locator('#desk-paper-preview iframe')).toHaveCount(0);
  expect(await scroll.evaluate(element=>element.scrollWidth<=element.clientWidth+1)).toBe(true);
  await page.locator('#desk-paper-reader').click();
  const returned=await paperFrame(page);
  expect(returned).not.toBe(frame);expect((await paperContent(returned)).page).toBe(first.page);
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();await expect(achievements).toBeFocused();await expect(page).toHaveURL(/\/$/);
  await page.keyboard.press('Enter');
  const reopened=await paperFrame(page);
  await expect(dialog).toHaveAttribute('data-paper-view','sheet');
  expect((await paperContent(reopened)).page).toBe(first.page);
  await paperLink(page,{href:'/about'});
  await expect(page).toHaveURL(/\/about$/);
  await expect(page.locator('main h1')).toHaveText('About');
});

test('paper: live reduced motion freezes authored idle motion and missing WebGL preserves content',async({page,browser})=>{
  await page.route('**/models/workspace-saved.glb*',route=>route.abort());
  await page.goto('/');await expect(page.locator('#desk-failure')).toBeVisible();
  await page.locator('.ws-nav [data-open-section=achievements]').click();
  const dialog=page.locator('#desk-content'),sheet=page.locator('#desk-paper');
  await expect(dialog).toHaveAttribute('data-paper','source');
  const movingFrame=await paperFrame(page);
  const movingTime=(await paperState(movingFrame)).time;
  await expect.poll(async()=>(await paperState(movingFrame)).time).toBeGreaterThan(movingTime);
  await page.emulateMedia({reducedMotion:'reduce'});
  await expect.poll(()=>movingFrame.isDetached()).toBe(true);
  const stillFrame=await paperFrame(page);
  expect((await paperState(stillFrame)).time).toBe(2.4);
  await expect(sheet).toHaveCSS('transform','none');
  await page.emulateMedia({reducedMotion:'no-preference'});
  await expect.poll(()=>stillFrame.isDetached()).toBe(true);
  const resumedFrame=await paperFrame(page);
  const resumedTime=(await paperState(resumedFrame)).time;
  await expect.poll(async()=>(await paperState(resumedFrame)).time).toBeGreaterThan(resumedTime);
  await expect(sheet).toHaveCSS('transform','none');
  await page.keyboard.press('Escape');await expect(dialog).not.toBeVisible();

  const context=await browser.newContext({reducedMotion:'reduce'});
  await context.addInitScript(()=>{
    const getContext=HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext=function(type:string,...args:unknown[]){
      if(type==='webgl'||type==='webgl2'||type==='experimental-webgl')return null;
      return getContext.call(this,type,...args);
    } as typeof getContext;
  });
  const fallback=await context.newPage();
  await fallback.goto('http://127.0.0.1:4322/');
  await expect(fallback.locator('#desk-failure')).toBeVisible();
  await fallback.locator('.ws-nav [data-open-section=achievements]').click();
  await expect(fallback.locator('#desk-content')).toHaveAttribute('data-paper','fallback');
  await expect(fallback.locator('[data-content-section=achievements]')).toBeVisible();
  await expect(fallback.locator('#desk-paper-preview iframe')).toHaveCount(0);
  await fallback.keyboard.press('Escape');
  const contact=fallback.locator('.ws-nav [data-open-section=contact]');
  await contact.click();
  await expectPlainContent(fallback,'contact');
  await expect(fallback.locator('[data-content-section=contact]')).toBeVisible();
  await expect(fallback.locator('[data-copy-email]')).toBeEnabled();
  await expect(fallback.locator('[data-content-section=contact] a[href="mailto:aadithva@outlook.com"]')).toBeVisible();
  await fallback.keyboard.press('Escape');
  await expect(fallback.locator('#desk-content')).not.toBeVisible();await expect(contact).toBeFocused();
  await context.close();
});

test('content: regular sections use readable HTML and contact actions survive room and computer history',async({page,context})=>{
  await context.grantPermissions(['clipboard-read','clipboard-write']);
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  await page.route('**/models/workspace-saved.glb*',route=>route.abort());
  await page.goto('/');await expect(page.locator('#desk-failure')).toBeVisible();
  const dialog=page.locator('#desk-content');
  // Begin with paper, then navigate to ordinary content in the same document.
  // The old iframe must be disposed instead of merely hidden behind the HTML.
  await page.locator('.ws-nav [data-open-section=achievements]').click();
  const achievementsFrame=await paperFrame(page);
  for(const section of ['work','about','writing','expeditions','experiments','design','play']){
    await page.goto(`/#desk-${section}`);
    await expectPlainContent(page,section);
    await expect(page.locator('[data-content-section]:visible')).toHaveCount(1);
    await expect(page.locator(`[data-content-section=${section}] .wc-title`)).toBeInViewport();
    await page.keyboard.press('Escape');await expect(dialog).not.toBeVisible();
  }
  expect(achievementsFrame.isDetached()).toBe(true);
  const contact=page.locator('.ws-nav [data-open-section=contact]');
  await contact.click();
  await expectPlainContent(page,'contact');
  await expect(dialog).toHaveAttribute('data-computer','false');
  await expect(dialog).toHaveAttribute('aria-labelledby','wc-contact-title');
  await expect(page.locator('[data-content-section]:visible')).toHaveCount(1);
  await expect(page).toHaveURL(/#desk-contact$/);
  await expect(page.locator('[data-content-section=contact]')).toContainText('aadithva@outlook.com');
  await page.locator('[data-copy-email]').click();
  await expect(page.locator('[data-copy-status]')).toHaveText('Email copied.');
  expect(await page.evaluate(()=>navigator.clipboard.readText())).toBe('aadithva@outlook.com');
  await page.keyboard.press('Escape');await expect(contact).toBeFocused();

  await page.locator('.ws-primary[data-open-computer]').click();
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-phase','ready');
  await page.locator('#computer-app-writing').click();
  await expectPlainContent(page,'writing');
  await page.keyboard.press('Escape');
  await expect(page.locator('#computer-app-writing')).toBeFocused();
  await page.locator('#computer-app-contact').click();
  await expectPlainContent(page,'contact');
  await expect(dialog).toHaveAttribute('data-computer','true');
  await expect(dialog).toHaveAttribute('aria-labelledby','wc-contact-title');
  await expect(page).toHaveURL(/#computer-contact$/);
  await page.goBack();await expect(dialog).not.toBeVisible();
  await expect(page.locator('#computer-desktop')).toBeVisible();
  await page.goForward();await expectPlainContent(page,'contact');
  await page.keyboard.press('Escape');await page.keyboard.press('Escape');
  await expect(page.locator('#computer-desktop')).not.toBeVisible();
  await expect(page).toHaveURL(/\/$/);
  await page.locator('.ws-nav [data-open-section=work]').click();
  await expectPlainContent(page,'work');
  const project=page.locator('[data-content-section=work] a[href="/work/owly-studio"]');
  await project.focus();await expect(project).toBeInViewport();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/work\/owly-studio$/);
  await expect(page.locator('main h1')).toHaveText('Owly');
  expect(errors).toEqual([]);
});

test('design: tactile navigation responds to keyboard and live reduced-motion changes', async ({page}) => {
  await ready(page);
  const dock=page.locator('[data-tactile-dock]');
  const work=dock.locator('[data-open-section=work]');
  await page.locator('.ws-wordmark').focus();
  await page.keyboard.press('Tab');
  await expect(work).toBeFocused();
  await expect.poll(()=>work.evaluate(element=>new DOMMatrixReadOnly(getComputedStyle(element).transform).a)).toBeGreaterThan(1.01);
  expect(await work.evaluate(element=>{
    const style=getComputedStyle(element);return style.outlineStyle!=='none'&&parseFloat(style.outlineWidth)>0;
  })).toBe(true);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.keyboard.press('Enter');
  await expect(page.locator('[data-content-section=work]')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(work).toBeFocused();
  await page.emulateMedia({reducedMotion:'reduce'});
  await expect.poll(()=>dock.locator('[data-dock-item]').evaluateAll(items=>items.every(item=>getComputedStyle(item).transform==='none'))).toBe(true);
  const writing=dock.locator('[data-open-section=writing]');
  await writing.focus();await page.keyboard.press('Enter');
  await expect(page.locator('[data-content-section=writing]')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(writing).toBeFocused();
  await expect(writing).toHaveCSS('transform','none');
});

test('design: touch guided views and navigation fit without horizontal overflow', async ({browser}) => {
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2,reducedMotion:'reduce'});
  const page=await context.newPage();await ready(page);
  for(const id of ['desk-detail','shelf-detail','overview']) {
    const control=page.locator(`[data-room-view="${id}"]`);
    await control.tap();
    await expect(control).toHaveAttribute('aria-pressed','true');
    await expect(page.locator('#desk-canvas')).toHaveAttribute('data-view',id);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  }
  const contact=page.locator('.ws-nav [data-open-section=contact]');
  await contact.tap();
  await expect(page.locator('[data-content-section=contact]')).toBeVisible();
  await expectPlainContent(page,'contact');
  await page.locator('#desk-back').tap();
  await expect(contact).toBeFocused();
  const wallCertificate=page.locator('[data-object=certificate_iitg]');
  await expect(wallCertificate).toBeVisible();
  await expect(wallCertificate).toBeInViewport();
  await wallCertificate.tap();
  await expect(page).toHaveURL(/#desk-achievements\/iitg-degree$/);
  await expectPaperFits(page);
  expect((await paperContent(await paperFrame(page))).section).toBe('achievements:iitg-degree');
  await page.locator('#desk-back').tap();
  await expect(wallCertificate).toBeFocused();
  const rideMedal=page.locator('[data-object=medal_1]');
  await expect(rideMedal).toBeVisible();
  await expect(rideMedal).toBeInViewport();
  const medalBounds=await rideMedal.boundingBox();
  if(!medalBounds)throw new Error('The Ride for Unity medal has no mobile tap target');
  expect(medalBounds.width).toBeGreaterThanOrEqual(44);
  expect(medalBounds.height).toBeGreaterThanOrEqual(44);
  await rideMedal.tap();
  await expect(page.locator('[data-content-section=achievements]')).toBeVisible();
  await expect(page).toHaveURL(/#desk-achievements\/ride-for-unity$/);
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-view','medal-detail');
  await expectRideMedalPaper(page);
  await page.locator('#desk-back').tap();
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(rideMedal).toBeFocused();
  const bounds=await page.locator('.ws-nav [data-dock-item], [data-room-view]').evaluateAll(items=>items.map(item=>{
    const rect=item.getBoundingClientRect();return {left:rect.left,right:rect.right,height:rect.height,transform:getComputedStyle(item).transform};
  }));
  for(const box of bounds) {
    expect(box.left).toBeGreaterThanOrEqual(0);expect(box.right).toBeLessThanOrEqual(390);
    expect(box.height).toBeGreaterThanOrEqual(44);expect(box.transform).toBe('none');
  }
  await context.close();
});

test('monitor enters the computer, Work opens a desktop window, Escape returns through both levels', async ({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await ready(page);
  const monitor=page.locator('[data-object=monitor]');
  await monitor.focus();await page.keyboard.press('Enter');
  await expect(page.locator('#computer-desktop')).toBeVisible();
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-phase','ready');
  await expect(page).toHaveURL(/#computer$/);
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-view','computer');
  const folder=page.locator('#computer-app-work');
  await folder.focus();await page.keyboard.press('Enter');
  await expect(page.locator('#desk-content')).toBeVisible();
  await expect(page.locator('#desk-content')).toHaveAttribute('data-computer','true');
  await expect(page.locator('[data-content-section=work] .wc-project')).toHaveCount(6);
  await expect(page.locator('[data-content-section=work] .wc-project').first()).toHaveAttribute('href','/work/owly-studio');
  await page.keyboard.press('Escape');
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(page.locator('#computer-desktop')).toBeVisible();
  await expect(folder).toBeFocused();
  await expect(page).toHaveURL(/#computer$/);
  await page.keyboard.press('Escape');
  await expect(page.locator('#computer-desktop')).not.toBeVisible();
  await expect(monitor).toBeFocused();
  await expect(page).toHaveURL(/\/$/);
  expect(errors).toEqual([]);
});

test('computer folders preserve browser history and the CRT toggle',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});
  await ready(page);await page.locator('[data-object=monitor]').click();
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-phase','ready');
  await page.locator('#computer-effects').click();
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-effects','off');
  await page.locator('#computer-app-writing').click();
  await expect(page.locator('[data-content-section=writing]')).toBeVisible();
  await expect(page.locator('#desk-content')).toHaveAttribute('data-effects','off');
  await expect(page).toHaveURL(/#computer-writing$/);
  await page.goBack();await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(page.locator('#computer-desktop')).toBeVisible();
  await page.goForward();await expect(page.locator('[data-content-section=writing]')).toBeVisible();
  await page.locator('#desk-back').click();
  await expect(page).toHaveURL(/#computer$/);
  await page.locator('#computer-exit').click();
  await expect(page.locator('#computer-desktop')).not.toBeVisible();
  await page.goForward();await expect(page.locator('#computer-desktop')).toBeVisible();
  await expect(page.locator('#desk-content')).not.toBeVisible();
});

test('computer entry can be cancelled before the camera arrives and boot can be skipped',async({page})=>{
  await ready(page);await page.locator('[data-object=monitor]').click();
  await expect(page.locator('#desk-stage')).toHaveAttribute('data-state','entering');
  await page.keyboard.press('Escape');
  await expect(page.locator('#desk-stage')).toHaveAttribute('data-state','idle');
  await expect(page.locator('#computer-desktop')).not.toBeVisible();
  await page.waitForTimeout(1100);
  await expect(page.locator('#computer-desktop')).not.toBeVisible();
  await page.locator('[data-object=monitor]').click();
  await page.locator('#desk-skip').click();
  await expect(page.locator('#computer-boot')).toBeVisible();
  await page.locator('#computer-skip').click();
  await expect(page.locator('#computer-desktop')).toHaveAttribute('data-phase','ready');
  await expect(page.locator('#computer-home')).toBeFocused();
});

test('computer deep links and folders work after WebGL asset failure',async({page})=>{
  await page.route('**/models/workspace-saved.glb*',route=>route.abort());
  await page.goto('/#computer-expeditions');
  await expect(page.locator('#computer-desktop')).toBeVisible();
  await expect(page.locator('[data-content-section=expeditions]')).toBeVisible();
  await page.locator('#desk-back').click();
  await expect(page).toHaveURL(/#computer$/);
  await page.locator('#computer-app-contact').click();
  await expect(page.locator('[data-content-section=contact]')).toBeVisible();
  await page.keyboard.press('Escape');await page.locator('#computer-exit').click();
  await expect(page.locator('#desk-failure')).toBeVisible();
  await expect(page).toHaveURL(/\/$/);
});

test('direct navigation during computer entry settles into a usable desktop window',async({page})=>{
  await ready(page);await page.locator('[data-object=monitor]').click();
  await page.locator('.ws-nav [data-open-section=writing]').click();
  await expect(page.locator('[data-content-section=writing]')).toBeVisible();
  await expect(page.locator('#computer-desktop')).toBeVisible();
  await page.locator('#desk-back').click();
  await expect(page.locator('#computer-app-work')).toBeVisible();
  await page.locator('#computer-exit').click();
  await expect(page.locator('#computer-desktop')).not.toBeVisible();
  await expect(page.locator('[data-object=monitor]')).toBeFocused();
});

test('mobile computer folders, scroll and return remain usable by touch',async({browser})=>{
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2,reducedMotion:'reduce'});
  const page=await context.newPage();await ready(page);
  await page.locator('[data-object=monitor]').tap();
  await expect(page.locator('#computer-desktop')).toBeVisible();
  expect(await page.locator('#computer-desktop').evaluate(n=>n.scrollWidth)).toBeLessThanOrEqual(390);
  await page.locator('#computer-app-work').tap();
  await expect(page.locator('[data-content-section=work] .wc-project')).toHaveCount(6);
  await expectPlainContent(page,'work');
  await page.locator('#desk-back').tap();
  await page.locator('#computer-app-expeditions').tap();
  await expect(page.locator('[data-content-section=expeditions]')).toBeVisible();
  await page.locator('#desk-close').tap();
  await page.locator('#computer-exit').tap();
  await expect(page.locator('[data-object=monitor]')).toBeFocused();
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-view','overview');
  await context.close();
});

test('cursor reveals upper and lower desk, reset recenters, and reduced motion stays still',async({page})=>{
  // Read the neutral pose from the loaded scene so composition changes do not
  // make this an assertion about one particular desk height.
  await page.emulateMedia({reducedMotion:'reduce'});
  await ready(page);
  const stage=await page.locator('#desk-stage').boundingBox();
  if(!stage)throw new Error('Desk stage is missing');
  const y=()=>page.locator('#desk-canvas').evaluate(el=>Number((el as HTMLElement).dataset.cameraTargetY));
  const settledY=async()=>{
    let previous=NaN,current=NaN,stableSamples=0;
    await expect.poll(async()=>{
      current=await y();stableSamples=Math.abs(current-previous)<.002?stableSamples+1:0;previous=current;
      return stableSamples;
    },{intervals:[80]}).toBeGreaterThanOrEqual(2);
    return current;
  };
  await expect.poll(async()=>Number.isFinite(await y())).toBe(true);
  const neutralY=await y();
  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.mouse.move(stage.x+stage.width/2,stage.y+12);
  // The composed overview intentionally caps travel at .24 up / .20 down.
  // A point 12px inside the stage is slightly below either maximum.
  await expect.poll(async()=>(await y())-neutralY).toBeGreaterThanOrEqual(.21);
  const upperTravel=(await settledY())-neutralY;
  expect(upperTravel).toBeLessThanOrEqual(.241);
  await page.mouse.move(stage.x+stage.width/2,stage.y+stage.height-12);
  await expect.poll(async()=>neutralY-(await y())).toBeGreaterThanOrEqual(.18);
  const lowerTravel=neutralY-(await settledY());
  expect(lowerTravel).toBeLessThanOrEqual(.201);
  await test.info().attach('overview-parallax-measurement',{body:JSON.stringify({upperTravel,lowerTravel,stage}),contentType:'application/json'});
  await page.locator('#desk-reset').click();
  await expect.poll(y).toBeCloseTo(neutralY,2);
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.mouse.move(stage.x+stage.width/2,stage.y+12);
  await page.waitForTimeout(300);
  expect(await y()).toBeCloseTo(neutralY,2);
});

test('wall certificate and medal open their own achievement content, preserve history, and retain two trophies',async({page})=>{
  // This flow opens several fresh paper frames and reloads the room. Keep the
  // per-action checks bounded while allowing time for the complete history flow.
  test.setTimeout(45000);
  await page.emulateMedia({reducedMotion:'reduce'});
  const loadedModel=page.waitForResponse(response=>/\/models\/workspace-saved\.glb(?:\?|$)/.test(response.url())&&response.ok()).then(response=>response.url());
  await ready(page);

  // Check the served asset as well as its controls: removing a binding alone
  // must not leave removed medals or the unwanted third trophy in the room.
  // Read the exact versioned URL through the request client. Chrome may evict
  // this large binary from its inspector body cache while Three.js decodes it.
  const modelResponse=await page.request.get(await loadedModel);
  expect(modelResponse.ok()).toBe(true);
  const model=await modelResponse.body();
  expect(model.readUInt32LE(16)).toBe(0x4e4f534a);
  const gltf=JSON.parse(model.subarray(20,20+model.readUInt32LE(12)).toString('utf8'));
  const nodeNames=(gltf.nodes as {name?:string}[]).map(node=>node.name);
  for(const name of ['trophy_1','trophy_2']) {
    expect(nodeNames).toContain(name);
    await expect(page.locator(`[data-object=${name}]`)).toHaveCount(1);
  }
  expect(nodeNames.some(name=>name==='trophy_3'||name?.startsWith('trophy_3_'))).toBe(false);
  await expect(page.locator('[data-object=trophy_3]')).toHaveCount(0);
  expect(nodeNames).toContain('medal_1');
  await expect(page.locator('[data-object=medal_1]')).toHaveCount(1);
  for(const name of ['medal_2','medal_3']) {
    expect(nodeNames.some(node=>node===name||node?.startsWith(`${name}_`))).toBe(false);
    await expect(page.locator(`[data-object=${name}]`)).toHaveCount(0);
  }
  expect(nodeNames).toContain('certificate_iitg');
  const certificate=page.locator('[data-object=certificate_iitg]');
  await expect(certificate).toBeVisible();
  await expect(certificate).toHaveAccessibleName('IIT Guwahati graduation certificate');
  await certificate.focus();await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/#desk-achievements\/iitg-degree$/);
  await expect(page.locator('#desk-content')).toHaveAttribute('data-achievement','iitg-degree');
  const certificateFrame=await paperFrame(page);
  expect((await paperContent(certificateFrame)).section).toBe('achievements:iitg-degree');
  await expect.poll(async()=>(await paperContent(certificateFrame)).artwork?.loaded).toBe(true);
  expect((await paperContent(certificateFrame)).artwork?.alt).toBe('Bachelor of Design · IIT Guwahati');
  expect((await paperContent(certificateFrame)).renderedText).not.toContain('Ride for Unity');
  await page.keyboard.press('Escape');
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(certificate).toBeFocused();

  const medal=page.locator('[data-object=medal_1]');
  await expect(medal).toBeVisible();
  await expect(medal).toHaveAccessibleName('Ride for Unity medal');
  await medal.focus();await page.keyboard.press('Enter');
  await expect(page.locator('[data-content-section=achievements]')).toBeVisible();
  await expect(page).toHaveURL(/#desk-achievements\/ride-for-unity$/);
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-view','medal-detail');
  await expectRideMedalPaper(page);
  await page.locator('#desk-paper-reader').click();
  await expect(page.locator('#desk-content')).toHaveAttribute('data-paper-view','reader');
  const achievement=page.locator('[data-achievement-id=ride-for-unity]');
  await expect(achievement).toBeVisible();
  await expect(page.locator('[data-achievement-id=iitg-degree]')).not.toBeVisible();
  expect(await page.locator('[data-content-section=achievements]').innerText()).not.toMatch(/IIT Guwahati|Bachelor of Design|Microsoft|Owly/);
  await expect(achievement).toContainText('roughly 4,000 km in 16 days');
  const medalPhoto=achievement.getByRole('img',{name:'Ride for Unity medal'});
  await expect(medalPhoto).toHaveAttribute('src','/textures/workspace/ride-for-unity-medal.jpg');
  await medalPhoto.scrollIntoViewIfNeeded();
  await expect.poll(()=>medalPhoto.evaluate(image=>(image as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  await expect(achievement.getByRole('link',{name:/Read more/})).toHaveAttribute('href','/expeditions#ride-for-unity');
  await page.locator('#desk-paper-reader').click();
  await expectRideMedalPaper(page);
  await page.goBack();
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(medal).toBeFocused();
  await page.goForward();
  await expect(page).toHaveURL(/#desk-achievements\/ride-for-unity$/);
  await expectRideMedalPaper(page);
  await page.reload();
  await expect(page).toHaveURL(/#desk-achievements\/ride-for-unity$/);
  await expectRideMedalPaper(page);
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-view','medal-detail');
  await page.keyboard.press('Escape');
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(medal).toBeFocused();
  await expect(page).toHaveURL(/\/$/);
  await page.locator('.ws-nav [data-open-section=achievements]').click();
  await expect(page).toHaveURL(/#desk-achievements$/);
  await expect(page.locator('#desk-content')).not.toHaveAttribute('data-achievement',/./);
  const collection=await paperFrame(page);
  expect((await paperContent(collection)).section).toBe('achievements');
  await expect.poll(async()=>(await paperContent(collection)).artwork?.loaded).toBe(true);
  expect((await paperContent(collection)).artwork?.alt).toBe('Bachelor of Design · IIT Guwahati');
  await page.locator('#desk-paper-reader').click();
  await expect(page.locator('[data-achievement-id=iitg-degree]')).toBeVisible();
  await expect(page.locator('[data-achievement-id=ride-for-unity]')).toBeVisible();
});

test('rapid section changes, browser Back and Forward, guide and contact copy', async ({page,context})=>{
  await context.grantPermissions(['clipboard-read','clipboard-write']);
  await ready(page);
  await page.locator('.ws-nav [data-open-section=work]').click();
  await page.locator('.ws-nav [data-open-section=about]').click();
  await expect(page.locator('[data-content-section=about]')).toBeVisible();
  await page.locator('#desk-back').click();
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(page).toHaveURL(/\/$/);
  await page.goForward();await expect(page.locator('[data-content-section=about]')).toBeVisible();
  await page.goBack();await expect(page.locator('#desk-content')).not.toBeVisible();
  await page.locator('#desk-guide').click();await expect(page.locator('#desk-guide-panel')).toBeVisible();
  await page.keyboard.press('Escape');await expect(page.locator('#desk-guide')).toBeFocused();
  await page.locator('.ws-nav [data-open-section=contact]').click();
  await expectPlainContent(page,'contact');
  await page.locator('[data-copy-email]').click();
  await expect(page.locator('[data-copy-status]')).toHaveText('Email copied.');
  expect(await page.evaluate(()=>navigator.clipboard.readText())).toBe('aadithva@outlook.com');
});

test('mobile has no horizontal overflow and laptop and black controller remain usable tap targets', async ({browser})=>{
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2});
  const page=await context.newPage();await ready(page);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBe(390);
  await page.locator('[data-object=laptop]').tap();
  await expect(page.locator('[data-content-section=experiments]')).toBeVisible();
  await expectPlainContent(page,'experiments');
  await expect(page.locator('[data-content-section=experiments]')).toContainText('Small builds. Useful questions.');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBe(390);
  await page.locator('#desk-back').tap();
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await page.locator('[data-object=controller_black]').tap();
  await expect(page.locator('[data-content-section=play]')).toBeVisible();
  await expectPlainContent(page,'play');
  await page.getByRole('button',{name:'Take a closer look at the laptop'}).tap();
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(page.locator('#desk-canvas')).toHaveAttribute('data-view','experiments');
  const limits=await page.locator('#desk-canvas').evaluate(n=>({calls:Number((n as HTMLElement).dataset.drawCalls),triangles:Number((n as HTMLElement).dataset.geometryTriangles),dpr:Number((n as HTMLElement).dataset.pixelRatio)}));
  expect(limits.calls).toBeLessThan(200);expect(limits.triangles).toBeLessThan(180000);expect(limits.dpr).toBeLessThanOrEqual(1.35);
  await context.close();
});

test('content works while model is loading and after a failed model request',async({page})=>{
  await page.route('**/models/workspace-saved.glb*',route=>route.abort());
  await page.goto('/');await expect(page.locator('#desk-failure')).toBeVisible();
  await page.locator('.ws-nav [data-open-section=work]').click();
  await expect(page.locator('[data-content-section=work]')).toBeVisible();
  await page.locator('#desk-back').click();
  await page.unroute('**/models/workspace-saved.glb*');await page.locator('#desk-retry').click();
  await expect(page.locator('#desk-stage')).toHaveAttribute('data-ready','true');
});

test('reduced motion skips arrival, preserves navigation, and sound is opt-in',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});await ready(page);
  await expect(page.locator('#desk-skip')).not.toBeVisible();
  await expect(page.locator('#desk-sound')).toHaveAttribute('aria-pressed','false');
  await page.locator('#desk-day').click();await expect(page.locator('body')).toHaveAttribute('data-period','day');
  await page.locator('#desk-sound').click();await expect(page.locator('#desk-sound')).toHaveAttribute('aria-pressed','true');
  await page.locator('#desk-sound').click();await expect(page.locator('#desk-sound')).toHaveAttribute('aria-pressed','false');
  await page.locator('.ws-nav [data-open-section=writing]').click();
  await expect(page.locator('[data-content-section=writing]')).toBeVisible();
});

test('no JavaScript preserves all primary destinations',async({browser})=>{
  const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();
  await page.goto('http://127.0.0.1:4322/');
  await expect(page.locator('.ws-nav a')).toHaveText(['Work','About','Writing','Achievements','Expeditions','Contact']);
  await page.locator('.ws-nav a').filter({hasText:'Achievements'}).click();
  await expect(page.locator('h1')).toHaveText('Achievements');
  await context.close();
});

test('a browser without WebGL still opens portfolio content',async({page})=>{
  await page.addInitScript(()=>{
    const getContext=HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext=function(type:string,...args:unknown[]){
      if(type==='webgl'||type==='webgl2'||type==='experimental-webgl')return null;
      return getContext.call(this,type,...args);
    } as typeof getContext;
  });
  await page.goto('/');await expect(page.locator('#desk-failure')).toBeVisible();

  await page.locator('.ws-nav [data-open-section=about]').click();
  await expect(page.locator('[data-content-section=about]')).toBeVisible();
});

test('Expeditions direct navigation supports keyboard, history and focus return without 3D',async({page})=>{
  await page.route('**/models/workspace-saved.glb*',route=>route.abort());
  await page.goto('/');
  await expect(page.locator('#desk-failure')).toBeVisible();
  const link=page.locator('.ws-nav [data-open-section=expeditions]');
  await link.focus();await page.keyboard.press('Enter');
  const panel=page.locator('[data-content-section=expeditions]');
  await expect(page.getByRole('dialog',{name:'Across India, twice.'})).toBeVisible();
  await expect(page).toHaveURL(/#desk-expeditions$/);
  await expect(link).toHaveAttribute('aria-current','true');
  await expect(panel.locator('article')).toHaveCount(2);
  await expectPlainContent(page,'expeditions');
  await expect(panel.getByRole('heading',{name:'Ride for Unity'})).toBeVisible();
  await expect(panel.locator('dd')).toHaveText(['Roughly 4,000 km','16 days','About 150 riders','Kerala']);
  await page.goBack();
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(link).toBeFocused();
  await expect(page).toHaveURL(/\/$/);
  await page.goForward();
  await expect(panel).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(link).toBeFocused();
  await expect(page).toHaveURL(/\/$/);
});

test('Expeditions hash entry survives model failure and closes without a prior desk history entry',async({page})=>{
  await page.route('**/models/workspace-saved.glb*',route=>route.abort());
  await page.goto('/#desk-expeditions');
  await expect(page.locator('[data-content-section=expeditions]')).toBeVisible();
  await expect(page.locator('#desk-failure')).toBeVisible();
  await expect(page.locator('#desk-content')).toHaveAttribute('aria-labelledby','wc-expeditions-title');
  await page.locator('#desk-back').click();
  await expect(page.locator('#desk-content')).not.toBeVisible();
  await expect(page).toHaveURL(/\/$/);
  await page.locator('#desk-guide').click();
  await page.locator('#desk-guide-panel [data-open-section=expeditions]').click();
  await expect(page.locator('[data-content-section=expeditions]')).toBeVisible();
  await expect(page.locator('#desk-guide-panel')).not.toBeVisible();
});

test('Expeditions standalone page retains the documented stories and links without JavaScript',async({browser})=>{
  const context=await browser.newContext({javaScriptEnabled:false});
  const page=await context.newPage();
  await page.goto('http://127.0.0.1:4322/');
  await page.locator('.ws-nav a[href="/expeditions"]').click();
  await expect(page).toHaveURL(/\/expeditions$/);
  await expect(page.getByRole('heading',{level:1})).toHaveText('Expeditions');
  await expect(page.locator('.expedition-story')).toHaveCount(2);
  await expect(page.locator('#ride-for-unity .prose')).toContainText('I represented Kerala and relied on a large support team.');
  await expect(page.locator('#first-cross-country-ride .expedition-note')).toContainText("The exact date, distance and duration of this ride aren't recorded here.");
  await expect(page.getByRole('img',{name:/Dotted map of India/})).toBeVisible();
  expect(await page.locator('.route-path').evaluate(el=>getComputedStyle(el).strokeDashoffset)).toBe('0px');
  await page.getByRole('link',{name:'The first ride north',exact:true}).focus();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/expeditions#first-cross-country-ride$/);
  await expect(page.locator('#first-cross-country-ride')).toBeInViewport();
  await page.getByRole('link',{name:'Original cycling stories',exact:true}).focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading',{level:1})).toHaveText('Adventures');
  await context.close();
});

test('Expeditions mobile content supports taps, scrolling and the standalone fallback',async({browser})=>{
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2});
  const page=await context.newPage();
  await page.route('**/models/workspace-saved.glb*',route=>route.abort());
  await page.goto('http://127.0.0.1:4322/');
  await expect(page.locator('#desk-failure')).toBeVisible();
  await page.locator('.ws-nav [data-open-section=expeditions]').tap();
  const panel=page.locator('[data-content-section=expeditions]');
  await expect(panel).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBe(390);
  await expectPlainContent(page,'expeditions');
  expect(await page.locator('#desk-content-scroll').evaluate(el=>el.scrollWidth<=el.clientWidth)).toBe(true);
  const firstRide=panel.getByRole('heading',{name:'The first ride north'});
  await firstRide.scrollIntoViewIfNeeded();
  await expect(firstRide).toBeInViewport();
  await expect(panel.locator('.wc-empty')).toHaveText("Ride photographs and day-by-day route notes haven't been added yet.");
  await panel.getByRole('link',{name:'Read the expedition notes'}).tap();
  await expect(page).toHaveURL(/\/expeditions$/);
  await expect(page.getByRole('heading',{level:1})).toHaveText('Expeditions');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBe(390);
  await page.getByRole('link',{name:'Back to the desk',exact:true}).tap();
  await expect(page.locator('.ws-nav [data-open-section=expeditions]')).toBeVisible();
  await context.close();
});
