# Linn Modder

Windows-first mod toolkit; MCP, JSON CLI and Python share one service.
Follow the user's requested scope. Toolkit/code work uses synthetic fixtures;
a real game installation, gameplay test or showcase is required only when requested.

## Load on demand
- Known modding task: open only its `skills/<name>/SKILL.md` and the reference needed for the current step.
- Unknown route: read `skills/README.md` to choose a skill. Do not preload the skill catalog's bodies.
- Toolkit code/integration: read `docs/development.md`; read `docs/architecture.md` when changing service boundaries.
- Installation or harness configuration: read `docs/setup.md`.
- Reuse prior game findings: search the knowledge base; read only relevant matches.

## Always keep
- Use owned offline games; no protected online-client modification or protection bypasses.
- Stage changes in the workspace; service game roots remain read-only. Back up affected saves/config first.
- Never commit game files, extracted assets, decompiled dumps or secrets; kill processes by exact PID.
- Desktop input, installation/registry changes and publication need user authorization; reuse authorization already given.
- Keep evidence/unknowns in `MODLOG.md` for mod work; distinguish prepared art, format validation and game verification.
- Keep MCP/JSON stdout clean and operational errors structured. State unsupported formats honestly.
