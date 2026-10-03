# Reverse engineering for mods

## Minimum workflow
1. Start from the unresolved question and game build; [search current official/maintainer sources online](../mod-research/GUIDE.md) before choosing readers or inventing a writer.
2. Select the inspection tool for managed code, native code, live behavior or graphics.
3. Keep decompiles and extracted assets outside the repository; record confirmed symbols/formats in `MODLOG.md`.
4. For containers, inspect/extract, prove a no-change repack, then modify and validate a staged output; preserve the source backup.
5. Separate hypotheses, offline evidence and runtime observations.

Only owned offline targets are in scope. Never attach live tools to protected online clients,
bypass protections or publish decompiled source/assets. Do not treat a guessed offset as verified.

## Read when needed
| Task | Read |
|---|---|
| Decompiler, debugger, live state or GPU inspection | [Code and runtime](references/code-and-runtime.md) |
| Archive/data readers and encoder round trips | [File formats](references/file-formats.md) |
| Known configuration, data or localization edits | [File modification](../file-mod/GUIDE.md) |
| Modify data inside a container and repack it | [Archive round trips](references/archive-roundtrip.md) |
| Replay comparisons and evidence journaling | [Evidence](references/evidence.md) |
| Ownership, permissions or distribution | [Safety](../mod-any-game/references/safety.md) |

Output: verified findings or a tested reader/writer, with unknowns and version constraints.
