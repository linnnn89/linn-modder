# Repeatable windows and test scenes

Read when building repeatable tests or a mod-side observation bridge. Follow the user's requested scope and validation level.

## Make the window predictable
- **Windowed mode at a fixed client size.** Every game hides this setting somewhere:
  - an ini (`[/Script/Engine.GameUserSettings]` in UE `GameUserSettings.ini`, Unity's
    `Screenmanager Fullscreen mode` / `Resolution` registry values under `HKCU\Software\<company>\<product>`);
  - a launch flag (`-windowed -w 1920 -h 1080`, Unity `-screen-fullscreen 0 -screen-width 1920 -screen-height 1080`,
    Source `-sw -w 1920 -h 1080`);
  - or the game's own registry (AoE2: `Mode Display` 0 + `Windowed Width/Height`).
  - `um win drive --proc X "size 1920 1080"` also resizes most windowed games.
- **Skip intros:** launch flags (`-skipintro`, `-nosplash`, Unity `-popupwindow`), or delete/rename intro
  videos in a **copy** of the game.
- **Jump straight in:** loader flags (tModLoader `-skipselect Player:World`), a save made for testing,
  scenario auto-load, a dev console command.
- **Background throttling:** many games throttle or pause unfocused. Find the setting (Terraria:
  `Main.instance.InactiveSleepTime = TimeSpan.Zero`; Unity: `Application.runInBackground = true`; UE:
  `t.IdleWhenNotForeground 0`).

## Better than clicking: a scripted scene or a bridge
- **Chat or console commands in your mod** give items, spawn enemies and teleport. They make tests one line
  (`/arsenal`, `/mothership`).
- **Test scenes:** a mod-side timeline (spawn waves at frame N, fire at N+30), a scenario with triggers
  (AoE2 via AoE2ScenarioParser), a dedicated test world with a pristine backup.
- **Agent bridge:** a JSON-lines socket inside the mod on `127.0.0.1` (see
  `examples/terraria-tmodloader/reference/AgentBridge.cs`).
  - Commands like `observe` (menu options or world state as text), `click <id>`, `controls`, `step`.
  - Handle every request on the game's main thread after an update, so replies are consistent.
  - Read menus generically from the UI tree, so the agent sees what a player would. Leave destructive
    buttons (delete) out.
  - An agent can then play without pixels at all.
- **Out-of-process backend:** keep the in-game part thin and put the brains outside (HTTP/file-drop). That
  pattern scales to AI NPCs and cross-game mashups.
