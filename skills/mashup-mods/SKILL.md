---
name: mashup-mods
description: Combine two games’ mechanics or runtimes in an offline mod. Use for host-native content ports, two-process passthrough or embedded simulations. 玩法融合；ゲーム融合。
---

# Mashups: putting one game inside another

## Minimum workflow
1. Identify host/guest builds, the requested interaction and ownership of required content.
2. Choose the simplest viable design: host-native imitation, passthrough, embedded library or reimplementation.
3. Define coordinate/time mappings and evidence for behavior before implementation.
4. Start with one shared object or mechanic; add rendering, collision and input incrementally.
5. Record failure/recovery behavior and exact validation scope.

Keep IPC local and authenticated where supported. Never connect to official online services
or distribute guest game assets/decompiles. Ship owned code, patches or user-side converters.

## Read when needed
| Design | Read |
|---|---|
| Host-native behavior/content | [Content port](references/content-port.md) |
| Two games exchanging state, frames or collision | [Passthrough](references/passthrough.md) |
| Guest library or replacement runtime | [Runtime integration](references/runtime-integration.md) |
| Distribution and offline boundaries | [Constraints](references/constraints.md) |
| Comparable historical implementations | [Case studies](../mod-any-game/references/case-studies.md) |

Output: a design with mappings, a minimal integrated slice and verification evidence.
