"""Application behavior on synthetic files; no installed games or network required."""
import codecs
import contextlib
import io
import json
import os
from pathlib import Path

import pytest
from PIL import Image

from um.contracts import ToolError
from um.service import Service
from um.workspace import Workspace


def call(service, operation, **args):
    result = service.invoke(operation, args)
    assert result.ok, result.to_dict()
    return result


def test_argument_errors_are_transport_independent(tmp_path):
    service = Service(tmp_path)
    for args in ({}, {"path": 10}, {"path": ".", "invented": True}):
        assert service.invoke("game_scan", args).error.code == "invalid_arguments"
    assert service.invoke("game_scan", []).error.code == "invalid_arguments"
    assert service.invoke("window_input", {}).error.code == "unknown_tool"
    assert service.invoke("knowledge_search", {"query": "x", "limit": True}).error.code == "invalid_arguments"


def test_workspace_traversal_and_read_only_game_roots(tmp_path):
    workspace = tmp_path / "work"
    game = tmp_path / "game"
    workspace.mkdir()
    game.mkdir()
    policy = Workspace(workspace, (game,))
    assert policy.path(game) == game
    with pytest.raises(ToolError, match="outside"):
        policy.path("../elsewhere")
    with pytest.raises(ToolError):
        policy.path(game / "mod.txt", write=True)
    nested = workspace / "installed"
    nested.mkdir()
    with pytest.raises(ToolError, match="read-only"):
        Workspace(workspace, (nested,)).path(nested / "x", write=True)


def test_symlink_escape_is_rejected(tmp_path):
    work = tmp_path / "work"
    outside = tmp_path / "outside"
    work.mkdir()
    outside.mkdir()
    try:
        (work / "escape").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation requires Windows developer mode or privilege")
    result = Service(work).invoke("project_create", {"destination": "escape/x", "profile": "ck3", "name": "test"})
    assert result.error.code == "path_outside_roots"
    assert not (outside / "x").exists()


@pytest.mark.parametrize("profile", ["ck3", "victoria2", "romance-of-the-three-kingdoms", "nobunagas-ambition"])
def test_game_specific_scaffolds(tmp_path, profile):
    service = Service(tmp_path)
    result = call(service, "project_create", destination="project", profile=profile, name="anime_test")
    project = tmp_path / "project"
    assert result.data["verification"] == "not-tested-in-game"
    manifest = json.loads((project / "project.json").read_text(encoding="utf-8"))
    assert manifest["profile"] == profile
    if profile == "ck3":
        loc = project / "mod/anime_test/localization/simp_chinese/anime_test_l_simp_chinese.yml"
        assert loc.read_bytes().startswith(codecs.BOM_UTF8)
        assert loc.read_text(encoding="utf-8-sig").startswith("l_simp_chinese:")
        assert (project / "mod/anime_test/descriptor.mod").is_file()
    elif profile == "victoria2":
        assert (project / "mod/anime_test/localisation").is_dir()
        assert not list(project.rglob("*.yml"))
        assert not (project / "mod/anime_test/descriptor.mod").exists()
    else:
        assert manifest["support"] == "planning-only"
        assert not (project / "mod").exists()
    before = (project / "project.json").read_bytes()
    assert not service.invoke("project_create", {"destination": "project", "profile": profile, "name": "another"}).ok
    assert (project / "project.json").read_bytes() == before


def test_real_scanner_on_synthetic_unity_tree(tmp_path):
    managed = tmp_path / "Game" / "Game_Data" / "Managed"
    managed.mkdir(parents=True)
    (managed / "Assembly-CSharp.dll").write_bytes(b"fixture")
    (tmp_path / "Game" / "UnityPlayer.dll").write_bytes(b"fixture")
    result = call(Service(tmp_path), "game_scan", path="Game")
    assert result.data["engine"]["key"] == "unity-mono"


def test_anime_image_preparation_preserves_alpha_and_source(tmp_path):
    original = tmp_path / "portrait.png"
    Image.new("RGBA", (20, 40), (255, 40, 60, 128)).save(original)
    before = original.read_bytes()
    service = Service(tmp_path)
    result = call(service, "image_prepare", source="portrait.png", output="prepared/portrait.png",
                  width=64, height=64, mode="contain", anchor="top")
    with Image.open(result.artifacts[0].path) as im:
        assert im.size == (64, 64)
        assert im.getpixel((0, 0))[3] == 0
        assert im.getpixel((32, 32))[3] == 128
    assert original.read_bytes() == before
    assert not result.data["engine_ready"]
    assert result.artifacts[0].sha256
    assert not service.invoke("image_prepare", {"source": "portrait.png", "output": "bad.png", "width": 9000, "height": 9000}).ok
    assert not (tmp_path / "bad.png").exists()


def test_backups_are_unique_and_do_not_pollute_stdout(tmp_path):
    (tmp_path / "saves").mkdir()
    (tmp_path / "saves/save.dat").write_bytes(b"original")
    service = Service(tmp_path)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        first = call(service, "backup_create", source="saves", name="test")
        second = call(service, "backup_create", source="saves", name="test")
    assert stdout.getvalue() == ""
    assert first.data["snapshot"] != second.data["snapshot"]
    assert service.invoke("backup_create", {"source": ".", "name": "test"}).error.code == "recursive_backup"
    assert not service.invoke("backup_create", {"source": "saves", "name": "../../escape"}).ok


def test_bundled_knowledge_and_resource_paths(tmp_path):
    service = Service(tmp_path)
    assert call(service, "knowledge_search", query="terraria").data["matches"]
    assert "Mod any game" in call(service, "manual_read", collection="skills", path="mod-any-game/SKILL.md").data["text"]
    assert not service.invoke("manual_read", {"collection": "skills", "path": "../../pyproject.toml"}).ok
    call(service, "manuals_export", destination="manuals")
    assert (tmp_path / "manuals/skills/mod-any-game/SKILL.md").is_file()
    assert not service.invoke("manuals_export", {"destination": "manuals"}).ok


class FakeWindows:
    def __init__(self):
        self.actions = []
        self.closed = False

    def list_windows(self):
        return [{"Id": 123, "Hwnd": 42, "ProcessName": "fixture"}]

    def capture(self, hwnd, destination):
        assert hwnd == 42
        destination.parent.mkdir(parents=True)
        Image.new("RGB", (1920, 1080), "pink").save(destination)

    def input(self, pid, command):
        self.actions.append((pid, command))
        return "ok"

    def close(self):
        self.closed = True


def test_windows_boundary_with_fake_backend(tmp_path):
    backend = FakeWindows()
    service = Service(tmp_path, allow_input=True, windows=backend)
    assert call(service, "windows_list").data["windows"][0]["Id"] == 123
    shot = call(service, "window_capture", hwnd=42)
    assert shot.data["preview_size"] == [1024, 576]
    assert [a.role for a in shot.artifacts] == ["output", "preview"]
    call(service, "window_input", pid=123, action="type", text="你好")
    assert backend.actions == [(123, "type 你好")]
    assert not service.invoke("window_input", {"pid": 123, "action": "type", "text": "hello\nfocus"}).ok
    assert not service.invoke("window_input", {"pid": 123, "action": "key", "key": "999"}).ok
    service.close()
    assert backend.closed


def test_input_is_not_exposed_by_default(tmp_path):
    backend = FakeWindows()
    service = Service(tmp_path, windows=backend)
    assert "window_input" not in service.tools()
    assert not service.invoke("window_input", {"pid": 123, "action": "focus"}).ok
    assert backend.actions == []


def test_unexpected_backend_failure_does_not_break_the_contract(tmp_path, monkeypatch):
    service = Service(tmp_path)
    def broken():
        raise AttributeError("simulated backend bug")
    monkeypatch.setattr(service, "environment_check", broken)
    result = service.invoke("environment_check")
    assert not result.ok
    assert result.error.code == "internal_error"
    assert service.invoke("game_profiles").ok


def test_json_cli_accepts_powershell_utf8_bom(tmp_path):
    import subprocess
    import sys
    arguments = tmp_path / 'args.json'
    arguments.write_text('{}', encoding='utf-8-sig')
    result = subprocess.run([sys.executable, '-m', 'um', 'tool', 'call', 'game_profiles',
                             '--workspace', str(tmp_path), '--args-file', str(arguments)],
                            capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['ok']
