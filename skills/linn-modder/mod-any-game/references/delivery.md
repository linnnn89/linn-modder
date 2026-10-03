# Optional showcase, release and field note

Read when the requested deliverable includes video, packaging or shared notes. Follow the user's requested scope and validation level.

### Showcase (the showcase-video topic guide)
Script the take so it's repeatable. Record the game window with the game's own audio (`um win record`).
Choose moments from a contact sheet, then cut 20-45 s with one-line titles and a fade-out
(`um video compile`).

### Package and publish (the publish-mod topic guide)
Run `um publish check <mod> --game "<install>"`. Write a README with install steps. Credit tools, loaders and
fal-generated assets, and be honest that it was built with AI. Ship no game files.

### Leave a field note (the share-field-notes topic guide)
Turn `MODLOG.md` into a knowledge-base note (`um kb new ...`, then `um kb check`). Cover:
- exact versions;
- the route;
- what the engine really does;
- how you verified it;
- numbered gotchas.

When contributing a note is requested and authorized, open a PR (`um kb pr <note> --yes`).
Unfinished work can still be useful if the note labels its status and verification limits.
