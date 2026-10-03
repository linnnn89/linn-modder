# Target format and verification

Read when measuring an asset contract or checking one converted asset. Follow the user's requested scope and validation level.

## Learn the target format from the game itself
Before converting anything, open two or three of the game's own assets and write down in MODLOG.md:
- **Dimensions:** frame size, frames per sheet, and the layout (vertical strip / grid / one file per frame).
- **Orientation:** which way the art faces (Terraria: items point right, NPCs face left, the engine flips
  them), and where the pivot or hotspot sits (AoE2: the unit's ground point at the canvas centre).
- **Alpha:** hard 1-bit edges (BC1 punch-through, pixel art) or soft.
- **Style:** palette size and outline (dark 1-2 px outline in most pixel-art games).
- **Format:** PNG, DDS BC1/BC3/BC7, XNB, SLD, atlas + JSON...

The draw code is the final authority. In Terraria, NPC frame height = texture height / `Main.npcFrameCount`,
so any consistent frame size works.

## Verify in the game
When runtime verification is in scope, put one converted asset into the game and screenshot it next to stock art (`um win shot`). Check the scale,
facing, pivot, outline and palette. Fix the recipe, then batch-convert the rest with the same commands (a
small script or Makefile, so the pipeline is reproducible from `assets/gen/`).

For offline-only work, validate dimensions/alpha/layout and the format with samples or fixtures.
Record game rendering as untested rather than requiring an installation.
