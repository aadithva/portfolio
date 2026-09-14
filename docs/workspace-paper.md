# ThreeUI achievement paper

Only Achievements uses the animated sheet. Work, About, Writing, Expeditions,
Experiments, Contact, design tools, and the controller challenge open ordinary
HTML panels. Those sections have selectable text, native links and buttons, and
continuous scrolling. They do not create a paper iframe, show pagination, or
require a Read text toggle.

Achievement content appears directly on the moving sheet above the actual desk.
Its host and iframe backgrounds are transparent, and a light backdrop blur
separates it from the room. Milestone pages use a charcoal glass sheet, while
the graduation artwork uses matte white paper. The iframe and its document use
the same dark color scheme so Chromium preserves transparency. The source's giant wordmark, black background, and decorative
backdrop layers are hidden.

The renderer is adapted directly from the registered
[ThreeUI 3D Paper source bundle](https://threeui.com/source-code/3d-paper.json),
Original variant. The registered files remain unchanged in `vendor/threeui` so
updates and provenance can be checked independently of the portfolio adapter.
The canonical HTML SHA-256 is
`8ec1b71c0dbcafbadf908100ae2a08045d0a1087c00a09d28245ef19366c7353`.
The other five file hashes are recorded in `vendor/threeui/source-manifest.json`.
The rendered achievement document has different content and therefore has a
different hash from the canonical certificate.

## Content and rendering

The IIT Guwahati graduation certificate uses the native JPEG extracted losslessly
from the user's `Degree.pdf`. The image is stored at
`public/textures/workspace/iitg-degree.jpg`. The first achievement page presents
that artwork on matte white paper; subsequent milestone pages retain the glass
material. The original bend shader animates both presentations.
The `certificate_iitg` wall frame opens only the degree at
`#desk-achievements/iitg-degree`. The `medal_1` object opens its photo and ride
details at `#desk-achievements/ride-for-unity`, with the camera aimed at the medal.
The Achievements menu uses `#desk-achievements` for the complete collection.
Each object-specific view keeps the matching entry in both the paper and HTML
reader. Browser Back, Forward and reload retain the selected item. The original
document's wording and graphics are retained in the certificate artwork.

`src/lib/ui/portfolio-paper-source.ts` adapts the canonical document, and
`portfolio-paper-runtime.js` prints content and resolves paper actions.
`paper-content.ts` extracts the achievement section and retains its original
action elements in the host. `paper-panel.ts` selects the presentation, manages
the iframe, and handles native controls, image delivery, and fallback.

The dialog uses `data-content-view="paper"` for Achievements and
`data-content-view="standard"` for the other sections. Only the paper view has
`data-paper`, `data-paper-view`, and `data-paper-motion` state. Switching to a
standard section removes the iframe and invalidates pending paper loads. This
also prevents a late iframe import from replacing ordinary HTML content.

The adapter retains the authored bundled Three.js r149, custom GLSL,
CanvasTexture, translucent material, procedural grain and environment, hover
lighting, drag inertia, and responsive camera composition. Achievement text and
available imagery are drawn into the paper's texture. They bend and turn with
the sheet instead of remaining in a stationary HTML column.

Content comes from the existing workspace definitions and rendered HTML. The
adapter does not invent award names or personal details. Missing information
stays explicitly marked. Original link destinations remain available.

Long achievement content is split into pages. Native page controls support
pointer, touch, and keyboard navigation. Arrow keys and Page Up/Down change pages
while the sheet is active. Wheel gestures change one page at a time with a
cooldown. Printed links use hit regions that follow the current paper geometry.
A drag turns the sheet without following a link at the end of the gesture.

## Navigation and accessibility

Both presentations keep Back, close, and Escape controls. Opening from the room
or a computer folder retains the appropriate browser history and focus return.
Regular panels use the desk's existing HTML layout and palette, including on
mobile. Their scroll and keyboard events are not handled as paper gestures.

Achievements also has a Read text control. Keyboard focus on an HTML link or
button exposes this reading mode and brings that control into view. The reader
has ordinary selectable text, links, and scrolling. It is the fallback when
WebGL or the paper renderer is unavailable. Standalone portfolio routes remain
usable without JavaScript.

The source's reduced-motion mode fixes shader time at `2.4` and removes idle
sway while preserving deliberate interaction. Entering Read text removes the
paper iframe, so its render loop stops. Back to paper recreates it at the current
page. Closing the dialog or hiding the browser document also removes the frame.
The bundled r149 runs inside the paper iframe, isolated from the desk's current
Three.js version. Standard sections never load this second renderer.

## Verification

`tests/workspace.spec.ts` checks source provenance separately from the customized
achievement sheet. Browser checks confirm the actual graduation artwork has
loaded on the first page, followed by the portfolio milestones. They also cover
page changes, drag and hover, printed links, reader focus, reduced motion, missing
WebGL, and mobile composition. They also check that every other section opens visible HTML without
paper controls or a paper renderer.

The served model and keyboard checks also verify the certificate frame and its
return focus. Shared navigation checks cover contact copy, project links, mobile scrolling,
keyboard and touch controls, focus return, Escape, and browser history. These
checks exercise the visible presentation instead of treating hidden HTML as
evidence that the paper renders correctly.

The September 14 verification used GLB revision `8c7b7b19b2c4`. The full browser
suite finished with 29 passing tests. The remaining failure is the existing
geometry budget check: the scene now has 182,626 triangles against a limit of
180,000. The threshold was not raised. The wall certificate passes keyboard and
mobile touch checks, including return focus after the camera returns to the desk.
The full run is recorded in
[`achievement-scope-tests-final.log`](../artifacts/workspace/achievement-scope-tests-final.log).
`npm run check:workspace` passes; its output is recorded in
[`achievement-scope-typecheck.log`](../artifacts/workspace/achievement-scope-typecheck.log).

The source includes the Three.js authors' MIT notice. That notice is retained;
it does not establish a license for all ThreeUI authoring code. Source provenance
is recorded separately in the local vendor package.
