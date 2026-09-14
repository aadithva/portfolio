import {chromium} from '@playwright/test';
const b=await chromium.launch({channel:'chrome',headless:true});const p=await b.newPage();p.on('console',m=>console.log(m.type(),m.text()));p.on('pageerror',console.log);
await p.goto('http://localhost:4322/#desk-design');
const result=await p.evaluate(async()=>{try{const m=await import('/src/lib/ui/paper-surface.ts');const c=document.createElement('canvas');const r=m.createPaperSurface(c);r.resize(900,800);r.render({bend:.12,pointerX:0,pointerY:0,light:0});r.dispose();return 'ok';}catch(e){return {message:e.message,stack:e.stack};}});console.log(result);await b.close();
