# Game-art prompts and consistency

Read when writing prompts or deriving variants from reference art. Follow the user's requested scope and validation level.

## Prompting game art that fits the game
- **Look at the game's own assets first:** pixel size, outline, palette, perspective, facing, how busy they
  are. Put that into a reusable style suffix. For Terraria: *"16-bit pixel art game sprite in the style of
  Terraria, crisp dark outline, limited palette, centered, plain flat white background, no shadow, no
  text"*.
- **Describe the view and orientation explicitly:** "perfectly horizontal side view with the muzzle pointing
  right" for held weapons, "seen from the side facing left" for enemies, "pointing straight down" for a
  falling bomb. Engines have conventions (Terraria items point right, NPCs face left) and fixing
  orientation afterwards costs quality.
- **Backgrounds:** transparent (gpt-image-2) or a flat colour that `um sprite cutout` can flood-fill.
  Avoid gradients, scenery and ground shadows. If a soft shadow sneaks in, use `--grey` / `--keep-top`
  in cutout.
- **Player / team colour:** ask for "bright saturated blue accents" on the parts that should take the
  player's colour, then `um sprite team-mask --hue blue` turns them into a mask.
- **Consistency across a set:** generate one hero image, then derive the rest with the edit endpoint and the
  hero as `--ref` ("same robot, now firing, muzzle flash"). Don't ask one prompt for a whole sprite sheet;
  grids come out uneven.
- **Many angles or frames of the same object:** go 3D. Take the concept, run `um fal model3d`, then
  `um render3d` from the game's camera (asset-pipeline topic guide). That's how the AoE2 robotaxi got 16
  consistent headings × 5 animations.
- **No text or logos** in art unless wanted: models love to add them.
