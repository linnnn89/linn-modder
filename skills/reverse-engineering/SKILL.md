---
name: reverse-engineering
description: Investigate offline game code, behavior or undocumented asset formats when supported mod APIs and documentation are insufficient. Use evidence and format round trips.
---

# Reverse engineering for mods

## Minimum workflow
1. Start from the unresolved question and the game build; prefer documented APIs or community readers first.
2. Select the inspection tool for managed code, native code, live behavior or graphics.
3. Keep decompiles and extracted assets outside the repository; record confirmed symbols/formats in `MODLOG.md`.
4. For a new file format, decode several samples, inspect the output, then prove an encoder round trip.
5. Separate hypotheses, offline evidence and runtime observations.

Only owned offline targets are in scope. Never attach live tools to protected online clients,
bypass protections or publish decompiled source/assets. Do not treat a guessed offset as verified.

## Read when needed
| Task | Read |
|---|---|
| Decompiler, debugger, live state or GPU inspection | [Code and runtime](references/code-and-runtime.md) |
| Archive/data readers and encoder round trips | [File formats](references/file-formats.md) |
| Replay comparisons and evidence journaling | [Evidence](references/evidence.md) |
| Ownership, permissions or distribution | [Safety](../mod-any-game/references/safety.md) |

Output: verified findings or a tested reader/writer, with unknowns and version constraints.
