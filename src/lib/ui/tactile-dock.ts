/*!
 * ThreeUI dock adaptation. MIT license.
 * Copyright (c) 2026 Meng To
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

type DockItem = {
  element: HTMLElement;
  transform: string;
  willChange: string;
  centerX: number;
  centerY: number;
  value: number;
  velocity: number;
  target: number;
};

const controllers = new WeakMap<HTMLElement, () => void>();
const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

function createTactileDock(nav: HTMLElement): () => void {
  const items: DockItem[] = Array.from(nav.querySelectorAll<HTMLElement>('[data-dock-item]'))
    .filter((element) => element.closest('[data-tactile-dock]') === nav)
    .map((element) => ({
      element,
      transform: element.style.transform,
      willChange: element.style.willChange,
      centerX: 0,
      centerY: 0,
      value: 0,
      velocity: 0,
      target: 0,
    }));
  if (!items.length) return () => {};

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const precise = window.matchMedia('(hover: hover) and (pointer: fine)');
  let frame = 0;
  let lastTime = 0;
  let disposed = false;

  const restore = (item: DockItem) => {
    item.element.style.transform = item.transform;
    item.element.style.willChange = item.willChange;
  };

  const apply = (item: DockItem) => {
    const value = clamp(item.value, 0, 1);
    if (value < 0.0001) {
      restore(item);
      return;
    }
    const base = item.transform ? `${item.transform} ` : '';
    item.element.style.transform = `${base}translate3d(0, ${(-2 * value).toFixed(3)}px, 0) scale(${(1 + 0.1 * value).toFixed(4)})`;
  };

  const reset = (immediate = false) => {
    items.forEach((item) => { item.target = 0; });
    if (immediate || reduced.matches || document.hidden) {
      cancelAnimationFrame(frame);
      frame = 0;
      lastTime = 0;
      items.forEach((item) => {
        item.value = 0;
        item.velocity = 0;
        restore(item);
      });
      return;
    }
    wake();
  };

  const draw = (now: number) => {
    frame = 0;
    if (disposed) return;
    if (reduced.matches || document.hidden) {
      reset(true);
      return;
    }
    const delta = lastTime ? clamp((now - lastTime) / (1000 / 60), 0.25, 2) : 1;
    lastTime = now;
    let moving = false;
    for (const item of items) {
      item.velocity += (item.target - item.value) * 0.16 * delta;
      item.velocity *= Math.pow(0.76, delta);
      item.value += item.velocity * delta;
      if (Math.abs(item.target - item.value) < 0.001 && Math.abs(item.velocity) < 0.001) {
        item.value = item.target;
        item.velocity = 0;
      } else {
        moving = true;
      }
      apply(item);
    }
    if (moving) {
      frame = requestAnimationFrame(draw);
    } else {
      lastTime = 0;
      items.forEach((item) => { item.element.style.willChange = item.willChange; });
    }
  };

  function wake() {
    if (disposed || frame || reduced.matches || document.hidden) return;
    if (!items.some((item) => Math.abs(item.target - item.value) > 0.001 || Math.abs(item.velocity) > 0.001)) return;
    items.forEach((item) => { item.element.style.willChange = 'transform'; });
    frame = requestAnimationFrame(draw);
  }

  const measure = () => {
    if (disposed) return;
    reset(true);
    // Measure the neutral targets once; pointer movement never forces layout.
    items.forEach((item) => {
      const rect = item.element.getBoundingClientRect();
      item.centerX = rect.left + rect.width * 0.5;
      item.centerY = rect.top + rect.height * 0.5;
    });
  };

  const onPointerMove = (event: PointerEvent) => {
    if (!precise.matches || reduced.matches || event.pointerType === 'touch') return;
    const distances = items.map((item) => Math.hypot(event.clientX - item.centerX, event.clientY - item.centerY));
    const nearest = distances.indexOf(Math.min(...distances));
    items.forEach((item, index) => {
      const proximity = clamp(1 - distances[index] / 104, 0, 1);
      const influence = proximity * proximity * (3 - 2 * proximity);
      item.target = Math.abs(index - nearest) > 1 ? 0 : influence * (index === nearest ? 1 : 0.25);
    });
    wake();
  };

  const onFocusIn = (event: FocusEvent) => {
    if (reduced.matches) return;
    const target = event.target instanceof Element ? event.target.closest('[data-dock-item]') : null;
    const focused = items.findIndex((item) => item.element === target);
    if (focused < 0) return;
    items.forEach((item, index) => {
      item.target = index === focused ? 1 : Math.abs(index - focused) === 1 ? 0.25 : 0;
    });
    wake();
  };
  const onFocusOut = (event: FocusEvent) => {
    if (!(event.relatedTarget instanceof Node) || !nav.contains(event.relatedTarget)) reset();
  };
  const onPointerLeave = () => reset();
  const onClick = () => reset();
  const onVisibilityChange = () => measure();
  const resizeObserver = new ResizeObserver(measure);
  resizeObserver.observe(nav);
  items.forEach((item) => resizeObserver.observe(item.element));
  nav.addEventListener('pointermove', onPointerMove, { passive: true });
  nav.addEventListener('pointerleave', onPointerLeave);
  nav.addEventListener('focusin', onFocusIn);
  nav.addEventListener('focusout', onFocusOut);
  nav.addEventListener('click', onClick);
  reduced.addEventListener('change', measure);
  precise.addEventListener('change', measure);
  window.addEventListener('resize', measure, { passive: true });
  window.addEventListener('scroll', measure, { passive: true, capture: true });
  document.addEventListener('visibilitychange', onVisibilityChange);
  measure();
  void document.fonts?.ready.then(measure);

  return () => {
    if (disposed) return;
    disposed = true;
    reset(true);
    resizeObserver.disconnect();
    nav.removeEventListener('pointermove', onPointerMove);
    nav.removeEventListener('pointerleave', onPointerLeave);
    nav.removeEventListener('focusin', onFocusIn);
    nav.removeEventListener('focusout', onFocusOut);
    nav.removeEventListener('click', onClick);
    reduced.removeEventListener('change', measure);
    precise.removeEventListener('change', measure);
    window.removeEventListener('resize', measure);
    window.removeEventListener('scroll', measure, true);
    document.removeEventListener('visibilitychange', onVisibilityChange);
  };
}

/** Enhance Astro-rendered links/buttons; the returned cleanup is idempotent. */
export function initTactileDocks(root: ParentNode = document): () => void {
  const docks = Array.from(root.querySelectorAll<HTMLElement>('[data-tactile-dock]'));
  if (root instanceof HTMLElement && root.matches('[data-tactile-dock]')) docks.unshift(root);
  const releases = docks.map((dock) => {
    controllers.get(dock)?.();
    const dispose = createTactileDock(dock);
    const release = () => {
      if (controllers.get(dock) !== release) return;
      dispose();
      controllers.delete(dock);
    };
    controllers.set(dock, release);
    return release;
  });
  return () => releases.forEach((release) => release());
}
