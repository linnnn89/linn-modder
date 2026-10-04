# Linn Modder tool interfaces

Read when selecting an operation, locating manuals or diagnosing an interface boundary.
Installed wheels contain the same skill/reference paths as the checkout.

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
| TKEditor database indexing, paged tables/records/text | `tk_index`, `tk_tables`, `tk_query`, `tk_read_field` |
| TKEditor staged data project and guarded edit preview/apply | `tk_project`, `tk_patch` |
| Add independent external CG options (default), search packs and recover registration | `tk_portraits`, `tk_portrait_options`, `tk_portrait_register` |
| Workspace snapshot/list/integrity verification | `backup_create`, `backup_list`, `backup_verify` |
| Restore preview and optional apply | `backup_restore` |
| Window discovery and capture | `windows_list`, `window_capture` |
| Authorized exact-PID input | `window_input`, exposed only with `--allow-input` |

Use the tool's discovered schema for exact parameters. Do not guess operations such as
`mod_build` or `archive_import`; they are not implemented.

For TKEditor, read [the targeted reference](../file-mod/references/tkeditor.md).
It covers independent new portrait options, explicit replacements, safe JSON edits
and SQLite retrieval. These operations do not install game content or compile bundles.

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
