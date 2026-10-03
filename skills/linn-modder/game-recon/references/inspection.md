# Game discovery and inspection

Read when finding an install, reading fingerprints or researching a loader. Follow the user's requested scope and validation level.

## Has another agent been here?
`um kb search "<game>"` (and the engine name). A field note in the shared knowledge base can hand you the
working versions, the route, and the gotchas before you touch anything. See the **share-field-notes** topic guide.

## Find it and fingerprint it
```bash
um scan --list                 # Steam, Epic and Xbox installs (Windows, WSL, Linux, macOS)
um scan "<name or folder>"     # engine, version, exes (.NET?), anti-cheat, loaders, mod folders, saves, routes
um scan "<game>" --json        # the same, machine-readable
```
`um` lives at `bin/um` in the Linn Modder checkout (plugins and clones put it on PATH). Anywhere else:
`uv tool install "linn-modder[mcp] @ git+https://github.com/linnnn89/linn-modder"`.

`um scan` reads files only. It indexes the install (bounded), sniffs PE headers, the Unity/Godot/GameMaker
headers and the Unreal version string, maps known games to their community loader, and points to the
playbook to read: `skills/linn-modder/mod-any-game/references/engines/<engine>.md`.

The scan can't see everything, so check these by hand:
- **Game not in a store library** (GOG, itch, a standalone folder): pass the folder path.
- **Several engines' signals:** launchers and web helpers are common. The top score wins, but read the
  "also" line.
- **Anti-cheat installed elsewhere:** kernel drivers (Vanguard's `vgk.sys`) and launcher-level protection
  don't live in the game folder. Search "<game> anti-cheat".
- **Online-only or live-service games:** treat them as protected even if nothing was detected.

## Research current community routes
Search, in order:
1. "<game> modding" / "<game> mod loader" / "<game> modding wiki". The game's wiki often has a modding page.
2. Nexus Mods (most popular mods show which frameworks they depend on), Thunderstore (Unity games: BepInEx
   packs), mod.io, the Steam Workshop (does the game have one? `um scan` shows installed Workshop content).
3. GitHub: "<game> mod", "<game> modding api", "<game> decompile", "<game> sdk", "<engine> mod loader".
4. Recent posts (X/Reddit/Discord announcements) for new frameworks. The loader might be days old.

Capture: the loader's name, repo, **current version and install steps**, the game versions it supports, a
"hello world" example mod, and where logs go.
