# Lamp direction and attachment

## Hidden overhead fill

The user subsequently requested a subtle warm ceiling source above the desk.
`Desk ceiling warm fill` is a 2.8 × 2.1 area light at exported position
`[0, 4.25, -0.7]`, pointing down, with no visible fixture mesh. Its Blender
power is 65 W and linear color is `[1, 0.68, 0.34]`. The runtime ceiling multiplier
is 0.2, reduced from the initial 0.3 following user review. Other source settings
remain as below. `scripts/blender/add_ceiling_fill.py` retains a backup and
hash-checked candidate under `artifacts/workspace/ceiling-fill/`; the normal bake
exports this light and its indirect contribution. Final desktop and narrow-layout
screenshots are in that directory. TypeScript and whitespace checks pass.

## Current spread and room brightness

The subsequent spread adjustment uses 112°, 108° and 116° cones with 0.85 blend
and a 0.085-unit Blender emitter radius. Powers are 100, 60 and 70 W for the
top, middle and lower heads. `soften_lamp_spread.py` records the source backup
and updates only these light settings before the standard bake.

After visual review, the user requested a darker room lit mainly by the lamps
and monitor. The extra room-wide lamp fill was removed. Runtime night hemisphere
intensity is 0.005, environment intensity 0.012, indirect-map intensity 0.035,
and practical intensity multiplier 0.18. Monitor multiplier remains 0.1 and
exposure remains 0.85. The broad cones and existing interactions remain active.
Final on/off captures are `artifacts/workspace/lamp-spread/web-source-lit.png`
and `web-source-lit-off.png`. TypeScript and whitespace checks pass.

## Original aiming adjustment

The September 15 adjustment gives the three red lamp heads separate targets:

- `lamp_1`: the center of the desktop, `[0, 1.31, -0.88]` in exported Y-up space.
- `lamp_2`: the bicycle, `[2.5, 1.25, 0.61]`.
- `lamp_3`: the chair seat area, `[-0.93, 0.82, 0.08]`.

The middle arm swings 180 degrees around its existing pole clamp so its shade
can face the bicycle on the other side of the pole. The other hinges stay fixed.
The shade meshes, liners, rolled rims and bulbs rotate together.

`scripts/blender/aim_lamp_heads.py` measures each opening from the rim geometry.
It positions one spotlight 0.012 units behind that opening and aligns the beam
with the hinge-to-opening axis. Each light is parented to its head in Blender.
The three measured alignment errors round to zero degrees. Furniture collision
checks against the bicycle, chair, right shelf and monitor return zero. The
shade/support contact remains at the articulated joints.

The top task light uses 113 W; the middle and lower lights use 42 W each. Their
existing warm colors remain. Beam angles are 64, 58 and 68 degrees with 0.6 blend.
The fourth, misplaced practical is retained in the master with render and viewport
visibility disabled. It is excluded from the lighting manifest.

`scripts/blender/bake_saved_workspace.py` exports `lampRoot` with each light.
`src/lib/workspace/scene.ts` uses that identity for independent lamp switches and
attaches both the spotlight and its target to the exported head. Hover and click
motion therefore carry the emitter and aim together. Older manifests without an
explicit binding retain their nearest-head fallback.

The indirect-light atlases were rebaked for this arrangement. They still represent
the all-lamps-on scene; individual switches affect direct light and the visible
bulb, rather than recalculating the indirect bake.

Backups, candidate, alignment report, Cycles overview, desktop on/off comparisons
and mobile capture are under `artifacts/workspace/lamp-aim/`. The initial exported
revision is `34fc1d5c2e9c`. TypeScript, production build and three focused browser
tests passed. Each head was independently toggled in the browser and its light
pool checked in the corresponding screenshot.
