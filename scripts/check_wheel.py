"""Verify an installed wheel outside the checkout. Run with that environment's Python."""
import json
import tempfile
from pathlib import Path

from um import resources
from um.service import Service


def main():
    for kind in resources.KINDS:
        assert "data" in resources.root(kind).parts, "resources resolved to a checkout, not the wheel"
    assert "Mod any game" in resources.read("skills", "mod-any-game/SKILL.md")
    assert (Path(__import__("um").__file__).parent / "ps1/WinDrive.ps1").is_file()
    with tempfile.TemporaryDirectory() as directory:
        service = Service(directory)
        assert len(service.invoke("game_profiles").data["profiles"]) == 4
        assert service.invoke("knowledge_search", {"query": "terraria"}).data["matches"]
        result = service.invoke("project_create", {"destination": "project", "profile": "ck3", "name": "wheel_test"})
        assert result.ok, result.to_dict()
        data = json.loads((Path(directory) / "project/project.json").read_text(encoding="utf-8"))
        assert data["profile"] == "ck3"
        service.close()
    print("Installed wheel: profiles, manuals, knowledge, PowerShell and project creation passed.")


if __name__ == "__main__":
    main()
