# DDS: inspect a reference, convert, read back

Read when a target actually requires DDS. Use a same-build, same-purpose game asset
as the format reference. Official character images and GPT Image output guide the
art; they do not establish the engine's texture format. Keep source art and editable
masters separate from converted files.

## Record the target contract

With an already available Microsoft DirectXTex installation, inspect a reference:

```powershell
texdiag info "reference.dds"
texdiag analyze "reference.dds"
```

Record the source path/hash, game build and tool version in the existing asset
manifest or MODLOG.md. `info` reports width, height, depth, mipLevels, arraySize,
format, dimension and alpha mode; `analyze` inspects the pixels. Confirm the actual
DDS header and channel use from the original file/material when not supplied by
these results. An Unknown alpha mode does not establish straight or premultiplied
alpha. A preview can look right while stored channels are wrong.

| Use | Determine before conversion |
|---|---|
| Portrait/cutout | Soft or cutout alpha, straight/premultiplied handling, edge colors and the actual UI crop |
| UI texture/atlas | Exact dimensions and layout, accepted header/format, whether the reference has mipmaps |
| Normal/material mask | Meaning of R/G/B/A, linear or sRGB interpretation, any swizzle; alpha may be data |

Match the observed format. BC1 may provide one-bit alpha; BC3 and BC7 have different
alpha/quality characteristics, but the loader and shader decide what is accepted.
Victoria II and CK3 cannot be assumed to use the same texture settings.

## Convert with explicit settings

Use only the flags justified by the reference:

- `-f` selects the DXGI format. `-dx9` requests a legacy header and cannot represent
  BC6/BC7 or texture arrays; sRGB formats lose their sRGB designation in that header.
  `-dx10` requests the extended header, which some old readers do not accept.
- `-m` explicitly selects mip levels. The default is a full chain; `-m 1` removes
  mipmaps. Neither is universally correct for UI. Some assets use authored mip
  content; do not replace that with an automatically averaged chain.
- sRGB flags change color interpretation/conversion. Color art and linear data
  masks need separate recipes; do not apply sRGB conversion to a mask by habit.
- `-pmalpha` changes pixels to premultiplied alpha; `-alpha` converts back to
  straight alpha. Avoid doing either twice.
- `-sepalpha` processes alpha separately during resize/mipmap generation. This is
  relevant when alpha is a data channel: normal WIC transparency handling can clear
  RGB where alpha is zero. Verify the channels, not just the composite.

For example, **only if a UI reference is legacy BC3 with one mip, straight alpha,
and no color conversion is required**, a matching conversion can be:

```powershell
texconv -f BC3_UNORM -dx9 -m 1 -o "assets/prepared" "assets/source/ui.png"
texdiag info "assets/prepared/ui.dds"
texdiag analyze "assets/prepared/ui.dds"
```

Create the output directory first; preserve prior outputs under a new versioned
directory. texconv skips existing outputs unless overwrite is requested. Check its
exit status and confirm the expected file was produced before treating read-back
of an old file as validation. This example is not a default CK3/Victoria II recipe.
Use explicit filenames or texconv's file list for batches; inspect one result before
applying the same verified settings to a batch. Missing tools are a dependency to
resolve when conversion is in scope, not a reason to install them during code work.

## Read back and record what passed

Compare the result's dimensions, format, mip chain, header and relevant channel
semantics with the reference contract. Reopen the image and inspect transparency
and mask channels. `texdiag compare` can measure error against a prepared source
of matching dimensions; it does not compare the artistic similarity to a different
character's reference. BC compression is lossy, so pixel hashes need not match.

Record input/output hashes, exact arguments, tool version and checks performed.
Separate prepared art, validated DDS and in-game rendering; this recipe does not
verify a shader/material binding, ordinary CK3 3D portrait, or runtime appearance.

Author sources read 2026-10-14:
[Microsoft texconv](https://github.com/microsoft/DirectXTex/wiki/texconv),
[Microsoft texdiag](https://github.com/microsoft/DirectXTex/wiki/texdiag).
No DirectXTex code is bundled and no conversion tool is installed by Linn Modder.
