# ThreeUI source attribution

`src/lib/ui/tactile-dock.ts` adapts the plain DOM spring controller from [ThreeUI Community](https://github.com/MengTo/threeui), by Meng To. Upstream source: [`topDockController.ts`](https://github.com/MengTo/threeui/blob/68802d5428071ada5c20db8094b1649e6bb770ed/src/shaders/animated-top-dock/topDockController.ts), commit `68802d5428071ada5c20db8094b1649e6bb770ed`.

The adaptation retains the proximity/smoothstep and spring approach, keyboard-focus response, media-query handling, and explicit cleanup. It uses real server-rendered links and buttons, bounded transforms instead of width/height changes, cached neutral item centers, no animation frames while idle, and cleanup that safely supports reinitialization. That dock adaptation does not use ThreeUI demo imagery or shader renderers. The separate paper view derives from the registered source, documented below.

## Registered 3D Paper source

The paper view vendors all six files from [the registered source bundle](https://threeui.com/source-code/3d-paper.json), fetched on 2026-09-13, without modifications. Canonical revision: `8ec1b71c0dbcafbadf908100ae2a08045d0a1087c00a09d28245ef19366c7353`. Full checksums and provenance are in `vendor/threeui/source-manifest.json` and `vendor/threeui/README.md`. The local package exposes `ThreeDPaper` and its shared styles under the requested import paths. The active portfolio document adapts the canonical Original source for achievements only. It replaces Nocturne artwork with the user's original IIT Guwahati certificate and documented milestones, using page controls and projected action hit regions. The certificate has a portrait aspect ratio and matte material; the authored bending shader, drag interaction and sandbox remain. Other menus use native HTML panels. The registered files remain unmodified in vendor/threeui; printing and host adaptations are in src/lib/ui/portfolio-paper-source.ts and portfolio-paper-runtime.js.

The following MIT license documents the earlier dock adaptation. The registered paper bundle includes its own Three.js runtime license notice; that is not a license declaration for the entire paper source.

## MIT License for the dock adaptation

Copyright (c) 2026 Meng To

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
