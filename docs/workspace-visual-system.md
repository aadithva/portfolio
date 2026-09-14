# Unified desk portfolio

The room, monitor desktop, content windows, and standalone pages share a warm charcoal, ivory, and red visual system. The reference is [ThreeUI Kage](https://threeui.com/landing-pages/kage-landing-page): its continuous 3D world, quiet navigation, guided chapters, and restrained typography informed the composition. No temple imagery or page renderer was copied.

## Shared decisions

- src/styles/tokens.css owns UI colors, font families, spacing, and motion curves. The matching design-system CSS/JSON files document those values.
- Headings and body text use self-hosted IBM Plex Sans. IBM Plex Mono is reserved for small labels and metadata. The existing Aadith wordmark remains.
- Charcoal #191918, panels #222220, raised controls #2b2b28, ivory #eeeae2, muted #aaa69e, red #e05243, and brighter red #f47867 run through every context.
- scenePalette in src/lib/workspace/config.ts mirrors these colors for the canvas monitor. Keep it aligned when changing the shared tokens.
- Physical desk objects and real project imagery retain their own colors.
- workspace.css and computer-desktop.css map their variables to shared tokens; the computer does not define a separate terminal palette.
- editorial-mono.css is the existing import path for the new standalone presentation. Its filename is retained for compatibility; page headings now use Sans.

## Interactions

Ordinary portfolio sections open readable HTML panels, including folders inside
the monitor desktop. The animated ThreeUI sheet is reserved for achievements.
It opens with the original IIT Guwahati Bachelor of Design certificate, followed
by documented milestones. The certificate uses its original scanned artwork and
a matte paper material with the source's bending motion. The sheet floats over
the live desk without the demo's black background or giant wordmark. A framed
copy on the wall opens the same achievement view. Read text offers native HTML
and a full-size certificate link.
[Source, interactions and fallbacks](./workspace-paper.md) are documented separately.

Visitors can drag the room or an object to rotate the camera within 22 degrees
horizontally and 10 degrees vertically. Wheel, pinch, and the accessible zoom
buttons change distance from 0.76 to 1.08 of the selected viewpoint. Dragging
never activates the object on release. Recenter restores the current viewpoint;
Reset view and Escape restore the overview. These offsets are centrally bounded
in `src/lib/workspace/camera-orbit.ts` and clear on guided or content transitions.

src/lib/ui/tactile-dock.ts adapts ThreeUI's MIT-licensed dock controller. It applies bounded pointer-proximity and keyboard-focus motion to real links, skips touch hover, honors reduced motion, and schedules no frames while idle. [Source and license](./threeui-attribution.md) are documented, and the license ships at /licenses/threeui.txt.

The overview, desk detail, and shelf detail buttons call centrally defined camera views. Repeated view changes cancel the preceding transition. Clicking objects still opens their existing content, and the monitor enters the responsive HTML desktop. Escape and Reset view restore the overview. The desktop folders have a short cover movement and content windows share the room's window design.

The screen texture is a subtle, stationary scanline treatment that can be disabled. It does not change the palette or add an animation loop. Project preview images start loading during the user-triggered camera approach.

## Scene and assets

This pass changes runtime composition, lighting, the monitor canvas, and UI. It preserves the editable Blender source and exported geometry. Broad nighttime fill is reduced; the red lamp produces the main pools of light. Canvas edges blend into the page. Mobile uses a closer composition, separate guided viewpoints, and baked contacts instead of real-time shadow passes.

The requested third-party bicycle and CRT mesh imports are still tracked in workspace-bicycle-source.md and workspace-monitor-source.md. This visual pass does not claim to have imported those models.

## Verification

Run npm run check:workspace, npm run test:workspace, and npm run build. Interaction tests include keyboard, touch, history, rapid camera changes, reduced motion, loading failures, direct navigation, and shared palette checks. Screenshots for this pass live in artifacts/workspace/unified/ and artifacts/portfolio-redesign/.

The Owly preview is an optimized encoding of the existing public marketing-page screenshot, reduced from 4.1 MB PNG to a 133 KB WebP at 1200×750. The shared projectPreviews helper selects it in both the desktop and standalone work list; case studies retain their original image. No pixels were redrawn or replaced.

Final validation: 22 interaction tests passed, 33 static pages built, and standalone QA covered 26 route/viewport cases. Production captures cover 1440, 1280, 390, and 320 pixel widths without horizontal overflow or browser errors. Mobile's first loaded frame at DPR 2 uses 172 draw calls with renderer density capped at 1.35. Desktop retains real-time shadows and can exceed 200 draw calls while refreshing the shadow maps.
