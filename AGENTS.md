# Linn Modder

Windows-first mod toolkit; MCP, JSON CLI and Python share one service.
Follow the user's requested scope. Toolkit/code work uses synthetic fixtures;
a real game installation, gameplay test or showcase is required only when requested.

## Load on demand
- Modding task: read the single entry `skills/linn-modder/SKILL.md`, then the matching topic's `GUIDE.md` and current reference.
- Topic folders are on-demand documents. Keep one discoverable `SKILL.md`; do not preload all guides.
- Toolkit code/integration: read `docs/development.md`; read `docs/architecture.md` when changing service boundaries.
- Installation or harness configuration: read `docs/setup.md`.
- Reuse prior game findings: search the knowledge base; read only relevant matches.
- Verify unfamiliar formats, tool choices and version changes online through the `mod-research` topic.

## Always keep
- Use owned offline games; no protected online-client modification or protection bypasses.
- Stage changes in the workspace; service game roots remain read-only. Back up affected saves/config first.
- Never commit game files, extracted assets, decompiled dumps or secrets; kill processes by exact PID.
- Desktop input, installation/registry changes and publication need user authorization; reuse authorization already given.
- Keep evidence/unknowns in `MODLOG.md` for mod work; distinguish prepared art, format validation and game verification.
- Keep MCP/JSON stdout clean and operational errors structured. State unsupported formats honestly.

## Harness compatibility

`AGENTS.md` is canonical. Codex/plugin and other client entry formats are documented
in `docs/setup.md`; keep shared workflows in `skills/`, not duplicated per harness.
On Windows a `../skills` text pointer is not an auto-discovered skill directory.
Use the existing plugin, MCP manual reads or exported real directories. Preserve
compatibility manifests; do not create empty platform skill directories.
