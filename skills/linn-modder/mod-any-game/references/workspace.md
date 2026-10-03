# Workspace and recovery setup

Read when preparing saves, configurations and a reproducible lab. Follow the user's requested scope and validation level.

### Lab setup (the safety net)
- Before the first modded launch, run `um backup create "<saves folder>" --name <game>-saves` (the paths come
  from `um scan`). Snapshot the config/profile folder too if you'll change settings.
- Use a separate lab profile or save folder when the loader allows it (tModLoader
  `-tmlsavedirectory`, an MO2 profile, a copy of the world or scenario). Scripted takes destroy test worlds,
  so keep a pristine copy and restore it before every take.
- Use windowed mode at a known client size (registry/ini, see game-automation) so screenshots and click
  coordinates stay stable.
- Keep decompiled code and extracted assets outside the repo (e.g. `~/<game>-decomp`) and gitignore any
  derived data. Never commit game files.
