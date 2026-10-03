# Modding field notes

Versioned findings from actual projects: chosen route, engine behavior, verification evidence
and symptom → cause → fix gotchas. Read the relevant note rather than every game's history.

| Task | Entry |
|---|---|
| Find prior work | [INDEX.md](INDEX.md), `index.json`, or `um kb search "<game>"` |
| Write or update a note | [share-field-notes](../skills/share-field-notes/SKILL.md) |
| Contribution rules | [Shared contribution reference](../skills/share-field-notes/references/contributing.md) |
| Engine-specific routes/tools | The matching playbook under `skills/mod-any-game/references/engines/` |
| Cross-game content design | [Resource layers, stable IDs and delivery boundaries](techniques/content-mod-design.md) |

## Search

```bash
um kb search "<game>"
um kb search unreal pak --route loader-api
um kb show games/gta-v/minecraft-passthrough.md
```

The CLI prefers checkout notes or the installed offline snapshot. Use `um kb sync` or
`--remote` explicitly for the GitHub copy. MCP `knowledge_search` always searches the
bundled offline collection; read a matching note with `manual_read(collection="knowledge", path=...)`.
No CLI? Read [INDEX.md](INDEX.md), or the fork's
[remote index](https://raw.githubusercontent.com/linnnn89/linn-modder/main/knowledge/index.json).

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
