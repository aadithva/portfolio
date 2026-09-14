# ThreeUI interaction audit

Checked 13 September 2026 against the public Community repository at commit `68802d5428071ada5c20db8094b1649e6bb770ed` and npm metadata for `@designcodeio/threeui@1.2.0`. No package was installed. The dock controller was subsequently adapted into an isolated frontend module; no scene or page layout was changed in this task.

## Recommendation

Use three related patterns throughout the portfolio: a restrained proximity dock, tactile action buttons, and one consistent physical switch. Carry the desk's warm white paper, charcoal hardware, and red lamp accent into the surrounding pages. Use the same typography, focus outline, selected state, and motion timing in the desk overlay, work index, case studies, writing, and contact.

The strongest direct reuse is ThreeUI's dependency-free TypeScript dock controller, copied under its MIT license and adapted to the portfolio's real links. Reuse selected button/switch source or translate their interaction into Astro HTML and CSS, documenting that adaptation. The packaged demos are not uniformly application-ready. Do not claim the site uses the ThreeUI npm package if it only adapts these sources or concepts.

## Package, license, and existing stack

The [official repository](https://github.com/MengTo/threeui) documents the real package as **`@designcodeio/threeui`**, not `threeui`. Its npm metadata reports version `1.2.0`, MIT licensing, and peers `react >=18 <20`, `react-dom >=18 <20`, and `three >=0.149 <1`. It additionally depends on `three128` and `three165`, aliases for legacy Three.js versions. The [repository package manifest](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/package.json) is the corresponding primary source.

Supported imports include the library root, shared `style.css`, and component subpaths such as `@designcodeio/threeui/components/CircleButtons`. Individual imports reduce the import graph; they do not make installing the whole package necessary for these three patterns. Package unpacked size was not obtained from the configured npm proxy, and a direct registry size lookup failed; no size estimate is asserted.

This repository already has React 19.2.7, React DOM, Motion, and Three 0.185.1. `astro.config.mjs` has no React integration; the existing hero mounts an isolated React effect through `createRoot`. Direct React reuse is possible through that same explicit mount strategy, with `root.unmount()` on cleanup. Essential navigation should remain server-rendered Astro HTML. No `@astrojs/react` installation is needed for the recommended DOM controller approach.

The [MIT license](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/LICENSE) requires preserving the copyright and license notice with copied substantial code. The [asset license document](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/ASSET-LICENSES.md) distinguishes included Community assets from remote catalog preview media. This plan uses code and our own design assets; it does not copy the Kage Japanese imagery, wording, or entire landing-page composition.

## 1. Proximity dock for persistent navigation

Primary references: [Animated Top Dock](https://threeui.com/css/animated-top-dock), [React API](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/src/shaders/animated-top-dock/AnimatedTopDock.tsx), [DOM controller](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/src/shaders/animated-top-dock/topDockController.ts).

The React component accepts `variant`, `proximity`, `spring`, `damping`, `widthGrowth`, `heightGrowth`, `drop`, and `className`, plus shader controls. Its variants are `sable`, `modern`, `retro`, and `glass`. It has **fixed demo labels and internal active state**, with no item/link/selection callback API. Mounting it unchanged would produce a visual demo rather than working portfolio navigation.

The useful reusable API is:

```ts
createTopDockController(root: HTMLElement, getOptions: () => TopDockOptions)
// Returns a cleanup function; items are [data-dock-item] descendants.
```

Render ordinary links for Work, About, Writing, Achievements, and Contact. Attach the controller to those links, with a white paper or charcoal bar and a small red selected mark. Suggested starting values are `proximity: 104`, `spring: 0.16`, `damping: 0.76`, `widthGrowth: 8`, `heightGrowth: 3`, and `drop: 2`. Keep the bar compact and stable; reserve space for the small expansion.

The source includes focus response, cleanup, resize/font remeasurement, and static behavior for reduced motion, coarse pointers, and viewports at or below 600px. It nevertheless schedules RAF continuously when idle or static, and animates width/height while reading item rectangles during pointer movement. Before reuse, make RAF event-driven and stop after settling, use frame-rate-independent spring timing, and preferably animate an inner face with transforms while the outer link target stays fixed. Remove the custom Enter/Space handler when using native links/buttons so normal browser semantics remain intact. Mobile gets fixed 44px-or-larger targets and no magnification. Avoid `retro` and `glass`, which introduce another WebGL effect and a conflicting visual treatment.

## 2. Tactile buttons for primary and utility actions

Primary references: [Circle Buttons source/API](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/src/shaders/circle-buttons/CircleButtons.tsx), [Circle Buttons CSS](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/src/shaders/circle-buttons/circle-buttons.css), [Rectangle Buttons source](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/src/shaders/rectangle-buttons/RectangleButtons.tsx).

`CircleButtons` is the most practical packaged action: `variant: 'play' | 'plus' | 'mail'`, `mode: 'light' | 'dark'`, `ariaLabel`, `disabled`, native `type`, `onClick`, and styling props. It renders a real button and includes visible focus/reduced-motion CSS. It has no built-in pressed-state prop or pause icon, so its play variant needs an adaptation for a stateful sound control.

For this site, use a warm white rectangular face for “Explore work” and a charcoal circular face for compact reset/contact actions, with the same shallow edge and 1–2px press movement. Red belongs to an active indicator or small face detail. The Rectangle collection's `meridian-keycap-primary` and `meridian-keycap-secondary` supply a useful mechanical shape, but those branches hardcode labels and have no useful click/href API. Copy the relevant MIT CSS/markup into a real Astro button/link with our labels instead of mounting the demo wrapper.

Strip the full-stage background, container sizing, blurred atmosphere, and decorative layers. The Circle play aura has a perpetual 3.6-second CSS rotation; disable it. Keep only transform/color changes on hover and press, typically 140–200ms. Mirror hover emphasis on keyboard focus, preserve the focus outline, and remove motion under reduced motion. There is no reason for these controls to allocate a WebGL context.

## 3. Physical switch for sound and room light

Primary references: [Skeuomorphic Toggle collection/API](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/src/shaders/skeuomorphic-toggle/SkeuomorphicToggleCollection.tsx), [ModernToggle implementation](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/src/shaders/skeuomorphic-toggle/ModernToggle.tsx), [ModernToggle CSS](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/src/shaders/skeuomorphic-toggle/modern-toggle.css).

Use the collection's **`modern`** variant as the source reference. Its API offers `mode`, `defaultOn`, `label`, `size`, visual tuning, and `onChange(on)`. It renders `role="switch"` and `aria-checked`, and its short spring runs only until the thumb settles. The reduced-motion path applies the final state immediately.

Important integration limits: state is uncontrolled (`defaultOn` only), so clicking the 3D lamp or speaker cannot update an already-mounted switch. Add a controlled `checked` value sourced from the central workspace state. Move the callback outside the React state-updater function if retaining React, and make reduced-motion changes observable during an animation. The default `skeuomorphic-toggle` branch does not forward `defaultOn`, `label`, or `onChange` to its packaged effect; do not use it for actual sound or lighting. The `glass` and `shader` variants add rendering work that is unnecessary here.

Rebuild the oversized demo stage as a small warm white thumb in a charcoal recessed track, with a red status detail. Keep a visible text label and “On/Off” state, use a generous hit area, and let touch and keyboard activation perform the same action. Sound starts off and only starts in the user action handler. The switch and the 3D object must dispatch the same central action and observe the same state.

## Scope and verification

These three patterns are enough. A separate 3D Paper canvas would compete with the desk renderer and is not part of this recommendation; existing writing cards can use a small CSS paper lift within the shared button/focus language.

After implementation, check links with JavaScript disabled, keyboard focus and activation, coarse-pointer layout, reduced motion before and after hydration, switch synchronization after clicking 3D objects, and idle CPU/frame activity. Also inspect the built JS/CSS graph to ensure no legacy Three runtime or whole demo catalog was added unintentionally.

## Implemented dock contract

`src/lib/ui/tactile-dock.ts` exports `initTactileDocks(root: ParentNode = document): () => void`. Invoke it in a client-side Astro script after rendering the navigation. The root can be the document, a containing element, or the dock itself. Mark each navigation container with `data-tactile-dock` and each native anchor/button with `data-dock-item`. Call its returned cleanup when disposing the page or replacing that navigation.

The adaptation caps the main item's displayed scale at 1.10; immediate neighbors settle at 1.025 on keyboard focus. The lift is at most 2px. Touch pointer movement is ignored. Reduced motion restores the original transforms immediately. RAF runs only while a spring is moving and is canceled by cleanup. Native link/button keyboard activation is preserved. Keep enough gap/edge padding for the small scale expansion and avoid a separate CSS animation that also owns these items' transforms.

Strict TypeScript compilation passed. A temporary deterministic DOM/RAF harness verified zero idle frames, touch exclusion, focused/neighbor scales, return after pointer leave, live reduced-motion changes, safe reinitialization, and full idempotent cleanup. Browser composition and actual pointer geometry remain part of the root integration check. Source inspection files are temporary under `/tmp/threeui-audit/`; the retained upstream license is in `docs/threeui-attribution.md`.
