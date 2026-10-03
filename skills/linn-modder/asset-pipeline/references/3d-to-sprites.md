# 3D models to sprite frames

Read when rendering one model into camera angles and animation frames. Follow the user's requested scope and validation level.

## 3D → sprites (consistent angles and animations)
```bash
um fal model3d concept.png --name unit                   # textured GLB (Trellis 2 by default)
um render3d assets/gen/unit.glb frames/ --preset aoe2 --length 80 --forward-yaw -90 \
  --anims idle:10:bob,walk:12:walk,attack:16:lunge,death:20:die --shadows --samples 40
um render3d assets/gen/unit.glb side/ --preset side --canvas 128 --length 110 --engine eevee   # platformer facing R + L
```
Presets:

| Preset | Projection | Camera | Facings |
|---|---|---|---|
| `aoe2` | ortho | 30° | 16 clockwise from east |
| `iso8` | ortho | 30° | 8 |
| `trueiso` | ortho | 35.264° | 8 |
| `topdown` | ortho | — | 8 |
| `side` | ortho | — | 2 (right, left) |
| `turntable` | persp | — | 24 (promo/icon spins) |

- `--length` sets the model's longest horizontal side in pixels at 1x, so match stock units.
- `--forward-yaw` turns the model so its nose faces +X; check the first frame.
- `--shadows` adds a shadow-only pass (`*_s.png`) for engines that keep shadows in their own layer.
- Motions: bob, walk, lunge, die, wreck, spin.
- Then pack with `um sprite sheet`, or with an engine writer (e.g. `examples/aoe2-de-civ/sld.py`).
- Needs Blender (`blender` on PATH or `BLENDER=...`). Cycles uses the GPU when available.
- Dark generated textures: raise `--sun` / `--ambient`, or brighten in post.
- For game-ready 3D (not sprites), remesh with `um fal run tripo3d/tripo/remesh mesh_url=@unit.glb face_limit:=8000`, then convert in Blender
  (GLB → FBX/OBJ) with the engine's scale and axis convention: Unity Y-up metres, Unreal Z-up
  centimetres, Bethesda NIF via PyNifly.
