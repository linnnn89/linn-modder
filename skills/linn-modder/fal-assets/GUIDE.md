# Game assets with fal

## Minimum workflow
1. For artwork, retrieve official references first. Confirm fal is selected and use existing cost authorization; Codex's available GPT Image does not require fal.
2. Check current model schema and pricing; defaults and endpoints can change.
3. Generate one representative asset, inspect it, then derive consistent variants from the reference.
4. Download required files and preserve `fal_manifest.jsonl` with prompts, seeds and request IDs.
5. Hand the output to [asset-pipeline](../asset-pipeline/GUIDE.md) for target-format conversion.

Never print or commit keys. For a batch outside the agreed budget, show the estimated cost
before submitting it. Local image preparation does not require fal or a key.

## Read when needed
| Task | Read |
|---|---|
| Official references or Codex GPT Image / PSD workflow | [Sourcing and PSD](../asset-pipeline/references/sourcing-and-psd.md) |
| Credentials, MCP/CLI setup or interface choice | [Connection](references/connection.md) |
| Sprite, texture, 3D, voice, music or video commands | [Recipes](references/recipes.md) |
| Style prompts, facing and character consistency | [Art direction](references/art-direction.md) |
| Engine audio formats, silence or loops | [Audio](references/audio.md) |
| Batch cost, provenance, licensing or credits | [Cost and provenance](references/cost-and-provenance.md) |

Output: downloaded assets and their generation manifest; engine compatibility remains a separate check.
