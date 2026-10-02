# Cast consistency and asset staging

Read when preparing a character set, portraits, flags or illustrations. Follow the user's requested scope and validation level.

## Build a consistent cast

Write ART_DIRECTION.md before batch asset generation. Record stable character IDs,
reference sheets, palette, line style, lighting, costumes, expressions and crop
rules. Maintain the same identity across face, bust, full-body and event variants.
Do not invent mandatory texture dimensions from memory: record measured target
sizes, alpha behavior, compression, mipmaps and resource IDs from known samples.

Keep source assets in `assets/source`, intermediate artwork in `assets/prepared`
and provenance/character mappings in `assets/manifest.json`. `image_prepare`
supports alpha-preserving PNG output, contain/cover fitting and center/top anchors.
Its output includes source and output hashes; copy those to the asset manifest.
Use a chosen generation provider (such as existing `um fal`) only when requested
and configured. Local image preparation does not require a provider.

## Stage a small slice

Start with one character, one event illustration or one flag family. In CK3,
prefer a namespaced data/UI/event slice before undertaking 3D portrait replacement.
In Victoria II, preserve all required political flag variants and localization
columns. In Koei games, prefer a supported portrait importer when available.
Do not assume a prepared PNG can be copied directly into a game's archive.

Keep generated changes in the project workspace. Game roots exposed to the shared
service are read-only. A future engine adapter must validate format round trips
and produce an installation plan before changing an installed game.
