# Intake, reconnaissance and route selection

Read when planning a full mod or choosing its implementation route. Follow the user's requested scope and validation level.

### Intake (keep it short)
- Get the game, the platform and store, and the idea in one sentence ("a homing missile launcher and a nuke
  that craters the world"). Record the requested deliverable and validation level; code-only work does not require gameplay or video.
- Settle online vs offline up front. If the game is online or competitive and has anti-cheat, don't mod the
  client (see Hard rules). Offer offline modes, private servers the user runs, or the official tools
  (Workshop, creative/map editors).
- Start `MODLOG.md` in the working folder as the journal. Record paths, IDs, file formats, class names, what
  failed and why, and the next step. Anything not in the journal is lost at the next context compaction.

### Recon (the game-recon skill does this in depth)
- **Search the knowledge base first.** Run `um kb search "<game>"` and `um kb search "<engine>"`. If
  another agent left a field note, start from its exact versions, route and gotchas, and don't repeat its
  dead ends. Without `um`, read
  https://github.com/linnnn89/linn-modder/blob/main/knowledge/INDEX.md.
- Run `um scan "<game>"`. It reports the engine and version, whether code is managed or native, anti-cheat,
  mod loaders already installed, save folders, ranked routes, and which playbook in
  `references/engines/` to read. Read that playbook.
- Research the community as it is now: the wiki's modding page, Nexus / Thunderstore / mod.io / Workshop,
  GitHub, and the loader's current release and install steps. Versions move, so don't install from memory.
  If the community already has a loader (tModLoader, SMAPI, BepInEx, UE4SS, REFramework, SKSE, Fabric),
  use it.

### Pick the cheapest route that reaches the idea

| Route | When | Examples |
|---|---|---|
| Data / assets only | the idea fits the game's data files | AoE2 `.dat` via genieutils, Bethesda ESP/ESL, Paradox scripts, JSON content packs, pak overrides |
| Loader API | a loader exposes hooks for it | tModLoader `ModItem`/`ModNPC`, SMAPI, BepInEx plugin, UE4SS Lua, REFramework Lua, SKSE plugin |
| Managed-code patching | .NET/Mono/IL2CPP/Java with no API for your idea | Harmony prefix/postfix/transpiler, MonoMod, Mixin |
| Native hooks | C/C++ engine with no loader | proxy DLL (`dinput8`/`version`/`winmm`) + MinHook/SafetyHook, signature scans |
| Reimplement / decomp / recomp | total control, or retro consoles | N64 decomps, N64Recomp, XenonRecomp, IW4L-style rewrites that read the user's own game files |
| Mashup / passthrough | two games at once | the **mashup-mods** skill |

Write the chosen route and the reason into MODLOG.md before building.
