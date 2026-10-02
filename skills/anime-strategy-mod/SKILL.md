---
name: anime-strategy-mod
description: Plan and build anime-style strategy-game mods for CK3, Victoria II, Romance of the Three Kingdoms and Nobunaga's Ambition. Use for character casts, portraits, event illustrations, flags, interface art and localization. Distinguish prepared artwork, validated game formats and in-game verification.
---

# Anime strategy-game mods

Use the `game_profiles` tool first, then `project_create`. Without MCP use
`um tool call <operation> --args-file <UTF-8 JSON file>`; all operations share the
same contract. Read the engine playbook with `manual_read` when needed.

## Establish the target

Record the exact title, version, language, store, expansion/PK edition and existing
mod dependencies. A series name is enough for a planning project but not for an
archive importer. If a version or format is unknown, record it as unknown.

Use these profile IDs:

- `ck3`: project scaffold; native mod descriptor, additive data and UTF-8 BOM YAML
  localization. Main character portraits use a 3D model/material/animation pipeline.
- `victoria2`: project scaffold; legacy .mod and semicolon CSV localization.
  Preserve language columns and verify encoding against the target build/patch.
- `romance-of-the-three-kingdoms`: planning only; select the exact title and edition
  before choosing built-in portrait import, an editor, or a resource adapter.
- `nobunagas-ambition`: planning only; Souzou, Taishi and Shinsei formats must be
  treated independently, including expansion editions.

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

## Verification

Offline checks can establish file dimensions, alpha, encoding, manifest integrity,
descriptor structure and deterministic conversion round trips. Record those checks
in MODLOG.md. Record runtime verification separately; if no game was run, retain
`not-tested-in-game`. Never imply that a planning-only profile is a working loader.
