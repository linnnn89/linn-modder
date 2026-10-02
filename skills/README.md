# Skill router

Read this index only when the next skill is unclear. A known task can go directly to its
`SKILL.md`. Load one entry and only the reference needed for the current step; do not
read every skill, engine playbook or historical example.

## Choose by the task

| User needs | Skill | Expected result |
|---|---|---|
| A whole mod or an unclear multi-stage route | [mod-any-game](mod-any-game/SKILL.md) | Route, staged changes and evidence |
| Install/engine/loader identification or feasibility | [game-recon](game-recon/SKILL.md) | `MODDING_PLAN.md` |
| Anime cast/portraits/flags/localization for strategy games | [anime-strategy-mod](anime-strategy-mod/SKILL.md) | Versioned staging project and asset requirements |
| Inspect internals or an undocumented file format | [reverse-engineering](reverse-engineering/SKILL.md) | Findings or a proven reader/writer |
| Generate new assets specifically with fal | [fal-assets](fal-assets/SKILL.md) | Downloaded assets and provenance |
| Find official references, use GPT Image, prepare PSD/art or render frames | [asset-pipeline](asset-pipeline/SKILL.md) | Traceable references, prepared files or an editable master |
| Capture/control a game or diagnose runtime behavior | [game-automation](game-automation/SKILL.md) | Runtime observations and repeatable steps |
| Combine two games' mechanics or simulations | [mashup-mods](mashup-mods/SKILL.md) | Integration design and a minimal slice |
| Make a demo/trailer/montage | [showcase-video](showcase-video/SKILL.md) | Video, edit recipe and credits |
| Package/release a mod | [publish-mod](publish-mod/SKILL.md) | Reviewable package and release draft |
| Search/write/contribute reusable modding findings | [share-field-notes](share-field-notes/SKILL.md) | Relevant notes or a validated contribution |

For toolkit development, use the checkout's `docs/development.md` instead of a game
workflow. For a small known task, a specialist is enough; load `mod-any-game` only
when coordinating multiple stages.

## Loading with different interfaces

- File-capable harness: read the linked file relative to this document.
- MCP: this index is `um://guide`. Read a skill with `manual_read` and
  `{"collection":"skills","path":"anime-strategy-mod/SKILL.md"}`. For a linked reference,
  resolve the link relative to the current document, then pass its collection-relative path.
- JSON CLI: use `um tool call manual_read --args-file read.json` with the same arguments.
- A harness needing local skill directories: `manuals_export` creates real copies;
  discover/export once, then read selected files instead of repeatedly exporting everything.

Example: from `anime-strategy-mod/SKILL.md`, `references/targets.md` resolves to
`anime-strategy-mod/references/targets.md` in the `skills` collection.
The [tool reference](references/tools.md) describes available operations and boundaries.

## Scope and evidence

Respect the requested validation level. Code-only work can use fixtures; do not install
or launch a game just to follow a workflow. Record unknown versions/formats as unknown.
CK3/Victoria II currently provide scaffolds; Koei series profiles are planning only.
Prepared PNGs are not verified archive imports. Video and publication are separate tasks.
