# Bicycle wall-mount planning audit

Read-only audit of `artifacts/workspace/workspace.blend` on 2026-09-13.

Source SHA-256:

`f26fbb05c2173e756204de1c2194db4a0b64816340bb8dcb992fbbc5eabf3284`

No source geometry, lights, cameras, assets, or Blender scripts were changed.
`source-audit.json` records actual vertex bounds and object transforms. The
positions below are a placement envelope, not a completed mesh collision check.
The selected bicycle file has not yet been acquired or measured.

## Scene units and occupied space

The scene uses 1.31 units for a 75 cm working height: approximately
1.74667 units/metre, or 0.57252 metres/unit. Use uniform scale for the bicycle.
Do not shrink individual wheels, frame members or handlebars merely to fit.

Actual bounds from mesh vertices, in exported Y-up coordinates:

| Object | X range | Y range | Z range |
| --- | --- | --- | --- |
| Monitor assembly | −0.5109 to 0.5109 | 1.3100 to 2.0245 | −1.6500 to −1.1249 |
| Left shelf wing and attached contents | −1.1880 to −0.3120 | 1.2980 to 3.4163 | −1.9672 to −1.0553 |
| Chair | −1.4079 to −0.3121 | −0.0150 to 2.0211 | −0.5104 to 0.5497 |
| Window | 0.5358 to 2.3636 | 2.7875 to 4.5200 | −1.7616 to 0.0662 |
| Floor top | −3.3200 to 3.3200 | −0.0150 | −2.6643 to 2.3600 |

The wall mesh is consolidated as `_static · Limewashed plaster`. Its object
transform is not the wall plane. Use the world-space faces, not that object's
origin or axis-aligned box, to position the mount.

The left wall's actual inner flat face is:

`x + z = −2.443934`

Its height is approximately Y = −0.005 to 4.565, with the bevel extending to
−0.020 and 4.580. A convenient orthonormal wall frame is:

- Rear corner datum `C = [0, 0, −2.55]`.
- Along the wall toward its outer left end `T = [−0.707107, 0, 0.707107]`.
- Into the room `N = [0.707107, 0, 0.707107]`.
- Up `U = [0, 1, 0]`.
- Inner face `C + s*T + 0.075*N + y*U`.

The inner face ends near s = 4.468. The desk and pegboard occupy approximately
s = 0 to 1.90. A practical free wall run is s = 2.00 to 4.46, about 2.46 units
or 1.41 metres. That is too short for an ordinary adult bicycle displayed
horizontally. A horizontal placement would require a longer wall or moving
existing furniture.

## Recommended mount on the existing room

Use a vertical side-profile display: front wheel up, wheel planes parallel to
the left wall, and saddle/frame projecting toward the outer wall end. This keeps
the bike beside the desk rather than behind the pegboard or above the monitor.

Use an adult road-bike envelope as the initial calibration. For context, the
official Specialized Allez size-56 table lists a 1008 mm wheelbase and 420 mm
handlebar width. Those dimensions correspond to 1.7606 and 0.7336 scene units.
The listing is only a size reference; it is not a claim that the user's bike is
an Allez. [Official geometry table](https://www.specialized.com/se/sv/allez/p/4221808).

Suggested modeling targets, to be replaced by the acquired asset's measurements:

| Dimension | Scene units | Approximate real size |
| --- | --- | --- |
| Wheel diameter including tyre | 1.19 to 1.22 | 68 to 70 cm |
| Wheelbase | 1.76 to 1.90 | 101 to 109 cm |
| Overall wheel-to-wheel length | 2.95 to 3.12 | 169 to 179 cm |
| Handlebar width | 0.73 to 0.87 | 42 to 50 cm |
| Wall-to-wheel-plane stand-off | 0.475 | 27 cm |

Place the midpoint between wheel centres at:

`bicycle = [−1.94454, 2.10, 0.17236]`

This is `C + 3.30*T + 0.550*N + 2.10*U`. The 0.550 normal coordinate includes
the wall's 0.075 inner-face offset plus the 0.475 mount stand-off.

Orient the asset's rear-to-front axle direction along `+U`, its original
bottom-to-top frame direction along `+T`, and its side-to-side direction along
`N` or `−N` as needed to preserve a right-handed basis. The front wheel is above
the rear wheel. The saddle extends toward the outer wall, away from the desk.

For a wheelbase of 1.76 and diameter of 1.20, wheel centres are approximately
Y = 1.22 and 2.98; the tyre extent is Y = 0.62 to 3.58. The bike should remain
within s ≈ 2.70 to 4.40. Check the actual saddle and bar tips against the wall's
outer end after import.

The lower wheel's nearest point to the chair is approximately X = −1.485,
allowing about 0.077 units before the chair's leftmost vertex. That calculation
includes a 0.04-unit half tyre thickness. The frame and pedals should extend
toward larger s; reversing this orientation would put them nearer the chair.
This is an envelope estimate. Validate the acquired mesh against chair, shelf,
pegboard and wall with actual transformed vertices and triangle intersections.

The proposed stand-off supports handlebars up to 50 cm wide while retaining a
small wall clearance. A wide flat-bar MTB will need a different stand-off or
orientation; do not push its bars through the wall or compress the asset.

## Brackets and interaction hierarchy

Use a separate interaction root named `bicycle`, with optional movable children
`bicycle_front_wheel`, `bicycle_rear_wheel`, and `bicycle_crank`. Give wheel roots their
actual axle pivots. The wall supports belong to a separate static
`bicycle_wall_mount` root so bicycle interaction does not rotate the supports.

Provide two visible supports:

1. An upper padded hook or cradle at the upper wheel rim. Its wall plate is near
   `[−2.2808, 3.55, −0.1635]`; the projecting support reaches the wheel plane near
   `[−1.9445, 3.55, 0.1724]`. Fit the final hook curvature to the imported tyre
   and rim, rather than leaving an unexplained gap.
2. A lower wheel stabilizer around the rear wheel's lower arc, near Y = 0.65 to
   0.75. Use the same wall and wheel-plane X/Z coordinates, with a shallow padded
   tray or retaining loop. This prevents the composition from reading as a bike
   floating in front of a wall.

Plate dimensions around 0.14 × 0.25 units, visible fasteners and a dark coated
steel arm are appropriate visual proportions. These are scene-design dimensions,
not a specification for installing a real load-bearing rack.

The portfolio binding can use label `Expeditions` and the established
`expeditions` content section. Avoid inventing a bicycle model, ownership story,
journey, or achievement until supplied by the user or existing content.

## Camera and discovery

Current desktop overview from `src/lib/workspace/config.ts`:

`position [0.04, 2.12, 1.8], target [0, 1.77, −1.28], fov 36°`

The mobile overview scales that camera offset by `max(1, 0.82/aspect)`. Current
screenshots confirm a close monitor/laptop composition. The proposed bicycle is
outside that frame. Preserve the initial monitor view and offer an explicit
Expeditions navigation/Desk guide target so discovery does not depend on hovering
an offscreen object.

Suggested dedicated bicycle view, pending exact asset bounds:

`position [1.42, 2.38, 3.81], target [−2.08, 2.13, 0.31], fov 40°`

This looks approximately along the wall normal and shows the bike's side profile
without free-roaming controls. The target is near the silhouette centre; the
interaction root remains at the axle midpoint. A roughly 5-unit viewing distance
gives about 3.64 units of vertical coverage. At a 0.62 portrait aspect ratio, the
horizontal coverage is about 2.26 units, enough for the intended vertical bike
envelope. For narrower portrait screens, scale the offset by
`max(1, 0.62/aspect)`.

Back/Escape/Reset should restore the current monitor hero. A wider optional
room view can include both the bicycle and desk, but making it the default would
substantially reduce the monitor's size and clarity.

## Before implementation

- Acquire an authorized model and record its licence and source.
- Measure wheel diameter, axle spacing, total width, and bar width before scaling.
- Confirm the asset can use the proposed vertical orientation and stand-off.
- Fit the two supports to actual contact points.
- Verify bike/wall, bike/pegboard, bike/desk, bike/chair, and bar/wall clearances.
- Check the default monitor view and the dedicated bike view on desktop/mobile.
- Preserve the recorded source and authored lighting; any later bake/export must
  use the authoritative scene after the approved bicycle edit.
