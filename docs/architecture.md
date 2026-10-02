# Linn Modder architecture

Linn Modder is a local Windows-oriented toolkit. A harness supplies planning and
code generation; the toolkit supplies explicit operations and versioned manuals.
The core works offline except for operations already explicitly using external
providers (such as the legacy `um fal` commands).

## Layers

```text
MCP client            Shell-capable harness          Python agent
    |                    um tool call                  |
 um/mcp.py              um/tool.py                     |
    +-----------------------+--------------------------+
                        Service
                 um/service.py + contracts.py
                    /         |          \
           Workspace      projects     WindowsBackend
         path boundaries  game profiles  injectable I/O
                    \         |          /
                existing um modules and WinDrive
```

`Service.invoke(name, arguments)` returns `Result(ok, data, artifacts, error)`.
The CLI prints precisely one JSON result and exits nonzero for errors. MCP tools
use the same named parameters and result schema, set `isError` on operational
failures, and return PNG preview content for vision-capable clients. stdout is
reserved for the protocol; legacy diagnostics remain on stderr.

The MCP transport uses the official Python SDK, pinned to its stable 1.x API.
It is an optional dependency: installing the CLI does not require MCP. Each server
owns a service; its lifespan closes input subprocesses. Blocking work runs on a
worker thread and service calls are serialized, so legacy caches cannot race.
Capture and input subprocess waits are bounded. This is a synchronous operation
API, not yet a persistent job scheduler.

## Workspaces and capabilities

- A required existing workspace owns staging files, captures and backup snapshots.
- Repeated `--game-root` options permit reads from installed game directories.
  Those roots remain read-only through the service, even when nested in a workspace.
- Paths are resolved before containment checks. Recursive scans/backups reject
  linked trees. This is protection from accidental traversal, not an OS sandbox
  against another local process racing filesystem changes.
- Input tools are absent unless the launcher enables `--allow-input` following
  user consent. MCP annotations describe tools; the service enforces configuration.
- Input is bound to an exact PID/process lifetime. Focusing is an explicit action;
  the service disables automatic refocusing. Errors/EOF release successfully held
  inputs. Capture output is automatically named and has a bounded vision preview.
- Existing direct `um win`, `um backup`, etc. retain their CLI interfaces. They do
  not inherit Service workspace restrictions. A harness with shell access still
  needs its own permissions policy.

## Distribution and harness integration

Both `um` and `linn-modder` entry points invoke the same CLI. The Windows checkout
launcher is `bin/um.cmd`; installed console entry points do not need Bash.
Wheels bundle PowerShell helpers, fonts, profiles, skills and an offline knowledge
snapshot. `manuals_export` copies real directories, avoiding Windows symlink
requirements. `manual_read` exposes the same instructions to MCP-only harnesses.

MCP starts over stdio using `um mcp serve --workspace PATH`. It does not open a TCP
listener or install a system service. A remote/cloud harness needs an explicitly
designed authenticated bridge and artifact transfer; local stdio alone does not
give it access to a user's PC.

## Design references

These projects informed the architecture; no implementation code was copied:

- [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk/tree/v1.29.0):
  official transport, generated named schemas, structured results and lifespan cleanup.
- [MCP filesystem server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem):
  explicit allowed roots and canonical path checks before file operations.
- [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp):
  capability flags, per-workspace artifacts and native image results for agents.

## Extension seams

Game profiles in `um/data/game_profiles.json` describe routes, support level,
localization and constraints. A future game adapter should expose `inspect`,
`validate`, `build` and `install_plan` against an explicit game build. It must not
declare a format supported merely because a generic profile exists.

Current service operations cover diagnostics, profiles, scans, bundled manuals,
project creation, 2D image preparation, backups, window discovery/capture and
opt-in input. Rendering, recording, paid generation and publishing remain in the
existing CLI. Before exposing them as background MCP tasks, add persistent job
IDs, bounded concurrency, subprocess cancellation and recoverable job manifests.
Loading/repacking Koei archives and automatic deployment are separate adapters.

Tests use synthetic game folders, images, saves, fake Windows backends and a real
stdio MCP client. Windows CI additionally compiles WinDrive without opening or
controlling a game. No test claims in-game gameplay or rendering verification.
