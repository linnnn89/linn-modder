# Contact sheets, EDL and editing

Read when selecting footage or building an edit from existing clips. Follow the user's requested scope and validation level.

## Look before you cut
```bash
um video probe clip.mp4
um video contact clip.mp4 sheet.png --every 1.5 --cols 6     # a timestamped grid; read it, pick in/out points
um video contact clip.mp4 zoom.png --start 20 --end 30 --every 0.5
```
Pick the peak moments: the explosion, the boss reveal, the unit in formation. Write in/out times into the
EDL.

## Edit with an EDL
`um video compile edl.json out.mp4` (`--preview` renders half size and fast). The full format is in
`um video --help`.
```json
{
  "size": [1920, 1080], "fps": 30,
  "theme": {"accent": "#B6FF3B"},
  "transition": {"type": "fade", "duration": 0.3},
  "clip_volume": 0.8,
  "music": {"path": "music.mp3", "volume": 0.5},
  "watermark": {"path": "logo.png", "height": 54, "corner": "br"},
  "segments": [
    {"clip": "take1.mp4", "in": 9.0, "dur": 3.0, "hook": "Terraria, but with a tactical nuke."},
    {"clip": "take1.mp4", "in": 24.2, "dur": 4.5, "title": "Tactical Nuke", "transition": {"type": "pixelize"}},
    {"clip": "take2.mp4", "in": 3.0, "dur": 5.0, "title": "Drone Mothership boss"},
    {"card": {"title": "Fal Arsenal", "sub": "a Terraria mod"}, "dur": 2.5}
  ]
}
```
- **Transitions:** any ffmpeg xfade type (fade, pixelize, slideleft, smoothleft, circleopen, zoomin,
  radial...) or `cut`.
- **Fills:** for non-16:9 clips, `fill: blur` (blurred backdrop), `crop` or `pad`.
- **Per clip:** `speed` and `volume`, `zoom` to punch in past UI, `crop` [x, y, w, h] to reframe.
- **Music:** `um fal music "..." --seconds 60` makes a bed. Set `bpm` and use `beats` instead of `dur` to
  cut on the beat; `um video beats music.mp3` estimates tempo and first beat.

## Style that works (from real feedback)
- **Titles:** one line naming what's on screen ("Wonder: the Transamerica Pyramid", "Robotaxis and Delivery
  Drones"). No small explanatory captions about how it was made; that goes in the post text.
- **Pace:** get into gameplay within 2-3 s; menus and setup stay under 3 s. Clips run 3-5 s each. End on the
  mod name or URL and fade out.
- **Sound:** keep the game's audio. It sells impacts. Music under a compilation, clip audio around 0.5-0.8.
- **Compilations of other people's clips:** credit every creator on screen (`credit: "@handle"`) and in the
  post, and ask permission when it's promotional. Don't imply their clips were made with your tool. Download
  only public posts, and only what you'll use.
- **Last step:** look at a contact sheet of the finished video before sharing it.
