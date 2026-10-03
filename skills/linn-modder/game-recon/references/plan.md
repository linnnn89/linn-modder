# Modding route and plan template

Read when choosing a route or writing MODDING_PLAN.md. Follow the user's requested scope and validation level.

## Decide
- **Can it be modded safely?** Look at anti-cheat, online-only parts, the EULA or mod policy, and the
  ownership checks that loaders rely on (see `skills/linn-modder/mod-any-game/references/safety.md`). If not: say so,
  and offer what is possible (official tools, offline modes, a different game with the same idea).
- **Route:** prefer a supported data/asset route or loader API. Use managed patching, native hooks or
  reimplementation only if simpler routes cannot reach the idea.

## Write MODDING_PLAN.md
```markdown
# <Game> modding plan
- Install: <path> (<store> <appid>), version <x>
- Engine: <engine + version>, code: managed .NET / IL2CPP / native, 64-bit
- Anti-cheat / online: <none | what + verdict>
- Saves: <path>   Config: <path>   Logs: <path>
- Community route: <loader vX.Y (repo)>, install: <steps>, example mod: <link>
- Chosen route for "<idea>": <route> because <reason>
- Lab plan: backup <folders> (um backup), lab profile <how>, windowed <how>
- Unknowns to resolve first: <list>
```
Then continue with the mod-any-game loop (lab setup → source of truth → vertical slice).
