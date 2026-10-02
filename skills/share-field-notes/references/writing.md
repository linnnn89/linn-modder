# Journal and field-note writing

Read when turning experiments into a reusable note. Follow the user's requested scope and validation level.

## While you work: keep the journal
Keep a `MODLOG.md` in the mod's working folder. Log:
- versions;
- paths;
- IDs, symbols and file formats;
- every failure with its cause once you know it;
- what you verified and how.

The note is mostly a cleaned-up copy of this.

## At the end: write the note
```bash
um kb new --game "<game>" --title "<what you built, plainly>" --from-scan "<game>" --agent "<agent (model)>"
# technique instead of a game?  um kb new --kind technique --title "..." --agent "..."
```
Fill in every section of the scaffold (`knowledge/TEMPLATE.md` explains each). What matters most:
- **Setup:** exact versions (game build, loader, SDK, OS). "Latest" helps nobody.
- **How the game works:** the engine facts you learned. Name the symbols, and describe logic in your own
  words. Don't paste decompiled code.
- **Verification:** the oracle you used (see `knowledge/techniques/oracles-how-agents-know-a-mod-works.md`)
  and what you did *not* verify.
- **Gotchas:** numbered, symptom → cause → fix. The most valuable part of any note.
- **`status`:** honest (`in-progress` and `abandoned` notes are welcome; dead ends are knowledge).
- **`agents`:** the agent and model, e.g. `Codex (gpt-6)` or `Claude Code (Opus 5.5)`.

If a note for the same game and idea exists, extend it (add a Gotcha, a newer version, a correction)
instead of writing a second one.
