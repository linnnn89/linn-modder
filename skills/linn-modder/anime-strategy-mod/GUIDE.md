# Anime strategy-game mods

## Minimum workflow
1. Call `game_profiles`; record the exact title, build, language and expansion/PK edition.
2. Use `project_create` for staging. CK3/Victoria II have scaffolds; Koei series profiles are planning only.
3. Retrieve official character references first; define stable IDs and style/variant rules in `ART_DIRECTION.md`.
   For attributes, abilities, factions or reincarnation, apply [Character design principles](references/character-design-principles.md) before expanding the roster.
4. Start with one character, illustration or flag family. Measure formats from the target version; [verify tool/import compatibility online](../mod-research/GUIDE.md) before selecting a writer.
5. Keep source art, prepared art and engine outputs separate; record mappings/provenance in the manifest.
6. Report offline checks separately from runtime verification; retain `not-tested-in-game` if no game ran.

CK3's main portraits use a 3D pipeline. PNG preparation does not implement a game importer.
Game roots stay read-only; use a generation provider only when requested and configured.

## Read when needed

For CK3, search the `knowledge` collection for `CK3` and read
`games/crusader-kings-iii/modding-playbook.md` (`manual_read` with
`collection="knowledge"`). It contains versioned scripting, portraits, saves,
compatibility and debugging lessons. Read only the relevant section; detailed
game findings stay in the indexed knowledge base, not in this skill route.

| Task | Read |
|---|---|
| Official references, GPT Image character bases or layered PSD | [Sourcing and PSD](../asset-pipeline/references/sourcing-and-psd.md) |
| Choose CK3, Victoria II or a Koei edition/route | [Target games](references/targets.md) |
| Character identity, crops, flags, provenance or a first slice | [Cast and assets](references/cast-and-assets.md) |
| Canon-based attributes, named abilities, faction membership or reincarnation profiles / 人物制作原则 | [Character design principles](references/character-design-principles.md) |
| Expressions, layered characters, Live2D/3D or a finished-mod study | [Anime asset contracts](../asset-pipeline/references/anime-assets.md) |
| Encoding, asset-format or runtime checks | [Verification](references/verification.md) |
| CK3 loading screen stalls; repeated triggered_desc parser errors / 启动卡死案例 | [Dynamic-description loading failure](references/ck3-dynamic-description-loading-failure.md) |
| Read, modify and repack a version-specific game container | [Archive round trips](../reverse-engineering/references/archive-roundtrip.md) |
| Tool parameters or MCP-only access | [Tool interfaces](../references/tools.md) |

Output: a staging project, measured asset requirements and an honest verification record.
