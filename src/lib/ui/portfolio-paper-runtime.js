/* Portfolio printing and hit testing around ThreeUI's original sheet renderer. */
(() => {
  const channel = __PAPER_CHANNEL__;
  const W = 1400, H = 1932, M = 110, bottom = H - 130;
  const images = new Map(), requested = new Set();
  const measure = document.createElement('canvas').getContext('2d');
  let content = null, page = 0, pages = [], links = [], renderedText = '', lastWheel = 0, revision = 0;
  let pointer = null, activeLink = null, compact = innerWidth < 760;
  const tell = (type, payload = {}) => parent.postMessage({ channel, type, section: content?.id, revision, ...payload }, '*');
  const font = (size, weight = 400) => `${weight} ${size}px Inter, sans-serif`;
  const bodySize = () => compact ? 62 : 46;
  const label = () => content?.label || content?.id || '';
  function wrap(text, size, width = W - M * 2, weight = 400) {
    measure.font = font(size, weight);
    const result = []; let line = '';
    for (const word of text.split(/\s+/)) {
      const next = line ? `${line} ${word}` : word;
      if (line && measure.measureText(next).width > width) { result.push(line); line = word; }
      else line = next;
    }
    if (line) result.push(line);
    return result;
  }
  function header(first) {
    const titleSize = first ? 92 : 72, titleHeight = titleSize * 1.16;
    const titleLines = wrap(content.title, titleSize, W - 2 * M, 500);
    const descriptionLines = first ? wrap(content.description, bodySize()) : [];
    const titleY = 216;
    const descriptionY = titleY + titleHeight * titleLines.length + 25;
    const bodyY = descriptionY + descriptionLines.length * bodySize() * 1.4 + 54;
    return { titleSize, titleHeight, titleLines, titleY, descriptionLines, descriptionY, bodyY, items: [] };
  }
  function layout() {
    if (!content) return;
    const documents = content.blocks.filter(block => block.kind === 'image' && block.document);
    pages = [...documents.map(document => ({ document })), header(true)]; let current = pages[pages.length - 1], y = current.bodyY;
    const next = () => { current = header(false); pages.push(current); y = current.bodyY; };
    for (const [blockIndex, block] of content.blocks.entries()) {
      if (block.document) continue;
      if (block.kind === 'image') {
        const height = compact ? 430 : 440;
        if (y + height > bottom) next();
        current.items.push({ ...block, x: M, y, width: W - M * 2, height });
        y += height + 28; continue;
      }
      const size = block.kind === 'heading' ? compact ? 76 : 65
        : block.kind === 'meta' ? compact ? 43 : 31
        : block.kind === 'action' ? compact ? 60 : 43 : bodySize();
      const weight = block.kind === 'heading' ? 500 : 400;
      const leading = size * 1.36;
      const textLines = wrap(block.text, size, W - M * 2 - (block.kind === 'action' ? 55 : 0), weight);
      // A date stays with its heading and short entry, rather than alone at a page edge.
      if (block.kind === 'meta' && content.blocks[blockIndex - 1]?.kind !== 'image') {
        let entryHeight = textLines.length * leading + 14;
        for (const following of content.blocks.slice(blockIndex + 1, blockIndex + 3)) {
          if (following.kind !== 'heading' && following.kind !== 'paragraph') break;
          const nextSize = following.kind === 'heading' ? compact ? 76 : 65 : bodySize();
          entryHeight += wrap(following.text, nextSize, W - M * 2, following.kind === 'heading' ? 500 : 400).length * nextSize * 1.36 + 32;
        }
        if (entryHeight <= bottom - header(false).bodyY && y + entryHeight > bottom) next();
      }
      // Keep ordinary paragraphs together when they fit on a fresh page.
      if (textLines.length * leading <= bottom - header(false).bodyY && y + textLines.length * leading > bottom) next();
      if ((block.kind === 'heading' || block.kind === 'meta') && y + leading * textLines.length + 120 > bottom) next();
      for (let index = 0; index < textLines.length; index++) {
        if (y + leading > bottom) next();
        current.items.push({ ...block, text: textLines[index], x: M, y, width: W - M * 2, height: leading, size, weight, first: index === 0 });
        y += leading;
      }
      y += block.kind === 'meta' ? 14 : block.kind === 'action' ? 30 : 32;
    }
    page = Math.max(0, Math.min(page, pages.length - 1));
  }
  function draw(ctx) {
    ctx.clearRect(0, 0, W, H);
    links = [];
    const document = pages[page]?.document;
    if (document) {
      // Use the original certificate pixels. Do not retype its border, names or signatures.
      ctx.fillStyle = '#f4f2e9'; ctx.fillRect(0, 0, W, H);
      const image = images.get(document.src);
      if (image) {
        const scale = Math.min(W / image.width, H / image.height);
        ctx.drawImage(image, (W - image.width * scale) / 2, (H - image.height * scale) / 2, image.width * scale, image.height * scale);
      } else {
        ctx.fillStyle = '#373631'; ctx.font = font(40); ctx.textAlign = 'center';
        ctx.fillText('Opening the certificate…', W / 2, H / 2); ctx.textAlign = 'left';
        if (!requested.has(document.src)) { requested.add(document.src); tell('paper-assets', { sources: [document.src] }); }
      }
      renderedText = [label(), document.alt, 'Original certificate'].join('\n');
      return;
    }
    ctx.fillStyle = 'rgba(24,27,30,.78)'; ctx.fillRect(0, 0, W, H);
    const frost = ctx.createLinearGradient(0, 0, 0, H);
    frost.addColorStop(0, 'rgba(255,255,255,.08)'); frost.addColorStop(1, 'rgba(255,255,255,.015)');
    ctx.fillStyle = frost; ctx.fillRect(35, 35, W - 70, H - 70);
    ctx.strokeStyle = 'rgba(255,255,255,.34)'; ctx.lineWidth = 2; ctx.strokeRect(24, 24, W - 48, H - 48);
    ctx.strokeStyle = 'rgba(255,255,255,.12)'; ctx.lineWidth = 1; ctx.strokeRect(40, 40, W - 80, H - 80);
    if (!content || !pages.length) return;
    const p = pages[page]; links = [];
    ctx.fillStyle = 'rgba(255,255,255,.7)'; ctx.font = font(30, 500);
    ctx.fillText(`AADITH  /  ${label().toUpperCase()}`, M, 109);
    ctx.fillStyle = '#ffffff'; ctx.font = font(p.titleSize, 500);
    p.titleLines.forEach((line, i) => ctx.fillText(line, M, p.titleY + i * p.titleHeight));
    ctx.font = font(bodySize()); ctx.fillStyle = 'rgba(255,255,255,.76)';
    p.descriptionLines.forEach((line, i) => ctx.fillText(line, M, p.descriptionY + i * bodySize() * 1.4));
    ctx.strokeStyle = 'rgba(255,255,255,.22)'; ctx.beginPath(); ctx.moveTo(M, p.bodyY - 35); ctx.lineTo(W - M, p.bodyY - 35); ctx.stroke();
    renderedText = [label(), content.title, ...(p.descriptionLines.length ? [content.description] : [])].join('\n');
    for (const item of p.items) {
      if (item.kind === 'image') {
        const image = images.get(item.src);
        ctx.fillStyle = 'rgba(255,255,255,.035)'; ctx.fillRect(item.x, item.y, item.width, item.height);
        if (image) {
          const scale = Math.min(item.width / image.width, item.height / image.height);
          ctx.drawImage(image, item.x + (item.width - image.width * scale) / 2, item.y + (item.height - image.height * scale) / 2, image.width * scale, image.height * scale);
        } else if (!requested.has(item.src)) { requested.add(item.src); tell('paper-assets', { sources: [item.src] }); }
      } else {
        ctx.font = font(item.size, item.weight);
        ctx.fillStyle = item.kind === 'meta' ? 'rgba(255,255,255,.58)' : item.kind === 'notice' ? 'rgba(255,255,255,.67)' : 'rgba(255,255,255,.94)';
        ctx.fillText(item.text, item.x, item.y + item.size);
        renderedText += '\n' + item.text;
        if (item.kind === 'action') {
          if (item.first) { ctx.textAlign = 'right'; ctx.fillText('↗', W - M, item.y + item.size); ctx.textAlign = 'left'; }
          ctx.strokeStyle = 'rgba(255,255,255,.25)'; ctx.beginPath(); ctx.moveTo(M, item.y + item.height + 5); ctx.lineTo(W - M, item.y + item.height + 5); ctx.stroke();
        }
      }
      if (item.actionId) {
        const action = content.actions.find(a => a.id === item.actionId);
        links.push({ actionId: item.actionId, label: action?.label || item.text || item.alt || '', href: action?.href,
          x: item.x, y: item.y, width: item.width, height: item.height });
      }
    }
    ctx.font = font(29); ctx.fillStyle = 'rgba(255,255,255,.5)';
    ctx.fillText(content.kicker, M, H - 72); ctx.textAlign = 'right'; ctx.fillText(`${String(page + 1).padStart(2, '0')} / ${String(pages.length).padStart(2, '0')}`, W - M, H - 72); ctx.textAlign = 'left';
  }
  window.__paperDraw = draw;
  function updateTexture() {
    const sheet = window.__sheet;
    if (!sheet?.mat.map?.image) return;
    draw(sheet.mat.map.image.getContext('2d')); sheet.mat.map.needsUpdate = true;
    const document = pages[page]?.document;
    sheet.mat.color.set(document ? 0xffffff : 0xc4d2e8);
    sheet.mat.roughness = document ? .68 : .06;
    sheet.mat.clearcoat = document ? .12 : 1;
    sheet.mat.iridescence = document ? 0 : .10;
    sheet.mat.envMapIntensity = document ? .65 : 1.15;
    sheet.mat.specularIntensity = document ? .2 : 1;
    sheet.uni.uSpecA.value = document ? .025 : .14;
    sheet.uni.uRimA.value = document ? .12 : .88;
    tell('paper-state', { section: content?.id, page, pageCount: pages.length, title: content?.title, renderedText, artwork: artwork() });
  }
  function go(value) {
    const next = Math.max(0, Math.min(value, pages.length - 1));
    if (next === page) return;
    page = next; activeLink = null; updateTexture();
  }
  function artwork() { const document = pages[page]?.document; return document ? { src: document.src, alt: document.alt, loaded: images.has(document.src) } : null; }
  window.__paperPortfolio = { state: () => ({ section: content?.id, page, pageCount: pages.length, title: content?.title, renderedText, artwork: artwork(), links: links.map(l => ({ ...l })) }) };
  window.__paperBoot = () => { tell('paper-ready'); updateTexture(); };
  window.__paperReflow = () => { layout(); updateTexture(); };
  addEventListener('message', e => {
    if (e.source !== parent || e.data?.channel !== channel) return;
    const data = e.data;
    if (data.type === 'paper-content') {
      const changed = content?.id !== data.content.id || revision !== data.revision;
      content = data.content; revision = data.revision; if (changed) page = 0;
      document.getElementById('paper-wordmark').textContent = label().toUpperCase();
      document.title = `${label()} · Aadith`;
      layout(); if (Number.isInteger(data.page)) page = Math.max(0, Math.min(data.page, pages.length - 1));
      updateTexture();
    } else if (data.type === 'paper-page' && data.section === content?.id && data.revision === revision) go(data.page);
    else if (data.type === 'paper-image') {
      const image = new Image(); image.onload = () => { images.set(data.src, image); updateTexture(); }; image.src = data.data;
    }
  });
  // Invert the original shader's CPU mirror, so printed links stay clickable
  // as the sheet bends and rotates. Screen coordinates alone are insufficient.
  function paperUV(x, y) {
    const point = window.__sheet?.point;
    if (!point) return null;
    const px = x / innerWidth * 2 - 1, py = 1 - y / innerHeight * 2;
    let u = .5, v = .5;
    for (let i = 0; i < 12; i++) {
      const p = point(u, v), pu = point(u + .001, v), pv = point(u, v + .001);
      const a = (pu.x - p.x) / .001, b = (pv.x - p.x) / .001, c = (pu.y - p.y) / .001, d = (pv.y - p.y) / .001;
      const det = a * d - b * c; if (Math.abs(det) < 1e-6) return null;
      const ex = px - p.x, ey = py - p.y;
      u += (d * ex - b * ey) / det; v += (a * ey - c * ex) / det;
      if (!Number.isFinite(u + v) || u < -.25 || u > 1.25 || v < -.25 || v > 1.25) return null;
      if (Math.abs(ex) + Math.abs(ey) < .0001) break;
    }
    return u >= 0 && u <= 1 && v >= 0 && v <= 1 ? { x: u * W, y: (1 - v) * H } : null;
  }
  function linkAt(x, y) {
    const uv = paperUV(x, y); if (!uv) return null;
    return links.find(link => uv.x >= link.x && uv.x <= link.x + link.width && uv.y >= link.y && uv.y <= link.y + link.height);
  }
  addEventListener('pointerdown', e => { if (e.button === 0) pointer = { id: e.pointerId, x: e.clientX, y: e.clientY, moved: 0 }; });
  addEventListener('pointermove', e => {
    if (pointer) pointer.moved = Math.max(pointer.moved, Math.hypot(e.clientX - pointer.x, e.clientY - pointer.y));
    activeLink = linkAt(e.clientX, e.clientY);
  }, { passive: true });
  addEventListener('pointerup', e => {
    if (pointer?.id === e.pointerId && pointer.moved < 6) {
      const link = linkAt(e.clientX, e.clientY); if (link) tell('paper-action', { actionId: link.actionId });
    }
    pointer = null;
  });
  addEventListener('pointercancel', () => { pointer = null; });
  addEventListener('keydown', e => {
    if (e.key === 'Escape') { e.preventDefault(); tell('paper-close'); }
    if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); go(page + 1); }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); go(page - 1); }
    if (e.key === 'Tab') { e.preventDefault(); tell('paper-reader'); }
  });
  addEventListener('wheel', e => {
    if (e.ctrlKey || e.metaKey || Math.abs(e.deltaY) < 8) return;
    e.preventDefault(); const now = performance.now();
    if (now - lastWheel > 500) { lastWheel = now; go(page + Math.sign(e.deltaY)); }
  }, { passive: false });
  addEventListener('resize', () => {
    if (compact !== (innerWidth < 760)) { compact = innerWidth < 760; layout(); updateTexture(); }
  });
  window.__paperCursor = () => activeLink && !pointer ? 'pointer' : null;
})();
