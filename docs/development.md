# Toolkit development

Read this for repository implementation work. Do not enter a game-modding workflow
unless the task changes a particular game's mod. Synthetic files and fake backends
are sufficient for toolkit tests; real game installation is not required.

## Boundaries and ownership

- Python 3.10+; core modules live in `um/`. CLI groups expose `register(sub)` and `--help`.
- Game editor entry points live in [`editors/`](../editors/README.md), shared-service
  implementations in `um/editors/<game_module>/`, and workflow tests in `tests/editors/`.
  Preserve existing operation names, Python imports and workspace data paths when moving code.
- Add agent operations to `um/service.py`; keep `um/tool.py` and `um/mcp.py` thin.
  Read [architecture](architecture.md) before changing boundaries or capability policy.
- Preserve one JSON result on CLI stdout and protocol-only MCP stdout. Return structured errors.
- Service game roots remain read-only; stage outputs in the workspace. Test path and restore changes
  with synthetic folders, invalid archives and fake Windows adapters.
- PowerShell helpers embed C# 5 for Windows PowerShell 5.1: no string interpolation,
  `out var` or expression-bodied members. Native Windows/Junction checks run in CI.
- Profiles in `um/data/game_profiles.json` describe actual support, not promised archive adapters.
  Confirm editions/versions before adding format claims; see [anime workflow](anime-mods.md).
- Skills and knowledge are bundled under `um/data/` in wheels. A moved reference must work
  from both checkout and installed package, without depending on symlinks.

## Setup and checks

```powershell
uv sync --extra mcp --extra dev
uv run pytest -q tests
uv run python scripts/check_docs.py
uv run um kb check --index
uv run um publish check .
uv run python -m build
```

For the independent installed-wheel check:

```powershell
uv venv wheel-env
uv pip install --python wheel-env/Scripts/python.exe dist/linn_modder-0.3.0-py3-none-any.whl
.\wheel-env\Scripts\python.exe scripts/check_wheel.py
```

On Linux use `wheel-env/bin/python` instead. CI covers Ubuntu/Windows × Python 3.10/3.12,
help screens, knowledge/publish checks, documentation structure and independent wheel installation.
The wheel check reads bundled manuals and runs a synthetic project/backup round trip.

## Documentation changes

Follow [skill design](skill-design.md). Keep fixed harness instructions short; do not duplicate
installation guides, command catalogs or complete workflows in `AGENTS.md` or skill metadata.
Maintain trigger wording and relative links when splitting references. Run `check_docs.py`
and build the installed wheel after moves, then verify a MCP client can read the routed files.
Do not add tests that simply assert prose; validate links, resource paths and protocol behavior.

CLI groups load on demand. When adding a group, also register its short root-help
description in `um/cli.py`; exercise that group's help and an actual operation.
Performance comparisons and rollback instructions live in [the efficiency report](performance.md).
Run the paired benchmark on one machine; do not gate CI on absolute timing from unrelated runners.

## Changes and publication

Run checks relevant to the change; record what was and was not verified. Reuse the user's
existing authorization for pushes/publication, or request it after preparing the reviewable result.
Do not commit game files, extracted assets, decompiled dumps or secrets.
Field-note conventions live in the [contribution reference](../skills/linn-modder/share-field-notes/references/contributing.md)
and [share-field-notes topic](../skills/linn-modder/share-field-notes/GUIDE.md).
