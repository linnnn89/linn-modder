# Anime strategy-game mods

## Minimum workflow
1. Call `game_profiles`; record the exact title, build, language and expansion/PK edition.
2. Use `project_create` for staging. CK3/Victoria II have scaffolds; Koei series profiles are planning only.
3. Retrieve official character references first; define stable IDs and style/variant rules in `ART_DIRECTION.md`.
4. Start with one character, illustration or flag family. Measure formats from the target version; [verify tool/import compatibility online](../mod-research/GUIDE.md) before selecting a writer.
5. Keep source art, prepared art and engine outputs separate; record mappings/provenance in the manifest.
6. Report offline checks separately from runtime verification; retain `not-tested-in-game` if no game ran.

CK3's main portraits use a 3D pipeline. PNG preparation does not implement a game importer.
Game roots stay read-only; use a generation provider only when requested and configured.

## Read when needed
| Task | Read |
|---|---|
| Official references, GPT Image character bases or layered PSD | [Sourcing and PSD](../asset-pipeline/references/sourcing-and-psd.md) |
| Choose CK3, Victoria II or a Koei edition/route | [Target games](references/targets.md) |
| Character identity, crops, flags, provenance or a first slice | [Cast and assets](references/cast-and-assets.md) |
| Expressions, layered characters, Live2D/3D or a finished-mod study | [Anime asset contracts](../asset-pipeline/references/anime-assets.md) |
| Encoding, asset-format or runtime checks | [Verification](references/verification.md) |
| Read, modify and repack a version-specific game container | [Archive round trips](../reverse-engineering/references/archive-roundtrip.md) |
| Tool parameters or MCP-only access | [Tool interfaces](../references/tools.md) |

Output: a staging project, measured asset requirements and an honest verification record.
