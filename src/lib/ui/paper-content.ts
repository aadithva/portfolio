/** Public content comes from the existing HTML, including its original actions.
 * Nothing here imports protected case-study data or copies portfolio prose.
 */
export type PaperTextKind = 'heading' | 'paragraph' | 'meta' | 'notice' | 'action';

export interface PaperTextRun {
  text: string;
  actionId?: string;
}

interface PaperBlockBase {
  id: string;
  /** Entries in an article/card share a group; pagination may keep them together. */
  groupId: string;
  actionId?: string;
}

export interface PaperTextBlock extends PaperBlockBase {
  kind: PaperTextKind;
  text: string;
  runs?: PaperTextRun[];
}

export interface PaperImageBlock extends PaperBlockBase {
  kind: 'image';
  src: string;
  alt: string;
  aspect: number;
  /** Original certificate artwork takes its own full sheet, without re-typesetting. */
  document?: boolean;
}

export type PaperBlock = PaperTextBlock | PaperImageBlock;

export interface PaperAction {
  id: string;
  kind: 'link' | 'button';
  label: string;
  element: HTMLAnchorElement | HTMLButtonElement;
  href?: string;
  target?: string;
  disabled: boolean;
}

export interface PaperContentDocument {
  id: string;
  kicker: string;
  title: string;
  description: string;
  /** Serializable entries to send to the paper renderer. */
  blocks: PaperBlock[];
  /** These stay in the host document and must not be sent through postMessage. */
  actions: Map<string, PaperAction>;
  source: HTMLElement;
}

const normalize = (value: string) => value.replace(/\s+/g, ' ').trim();
const ignored = 'script, style, template, .sr-only, [data-paper-ignore]';

function visibleText(node: Node): string {
  if (node.nodeType === Node.TEXT_NODE) return node.textContent ?? '';
  if (!(node instanceof Element) || node.matches(ignored)) return '';
  if (node.tagName === 'BR') return ' ';
  return Array.from(node.childNodes, visibleText).join('');
}

function textOf(element: Element | null): string {
  return element ? normalize(visibleText(element)) : '';
}

/** Inline SVGs need their resolved paint/font rules when used as Canvas images. */
function svgImage(svg: SVGSVGElement): {src: string; alt: string; aspect: number} {
  const copy = svg.cloneNode(true) as SVGSVGElement;
  const originals = [svg, ...svg.querySelectorAll<SVGElement>('*')];
  const copies = [copy, ...copy.querySelectorAll<SVGElement>('*')];
  const properties = [
    'fill', 'fill-opacity', 'stroke', 'stroke-opacity', 'stroke-width',
    'stroke-linecap', 'stroke-linejoin', 'opacity', 'font-family', 'font-size',
    'font-weight', 'letter-spacing', 'text-anchor',
  ];
  originals.forEach((original, index) => {
    const style = getComputedStyle(original);
    for (const property of properties) {
      let value = style.getPropertyValue(property);
      // A computed SVG paint URL can include the document's absolute URL.
      // Retain only its fragment so the pattern resolves in the image document.
      if (value.startsWith('url(')) value = value.replace(/url\([^#]*#([^)'"\s]+)[^)]*\)/g, 'url(#$1)');
      if (value) copies[index].style.setProperty(property, value);
    }
  });
  const box = svg.viewBox.baseVal;
  const width = box.width || Number(svg.getAttribute('width')) || 1;
  const height = box.height || Number(svg.getAttribute('height')) || 1;
  copy.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  copy.setAttribute('width', String(width));
  copy.setAttribute('height', String(height));
  return {
    src: `data:image/svg+xml;charset=utf-8,${encodeURIComponent(new XMLSerializer().serializeToString(copy))}`,
    alt: svg.getAttribute('aria-label') || textOf(svg.querySelector('title')),
    aspect: width / height,
  };
}

/** Extract again after a section/status change; action IDs remain stable. */
export function extractPaperContent(section: HTMLElement, entry?: HTMLElement): PaperContentDocument {
  const root = entry && section.contains(entry) ? entry : section;
  const sectionId = section.dataset.contentSection || section.id || 'section';
  const id = root === section ? sectionId : `${sectionId}:${root.dataset.achievementId}`;
  const kickerElement = root.querySelector(root === section ? ':scope > .wc-eyebrow' : ':scope > .wc-meta');
  const titleElement = root.querySelector(root === section ? ':scope > .wc-title' : ':scope > h3');
  const descriptionElement = root.querySelector(root === section ? ':scope > .wc-description' : ':scope > p:not(.wc-meta)');
  const intro = new Set([kickerElement, titleElement, descriptionElement]);
  const actions = new Map<string, PaperAction>();
  const actionForElement = new Map<Element, string>();
  const blocks: PaperBlock[] = [];
  let groupIndex = 0;

  root.querySelectorAll<HTMLAnchorElement | HTMLButtonElement>('a[href], button').forEach((element, index) => {
    const actionId = `${id}-action-${index}`;
    const isLink = element instanceof HTMLAnchorElement;
    actionForElement.set(element, actionId);
    actions.set(actionId, {
      id: actionId,
      kind: isLink ? 'link' : 'button',
      label: element.getAttribute('aria-label') || textOf(element.querySelector('h3')) || textOf(element),
      element,
      ...(isLink ? { href: element.getAttribute('href') || '', target: element.target || undefined } : {}),
      disabled: element instanceof HTMLButtonElement && element.disabled,
    });
  });

  function appendText(kind: PaperTextKind, element: Element, groupId: string, actionId?: string) {
    const text = textOf(element);
    if (!text) return;
    const runs: PaperTextRun[] = [];
    const collect = (node: Node, inheritedAction?: string) => {
      if (node.nodeType === Node.TEXT_NODE) {
        if (node.textContent) runs.push({ text: node.textContent, ...(inheritedAction ? { actionId: inheritedAction } : {}) });
      } else if (node instanceof Element && !node.matches(ignored)) {
        const ownAction = actionForElement.get(node) || inheritedAction;
        if (node.tagName === 'BR') runs.push({text: ' '});
        else node.childNodes.forEach(child => collect(child, ownAction));
      }
    };
    collect(element, actionId);
    blocks.push({ id: `${id}-block-${blocks.length}`, groupId, kind, text,
      ...(actionId ? { actionId } : {}),
      ...(runs.some(run => run.actionId) ? { runs } : {}),
    });
  }

  function walk(element: Element, groupId: string, inheritedAction?: string) {
    if (intro.has(element) || element.matches(ignored) || element.hasAttribute('hidden')) return;
    // The Copilot card's decorative fallback repeats its accessible heading.
    if (element.matches('.wc-image--typographic, [aria-hidden="true"]:not(span)')) return;
    if (element.matches('article, a.wc-project')) groupId = `${id}-group-${++groupIndex}`;
    const actionId = actionForElement.get(element) || inheritedAction;
    const common = { id: `${id}-block-${blocks.length}`, groupId, ...(actionId ? { actionId } : {}) };
    if (element instanceof HTMLImageElement) {
      const source = element.currentSrc || element.getAttribute('src');
      if (source) blocks.push({ ...common, kind: 'image', src: new URL(source, section.ownerDocument.baseURI).href,
        alt: element.alt, aspect: (element.naturalWidth || element.width || 800) / (element.naturalHeight || element.height || 500),
        ...(element.hasAttribute('data-paper-document') ? { document: true } : {}) });
      return;
    }
    if (element instanceof SVGSVGElement) {
      if (element.getAttribute('role') === 'img') blocks.push({ ...common, kind: 'image', ...svgImage(element) });
      return;
    }
    if (/^H[1-6]$/.test(element.tagName)) {
      appendText('heading', element, groupId, actionId || actionForElement.get(element.querySelector('a')!));
      return;
    }
    if (element.tagName === 'P' || element.tagName === 'FIGCAPTION') {
      const kind = element.matches('.wc-empty, .wc-expedition-note') ? 'notice'
        : element.matches('.wc-meta, figcaption') ? 'meta' : 'paragraph';
      appendText(kind, element, groupId, actionId);
      // A Canvas paragraph may not expose inline hit regions. Keep each inline
      // destination as a native action as well, without repeating its paragraph.
      if (!actionId) for (const link of element.querySelectorAll('a[href]')) {
        appendText('action', link, groupId, actionForElement.get(link));
      }
      return;
    }
    if (element.tagName === 'DL') {
      for (const term of element.querySelectorAll('dt')) {
        const definition = term.nextElementSibling;
        const text = [textOf(term), definition?.tagName === 'DD' ? textOf(definition) : ''].filter(Boolean).join(': ');
        if (text) blocks.push({ id: `${id}-block-${blocks.length}`, groupId, kind: 'meta', text });
      }
      return;
    }
    if (element instanceof HTMLButtonElement || (element instanceof HTMLAnchorElement && !element.classList.contains('wc-project'))) {
      appendText('action', element, groupId, actionId);
      return;
    }
    for (const child of element.children) walk(child, groupId, actionId);
  }

  for (const child of root.children) walk(child, `${id}-group-${groupIndex}`);
  return { id, kicker: textOf(kickerElement), title: textOf(titleElement),
    description: textOf(descriptionElement), blocks, actions, source: root };
}

/** Use the original event listener/link, including clipboard, hunt and routes. */
export function activatePaperAction(content: PaperContentDocument, actionId: string): boolean {
  const action = content.actions.get(actionId);
  if (!action || !action.element.isConnected || !content.source.contains(action.element)) return false;
  if (action.element instanceof HTMLButtonElement && action.element.disabled) return false;
  action.element.click();
  return true;
}
