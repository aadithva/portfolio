# Grey office chair

The desk chair now uses the user's supplied `office-chair.zip`, containing
`source/OfficeChair.fbx` and the original Main/Net PBR texture sets. The archive
is extracted under `artifacts/workspace/chair-replacement/source/`.

## Model and proportions

- Editable scene: `artifacts/workspace/workspace.blend`.
- Original room backup: `artifacts/workspace/chair-replacement/source-before-chair.blend`.
- Imported model: `chair · Supplied ergonomic office chair`, parented to the
  existing `chair` interaction root. Its pivot, position and rotation remain intact.
- The metric FBX measures approximately 67.6 × 65.6 × 116.3 cm. Its uniform
  scale is 1.31 / 0.75, matching the scene's 75 cm desk height.
- The chair faces the desk; its caster contact height matches the previous
  chair's ground level. All unrelated object transforms and mesh vertices were
  checked for exact equality before saving.

## Materials and export

`scripts/blender/prepare_office_chair_textures.py` derives neutral grey PBR maps
from the supplied 4K textures. The original UV layout, roughness, chrome mask,
normal detail and transparent mesh weave are retained. Source textures remain
available in the extracted archive directory; web derivatives use 1K maps and
a 2K main albedo under `public/textures/workspace/office-chair/`.

`scripts/blender/replace_office_chair.py` creates the review candidate from the
pre-edit backup. It deliberately does not promote or export it, and should not
be used to replace a later room revision without rebasing onto that revision.
The full 167,212-triangle imported mesh remains editable with a non-destructive
decimation modifier. The normal saved-scene exporter reduces its web copy.

The published scene uses the existing `scripts/blender/bake_saved_workspace.py`
pipeline: `public/models/workspace-saved.glb`, its manifest, and the saved-bake
lightmaps. Chair recolouring does not require changes to frontend scene logic.

Review renders, the unrelated-object verification report, and desktop/mobile
browser captures are under `artifacts/workspace/chair-replacement/`.
