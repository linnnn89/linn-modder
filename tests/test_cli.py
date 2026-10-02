"""CLI loading and argument behavior; no external tools or games required."""
import json
import subprocess
import sys

import pytest

from um.cli import GROUPS, main


@pytest.mark.parametrize("group", GROUPS)
def test_every_group_can_load_its_help(group, capsys):
    with pytest.raises(SystemExit) as exited:
        main([group, "--help"])
    assert exited.value.code == 0
    assert f"um {group}" in capsys.readouterr().out


@pytest.mark.parametrize("args", [["--version"], ["--help"], ["scan", "--help"]])
def test_unrelated_modules_are_not_imported(args):
    code = """
import json, sys
from um.cli import main
try: main(json.loads(sys.argv[1]))
except SystemExit as exc:
    assert exc.code == 0
assert 'um.fal' not in sys.modules
assert 'um.mcp' not in sys.modules
assert 'um.service' not in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", code, json.dumps(args)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("args", [["invented"], ["--invented"], ["tool", "call"]])
def test_bad_arguments_remain_errors(args):
    with pytest.raises(SystemExit) as exited:
        main(args)
    assert exited.value.code == 2


def test_group_without_command_shows_its_own_help(capsys):
    with pytest.raises(SystemExit) as exited:
        main(["kb"])
    assert exited.value.code == 0
    assert "um kb" in capsys.readouterr().out


def test_profile_call_does_not_import_unrelated_backends(tmp_path):
    code = """
import sys
from um.service import Service
assert Service(sys.argv[1]).invoke('game_profiles').ok
for name in ('backup', 'kb', 'scan', 'doctor', 'win', 'fal'):
    assert 'um.' + name not in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_json_cli_tool_selection_and_configuration_error(tmp_path):
    command = [sys.executable, "-m", "um", "tool", "list", "--workspace", str(tmp_path), "--enable-tool"]
    valid = subprocess.run([*command, "game_profiles"], capture_output=True, text=True, encoding="utf-8")
    assert valid.returncode == 0
    assert [t["name"] for t in json.loads(valid.stdout)["data"]["tools"]] == ["game_profiles"]
    invalid = subprocess.run([*command, "invented"], capture_output=True, text=True, encoding="utf-8")
    assert invalid.returncode == 1
    assert json.loads(invalid.stdout)["error"]["code"] == "invalid_tools"
