# Port content into a host game

Read when implementing guest behavior with host-native mod APIs. Follow the user's requested scope and validation level.

## Pattern 1: port the content (lightest)
Bring an enemy, weapon or block type into the host as **new host content** that imitates the guest.
Examples: "Claude added creepers to Dark Souls", Minecraft blocks as Elden Ring items.
- Read the guest's behaviour from its source of truth: decompile or read the wiki's exact numbers (speeds,
  timers, damage). Reimplement it in the host's mod API (host AI state machine, host projectile).
- **Assets:** never copy the guest's files into your mod. Convert them from the user's install at runtime or
  install time (a converter script), or recreate lookalikes with fal.
- It's cheap and robust, with no IPC. It works with any host that has a loader.
