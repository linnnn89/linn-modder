# Asset pipeline

## Minimum workflow
1. For needed art, retrieve and inspect official references first; reuse verified local copies.
2. Confirm size, alpha, pivot, facing, layout, palette and format; [verify unfamiliar/version-sensitive contracts online](../mod-research/GUIDE.md). Codex may use available GPT Image; PSD requires a real layered writer.
3. Preserve source artwork; choose PNG preparation, layered master assembly, sprite conversion, 3D rendering or material conversion.
4. Process one asset and inspect it before batching with the same recipe.
5. Record reference URLs, source/output hashes and settings. Validate the output format; perform runtime checks only in scope.

`image_prepare` returns intermediate RGBA PNGs. It does not create DDS/SLD/XNB or import
archives. Local conversion needs no generation provider. Pixel art uses one nearest-neighbor
scale; painted art can use smooth fitting.

## Read when needed
| Task | Read |
|---|---|
| TKEditor 新增可选头像、三尺寸 PNG 或明确替换旧头像 | [TKEditor Agent 接口](../file-mod/references/tkeditor.md) |
| Official images, GPT Image bases/edits or an editable PSD | [Sourcing and PSD](references/sourcing-and-psd.md) |
| Anime portraits, expressions, Live2D or anime-style 3D | [Anime assets](references/anime-assets.md) |
| Menus, HUD, skins or fonts | [UI MOD](../ui-mod/GUIDE.md) |
| Measure formats or inspect the result | [Target contract](references/target-format.md) |
| Cutout, crop, alpha, palettes, animation frames or sprite sheets | [2D sprites](references/sprites.md) |
| Blender cameras, headings and animation rendering | [3D to sprites](references/3d-to-sprites.md) |
| Tiling, PBR channel packing or DDS | [Materials](references/materials.md) |
| MCP operations versus CLI-only commands | [Tool interfaces](../references/tools.md) |

Output: converted assets, a reproducible recipe and the validation level reached.
