# Official references, GPT Image and editable PSD masters

Read when a task needs art, a character base, variants or a layered PSD. Start from
the requested character/game and deliverable; generation is conditional on a real
asset need, not an automatic project setup step.

## Obtain and reuse references first

1. Identify the character, franchise, costume/version, pose and target use. Search
   official character/game pages, publisher or rights-holder media/press kits and
   verified official accounts before fan wikis, reposts or generated references.
2. Verify the source page and its owner. A search thumbnail or a file hosted on a
   CDN is not evidence of an official source by itself. Download the actual image
   when accessible through the harness's browser/download tools, and inspect it.
3. Store references under `references/` and record them in `references/manifest.json`:
   stable reference/character IDs, publisher, source-page URL, image URL, retrieval
   date, local path, SHA-256, source verification and intended reference-only use.
   Keep attribution/usage terms when available. Official reference status does not
   by itself authorize redistribution as a mod asset.
4. Reuse a verified local copy while its hash and required edition still match.
   Fetch again only when missing, changed or a different variant is needed. If the
   official source cannot be verified or downloaded, record that limitation and
   distinguish a user-provided or secondary reference; do not label it official.

Downloaded official images stay in the user's project, not this toolkit repository.
The core service has no web-search/download operation: use the harness's available
tools and record actual results, rather than inventing a Linn Modder command.

## Generate only what is missing

For Codex, use the available GPT Image/image-generation tool for requested base art,
new assets or image edits. The user's authorization to use it persists. Do not
require a fal account or API key when the harness already exposes image generation.
Other harnesses use their configured provider; fal-specific instructions apply
only when fal is selected. Respect any explicit cost or batch limits.

Inspect the reference before an edit and supply the reference through the tool's
supported image input. For a character base, specify identity, body proportions,
pose, camera, silhouette, costume constraints, lighting and the required canvas.
Use transparent output when a cutout is required; a painted checkerboard is not alpha.
Keep the approved base and derive variants through reference-based edits rather
than unrelated fresh prompts. Verify identity and alignment on each result.

Record provider/tool, model when exposed, prompt/edit instructions, input reference
IDs and hashes, output hash, and seed/request ID only when actually provided.
Unknown metadata stays unknown. GPT Image produces raster artwork; layer construction
and game-format conversion are separate operations.

## Build a real layered PSD when requested

Agree the editable parts and canvas from the requested use. Typical character
parts may include base, hair, costume and face/expression variants; use only needed
layers. GPT Image can help produce the base and component artwork, but cannot be
assumed to return a native multi-layer PSD or automatically separate hidden parts.

1. Preserve original images in `assets/source/`; keep aligned transparent component
   PNGs in `assets/layers/`. Establish one canvas and coordinate system. Inspect
   overlaps, masks, alpha edges and whether interchangeable parts actually align.
2. Use an available PSD-capable editor/writer, such as Photoshop or Krita, to assemble
   meaningful named layers/groups. Keep components independently editable and store
   the master under `assets/editable/`. Retain the editor's native source if conversion
   would lose features. Do not rename a PNG to `.psd` or call a flattened image layered.
3. Reopen the saved PSD in a compatible reader/editor. Verify layer names/count/order,
   visibility, canvas, masks and alpha; compare the composite preview and toggle a
   component to confirm it remains separately editable. Complex effects can differ
   across editors, so record the editor/version and actual checks.
4. Record the master, layer sources, preview, source/output hashes and reference IDs
   in `assets/manifest.json`. Use new versions rather than overwriting the only valid
   master. Export engine-specific prepared art to `assets/prepared/` separately.

If no real PSD writer is available, deliver component PNGs and an assembly manifest
as an explicitly incomplete PSD deliverable. This repository currently supplies
PNG preparation, not a native GPT Image API integration or PSD assembler.

## Delivery evidence

Distinguish official reference retrieved, generated art inspected, PSD reopened with
editable layers, engine format validated, and in-game verified. For code-only work,
use synthetic fixtures; do not download character art or generate images just to test
the toolkit. Do not claim game compatibility from a correct PSD or PNG alone.

References checked 2026-10-02:
- [OpenAI image generation](https://developers.openai.com/api/docs/guides/image-generation): image references,
  edits and raster output; inspect the actual tool's supported options rather than pinning a model name here.
- [Krita PSD support](https://docs.krita.org/en/general_concepts/file_formats/file_psd.html): layer support
  and cross-editor limitations make reopening/verification necessary.
