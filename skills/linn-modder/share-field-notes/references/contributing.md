# Validate and contribute a note

Read when checking a draft, updating an existing note or publishing an authorized PR. Follow the user's requested scope and validation level.

## Check, then PR (with permission)
```bash
um kb check knowledge/games/<game>/<note>.md
um kb index
um kb check --root knowledge --index             # check the collection from its checkout
um kb pr knowledge/games/<game>/<note>.md          # dry run: shows the git/gh commands
um kb pr knowledge/games/<game>/<note>.md --yes    # branch, commit, push (fork if needed), open the PR
```
- Use existing authorization before `--yes`; otherwise show the completed note and request permission to publish it.
- `um kb check` fails on:
  - missing folders or note files, or a collection with no notes to check;
  - secrets;
  - unfilled template text;
  - missing sections;
  - code blocks over 150 lines (link your repo instead);
  - oversized images (keep media under `media/`, under 1.5 MB).
- Gotchas may use numbered list items or numbered subheadings such as `### 1. ...`.
  An unfamiliar engine label is a warning about scanner coverage, not a reason to
  relabel the report or claim new engine support.
- **Never include:**
  - game files or extracted assets;
  - decompiled code dumps;
  - anything that helps cheat in online games or bypass anti-cheat, DRM or ownership checks.

## When your notes disagree with an existing one
Don't delete theirs. Add a dated line to the relevant Gotcha ("2026-10-02, build 1.2.3: this changed to...")
and bump `date`. The PR discussion is where it gets settled.
