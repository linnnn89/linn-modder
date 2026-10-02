# Linux and macOS automation

Read when working on a non-Windows desktop. Follow the user's requested scope and validation level.

## Linux and macOS
- **Linux (X11):** `xdotool search --name "Game" windowactivate --sync key Escape`, `xdotool mousemove
  --window $W 640 360 click 1`. Screenshots: `import -window $(xdotool search --name Game) shot.png`, or
  ffmpeg `x11grab`.
- **Linux (Wayland):** ydotool + `grim`. Proton games are Windows games under Wine: launch options
  (`WINEDLLOVERRIDES`, `PROTON_LOG=1`) go in Steam.
- **macOS:** `screencapture -l <windowid> shot.png` (window id via `GetWindowID` or AppleScript),
  `osascript` / `cliclick` for input. Input and screen recording need Accessibility and Screen Recording
  permission for the terminal.
