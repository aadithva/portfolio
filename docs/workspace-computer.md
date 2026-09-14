# Monitor and desktop experience

The monitor now opens a full-page personal desktop. Its folders use the existing
portfolio data and detailed HTML content. Existing project URLs and access gates
are unchanged.

## Interaction

1. Click or keyboard-activate the monitor. The camera approaches the actual screen
   plane until the glass covers the scene viewport.
2. A short, skippable readiness sequence leads to the desktop. Reduced motion
   skips the camera travel and readiness sequence.
3. A single click opens a folder in a content window. Escape or the window's Back
   button returns to the desktop. Escape again or Back to room restores the desk
   and keyboard focus on the original entry control.

The desktop is a native modal dialog; its content window is a separate native
dialog above it. This lets the browser manage focus containment at each level.
Both dialogs use accessible HTML. Each folder has a real page URL for modified
clicks and navigation without JavaScript.

`#computer` opens the desktop directly. `#computer-work`, `#computer-writing` and
the other existing section IDs open desktop content windows. Browser Back and
Forward preserve these levels. Existing `#desk-*` content links still work.
The desktop and its content work when the 3D asset fails to load.

## Visual direction

The reference is [ThreeUI's CRT Terminal](https://threeui.com/backgrounds/crt/terminal).
This implementation uses original Canvas 2D and CSS, rather than importing the
ThreeUI renderer or copying its fictional terminal log. It uses green phosphor
colors, a stationary scanline/grille, a restrained vignette and a short boot.
CRT on/off removes the desktop and content-window overlays. Text and project
images remain HTML, with no shader distortion on reading content.

Design calibration: variance 6, motion 5, density 5. The folder layout and selected
work panel support portfolio browsing; the camera movement explains entry into
the screen. The original room remains the primary landing view.

## Files and responsibilities

- `src/components/workspace/ComputerDesktop.astro` contains folders and desktop
  chrome; `src/styles/computer-desktop.css` supplies its responsive styling.
- `src/lib/workspace/controller.ts` owns entry, exit, boot, effects, history and
  focus. The same `WorkspaceContent.astro` renders both ordinary content panels
  and desktop windows.
- `src/lib/workspace/scene.ts` derives the computer camera from the screen's true
  transformed vertices and normal. It holds the monitor's preview steady and
  stops idle previews during computer use.
- `getScreenRect()` exposes the projected screen bounds for future transitions;
  the current transition uses the screen-filling camera followed by an HTML fade.

## Requested replacement monitor

The exact [CRT Computer Monitor by fizyman](https://sketchfab.com/3d-models/crt-computer-monitor-f2ff0013f86e4cd0a2aee183a23bdfee)
is CC BY 4.0, but its official download requires a Sketchfab login. The source
file has not yet been supplied. The existing saved Blender monitor remains in
use; this work does not claim to have imported the requested replacement.

Once supplied, import the authorized archive into a backed-up Blender scene,
retain the `monitor` root and a separate `monitor_screen` mesh, fit the housing
and its depth to the corner desk, and replace the screen material at runtime.
Add the required visible credit and modification note before exporting. See
`docs/workspace-monitor-source.md` for attribution and source details.

## Verification

The computer tests cover entry, both Escape levels, original project routes,
browser history, CRT toggling, cancellation during camera entry, skipped boot,
direct links with model failure, mobile taps, content overflow and focus return.
Existing room and Expeditions tests remain in `tests/workspace.spec.ts`.
