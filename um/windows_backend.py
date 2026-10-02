"""Injectable Windows boundary, separated from application operations for offline tests."""
from pathlib import Path

from um import win
from um.common import is_windows, is_wsl
from um.contracts import ToolError


class WindowsBackend:
    def __init__(self):
        if not (is_windows() or is_wsl()):
            raise ToolError("unsupported_platform", "This operation needs native Windows or WSL.")
        self._drives = {}

    def list_windows(self) -> list[dict]:
        return win.processes()

    def capture(self, hwnd: int, destination: Path):
        win.shot(str(destination), hwnd=hwnd)

    def input(self, pid: int, command: str) -> str:
        if pid not in self._drives:
            if not any(p["Id"] == pid for p in self.list_windows()):
                raise ToolError("not_found", "PID does not have a visible window.")
            self._drives[pid] = win.Drive(pid=pid)
        try:
            return self._drives[pid].cmd(command, retry=False)
        except (OSError, RuntimeError):
            self._drives.pop(pid).close()
            raise

    def close(self):
        for drive in self._drives.values():
            drive.close()
        self._drives.clear()
