"""Windows-specific syntax and adapter checks without controlling a real window."""
import os
import queue
import subprocess
from pathlib import Path

import pytest

from um import dependencies, doctor, win


def test_doctor_does_not_mistake_an_error_for_gfxcapture(monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda _: "fixture-tool")
    monkeypatch.setattr(dependencies.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, "Unknown filter 'gfxcapture'", ""))
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


def test_diagnostics_and_capture_choose_the_same_installed_ffmpeg(tmp_path, monkeypatch):
    on_path = tmp_path / 'path-ffmpeg.exe'; on_path.touch()
    installed = tmp_path / 'appdata/universal-modder/ffmpeg/bin/ffmpeg.exe'
    installed.parent.mkdir(parents=True); installed.touch()
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'appdata'))
    monkeypatch.delenv('UM_FFMPEG_WIN', raising=False)
    for module in (doctor, win):
        monkeypatch.setattr(module, 'is_windows', lambda: True)
        monkeypatch.setattr(module, 'is_wsl', lambda: False)
    monkeypatch.setattr(dependencies.shutil, 'which', lambda name: str(on_path) if name == 'ffmpeg' else None)
    probed = []
    def probe(command, **kwargs):
        probed.append(command[0])
        return subprocess.CompletedProcess(command, 0, ' ... gfxcapture |->V Capture window\n', '')
    monkeypatch.setattr(dependencies.subprocess, 'run', probe)
    state = doctor.inspect_environment()
    assert state['capabilities']['window_capture']
    assert state['dependencies']['ffmpeg'] == win.ffmpeg_win() == str(installed)
    assert probed == [str(installed)]
    monkeypatch.setenv('UM_FFMPEG_WIN', str(on_path))
    assert doctor.inspect_environment()['dependencies']['ffmpeg'] == win.ffmpeg_win() == str(on_path)


def test_missing_ffmpeg_probe_stays_read_only(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'missing'))
    monkeypatch.delenv('UM_FFMPEG_WIN', raising=False)
    monkeypatch.setattr(dependencies.shutil, 'which', lambda _: None)
    assert dependencies.find_ffmpeg(windows=True) is None
    assert not list(tmp_path.iterdir())


@pytest.mark.skipif(os.name != 'nt', reason='Native Windows directory junction')
def test_recursive_read_rejects_windows_junction(tmp_path):
    from um.contracts import ToolError
    from um.workspace import Workspace
    work = tmp_path / 'work'; work.mkdir()
    real = work / 'real'; real.mkdir()
    result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(work / 'linked'), str(real)],
                            capture_output=True, timeout=10)
    assert result.returncode == 0, result.stderr
    # Exercise Python 3.10 as well: Path.is_junction exists only from 3.12.
    with pytest.raises(ToolError, match='links/junctions'):
        Workspace(work).check_tree(work)

    from um.service import Service
    report = Service(work).invoke('game_scan', {'path': '.'})
    assert not report.ok and report.error.code == 'linked_tree'
