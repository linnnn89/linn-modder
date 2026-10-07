"""Read-only executable discovery shared by diagnostics and runtime backends."""
import json
import os
import shutil
import subprocess
from pathlib import Path

from um.common import ps_exe, to_posix


def find_ffmpeg(*, windows: bool, wsl: bool = False) -> str | None:
    if not (windows or wsl):
        return shutil.which('ffmpeg')
    override = os.environ.get('UM_FFMPEG_WIN')
    if override and Path(to_posix(override)).is_file():
        return to_posix(override) if wsl else override
    local, on_path = os.environ.get('LOCALAPPDATA'), None
    if wsl:
        # Query the Windows environment, not the Linux PATH. No directories are created.
        script = ("[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false); "
                  "@{local=[Environment]::GetFolderPath('LocalApplicationData'); "
                  "ffmpeg=(Get-Command ffmpeg.exe -ErrorAction SilentlyContinue).Source} | ConvertTo-Json -Compress")
        try:
            result = subprocess.run([ps_exe(), '-NoProfile', '-NonInteractive', '-Command', script],
                                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                local, on_path = data.get('local'), data.get('ffmpeg')
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return None
    else:
        on_path = shutil.which('ffmpeg')
    candidates = []
    if local:
        candidates.append(str(Path(to_posix(local)) / 'universal-modder/ffmpeg/bin/ffmpeg.exe'))
    if on_path:
        candidates.append(to_posix(on_path) if wsl else on_path)
    return next((candidate for candidate in candidates if Path(candidate).is_file()), None)


def probe_ffmpeg(path: str) -> dict:
    try:
        result = subprocess.run([path, '-hide_banner', '-filters'], capture_output=True,
                                text=True, encoding='utf-8', errors='replace', timeout=10)
        if result.returncode:
            return {'gfxcapture': False, 'error': f'ffmpeg exited with code {result.returncode}'}
        filters = [line.split() for line in result.stdout.splitlines()]
        return {'gfxcapture': any(len(parts) > 1 and parts[1] == 'gfxcapture' for parts in filters), 'error': None}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'gfxcapture': False, 'error': str(exc)}
