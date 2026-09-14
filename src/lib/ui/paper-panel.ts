import { extractPaperContent, activatePaperAction, type PaperContentDocument } from './paper-content';

/** Achievements use a sheet; every other section opens directly as readable HTML. */
export function initPaperPanel(dialog: HTMLDialogElement) {
  const host = dialog.querySelector<HTMLElement>('#desk-paper-preview')!;
  const scroll = dialog.querySelector<HTMLElement>('#desk-content-scroll')!;
  const reader = dialog.querySelector<HTMLButtonElement>('#desk-paper-reader')!;
  const previous = dialog.querySelector<HTMLButtonElement>('#desk-paper-prev')!;
  const next = dialog.querySelector<HTMLButtonElement>('#desk-paper-next')!;
  const pageLabel = dialog.querySelector<HTMLElement>('#desk-paper-page')!;
  const status = dialog.querySelector<HTMLElement>('#desk-paper-status')!;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const contrast = matchMedia('(forced-colors: active)');
  const abort = new AbortController();
  const channel = `aadith-paper-${crypto.randomUUID()}`;
  const imageCache = new Map<string, Promise<string>>();
  let iframe: HTMLIFrameElement | undefined, content: PaperContentDocument | undefined;
  let disposed = false, paperActive = false, generation = 0, frameReady = false;
  let available: boolean | undefined, page = 0, pageCount = 1, contentRevision = 0;
  let timeout: ReturnType<typeof setTimeout> | undefined;
  let scopedEntry: HTMLElement | undefined;
  let scopedTitleId: string | undefined;
  const scopedHidden = new Map<HTMLElement, boolean>();

  function selectedSection() {
    return scroll.querySelector<HTMLElement>('[data-content-section]:not([hidden])');
  }
  function usesPaper() {
    return dialog.open && selectedSection()?.dataset.contentSection === 'achievements';
  }
  function clearAchievementScope() {
    for (const [element, wasHidden] of scopedHidden) {
      if (element.hidden !== wasHidden) element.hidden = wasHidden;
    }
    scopedHidden.clear(); scopedEntry = undefined;
    if (scopedTitleId && dialog.getAttribute('aria-labelledby') === scopedTitleId) {
      const title = selectedSection()?.querySelector<HTMLElement>(':scope > .wc-title');
      dialog.setAttribute('aria-labelledby', title?.id || 'desk-dialog-title');
    }
    scopedTitleId = undefined;
  }
  function achievementScope(section: HTMLElement) {
    const target = dialog.dataset.achievement;
    const entry = target ? [...section.querySelectorAll<HTMLElement>('[data-achievement-id]')]
      .find(element => element.dataset.achievementId === target) : undefined;
    if (entry === scopedEntry) {
      if (entry && scopedTitleId) dialog.setAttribute('aria-labelledby', scopedTitleId);
      return entry;
    }
    clearAchievementScope();
    if (!entry) return;
    scopedEntry = entry;
    // Keep the original entry and its ancestors. Hidden sibling branches remain
    // in the DOM, so returning to the collection retains every native action.
    const hideOthers = (parent: HTMLElement) => {
      for (const child of parent.children) {
        if (!(child instanceof HTMLElement) || child === entry) continue;
        if (child.contains(entry)) hideOthers(child);
        else if (!child.hidden) { scopedHidden.set(child, false); child.hidden = true; }
      }
    };
    hideOthers(section);
    const title = entry.querySelector<HTMLElement>('h3');
    if (title) {
      title.id ||= `wc-achievement-${entry.dataset.achievementId}-title`;
      scopedTitleId = title.id;
      dialog.setAttribute('aria-labelledby', title.id);
    }
    scroll.scrollTop = 0;
    return entry;
  }
  function showStandard() {
    paperActive = false;
    unmount(); content = undefined;
    clearAchievementScope();
    dialog.dataset.contentView = 'standard';
    delete dialog.dataset.paper;
    delete dialog.dataset.paperView;
    delete dialog.dataset.paperMotion;
    reader.hidden = true;
    reader.setAttribute('aria-pressed', 'false');
    status.textContent = '';
  }

  function supportsWebGL() {
    if (available !== undefined) return available;
    const probe = document.createElement('canvas');
    try {
      const context = probe.getContext('webgl2') || probe.getContext('webgl');
      available = !!context; context?.getExtension('WEBGL_lose_context')?.loseContext();
    } catch { available = false; }
    return available;
  }
  function send(type: string, data: Record<string, unknown> = {}) {
    iframe?.contentWindow?.postMessage({ channel, type, section: content?.id, revision: contentRevision, ...data }, '*');
  }
  function showReader(value: boolean, focus = false) {
    if (!paperActive) return;
    dialog.dataset.paperView = value ? 'reader' : 'sheet';
    reader.textContent = value ? 'Back to paper' : 'Read text';
    reader.setAttribute('aria-pressed', String(value));
    if (value && iframe) unmount();
    if (value && focus) [...scroll.querySelectorAll<HTMLElement>('a, button')]
      .find(element => !element.closest('[hidden]'))?.focus({ preventScroll: true });
  }
  function updateControls() {
    previous.disabled = !frameReady || page === 0;
    next.disabled = !frameReady || page >= pageCount - 1;
    pageLabel.textContent = `${String(page + 1).padStart(2, '0')} / ${String(pageCount).padStart(2, '0')}`;
  }
  function syncContent() {
    const section = selectedSection();
    if (!section || !dialog.open) return;
    if (!usesPaper()) {
      if (paperActive || dialog.dataset.contentView !== 'standard') showStandard();
      return;
    }
    if (!paperActive) {
      paperActive = true;
      dialog.dataset.contentView = 'paper';
      page = 0; pageCount = 1; content = undefined;
      showReader(false);
      void mount();
    }
    const entry = achievementScope(section);
    const updated = extractPaperContent(section, entry);
    const changed = content?.id !== updated.id;
    content = updated;
    if (changed) { ++contentRevision; page = 0; pageCount = 1; if (frameReady && !contrast.matches) showReader(false); }
    if (!frameReady) return;
    send('paper-content', { content: {
      id: content.id, label: entry ? content.title : dialog.querySelector('#desk-dialog-title')?.textContent || content.id,
      title: content.title, kicker: content.kicker, description: content.description, blocks: content.blocks,
      actions: [...content.actions.values()].map(({ id, label, href, kind, disabled }) => ({ id, label, href, kind, disabled })),
    }, page });
  }
  function unmount() {
    ++generation; clearTimeout(timeout); frameReady = false;
    iframe?.remove(); iframe = undefined; host.replaceChildren(); updateControls();
  }
  function fail() {
    if (!paperActive || !usesPaper()) return;
    unmount(); dialog.dataset.paper = 'fallback'; showReader(true);
    reader.hidden = true;
    status.textContent = 'Paper animation is unavailable. You can read everything here.';
  }
  async function mount() {
    unmount(); const token = generation;
    if (disposed || !paperActive || !usesPaper() || document.hidden) return;
    dialog.dataset.paperMotion = reduced.matches ? 'reduced' : 'original';
    if (!supportsWebGL() || contrast.matches) { fail(); return; }
    status.textContent = 'Opening the page…'; dialog.dataset.paper = 'loading'; reader.hidden = false;
    try {
      const { portfolioPaperSource } = await import('./portfolio-paper-source');
      if (disposed || !paperActive || !usesPaper() || token !== generation) return;
      iframe = document.createElement('iframe');
      iframe.title = 'Interactive portfolio paper'; iframe.setAttribute('sandbox', 'allow-scripts');
      iframe.srcdoc = portfolioPaperSource(channel);
      host.append(iframe);
      timeout = setTimeout(() => { if (generation === token && !frameReady) fail(); }, 15000);
    } catch { if (generation === token) fail(); }
  }
  function syncOpen() {
    if (!dialog.open) { showStandard(); return; }
    syncContent();
  }
  function imageData(src: string): Promise<string> {
    if (src.startsWith('data:image/')) return Promise.resolve(src);
    let result = imageCache.get(src);
    if (!result) {
      result = fetch(src, { signal: abort.signal }).then(response => {
        if (!response.ok) throw new Error('Preview image unavailable'); return response.blob();
      }).then(blob => new Promise<string>((resolve, reject) => {
        const file = new FileReader(); file.onload = () => resolve(String(file.result)); file.onerror = reject; file.readAsDataURL(blob);
      })); imageCache.set(src, result);
    }
    return result;
  }
  window.addEventListener('message', event => {
    if (event.source !== iframe?.contentWindow || event.data?.channel !== channel || !paperActive || !usesPaper()) return;
    const data = event.data;
    // Item IDs distinguish a medal from a certificate even inside the same
    // section. Ignore events already queued by the previous displayed item.
    if (data.type !== 'paper-ready' && (data.section !== content?.id || data.revision !== contentRevision)) return;
    if (data.type === 'paper-ready') {
      frameReady = true; clearTimeout(timeout); dialog.dataset.paper = 'source'; status.textContent = '';
      syncContent(); updateControls();
    } else if (data.type === 'paper-state') {
      if (data.section !== content?.id) return;
      page = data.page; pageCount = data.pageCount; updateControls();
    } else if (data.type === 'paper-action' && content) activatePaperAction(content, data.actionId);
    else if (data.type === 'paper-close') dialog.querySelector<HTMLButtonElement>('#desk-back')?.click();
    else if (data.type === 'paper-reader') showReader(true, true);
    else if (data.type === 'paper-assets' && content) {
      const allowed = new Set(content.blocks.flatMap(block => block.kind === 'image' ? [block.src] : []));
      const target = iframe;
      for (const src of data.sources as string[]) if (allowed.has(src)) {
        void imageData(src).then(image => {
          if (iframe === target) send('paper-image', { src, data: image });
        }).catch(() => { /* Text and destination remain available if imagery fails. */ });
      }
    }
  }, { signal: abort.signal });
  previous.addEventListener('click', () => send('paper-page', { page: page - 1 }), { signal: abort.signal });
  next.addEventListener('click', () => send('paper-page', { page: page + 1 }), { signal: abort.signal });
  reader.addEventListener('click', () => {
    if (!paperActive) return;
    const reading = dialog.dataset.paperView !== 'reader';
    showReader(reading);
    if (!reading && !iframe) void mount();
  }, { signal: abort.signal });
  // Keyboard users never land on an invisible link: focus exposes native reading mode.
  scroll.addEventListener('focusin', event => {
    if (!dialog.open || !paperActive) return;
    showReader(true);
    const target = event.target as HTMLElement;
    requestAnimationFrame(() => {
      if (dialog.open && dialog.dataset.paperView === 'reader') target.scrollIntoView({ block: 'nearest' });
    });
  }, { signal: abort.signal });
  dialog.addEventListener('keydown', event => {
    if (!paperActive || dialog.dataset.paperView === 'reader') return;
    if (event.key === 'ArrowRight' || event.key === 'PageDown') { event.preventDefault(); send('paper-page', { page: page + 1 }); }
    if (event.key === 'ArrowLeft' || event.key === 'PageUp') { event.preventDefault(); send('paper-page', { page: page - 1 }); }
  }, { signal: abort.signal });
  const remount = () => { if (paperActive && usesPaper() && dialog.dataset.paperView !== 'reader') void mount(); };
  reduced.addEventListener('change', remount, { signal: abort.signal });
  contrast.addEventListener('change', remount, { signal: abort.signal });
  document.addEventListener('visibilitychange', () => { if (document.hidden) unmount(); else remount(); }, { signal: abort.signal });
  dialog.addEventListener('close', syncOpen, { signal: abort.signal });
  const openObserver = new MutationObserver(syncOpen);
  openObserver.observe(dialog, { attributes: true, attributeFilter: ['open', 'data-achievement'] });
  const contentObserver = new MutationObserver(syncContent);
  contentObserver.observe(scroll, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ['hidden', 'disabled'] });
  showStandard(); syncOpen();
  return () => { disposed = true; unmount(); abort.abort(); openObserver.disconnect(); contentObserver.disconnect(); clearAchievementScope(); };
}
