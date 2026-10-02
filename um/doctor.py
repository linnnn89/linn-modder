"""Read-only dependency checks; never installs software or opens a game."""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from um.common import is_windows, is_wsl


def inspect_environment() -> dict:
    from um import resources
    windows = is_windows() or is_wsl()
    ps = shutil.which("powershell.exe" if is_wsl() else "powershell")
    ffmpeg = os.environ.get("UM_FFMPEG_WIN") if windows else None
    ffmpeg = ffmpeg or shutil.which("ffmpeg")
    if not ffmpeg and is_windows():
        candidate = Path(os.environ.get("LOCALAPPDATA", "")) / "universal-modder/ffmpeg/bin/ffmpeg.exe"
        if candidate.is_file():
            ffmpeg = str(candidate)
    gfxcapture = False
    ffmpeg_error = None
    if ffmpeg:
        try:
            r = subprocess.run([ffmpeg, "-hide_banner", "-filters"], capture_output=True,
                               text=True, encoding="utf-8", errors="replace", timeout=10)
            gfxcapture = r.returncode == 0 and any(
                len(parts := line.split()) > 1 and parts[1] == "gfxcapture"
                for line in r.stdout.splitlines())
            if r.returncode:
                ffmpeg_error = f"ffmpeg exited with code {r.returncode}"
        except (OSError, subprocess.TimeoutExpired) as exc:
            ffmpeg_error = str(exc)
    collections = {kind: str(resources.root(kind)) for kind in resources.KINDS}
    return {
        "python": platform.python_version(), "platform": sys.platform,
        "windows": is_windows(), "wsl": is_wsl(),
        "dependencies": {"powershell": ps, "ffmpeg": ffmpeg,
                         "blender": os.environ.get("BLENDER") or shutil.which("blender")},
        "capabilities": {"core": True, "windows_input": windows and bool(ps),
                         "window_capture": windows and gfxcapture,
                         "gfxcapture": gfxcapture},
        "resources": collections, "ffmpeg_error": ffmpeg_error,
        "notes": ["Input requires an explicit --allow-input server configuration.",
                  "GPU capture and process audio require Windows runtime verification."]}


def register(sub):
    import json
    p = sub.add_parser("doctor", help="report dependencies and platform capabilities as JSON")
    p.set_defaults(func=lambda _: print(json.dumps(inspect_environment(), indent=2, ensure_ascii=False)))
