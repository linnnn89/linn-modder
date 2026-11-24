# Modding field notes

Versioned findings from actual projects: chosen route, engine behavior, verification evidence
and symptom → cause → fix gotchas. Read the relevant note rather than every game's history.

| Task | Entry |
|---|---|
| Find prior work | [INDEX.md](INDEX.md), `index.json`, or `um kb search "<game>"` |
| Write or update a note | [share-field-notes](../skills/linn-modder/share-field-notes/GUIDE.md) |
| Contribution rules | [Shared contribution reference](../skills/linn-modder/share-field-notes/references/contributing.md) |
| Browse the 11 upstream example projects by task | [Game examples](techniques/upstream-game-examples.md) |
| Make an anime portrait pack for Stellaris | [群星萌化：物种与领袖立绘](games/stellaris/anime-species-portraits.md) |
| Engine-specific routes/tools | The matching playbook under `skills/linn-modder/mod-any-game/references/engines/` |
| Cross-game content design | [Resource layers, stable IDs and delivery boundaries](techniques/content-mod-design.md) |

## Search

### CLI and MCP lookup

```bash
um kb search "<game>"
um kb search unreal pak --route loader-api
um kb search "alpha test shader"           # exact phrase or all three words in the same note
um kb show games/gta-v/minecraft-passthrough.md
```

- **CLI sources**: prefers checkout notes or the installed offline snapshot; pass `um kb sync` or `--remote` explicitly for the GitHub copy.
- **MCP sources**: `knowledge_search` always searches the bundled offline collection; read a matching note with `manual_read(collection="knowledge", path=...)`.
- **Long notes**: add `outline:true` to get headings and source lines, then read only the selected range. Confirm the opening version/evidence context once and reuse it for that manual version. Outlines omit body text, YAML and fenced code examples.
- **No CLI**: read [INDEX.md](INDEX.md), or the fork's [remote index](https://raw.githubusercontent.com/linnnn89/linn-modder/main/knowledge/index.json).

### Query matching

A quoted topic matches the full phrase or all of its words, even when they occur
apart. Exact phrases rank higher; separate CLI arguments remain alternatives.
Game filters and section line ranges are available in both interfaces. Structured
`knowledge_search` queries keep their existing keyword semantics.

### Remote sync behavior

Remote sync downloads one revision with at most eight concurrent requests and a
20-second timeout per request. The previous cache stays available until every file
has arrived. Empty or incomplete responses are rejected; a failed refresh uses the
old cache with a warning. Progress goes to stderr so JSON output remains readable.

## Write only when contributing findings

Keep a journal while investigating. Exact builds, supported routes, evidence and known failures
matter more than length. A useful unfinished or abandoned project is welcome if labeled honestly.

```bash
um kb new --game "<game>" --title "<finding>" --agent "<agent and model>"
um kb check knowledge/games/<game>/<note>.md
um kb index
um kb pr knowledge/games/<game>/<note>.md
```

The last command is a dry run; add `--yes` only within user authorization after the note is
reviewable. Do not publish game files, extracted assets, decompiled dumps or secrets.
Writing a note needs a writable checkout or explicit `--root`, not the installed package directory.
Read the writing/contributing reference in the field-note skill only when needed.

## Upstream reports

Imported reports retain their original authors, dates, status and version limits.
Their game verification was performed by upstream authors, not repeated by Linn Modder.
Each imported note records its pinned source in the `upstream` metadata field.
The collection includes both game-specific investigations and reusable techniques;
search by game, engine, file format or error before choosing a route.

A report can refer to an upstream example or optional command that Linn Modder does
not provide. Such references describe the author's setup, not an installed capability.
Use the linked source when reproducing that setup, and keep the current project's
workflow and verification requirements. Integration details are in
[upstream updates](../docs/upstream-updates.md).
