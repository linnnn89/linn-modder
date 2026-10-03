# Game recon

## Minimum workflow
1. Search existing field notes for the game/engine.
2. Inspect the provided folder with `game_scan` or `um scan`; use `um scan --list` only to find an install.
3. Verify evidence for the engine/build, mod loader, saves/config and online/anti-cheat constraints.
4. Verify current official/maintainer documentation online before choosing a loader or import route; use [mod-research](../mod-research/GUIDE.md), including English, Chinese or Japanese searches as relevant.
5. Write `MODDING_PLAN.md` with the selected route, evidence, paths and unresolved questions.

Inspection is read-only. A series-level profile is not proof of an archive format.
If no install exists, write a provisional plan with unknowns; do not require game installation
for repository or code-only work. Do not inspect protected online clients with live tools.

## Read when needed
| Task | Read |
|---|---|
| Discovery commands, ambiguous fingerprints or community research | [Inspection](references/inspection.md) |
| Installed Steam mod is missing from the game folder | [Workshop and local mod paths](references/steam-workshop.md) |
| Route choice and the plan template | [Plan](references/plan.md) |
| Engine details | The playbook named by the scan under `../mod-any-game/references/engines/` |
| Service versus direct CLI | [Tool interfaces](../references/tools.md) |

Output: `MODDING_PLAN.md`, with confirmed facts separated from assumptions.
