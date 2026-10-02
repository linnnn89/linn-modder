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
        saves = Path(directory) / "saves"
        saves.mkdir()
        (saves / "save.dat").write_bytes(b"fixture")
        snapshot = service.invoke("backup_create", {"source": "saves", "name": "wheel"})
        assert snapshot.ok, snapshot.to_dict()
        assert service.invoke("backup_verify", {"name": "wheel"}).data["valid"]
        restored = service.invoke("backup_restore", {"name": "wheel", "target": "restored", "apply": True})
        assert restored.ok, restored.to_dict()
        assert (Path(directory) / "restored/save.dat").read_bytes() == b"fixture"
        service.close()
    print("Installed wheel: resources, PowerShell, projects and backup round trip passed.")


if __name__ == "__main__":
    main()
