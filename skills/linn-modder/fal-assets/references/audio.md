# Audio preparation

Read when converting or looping generated sounds. Follow the user's requested scope and validation level.

## Audio for engines
- The SFX and music endpoints return MP3. Convert to what the engine wants:
  - `ffmpeg -i x.mp3 -ar 44100 x.wav` (XNA/tModLoader, most engines);
  - `ffmpeg -i x.mp3 -c:a libvorbis -q:a 5 x.ogg` (Minecraft, Godot, Unity);
  - trim silence first: `-af silenceremove=start_periods=1:start_threshold=-50dB`.
- Loops: `um fal sfx ... --loop`, or ask the music model for a loopable track and crossfade the ends.
- Keep SFX short (0.2-2 s) and normalize loudness (`-af loudnorm=I=-16`) so they sit with the game's own
  sounds.
