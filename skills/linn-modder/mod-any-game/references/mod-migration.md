# Preserve an existing mod across game or loader versions

Use for upgrading, reviving or changing the loader of an existing mod. For bringing
another game's mechanics into a host, use [content porting](../../mashup-mods/references/content-port.md).
Migration changes the implementation environment; it does not authorize redesigning gameplay.

## Establish the behavior to preserve

Pin the source mod release/commit and target game build/loader. Record source hashes for
the affected inputs, not the whole installation. Read the matching source or a private
reference from the user's files; later rewrites and wikis are secondary evidence.
If the reference version changes, explicitly revisit the affected mappings.

For the requested feature set, identify data, scripts, lifecycle callbacks, UI, assets,
configuration and persisted IDs. Keep a compact mapping in the existing project notes:

| Source contract | Target representation | Preserved behavior | Evidence / unresolved item |
|---|---|---|---|
| Stable item/character ID | Same ID, or explicit old-to-new map | Existing references remain valid | Import/read-back or reference check |
| Callback and scope | Target callback, same owner | Fires once under the same conditions | State transition scenario |
| Texture/voice reference | Target path and format | Correct identity, dimensions, timing | Preview plus target-format check |

Keep observed quirks when they are part of the requested compatibility contract. Do not
reproduce crashes or corruption merely to match the source; disclose necessary deviations.
Check callers before treating unused original code as a missing feature.

## Transform data without changing its meaning

- Extract repeated tables and resource references with a small script when manual edits
  would lose entries. Preserve ordering, duplicate accumulation and first-match behavior.
- Keep stable IDs whenever the target allows it. Flatten legacy `(id, variant)` pairs only
  with an explicit mapping; unresolved references must remain visible, not silently dropped.
- Reconcile the affected inventory before/after: expected IDs, variants, references and
  counts. Counts alone do not establish equivalent behavior.
- Work on a separate output. Do not edit the source mod, delete assets or migrate manual
  saves in place. Existing save compatibility is a separate requirement: declare whether
  old saves are supported, need a tested copy migration, or require a new game.

## Port and prove one complete behavior

Read the source path, implement its target equivalent, then verify an observable scenario
against that source contract. Use fixed examples and target-native checks where available;
avoid tests that merely echo the new implementation. Cover high-risk ordering, repeated
callbacks or persisted references within the project's test budget.

For a game update, first reproduce the failing behavior and compare the changed API/schema.
Do not replace a loader, convert all assets or rewrite systems when a local compatibility
change is sufficient. For resource writers follow the [no-change round trip](../../reverse-engineering/references/archive-roundtrip.md).

Keep delivery evidence separate: source mapping, build/format checks, loaded mod and actual
gameplay. If game execution is outside scope, report it as untested. Installation uses the
affected-file manifest and backups; preserve unrelated mods, configuration and saves.

## Source and distribution

Adapted from Rehan's MIT-licensed universal-modder
[port-a-mod at c1dff21](https://github.com/rehan-remade/universal-modder/blob/c1dff21/skills/port-a-mod/SKILL.md).
Its large Minecraft example is methodological evidence, not local validation. Follow the
source mod's own code/asset permissions for distribution; keep game assets and private
decompiled references out of this toolkit and public PRs.
