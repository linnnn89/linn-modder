# Selected upstream updates — 2026-10-07

Source: [rehan-remade/universal-modder](https://github.com/rehan-remade/universal-modder),
MIT-licensed, pinned at `baff1e5d01f63ae7cc81a049b6f4cf60e6c91dec`.
Fork baseline: `5dd45036fce2121af63834e5656dc58e4cd0e386`.
The changes are selective ports into Linn Modder's existing shared service and
single-entry manuals. No new runtime dependency or default MCP tool is needed.

## Runtime fixes

| Source commit | Port |
|---|---|
| [00b071a](https://github.com/rehan-remade/universal-modder/commit/00b071a) | Preserve RGBA when fitting, sheeting and placing animation frames; keep the deliberate hard-alpha pixelation mode |
| [d649151](https://github.com/rehan-remade/universal-modder/commit/d649151) | Shared PowerShell locator with a SystemRoot/WSL fallback, also used by diagnostics and WSL ffmpeg discovery; existing `um.win.ps_exe` import remains usable |
| [cbffa12](https://github.com/rehan-remade/universal-modder/commit/cbffa12) | Read Steam's installation directory from Windows registry, including WSL discovery |
| [89f4f09](https://github.com/rehan-remade/universal-modder/commit/89f4f09), [3437c20](https://github.com/rehan-remade/universal-modder/commit/3437c20) | Prefer specific game-name routes; distinguish Slay the Spire 2 |
| [3611eb8](https://github.com/rehan-remade/universal-modder/commit/3611eb8) | Match online-only games by normalized whole names; knowledge searches avoid `rust` matching `trust` |
| [63f2f77](https://github.com/rehan-remade/universal-modder/commit/63f2f77) | Report impossible YAML dates as invalid frontmatter rather than crashing |
| [ec9c8df](https://github.com/rehan-remade/universal-modder/commit/ec9c8df) | Recognize current OpenAI key and GitHub fine-grained token formats in existing publish checks |
| [6e023ce](https://github.com/rehan-remade/universal-modder/commit/6e023ce) | ZIP backups accept pre-1980 source timestamps; existing exclusive snapshot creation and restore checks remain |

The bounded streaming scan, staged TKEditor edits and snapshot verification stay
in place. The upstream same-second backup repair is already covered by our existing
microsecond names and exclusive creation, so that implementation was not replaced.

## On-demand reports and research

- [Victoria II total conversion](../knowledge/games/victoria-2/south-central-gang-total-conversion.md):
  map formats, `replace_path`, events and icons for HoD 3.04.
- [GameMaker VM versus YYC](../knowledge/techniques/gamemaker-yyc-vs-vm-check-the-code-chunks-before-trusting-th.md):
  confirm CODE chunks before selecting a GML editing route.
- [Bannerlord asset packages](../knowledge/techniques/editor-free-bannerlord-assets.md):
  version-specific packing, skeleton and animation observations, including unfinished work.
- [Workshop version evidence](../knowledge/techniques/checking-steam-workshop-mods-against-a-game-version.md):
  distinguish metadata dates from actual compatibility evidence.
- [Archived-source research](../skills/linn-modder/mod-research/references/archived-sources.md):
  a reference under the existing research topic, rather than another discoverable skill.

Imported reports retain the original authors, dates, status and per-game verification
claims, with a pinned source link. Those game conclusions were not independently
reproduced here. No game files or images were imported.

ComfyUI, fal changes, HDR/recording changes and the rest of the upstream knowledge
collection are deferred. A future port should be driven by a concrete task.

## Acceptance and rollback

Local acceptance: 127 tests passed, two native Windows checks skipped. Documentation,
12-note knowledge index, publish checks, distribution build and independent installed-wheel
checks passed. No real games were installed or tested.

Focused synthetic fixtures cover
alpha values, discovery fallbacks, name routing, search, date errors, key matching
and old-timestamp backup round trips. Wheel checks cover the imported offline note
and archived-source reference. Real games are not required for this iteration.

Remote branch [backup/pre-upstream-20261007](https://github.com/linnnn89/linn-modder/tree/backup/pre-upstream-20261007)
preserves the baseline. To undo the whole port after merging, revert its squash
commit and push normally. No project-data migration or harness-argument change is needed.
