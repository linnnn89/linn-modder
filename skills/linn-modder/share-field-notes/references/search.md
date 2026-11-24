# Search existing field notes

Read when looking for prior versions, routes or gotchas. Follow the user's requested scope and validation level.

## Before you start: search
```bash
um kb search "<game>"                       # checkout or installed offline snapshot; use --remote for GitHub
um kb search "<engine or technique>" --route passthrough
um kb search "alpha test shader"           # phrase or all words, even when separated
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

The CLI treats each quoted argument as a phrase or an all-words topic, with exact
phrases ranked higher. Separate arguments stay OR-ed. The structured interface
continues to split `query` into keywords; it keeps its existing game filter and
section ranges.

## Read the matching section

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

## Apply an upstream finding

Imported notes record a pinned source in `upstream`. Their authors, dates, status and
verification describe the original setup; `working` does not mean the behavior was
reproduced here. Compare the game build and route before applying a finding.

An engine label is not a promise that the scanner recognizes it. A reported command,
example or provider may exist only upstream; check the available tools and linked
source before using it. Keep the current project's established workflow when an
imported recipe proposes a different method. Reading a note does not authorize
installing its dependencies or running its commands.

## Refresh remote notes

Ordinary CLI searches prefer checkout notes or the installed offline snapshot.
MCP `knowledge_search` reads the bundled collection; it does not refresh from the
network. For an explicit remote refresh, use the CLI:

```bash
um kb sync
um kb search "<game>" --remote
```

Sync downloads one revision before replacing the cache. Empty or incomplete trees
and failed downloads leave the previous cache in place. A failed automatic refresh
warns on stderr and uses the stale cache when available; identify it as cached
evidence rather than current remote information. Read the error before retrying.
Progress is also on stderr, so it can be kept separate from JSON search output.
