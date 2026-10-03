"""Verify an installed wheel outside the checkout. Run with that environment's Python."""
import json
import tempfile
from pathlib import Path

from um import resources
from um.service import Service
from check_docs import check_skill_tree


def main():
    for kind in resources.KINDS:
        assert "data" in resources.root(kind).parts, "resources resolved to a checkout, not the wheel"
    assert "Mod any game" in resources.read("skills", "mod-any-game/SKILL.md")
    assert not check_skill_tree(resources.root("skills")), "Installed skill links or entry metadata are invalid"
    assert "anime-strategy-mod/SKILL.md" in resources.read("skills", "README.md")
    assert "ck3" in resources.read("skills", "anime-strategy-mod/references/targets.md")
    assert (Path(__import__("um").__file__).parent / "ps1/WinDrive.ps1").is_file()
    with tempfile.TemporaryDirectory() as directory:
        service = Service(directory)
        assert len(service.invoke("game_profiles").data["profiles"]) == 4
        assert service.invoke("knowledge_search", {"query": "terraria"}).data["matches"]
        args = {"collection": "knowledge", "path": "games/gta-v/minecraft-passthrough.md"}
        first = service.invoke("manual_read", args | {"max_lines": 40})
        assert first.ok and first.data["next_line"] == 41
        assert service.invoke("manual_read", args).data["text"].startswith(first.data["text"])
        # Export must keep sibling drawers and optional Codex metadata usable without symlinks.
        exported = service.invoke("manuals_export", {"destination": "manuals"})
        assert exported.ok, exported.to_dict()
        for relative in ("mod-research/references/art-and-ui-sources.md",
                         "ui-mod/references/fonts-and-localization.md",
                         "file-mod/references/text-and-data.md",
                         "asset-pipeline/references/anime-assets.md"):
            read = service.invoke("manual_read", {"collection": "skills", "path": relative})
            assert read.ok, read.to_dict()
            assert read.data["text"] == (Path(directory) / "manuals/skills" / relative).read_text(encoding="utf-8")
        for name in ("mod-research", "ui-mod", "file-mod"):
            assert (Path(directory) / "manuals/skills" / name / "agents/openai.yaml").read_bytes() == (
                resources.root("skills") / name / "agents/openai.yaml").read_bytes()
        scoped = Service(directory, enabled_tools=("manual_read",))
        assert set(scoped.tools()) == {"manual_read"}
        assert scoped.invoke("project_create", {}).error.code == "unknown_tool"
        scoped.close()
        result = service.invoke("project_create", {"destination": "project", "profile": "ck3", "name": "wheel_test"})
        assert result.ok, result.to_dict()
        data = json.loads((Path(directory) / "project/project.json").read_text(encoding="utf-8"))
        assert data["profile"] == "ck3"
        assert (Path(directory) / "project" / data["asset_workflow"]).read_text(encoding="utf-8") == resources.read(
            "skills", "asset-pipeline/references/sourcing-and-psd.md")
        assert json.loads((Path(directory) / "project" / data["reference_manifest"]).read_text(encoding="utf-8"))["references"] == []
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
