# Textures and materials

Read when making tiling textures or converting material channels. Follow the user's requested scope and validation level.

## Textures and materials
- **Tiling:** `um fal texture` generates it tiled. Check with `um sprite tile-preview t.png t3.png`. Fix
  seams on other images with `um sprite seamless`.
- **PBR sets:** `um fal pbr`. Convert to the engine's packing: Unreal ORM (occlusion/roughness/metal in RGB),
  Unity metallic-smoothness (smoothness = 1 - roughness in alpha).
- **DDS:** match a same-build reference's format, header, mip levels and channel use before choosing
  compression. BC7 is not a universal upgrade, and alpha may store data. Follow the
  [DDS inspection and conversion recipe](dds.md).
