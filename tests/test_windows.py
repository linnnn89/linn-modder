"""Windows-specific syntax and adapter checks without controlling a real window."""
import os
import queue
import subprocess
from pathlib import Path

import pytest

from um import doctor, win


def test_doctor_does_not_mistake_an_error_for_gfxcapture(monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda _: "fixture-tool")
    monkeypatch.setattr(doctor.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, "Unknown filter 'gfxcapture'", ""))
    assert not doctor.inspect_environment()["capabilities"]["gfxcapture"]


def test_drive_timeout_closes_child():
    drive = object.__new__(win.Drive)
    drive._replies = queue.Queue()
    drive.timeout = 0.01
    closed = []
    drive.close = lambda: closed.append(True)
    with pytest.raises(RuntimeError, match="timed out"):
        drive._read()
    assert closed


@pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell compiler")
def test_windrive_compiles_and_exits_without_a_target():
    script = Path(win.__file__).parent / "ps1/WinDrive.ps1"
    result = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
                             "-Proc", "um_fixture_process_does_not_exist"], input="", capture_output=True,
                            text=True, encoding="utf-8", timeout=30)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ready no-window"
