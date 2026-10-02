---
name: game-automation
description: Capture or control an authorized game session, diagnose runtime failures or build repeatable test scenes. Windows first; use only when runtime interaction is in scope.
---

# Game automation

## Minimum workflow
1. Confirm runtime interaction is requested and desktop input is authorized. Read-only capture does not enable input.
2. Use `environment_check`, discover an exact PID/window, and snapshot affected saves/config before changes.
3. Define a repeatable scene; prefer mod-side commands/state observation over fragile menu clicks.
4. Capture evidence and read logs. Record client size and coordinate scale when input is used.
5. Close capture/input processes and report observed results, failures and remaining unknowns.

`window_input` is absent by default and requires `--allow-input`. Focus is explicit.
Never redirect the user's active typing into a game or modify protected online clients.
Kill only exact PIDs. Code-only tasks use fixtures instead of launching a game.

## Read when needed
| Task | Read |
|---|---|
| Windows capture, client coordinates or WinDrive commands | [Windows](references/windows.md) |
| Fixed windows, scripted scenes or a mod bridge | [Test scenes](references/test-scenes.md) |
| Crashes, logs or orphan-process cleanup | [Diagnostics](references/diagnostics.md) |
| Linux/macOS input or capture | [Other platforms](references/other-platforms.md) |
| Capability and workspace boundaries | [Tool interfaces](../references/tools.md) |

Output: runtime evidence with exact target/process and reproducible steps.
