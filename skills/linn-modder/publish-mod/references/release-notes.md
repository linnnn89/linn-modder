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
  - official reference sources and the actual generation provider/model (GPT Image, fal or another tool);
    use recorded provenance, and include `fal_manifest.jsonl` details only for fal-generated assets;
  - honest AI disclosure (which agent and model built it).
- License for your code (MIT/Apache is common). Record the applicable source-asset and
  generation-provider terms; reference-only official images are not automatically part of the release.

## Version and changelog
Use semver in the manifest/build file, name the supported game version, and keep a changelog. When the game
updates, re-run the in-game test scene before bumping.

## The post
- Lead with the video: the showcase-video topic guide; 20-45 s, gameplay within 2-3 s.
- Post text: the hook, what it is, accurate agent/tool credits, a link.
- If the video uses anyone else's footage, credit them by handle and ask first.
- Prepare a reviewable package and post. Publish only within the user's authorization; request permission if it has not been given.
