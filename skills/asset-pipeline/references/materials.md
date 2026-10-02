# Textures and materials

Read when making tiling textures or converting material channels. Follow the user's requested scope and validation level.

## Textures and materials
- **Tiling:** `um fal texture` generates it tiled. Check with `um sprite tile-preview t.png t3.png`. Fix
  seams on other images with `um sprite seamless`.
- **PBR sets:** `um fal pbr`. Convert to the engine's packing: Unreal ORM (occlusion/roughness/metal in RGB),
  Unity metallic-smoothness (smoothness = 1 - roughness in alpha).
- **DDS:** texconv (DirectXTex) or `magick` with DXT settings. BC7 for quality, BC1 for cutout sprites, BC3
  when alpha is soft.
