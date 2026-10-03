# Repeatable capture and audio

Read when recording a new authorized gameplay take. Follow the user's requested scope and validation level.

## Make the take repeatable
- **Script the action.** Use a mod-side timeline or command sequence (spawn enemies, fire the weapon, cue
  the boss), a scenario with triggers and camera moves, or a WinDrive command list. The first clean take
  should be reproducible exactly, so you can reshoot after a fix.
- **Restore the world before each take.** Explosions crater worlds; units die. Keep a pristine copy with
  `um backup` and restore it every take.
- **Clean frame.** Hide debug text, fix the camera zoom (the Terraria showcase used 1.5x so 1080p frames
  read like a 720p cut), run at full speed when unfocused, and hide the cursor (capture uses
  `capture_cursor=0`).

## Record the window + the game's own audio
```bash
um win record --exe Game.exe --out captures/take1 --seconds 40      # -> take1.mkv, take1.audio.raw, take1.json
um video first-frame captures/take1.mkv                           # where gameplay starts (skips loading screens)
um video mux captures/take1.mkv captures/take1.audio.raw captures/take1.json take1.mp4 [--offset 0.25]
```
- **Video:** ffmpeg gfxcapture of that window only (GPU frames, no desktop). It encodes with NVENC, AMF or
  QSV when available. NVENC H.264 maxes out at **4096 px wide**, so the recorder scales above that; for
  32:9 screens, crop to the centre 16:9 with `--crop`.
- **Audio:** WASAPI **process loopback** of the game's PID (`um/ps1/ProcLoopback.ps1`). Only the game is
  recorded; no Spotify, no notifications. It's timestamped so the file position is wall time. Muxing uses
  the recorded offset. Fine-tune with a visual/audio sync event (a flash vs its boom) and pass `--offset`.
- **Inside a mod (optional):** start and stop recording from the mod for frame-exact takes. Never block the
  game's main thread while stopping ffmpeg: send `q`, then wait off-thread. Write `.mkv` so a killed
  recorder still leaves a playable file (see `examples/terraria-tmodloader/reference/InModRecorder.cs`).
