---
name: asset-pipeline
description: Prepare existing artwork for measured game requirements. Use for image crops, alpha, palettes, sprite layouts, texture channels or 3D-to-sprite rendering.
---

# Asset pipeline

## Minimum workflow
1. Confirm the target size, alpha, pivot, facing, layout, palette and format from versioned samples.
2. Keep source artwork unchanged; choose PNG preparation, sprite conversion, 3D rendering or material conversion.
3. Process one asset and inspect it before batching with the same recipe.
4. Record source/output hashes and settings. Validate the output format; perform runtime checks only in scope.

`image_prepare` returns intermediate RGBA PNGs. It does not create DDS/SLD/XNB or import
archives. Local conversion needs no generation provider. Pixel art uses one nearest-neighbor
scale; painted art can use smooth fitting.

## Read when needed
| Task | Read |
|---|---|
| Measure formats or inspect the result | [Target contract](references/target-format.md) |
| Cutout, crop, alpha, palettes, animation frames or sprite sheets | [2D sprites](references/sprites.md) |
| Blender cameras, headings and animation rendering | [3D to sprites](references/3d-to-sprites.md) |
| Tiling, PBR channel packing or DDS | [Materials](references/materials.md) |
| MCP operations versus CLI-only commands | [Tool interfaces](../references/tools.md) |

Output: converted assets, a reproducible recipe and the validation level reached.
