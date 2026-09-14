import original from '../../../vendor/threeui/src/shaders/3d-paper/sources/3d-paper.html?raw';
import integration from './portfolio-paper-runtime.js?raw';

/** Derive the achievement sheet from the registered source, retaining its bending shader. */
export function portfolioPaperSource(channel: string) {
  const drawStart = original.indexOf('function drawGlass(ctx){');
  const drawEnd = original.indexOf('function makeCertTexture(){', drawStart);
  if (drawStart < 0 || drawEnd < 0) throw new Error('Registered ThreeUI source structure changed');
  let source = original.slice(0, drawStart)
    + 'function drawGlass(ctx){ window.__paperDraw(ctx); }\n\n'
    + original.slice(drawEnd);
  source = source.replace('<h1>NOCTURNE</h1>', '<h1 id="paper-wordmark"></h1>')
    .replace('const SW = 2.30, SH = 2.72;', 'const SW = 2.72 * 1400 / 1932, SH = 2.72;')
    .replace('</style>', 'html{color-scheme:dark} html,body{background:transparent!important} #bg,#dof,#vig{display:none} #grain{opacity:.025} #grain2{opacity:.008} #hint{bottom:12px}\n</style>')
    .replace('function boot(){', 'function boot(){ window.__paperReflow();')
    .replace('<title>3D Paper</title>', '<title>Aadith · Portfolio</title>')
    .replace('<script>\n(function(){', `<script>${integration.replace('__PAPER_CHANNEL__', JSON.stringify(channel))}</script>\n<script>\n(function(){`)
    .replace("const wantCursor = dragging ? 'grabbing' : (overSheet ? 'grab' : '');", "const wantCursor = dragging ? 'grabbing' : (window.__paperCursor() || (overSheet ? 'grab' : ''));")
    .replace('window.__sheet = {group,', 'window.__sheet = {point:(u,v)=>cornerPoint(u,v).clone().applyMatrix4(group.matrixWorld).project(camera), group,')
    .replace('spin:(y)=>{ dragYaw=y; release=1e9; }};', 'spin:(y)=>{ dragYaw=y; release=1e9; }};\nwindow.__paperBoot();')
    .replace('<b>Drag</b> to turn it', '<b>Drag</b> to turn the paper');
  return source;
}
