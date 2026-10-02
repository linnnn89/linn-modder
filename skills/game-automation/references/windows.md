# Windows capture and input

Read when launching, capturing or controlling an authorized Windows session. Follow the user's requested scope and validation level.

## Windows (native or from WSL): `um win`
```bash
um win setup                                   # once: PowerShell tools + an ffmpeg with gfxcapture, picks NVENC/AMF/QSV/x264
um win ps                                      # windowed processes: pid, name, title
um win launch --steam 105600                   # or: um win launch "C:\Games\Foo\Foo.exe" -- -windowed
um win shot --exe Terraria.exe shot.png --scale 0.33   # full frame + a 1/3 copy that's cheap to look at
um win drive --proc Terraria "focus" "click 640 360" "key 0x1B" "type hello" "hold 0x44 1500"
um win drive --proc Terraria idle              # seconds since the user last touched mouse/keyboard
um win kill <pid>                              # exact PID only
um win reg get "HKCU\Software\..."             # registry (reg set backs the key up first)
```
From Python (for longer scripts), `from um.win import Drive, shot, Recorder`, then `d = Drive("AoE2DE_s")`,
`d.focus()`, `d.click(x, y)`, `d.key("0x0D")`.

**WinDrive commands** (`um/ps1/WinDrive.ps1`; stdin protocol, one reply per line). Coordinates are in
the game window's **client area**.
- Mouse: `move x y`, `click x y [right]`, `mdown`/`mup`, `drag x0 y0 x1 y1`, `rel dx dy` (FPS cameras /
  raw input), `wheel 120`.
- Keyboard: `key <vk> [tap|down|up]`, `hold <vk> <ms>`, `type <text>`, `scanmode on` (DirectInput /
  raw-input games that ignore virtual-key events).
- Window: `focus`, `rect`, `size <w> <h>` (sets the client size), `title`, `fg`, `idle`, `untop`.
- Virtual-key codes: Esc 0x1B, Enter 0x0D, Space 0x20, W/A/S/D 0x57/0x41/0x53/0x44, F1 0x70, Shift 0x10,
  Ctrl 0x11, arrows 0x25-0x28.

**Rules of the road**
- **Never focus a game with an online mode while the human is typing.** It happened with GTA V: the agent
  focused GTA to click Story Mode, the human's keystrokes hit GTA's landing page, and GTA warned about
  "accessing GTA Online servers with an altered version". ScriptHookV blocked it; don't rely on that.
  Check `idle`, ask the human to click, and use only the game's official offline modding launch option where available. See
  `knowledge/techniques/driving-real-games-safely.md`.
- **Input only goes to the game.** WinDrive refuses to send while another app is in the foreground. The one
  exception is when nothing is and the cursor is over the game, which windowed games cause by dropping the
  foreground on clicks.
- **The user may be at the PC.** If `idle` is under a minute, ask before driving, and keep sessions short.
  Unattended runs are fine once the user says so.
- **Screenshots cost tokens.** Look at `--scale 0.33` copies. Multiply coordinates back ×3 for clicks, and
  keep a table of menu click points in MODLOG.md, measured once.
- **Why gfxcapture:** GPU-rendered games come out black with GDI capture. gfxcapture (Windows.Graphics.Capture)
  grabs one window's real frames, even when covered. It can't capture minimized windows.
