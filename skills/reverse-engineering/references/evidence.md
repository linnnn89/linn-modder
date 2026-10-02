# Evidence and runtime comparisons

Read when comparing a port to observed behavior or recording confirmed facts. Follow the user's requested scope and validation level.

## Make it an oracle
- **Engine logic you port** (for a simulator, a trainer, a reimplementation): record real traces from the
  game (positions, velocities per tick) and replay them against your port. In the Terraria Eye of Cthulhu
  work, the Eye's velocity matched 99.9% once the port used the action applied on frame t+1. Float32
  constants mattered too (`0.2f` ≠ `0.2`). A leftover mismatch was traced to a hidden buff (Happy!, x1.21
  move speed). Replays find what reading the code misses.
- **For long RE runs:**
  - a journal file;
  - small verified steps;
  - cap attempts per problem (about 3 identical failures, then change approach);
  - commit every confirmed fact.
