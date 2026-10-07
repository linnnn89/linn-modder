"""Read-only dependency checks; never installs software or opens a game."""
import os
import platform
import shutil
import sys
from pathlib import Path

from um.common import is_windows, is_wsl, ps_exe
from um.dependencies import find_ffmpeg, probe_ffmpeg


def inspect_environment() -> dict:
    from um import resources
    windows = is_windows() or is_wsl()
    ps = ps_exe()
    ps = ps if Path(ps).is_file() else shutil.which(ps)
    ffmpeg = find_ffmpeg(windows=is_windows(), wsl=is_wsl())
    probe = probe_ffmpeg(ffmpeg) if ffmpeg else {"gfxcapture": False, "error": None}
    gfxcapture, ffmpeg_error = probe["gfxcapture"], probe["error"]
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
