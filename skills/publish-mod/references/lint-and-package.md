# Release lint and platform packaging

Read when checking or packaging a mod for its target platform. Follow the user's requested scope and validation level.

## Lint
```bash
um publish check ./MyMod --game "<game install folder>"
```
- **FAIL:** files byte-identical to game files, leaked keys (fal/Anthropic/OpenAI/GitHub/AWS), `.env` files.
- **WARN:** decompiler fingerprints in source (`FUN_`/`DAT_`/`sub_` names, "Decompiled with" headers), large
  engine archives, absolute user paths, a missing README, fal assets without credit.

Fix every FAIL. Resolve each WARN deliberately. For example, AoE2 data mods do ship a modified `.dat`, which
is the platform's norm.

## Package the way the platform expects

| Platform / loader | Package |
|---|---|
| tModLoader | Build → `.tmod`; publish from the in-game Mod Sources menu (Steam Workshop) |
| BepInEx / Thunderstore | zip with `manifest.json`, `icon.png` (256×256), `README.md`, `plugins/<Mod>.dll`; dependency strings like `BepInEx-BepInExPack-5.4.2100` |
| Nexus Mods | zip laid out as it installs (`Data/...` for Bethesda, `BepInEx/plugins/...`, `ue4ss/Mods/...`, `~mods/*.pak`) |
| AoE2 DE | the official mod site (ageofempires.com/mods) or the in-game uploader; data mods include `resources/_common/dat/...` |
| Steam Workshop | the game's own uploader or SDK tool |
| Minecraft | Modrinth / CurseForge jar with `fabric.mod.json` / `neoforge.mods.toml` |
| ROM hacks / GameMaker | patches only (BPS/IPS/xdelta), never the modified game file |
