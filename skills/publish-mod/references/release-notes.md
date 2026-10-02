# README, versioning and release post

Read when writing install instructions, credits or a release draft. Follow the user's requested scope and validation level.

## README (in the zip and on the page)
- What it adds: bullets, a GIF or the showcase video.
- Requirements: game version, the loader and its version, dependencies.
- Install, uninstall and troubleshooting (where the log is).
- Compatibility: multiplayer? Known conflicts?
- Credits:
  - the loader and libraries;
  - references you learned from;
  - **"Art/audio generated with fal (fal.ai) using <models>"** (`fal_manifest.jsonl` lists them);
  - honest AI disclosure (which agent and model built it).
- License for your code (MIT/Apache is common). Your assets' terms follow the models' licenses.

## Version and changelog
Use semver in the manifest/build file, name the supported game version, and keep a changelog. When the game
updates, re-run the in-game test scene before bumping.

## The post
- Lead with the video: the showcase-video skill; 20-45 s, gameplay within 2-3 s.
- Post text: the hook, what it is, the "how" credit (which agent + fal built it), a link.
- If the video uses anyone else's footage, credit them by handle and ask first.
- Prepare a reviewable package and post. Publish only within the user's authorization; request permission if it has not been given.
