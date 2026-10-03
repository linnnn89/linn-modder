# Mod any game

Use this guide to coordinate a mod from an idea to the user's requested deliverable.
For one known task, use the matching topic from the [unified entry](../SKILL.md).

## Minimum workflow
1. Record the exact game/build, idea and requested validation level in `MODLOG.md`.
2. Search existing notes; verify current route/tool compatibility online before choosing a data, asset or loader route. Use [mod-research](../mod-research/GUIDE.md) for unknowns.
3. Stage work separately from game files; snapshot saves/config before changing them.
4. Implement one complete feature with placeholder assets before expanding.
5. Validate within the authorized scope. Separate prepared art, format checks and game runs.
6. Deliver the requested files and evidence. Video, public release and field-note publication are optional.

For code-only work, use synthetic fixtures and report runtime as untested. Follow existing
user authorization; do not install or launch a game just to complete this checklist.
Never bypass protections, modify protected online clients or distribute game assets/decompiles.

## Read only for the current stage
| Task | Read |
|---|---|
| Intake, unknown engine or route | [Planning](references/planning.md), then [game-recon](../game-recon/GUIDE.md) if needed |
| Workspace, saves and recovery | [Workspace](references/workspace.md) |
| Internals or first feature | [Implementation](references/implementation.md) |
| Asset integration or evidence | [Verification](references/verification.md) |
| Video, package or field note requested | [Delivery](references/delivery.md), then the matching topic guide |
| Anime strategy-game conversion | [anime-strategy-mod](../anime-strategy-mod/GUIDE.md) |
| HUD, menu, fonts or interface localization | [ui-mod](../ui-mod/GUIDE.md) |
| Known data, script or asset file edits | [file-mod](../file-mod/GUIDE.md) |
| Engine-specific behavior | Only the playbook named by the scan in `references/engines/` |
| Permissions or distribution question | [Safety](references/safety.md) |
| A comparable historical project | [Case studies](references/case-studies.md) |

Output: a chosen route, staged changes, verification evidence and explicit untested items.
