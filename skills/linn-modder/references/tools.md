# Linn Modder tool interfaces

Read when selecting an operation, locating manuals or diagnosing an interface boundary.
Installed wheels contain the same skill/reference paths as the checkout.

## Locate the toolkit and manuals

Linn Modder is the toolkit; `um` is its CLI. The local MCP server identifier is
`linn-modder`; client display names depend on configuration. Ordinary file tools
can read the skill without a running server. Resolve relative links from the
current document, including when the skill directory was copied elsewhere.

MCP `um://guide` and `um://workflow` expose the entry. JSON CLI, Python and MCP
share `manual_read`, for example:

```json
{"collection":"skills","path":"linn-modder/ui-mod/GUIDE.md"}
```

The next reference can be `linn-modder/ui-mod/references/layout-and-state.md`.
Reuse an already loaded route; do not reread the entry between steps. With toolkit
operations use `knowledge_search`, then read a matching `knowledge` note. With
file tools alone search the checkout or exported `knowledge/` directory. Web
sources use the harness's own network tools.

For toolkit development or installation, find the source checkout in the installation
record or client configuration and read `docs/development.md` or `docs/setup.md` there.
These checkout documents are not part of a copied skill directory. Engine manuals
are linked from the [workflow](../mod-any-game/GUIDE.md).

## Choose one interface

| Harness capability | Interface | Discovery |
|---|---|---|
| Local stdio MCP | Linn Modder MCP server | List tools; `um://guide` routes skills |
| Shell commands | `um tool call <name> --args-file args.json` | `um tool list` |
| Python | `Service.invoke(name, arguments)` | `Service.tools()` |

These interfaces share strict argument validation and
`Result(ok, data, artifacts, error)`. An artifact has a path, media type, size and SHA-256.
MCP returns `isError` plus structured errors and PNG content for capture previews.
PowerShell JSON files may use UTF-8 with or without BOM.

Servers can select tools with repeated `--enable-tool NAME` options. Use only the
discovered tools; omitted operations require a configuration change and server restart.
With no selection all default tools remain available; input still needs `--allow-input`.

## Operations available by default

| Task | Operation |
|---|---|
| Platform, dependencies and allowed capabilities | `environment_check` |
| Support levels and constraints | `game_profiles` |
| Fingerprint an explicit allowed game directory | `game_scan` |
| Search bundled notes offline | `knowledge_search` |
| Read one skill/reference/note | `manual_read` |
| Copy skill and knowledge directories once | `manuals_export` |
| Create a staging project | `project_create` |
| Alpha-preserving contain/cover crop to PNG | `image_prepare` |
| Workspace snapshot/list/integrity verification | `backup_create`, `backup_list`, `backup_verify` |
| Restore preview and optional apply | `backup_restore` |
| Window discovery and capture | `windows_list`, `window_capture` |
| Authorized exact-PID input | `window_input`, exposed only with `--allow-input` |

Use the tool's discovered schema for exact parameters. Do not guess operations such as
`mod_build` or `archive_import`; they are not implemented.

Start at `um://guide` or `um://workflow`, which return the same unified `SKILL.md`.
Choose the task's topic `GUIDE.md`, then read the reference needed for the current
step. Use `knowledge_search` for reusable findings and read its matching note from the
`knowledge` collection. Current web sources are handled by the harness through `mod-research`.

## Boundaries

- The workspace must already exist. Repeated `--game-root` flags add read-only directories.
- Service operations write staged outputs under the workspace; direct legacy CLI commands
  do not inherit these directory restrictions.
- Stdio needs the harness and tools on the same machine. A cloud harness has no automatic
  access to the user's PC; an authenticated bridge is a separate future adapter.
- A MCP-only harness can use the operations above but needs its own file-editing tools to
  author scripts, localization and manifests. This server is not a general filesystem API.
- `manual_read` accepts `skills` or `knowledge` collection paths. Checkout-only `docs/` and
  `examples/` are not exposed through that tool. Reference prose mentioning those files
  describes checkout examples, not extra MCP operations.

## Reading a long manual

`manual_read(collection, path)` returns the full text with its existing result fields.
For an initial bounded read, add `start_line:1,max_lines:40`. Ranged results include
`start_line`, `end_line`, `total_lines` and `next_line`; continue with `next_line` until
it is `null`. `max_lines` accepts 1..1000; 0 means all remaining lines. Line numbers
start at 1. These are line limits, not token limits, and a page can cut a code block.
Read the continuation before using an incomplete example. If the whole document is
needed, one full read avoids repeated requests and page metadata.

## Backups and recovery

Snapshots live in `.um/backups/<name>/` under the workspace. `backup_restore` requires
an explicit writable workspace target. With `apply:false` (default), it returns a diff.
Set `apply:true` only for an authorized restore; `clean:true` removes files absent from
that snapshot. Verify paths/checksums before changes and keep `undo_snapshot` from the result.
To access service snapshots through the legacy CLI, pass `--store <workspace>/.um` to
`um backup list/diff/restore`. For long IDs, the undo group uses the first 52 characters
plus `-pre-restore`; the returned path identifies the exact snapshot.

## Additional CLI-only tools

`um fal`, `sprite`, `render3d`, `video`, `win` and `publish` retain their existing commands.
Generation, 3D rendering, recording and publishing are not exported as service tools.
Read only the relevant topic reference and `um <group> --help` when needed.
