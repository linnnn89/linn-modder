# Embedded and reimplemented runtimes

Read when considering a library or a replacement guest runtime. Follow the user's requested scope and validation level.

## Pattern 3: embed a decomp as a library
libsm64 turns the Super Mario 64 decomp into a library: feed it collision and input, and it returns Mario's
state and mesh. G64 embeds it in Garry's Mod; the host feeds its collision into the guest sim. Any
decomp/recomp (see `skills/mod-any-game/references/engines/retro-decomp.md`) can be wrapped this way. The
user supplies their own ROM for assets.

## Pattern 4: reimplement, then fuse (heaviest, most control)
- **IW4L:** an LLM-written Rust MW2 runtime (Bevy + wgpu). It reads MW2's FastFiles from the user's install
  and translates the D3D9 shaders to WGSL.
- **The Skate 3 Rust engine:** built against a static recomp and an IDA database as oracles.
- **The mashup:** fuses both, plus a Minecraft Rust reimplementation, in one process. The skate sim is a
  worker that takes over the MW2 soldier. MW2 map collision feeds the skate world. Grind rails come from
  walkable collision edges. Skate bones are retargeted onto the MW2 skeleton.
- **What made it work:**
  - A **scriptable runtime as the oracle:** `spawn; wait 2s; screenshot; dump`, with blocking verbs and
    evidence files per run.
  - An **evidence journal** (`context/artifacts/<date>/<step>-FINAL|PART`). "Knowledge that is not in an
    artifact does not exist."
  - Owner-approved end-to-end tests only.
  - A **publish check** that greps for retail offsets and decompiler names before any push
    (`um publish check` does a version of this).
  - Converters that run on the user's files; game assets never committed.
