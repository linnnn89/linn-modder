---
name: game-recon
description: Identify a game’s install, engine, build, existing loader and modding route. Use for feasibility questions or an unknown target before implementation.
---

# Game recon

## Minimum workflow
1. Search existing field notes for the game/engine.
2. Inspect the provided folder with `game_scan` or `um scan`; use `um scan --list` only to find an install.
3. Verify evidence for the engine/build, mod loader, saves/config and online/anti-cheat constraints.
4. Check current community documentation when choosing a loader or import route.
5. Write `MODDING_PLAN.md` with the selected route, evidence, paths and unresolved questions.

Inspection is read-only. A series-level profile is not proof of an archive format.
If no install exists, write a provisional plan with unknowns; do not require game installation
for repository or code-only work. Do not inspect protected online clients with live tools.

## Read when needed
| Task | Read |
|---|---|
| Discovery commands, ambiguous fingerprints or community research | [Inspection](references/inspection.md) |
| Route choice and the plan template | [Plan](references/plan.md) |
| Engine details | The playbook named by the scan under `../mod-any-game/references/engines/` |
| Service versus direct CLI | [Tool interfaces](../references/tools.md) |

Output: `MODDING_PLAN.md`, with confirmed facts separated from assumptions.
