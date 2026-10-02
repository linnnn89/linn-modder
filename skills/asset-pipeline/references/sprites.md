# 2D sprite commands

Read when cutting out, fitting, pixelating or packing 2D images. Follow the user's requested scope and validation level.

## 2D pipeline
```bash
um sprite info raw.png                                    # size, alpha coverage, corner colour
um sprite cutout raw.png cut.png                          # flat bg → transparent (border flood fill keeps interior whites)
um sprite cutout raw.png cut.png --grey 150 --keep-top 0.8   # also remove a soft grey shadow / the floor under it
um sprite fit cut.png item.png --size 64x26 --hard-alpha  # trim + ONE nearest-neighbour scale into the frame
um sprite fit cut.png npc.png --size 38x34 --anchor bottom   # standing sprites sit on the frame's bottom edge
um sprite pixelate cut.png px.png --size 32x32 --colors 16 --outline   # true pixel art from painterly art
um sprite palette px.png px2.png --from stock_sprite.png  # snap to the game's own colours
um sprite frames npc.png frames/ --n 3 --kind bob          # cheap idle animation (bob/squash/wobble/flash)
um sprite sheet sheet.png frames/*.png --vertical         # Terraria-style strip (or --cols N grid)
um sprite slice sheet.png out/ --frame 32x32              # the other direction
um sprite team-mask unit.png unit_grey.png --hue blue     # player-colour mask (+ desaturated sprite)
um sprite preview item.png look.png --scale 6             # checkerboard + zoom: LOOK at it before shipping
```
- **Pixel art:** scale once, with nearest neighbour, to the final size. Never scale pixel art twice.
- **Painted / HD art:** use `fit --smooth`.
- **Real frames:** for animation frames beyond bob/squash, generate each frame with an available image-edit tool (Codex GPT Image or selected provider)
  using the base sprite as reference ("same drone, rotors tilted, frame 2 of 4"), then cut out and fit each
  frame the same way. Or go 3D (below).
