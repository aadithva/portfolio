import { DeskAudio } from './audio';
import { objectBindings, achievementViews, type AchievementId, type SectionId, type GuidedViewId } from './config';
import type { DeskScene, MonitorProject } from './scene';
import { initPaperPanel } from '../ui/paper-panel';

/** The DOM owns content; Three.js only owns the room and camera. */
export function initWorkspace() {
  const el = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
  const stage=el('desk-stage'),mount=el('desk-canvas'),hotspots=el('desk-hotspots');
  const dialog=el<HTMLDialogElement>('desk-content'),loader=el('desk-loader'),failure=el('desk-failure');
  const disposePaper=initPaperPanel(dialog);
  const computer=el<HTMLDialogElement>('computer-desktop');
  const skip=el<HTMLButtonElement>('desk-skip'),progress=el<HTMLProgressElement>('desk-progress');
  const guide=el('desk-guide-panel'),guideButton=el<HTMLButtonElement>('desk-guide');
  const tooltip=el('desk-tooltip'),toast=el('desk-toast');
  const audio=new DeskAudio(),media=window.matchMedia('(prefers-reduced-motion: reduce)');
  const sections=new Set<SectionId>(['work','about','writing','achievements','experiments','contact','design','play','expeditions']);
  const titles: Record<SectionId,string>={work:'Work',about:'About',writing:'Writing',achievements:'Achievements',experiments:'Experiments',contact:'Contact',design:'Design experiments',play:'A little side quest',expeditions:'Expeditions'};
  let scene: DeskScene | undefined;
  let ready=false,selected: SectionId|null=null,selectionToken=0,source: HTMLElement|null=null,day=false,disposed=false,loadAttempt=0;
  let selectedAchievement: AchievementId | undefined;
  let computerActive=false,computerSource: HTMLElement|null=null,effects=true;
  let bootTimer: ReturnType<typeof setTimeout>;
  let routedHash=location.hash;
  let toastTimer: ReturnType<typeof setTimeout>,arrivalTimer: ReturnType<typeof setTimeout>;
  let transitionState: 'loading'|'idle'|'selected'|'returning'|'entering'|'computer'|'guided'='loading';
  const abort=new AbortController(),signal=abort.signal,found=new Set<string>();
  const projects: MonitorProject[]=JSON.parse(el('workspace-projects').textContent||'[]');

  function notify(message: string) {toast.textContent=message;toast.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.hidden=true,3500);}
  function markRoomView(view: GuidedViewId) {
    document.querySelectorAll<HTMLElement>('[data-room-view]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.roomView===view)));
  }
  function setState(state: typeof transitionState) {transitionState=state;stage.dataset.state=state;if(state==='returning')markRoomView('overview');}
  async function showRoomView(view: GuidedViewId) {
    if(!ready||!scene||selected||computerActive)return;
    const token=++selectionToken;
    closeGuide();clearTimeout(arrivalTimer);skip.hidden=true;scene.setHunt(false);
    markRoomView(view);setState('guided');scene.activity();
    await scene.toView(view,media.matches?0:850);
    if(token===selectionToken&&!selected&&!computerActive)setState('idle');
  }
  function updateAudio(){const b=el<HTMLButtonElement>('desk-sound');b.setAttribute('aria-pressed',String(audio.enabled));b.childNodes[0].textContent=audio.enabled?'Sound on ':'Sound off ';b.title=audio.playing?'Ambient sound is playing. Click to mute.':'Enable or mute desk sounds';}
  function setDay(value: boolean){day=value;scene?.setDay(value);document.body.dataset.period=value?'day':'night';const b=el<HTMLButtonElement>('desk-day');b.setAttribute('aria-pressed',String(value));b.setAttribute('aria-label',value?'Switch to nighttime':'Switch to daytime');b.childNodes[0].textContent=value?'Day ':'Night ';el('desk-scene-status').textContent=value?'Daylight at the desk':'Night at the desk';}
  function closeGuide(){guide.hidden=true;guideButton.setAttribute('aria-expanded','false');}
  function currentHash(){const id=location.hash.replace('#desk-','').split('/')[0] as SectionId;return location.hash.startsWith('#desk-')&&sections.has(id)?id:null;}
  function currentAchievement(){const id=location.hash.split('/')[1] as AchievementId;return currentHash()==='achievements'&&Object.hasOwn(achievementViews,id)?id:undefined;}
  function contentView(){return selected==='achievements'&&selectedAchievement?achievementViews[selectedAchievement]:selected!;}
  function updateStickerCount(){document.querySelectorAll<HTMLElement>('[data-sticker-count]').forEach(node=>node.textContent=String(found.size));}
  function computerRoute() {
    if(location.hash==='#computer')return {section:null};
    const id=location.hash.replace('#computer-','') as SectionId;
    return location.hash.startsWith('#computer-')&&sections.has(id)?{section:id}:null;
  }
  function writeHistory(hash:string,state:object,replace=false) {
    history[replace?'replaceState':'pushState'](state,'',hash);routedHash=location.hash;
  }
  function finishBoot() {
    clearTimeout(bootTimer);computer.dataset.phase='ready';
    if(computer.open&&!dialog.open)el<HTMLButtonElement>('computer-home').focus({preventScroll:true});
  }
  async function enterComputer(trigger?:HTMLElement,updateHistory=true,animate=true) {
    if(computerActive)return;
    closeGuide();clearTimeout(arrivalTimer);clearTimeout(bootTimer);
    const token=++selectionToken;
    computerActive=true;selected=null;computerSource=trigger||document.activeElement as HTMLElement;
    // Load desktop previews during the camera approach, after the visitor enters.
    computer.querySelectorAll<HTMLImageElement>('img[loading="lazy"]').forEach(image=>image.loading='eager');
    source=null;if(dialog.open)dialog.close();
    computer.dataset.phase=media.matches||!animate?'ready':'booting';
    setState('entering');scene?.setEnabled(false);scene?.setComputerMode(true);
    if(updateHistory)writeHistory('#computer',{deskComputer:true,deskComputerEntry:true});
    skip.textContent='Skip entry';skip.hidden=media.matches||!animate||!ready;
    if(ready&&scene)await scene.toView('computer',media.matches||!animate?0:1000);
    if(token!==selectionToken||disposed)return;
    skip.hidden=true;skip.textContent='Skip arrival';
    if(!computer.open)computer.showModal();
    setState('computer');
    if(media.matches||!animate)finishBoot();
    else {el<HTMLButtonElement>('computer-skip').focus({preventScroll:true});bootTimer=setTimeout(finishBoot,900);}
  }
  async function returnToDesktop(updateHistory=true) {
    ++selectionToken;selected=null;if(dialog.open)dialog.close();
    document.querySelectorAll('[data-open-section]').forEach(a=>a.removeAttribute('aria-current'));
    if(updateHistory&&computerRoute()?.section) {
      if(history.state?.deskComputerSection)history.back();
      else writeHistory('#computer',{deskComputer:true},true);
    }
    setState('computer');(source||el('computer-home')).focus({preventScroll:true});source=null;
  }
  async function exitComputer(updateHistory=true,animate=true) {
    const token=++selectionToken;
    clearTimeout(bootTimer);computerActive=false;selected=null;source=null;
    if(dialog.open)dialog.close();if(computer.open)computer.close();
    computer.dataset.phase='ready';skip.hidden=true;skip.textContent='Skip arrival';
    document.querySelectorAll('[data-open-section]').forEach(a=>a.removeAttribute('aria-current'));
    if(updateHistory&&computerRoute()) {
      if(history.state?.deskComputerEntry)history.back();
      else writeHistory(location.pathname+location.search,{},true);
    }
    scene?.setComputerMode(false);scene?.setEnabled(true);setState('returning');
    const restore=computerSource;computerSource=null;
    if(ready&&scene)await scene.toView('overview',media.matches||!animate?0:650);
    if(token!==selectionToken)return;
    // The on-screen hotspot becomes visible on the next Three.js frame after an
    // instant reduced-motion camera return. Focusing a hidden button is ignored.
    if(restore?.isConnected){await new Promise<void>(resolve=>requestAnimationFrame(()=>resolve()));if(token!==selectionToken)return;restore.focus({preventScroll:true});}
    setState(ready?'idle':'loading');
  }

  async function openSection(section: SectionId, trigger?: HTMLElement, updateHistory=true, achievement?: AchievementId) {
    if(!sections.has(section))return;
    closeGuide();skip.hidden=true;clearTimeout(arrivalTimer);
    const token=++selectionToken;
    const wasSelected = selected !== null;
    selected=section;source=trigger||document.activeElement as HTMLElement;setState('selected');
    selectedAchievement=section==='achievements'?achievement:undefined;
    if(selectedAchievement)dialog.dataset.achievement=selectedAchievement;
    else delete dialog.dataset.achievement;
    if(computerActive){
      clearTimeout(bootTimer);computer.dataset.phase='ready';
      // A direct navigation click may arrive during the camera approach.
      // Complete that entry before opening a window above the desktop.
      if(!computer.open){scene?.skipTransition();computer.showModal();}
      skip.hidden=true;skip.textContent='Skip arrival';
      if(updateHistory&&computerRoute()?.section!==section)writeHistory(`#computer-${section}`,{deskComputer:true,deskComputerSection:section},wasSelected);
    }else if(updateHistory){
      const hash=`#desk-${section}${selectedAchievement?`/${selectedAchievement}`:''}`;
      if(location.hash!==hash)writeHistory(hash,{deskSection:section},wasSelected);
    }
    document.querySelectorAll('[data-open-section]').forEach(a=>{if((a as HTMLElement).dataset.openSection===section)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});
    document.querySelectorAll<HTMLElement>('[data-content-section]').forEach(node=>node.hidden=node.dataset.contentSection!==section);
    const entryTitle=selectedAchievement?dialog.querySelector(`[data-achievement-id="${selectedAchievement}"] h3`)?.textContent:undefined;
    el('desk-dialog-title').textContent=entryTitle||titles[section];dialog.setAttribute('aria-labelledby',`wc-${section}-title`);
    dialog.dataset.computer=String(computerActive);dialog.dataset.effects=effects?'on':'off';
    el('desk-back').innerHTML=computerActive?'<span aria-hidden="true">←</span> Desktop':'<span aria-hidden="true">←</span> Back to desk';
    el('desk-close').setAttribute('aria-label',computerActive?'Close window and return to desktop':'Close and return to desk');
    scene?.setEnabled(false);
    // Fast HTML access is independent of WebGL, network speed, or camera readiness.
    if(!computerActive&&ready&&scene&&!dialog.open)await scene.toView(contentView(),media.matches?0:760);
    if(token!==selectionToken||disposed)return;
    if(!dialog.open)dialog.showModal();
    el('desk-content-scroll').scrollTop=0;
    el<HTMLButtonElement>('desk-back').focus({preventScroll:true});
  }
  async function returnToDesk(updateHistory=true) {
    if(computerActive){await returnToDesktop(updateHistory);return;}
    ++selectionToken;selected=null;setState('returning');
    if(dialog.open)dialog.close();
    document.querySelectorAll('[data-open-section]').forEach(a=>a.removeAttribute('aria-current'));
    if(updateHistory&&currentHash()) {
      // An owned history entry lets browser Back and the UI's Back agree.
      if(history.state?.deskSection)history.back();
      else history.replaceState(null,'',location.pathname+location.search);
    }
    scene?.setEnabled(true);
    // A detail URL can load before hotspots exist; resolve its return target
    // after the scene has loaded instead of trying to focus the document body.
    const objectName=selectedAchievement?Object.entries(objectBindings).find(([,binding])=>binding.achievement===selectedAchievement)?.[0]:undefined;
    const entryTrigger=objectName?hotspots.querySelector<HTMLButtonElement>(`[data-object="${objectName}"]`):null;
    const restore=source&&source!==document.body&&source!==document.documentElement&&source.isConnected?source:entryTrigger;
    source=null;
    const token=selectionToken;
    if(ready&&scene)await scene.toView('overview');
    if(token!==selectionToken||disposed)return;
    // Camera-focused sections can hide their original hotspot. Wait for the
    // overview and its next projected frame before returning keyboard focus.
    if(restore?.isConnected){
      await new Promise<void>(resolve=>requestAnimationFrame(()=>resolve()));
      if(token!==selectionToken||disposed)return;
      restore.focus({preventScroll:true});
    }
    setState(ready?'idle':'loading');
  }
  async function objectAction(name: string,trigger?: HTMLElement) {
    const binding=objectBindings[name];if(!binding)return;
    if(name==='monitor'){void enterComputer(trigger);return;}
    if(binding.section){void openSection(binding.section,trigger,true,binding.achievement);return;}
    if(binding.action==='can'){audio.tap('metal');notify(audio.enabled?'Clink. Back to it.':'A tiny caffeine break. Sound is off.');}
    else if(binding.action?.startsWith('lamp_')){const index=Number(binding.action.split('_')[1])-1;const on=scene?.toggleLamp(index);audio.tap('switch');notify(`Light ${index+1} ${on?'on':'off'}.`);}
    else if(binding.action==='day'){setDay(!day);notify(day?'A little daylight.':'Back to the night shift.');}
    else if(binding.action==='speaker'){try{await audio.toggleAmbient();updateAudio();notify(audio.playing?'Ambient sound on. Mute any time below.':'Ambient sound paused.');}catch{notify('Audio is unavailable in this browser.');}}
    else if(binding.action==='sticker'){if(!found.has(name)){found.add(name);updateStickerCount();notify(found.size===2?'Both stickers found. Nicely spotted.':`${found.size} of 2 stickers found. Keep looking around the laptop.`);}else notify('You already found this one.');}
  }

  async function loadScene() {
    const attempt=++loadAttempt;ready=false;scene?.dispose();scene=undefined;loader.hidden=false;failure.hidden=true;progress.value=0;setState('loading');
    try{
      const {DeskScene}=await import('./scene');
      if(disposed||attempt!==loadAttempt)return;
      scene=new DeskScene({mount,hotspots,reducedMotion:media.matches,projects,
        onProgress:(value,detail)=>{progress.value=value;el('desk-load-detail').textContent=detail;},
        onReady:()=>{
          if(attempt!==loadAttempt)return;
          ready=true;loader.hidden=true;failure.hidden=true;stage.dataset.ready='true';el('desk-caption').hidden=false;setState(computerActive?(selected?'selected':computer.open?'computer':'entering'):selected?'selected':'idle');setDay(day);updateCameraControls();
           if(computerActive){scene?.setEnabled(false);scene?.setComputerMode(true);void scene?.toView('computer',0);}
           else if(selected){scene?.setEnabled(false);void scene?.toView(contentView(),0);}
           else if(!media.matches){skip.hidden=false;arrivalTimer=setTimeout(()=>skip.hidden=true,1200);}
        },
        onError:message=>{if(attempt!==loadAttempt)return;ready=false;scene?.setEnabled(false);loader.hidden=true;failure.hidden=false;el('desk-error-message').textContent=message;skip.hidden=true;stage.dataset.ready='false';},
        onObject:(name,trigger)=>void objectAction(name,trigger),
        onHover:(label,x,y)=>{tooltip.hidden=!label||!!selected;if(label){tooltip.textContent=label;tooltip.style.left=`${Math.max(12,Math.min(x+17,stage.clientWidth-210))}px`;tooltip.style.top=`${Math.max(5,y-43)}px`;}}
      });
      await scene.load();
    }catch(error){if(disposed)return;console.error('3D is unavailable',error);loader.hidden=true;failure.hidden=false;el('desk-error-message').textContent='Your browser could not start the 3D room. You can still explore every project and section.';}
  }

  document.addEventListener('click',event=>{
    const entry=(event.target as HTMLElement).closest<HTMLElement>('[data-open-computer]');
    if(entry&&!event.ctrlKey&&!event.metaKey&&!event.shiftKey&&!event.altKey&&event.button===0){event.preventDefault();void enterComputer(entry);return;}
    const link=(event.target as HTMLElement).closest<HTMLAnchorElement>('[data-open-section]');
    if(!link||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||event.button!==0)return;
    const section=link.dataset.openSection as SectionId;if(!sections.has(section))return;
    event.preventDefault();void openSection(section,link);
  },{signal});
  el('computer-exit').addEventListener('click',()=>void exitComputer(),{signal});
  el('computer-home').addEventListener('click',()=>{finishBoot();if(selected)void returnToDesktop();},{signal});
  el('computer-skip').addEventListener('click',finishBoot,{signal});
  el('computer-effects').addEventListener('click',()=>{
    effects=!effects;computer.dataset.effects=effects?'on':'off';dialog.dataset.effects=effects?'on':'off';
    const button=el('computer-effects');button.setAttribute('aria-pressed',String(effects));button.textContent=effects?'Texture on':'Texture off';
  },{signal});
  computer.addEventListener('cancel',event=>{event.preventDefault();void exitComputer();},{signal});
  for(const id of ['desk-back','desk-close'])el(id).addEventListener('click',()=>void returnToDesk(),{signal});
  dialog.addEventListener('cancel',event=>{event.preventDefault();void returnToDesk();},{signal});
  dialog.addEventListener('click',event=>{if(event.target!==dialog)return;const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)void returnToDesk();},{signal});
  el('desk-reset').addEventListener('click',()=>{if(selected)void returnToDesk();else void showRoomView('overview');}, {signal});
  const zoomIn=el<HTMLButtonElement>('desk-zoom-in'),zoomOut=el<HTMLButtonElement>('desk-zoom-out'),cameraCenter=el<HTMLButtonElement>('desk-camera-center');
  function updateCameraControls(){
    const state=scene?.getNavigationState();
    el('desk-camera-controls').hidden=!ready||!!selected||computerActive;
    zoomIn.disabled=!state?.canZoomIn;zoomOut.disabled=!state?.canZoomOut;
    cameraCenter.disabled=!state?.enabled;
  }
  mount.addEventListener('desk-camera-change',updateCameraControls,{signal});
  zoomIn.addEventListener('click',()=>scene?.zoomBy(1),{signal});
  zoomOut.addEventListener('click',()=>scene?.zoomBy(-1),{signal});
  cameraCenter.addEventListener('click',async()=>{
    const restore=document.activeElement===cameraCenter;
    await scene?.resetCamera();
    if(restore&&!selected&&!computerActive&&document.activeElement===document.body)cameraCenter.focus({preventScroll:true});
  },{signal});
  document.querySelectorAll<HTMLButtonElement>('[data-room-view]').forEach(button=>{
    button.addEventListener('click',()=>void showRoomView(button.dataset.roomView as GuidedViewId),{signal});
  });
  skip.addEventListener('click',()=>{scene?.skipTransition();skip.hidden=true;},{signal});
  el('desk-retry').addEventListener('click',()=>void loadScene(),{signal});
  el('desk-day').addEventListener('click',()=>setDay(!day),{signal});
  el('desk-sound').addEventListener('click',async()=>{try{await audio.enable(!audio.enabled);updateAudio();if(audio.enabled)audio.tap('switch');}catch{notify('Audio is unavailable in this browser.');}},{signal});
  guideButton.addEventListener('click',()=>{guide.hidden=!guide.hidden;guideButton.setAttribute('aria-expanded',String(!guide.hidden));if(!guide.hidden)el('desk-guide-close').focus();},{signal});
  el('desk-guide-close').addEventListener('click',()=>{closeGuide();guideButton.focus();},{signal});
  document.addEventListener('keydown',event=>{scene?.activity();if(event.key==='Escape'&&!dialog.open&&!computer.open){if(computerActive)void exitComputer();else if(!guide.hidden){closeGuide();guideButton.focus();}else if(selected)void returnToDesk();else void showRoomView('overview');}},{signal});
  async function syncRoute() {
    if(routedHash===location.hash)return;routedHash=location.hash;
    const desktopRoute=computerRoute(),section=currentHash();
    if(desktopRoute){
      if(!computerActive)await enterComputer(undefined,false,false);
      if(desktopRoute.section&&selected!==desktopRoute.section)await openSection(desktopRoute.section,undefined,false);
      else if(!desktopRoute.section&&selected)await returnToDesktop(false);
    }else{
      if(computerActive)await exitComputer(false,false);
      if(section)await openSection(section,undefined,false,currentAchievement());
      else if(selected)await returnToDesk(false);
    }
  }
  window.addEventListener('popstate',()=>void syncRoute(),{signal});
  window.addEventListener('hashchange',()=>void syncRoute(),{signal});
  media.addEventListener('change',()=>{scene?.setReducedMotion(media.matches);if(media.matches){skip.hidden=true;if(computerActive)finishBoot();}},{signal});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)audio.suspend();else audio.resume();},{signal});
  document.querySelectorAll<HTMLButtonElement>('[data-copy-email]').forEach(button=>button.addEventListener('click',async()=>{
    const email=button.dataset.copyEmail||'aadithva@outlook.com',status=document.querySelector<HTMLElement>('[data-copy-status]');
    try{await navigator.clipboard.writeText(email);if(status)status.textContent='Email copied.';button.textContent='Copied';setTimeout(()=>button.textContent='Copy email',2000);}catch{if(status)status.textContent=`Copy this address: ${email}`;}
  },{signal}));
  document.querySelector('[data-sticker-reset]')?.addEventListener('click',()=>{found.clear();updateStickerCount();notify('A fresh hunt. Look for two small stickers near the laptop.');},{signal});
  document.querySelector('[data-sticker-start]')?.addEventListener('click',async()=>{
    await returnToDesk();
    scene?.setHunt(true);
    await scene?.toView('experiments');
    notify('Look for two stickers on the laptop. Reset view returns to the room.');
  },{signal});
  window.addEventListener('pagehide',event=>{if(event.persisted){audio.suspend();return;}disposed=true;++loadAttempt;abort.abort();scene?.dispose();audio.dispose();disposePaper();clearTimeout(toastTimer);clearTimeout(arrivalTimer);clearTimeout(bootTimer);},{signal});
  window.addEventListener('pageshow',event=>{if(event.persisted)audio.resume();},{signal});
  const initial=currentHash(),initialComputer=computerRoute();
  if(initialComputer)void enterComputer(undefined,false,false).then(()=>{if(initialComputer.section)void openSection(initialComputer.section,undefined,false);});
  else if(initial)void openSection(initial,undefined,false,currentAchievement());
  void loadScene();
}
