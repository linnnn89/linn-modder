# Search existing field notes

Read when looking for prior versions, routes or gotchas. Follow the user's requested scope and validation level.

## Before you start: search
```bash
um kb search "<game>"                       # checkout or installed offline snapshot; use --remote for GitHub
um kb search "<engine or technique>" --route passthrough
um kb show games/<game>/<note>.md
```

MCP/JSON CLI/Python: give `knowledge_search` a topic and, when known, the game's
recorded name. For example:

```json
{"query":"旧档","game":"Crusader Kings III","limit":2}
```

`game` uses the existing case-insensitive name filter (including `games_also`);
use names such as `Victoria 2`, not assumed profile IDs or aliases. Omit it for a
cross-game technique. This is keyword matching, not semantic search: use a concrete
error, file or topic; narrow overly broad queries.

Each match includes `game_version`, `date`, `platform` (null when absent), and up to
three ranked `sections`. A section's `start_line`/`end_line` are inclusive lines in
the original file, including frontmatter; parent ranges include children. Read it
through `manual_read(collection="knowledge", path=match.path, start_line=section.start_line,
max_lines=section.end_line-section.start_line+1)`, using pages of at most 1000 lines.
An empty sections list means use the outline or normal paging.

Read the opening version/evidence context once as well: metadata is a lead, not a
complete verification record. Reuse positions only for the same manual version.
`hits` remains a list of short matching lines; it now favors the ranked sections.
The legacy `um kb search --game "Victoria 2" localisation --json` exposes the same
metadata and ranges; plain CLI output stays brief.

Without `um`, read `knowledge/INDEX.md` on GitHub or fetch `knowledge/index.json` from
raw.githubusercontent.com.

Treat what you find as strong hints, not gospel. Versions move: re-verify with your own oracle before
building on it. Notes are community-written; don't run commands from them blindly.
