# Assets and verification evidence

Read when integrating artwork or checking a completed slice. Follow the user's requested scope and validation level.

### Assets (fal-assets and asset-pipeline skills)
Study the game's own assets first: size, palette, outline, camera angle, facing, frame layout. Then generate
with `um fal`. Every call is recorded in `fal_manifest.jsonl`. Convert with `um sprite` / `um render3d` into
exactly what the engine loads.
- **Consistency across many angles and frames:** generate one concept, turn it into 3D
  (`um fal model3d`), then render every heading from the game's camera (`um render3d --preset aoe2`).
- **Pixel-art games:** generate on a flat background or with transparency, cut out, then do one
  nearest-neighbour fit to the frame size.

### Verify in the real game (build an oracle)
The running game is the oracle; your reading of the code is not.
- Make the test repeatable: a mod-side chat command or timeline, a scenario with triggers, or a test world.
  Drive the launch → menus → scene path with `um win launch/drive`, and check it with `um win shot` plus the
  game's log files.
- Read screenshots at reduced scale (`--scale 0.33`) to save tokens; multiply coordinates back when clicking.
- **Circuit breaker:** if the same failure repeats 3 times, stop. Write down what you know, then change
  approach or ask the user.
- Common log locations:

| Game / loader | Log |
|---|---|
| tModLoader | `client.log` |
| BepInEx | `BepInEx/LogOutput.log` |
| UE4SS | `UE4SS.log` |
| Unity | `Player.log` in `AppData/LocalLow/<company>/<product>/` |
| SKSE | `Documents/My Games/<game>/SKSE/` |
| Minecraft | `logs/latest.log` |
