"""Verify an installed wheel outside the checkout. Run with that environment's Python."""
import json
import tempfile
from pathlib import Path

from um import resources
from um import tkeditor as legacy_tkeditor
from um.editors.heroes_vow import tkeditor
from um.service import Service
from check_docs import check_skill_tree


def main():
    assert legacy_tkeditor is tkeditor, "Legacy editor imports must use the packaged implementation"
    for kind in resources.KINDS:
        assert "data" in resources.root(kind).parts, "resources resolved to a checkout, not the wheel"
    assert "Mod any game" in resources.read("skills", "linn-modder/mod-any-game/GUIDE.md")
    assert not check_skill_tree(resources.root("skills")), "Installed skill links or entry metadata are invalid"
    assert "anime-strategy-mod/GUIDE.md" in resources.read("skills", "linn-modder/SKILL.md")
    assert len(list(resources.root("skills").rglob("SKILL.md"))) == 1
    assert "ck3" in resources.read("skills", "linn-modder/anime-strategy-mod/references/targets.md")
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
        for relative in ("linn-modder/mod-research/references/art-and-ui-sources.md",
                         "linn-modder/ui-mod/references/fonts-and-localization.md",
                         "linn-modder/file-mod/references/text-and-data.md",
                         "linn-modder/file-mod/references/tkeditor.md",
                         "linn-modder/asset-pipeline/references/anime-assets.md"):
            read = service.invoke("manual_read", {"collection": "skills", "path": relative})
            assert read.ok, read.to_dict()
            assert read.data["text"] == (Path(directory) / "manuals/skills" / relative).read_text(encoding="utf-8")
        skill_tree = Path(directory) / "manuals/skills"
        assert [p.relative_to(skill_tree).as_posix() for p in skill_tree.rglob("SKILL.md")] == ["linn-modder/SKILL.md"]
        assert (skill_tree / "linn-modder/agents/openai.yaml").read_bytes() == (
            resources.root("skills") / "linn-modder/agents/openai.yaml").read_bytes()
        for legacy, current in (("mod-any-game/SKILL.md", "linn-modder/mod-any-game/GUIDE.md"),
                                ("asset-pipeline/references/sourcing-and-psd.md", "linn-modder/asset-pipeline/references/sourcing-and-psd.md")):
            assert resources.read("skills", legacy) == resources.read("skills", current)
        scoped = Service(directory, enabled_tools=("manual_read",))
        assert set(scoped.tools()) == {"manual_read"}
        assert scoped.invoke("project_create", {}).error.code == "unknown_tool"
        scoped.close()
        result = service.invoke("project_create", {"destination": "project", "profile": "ck3", "name": "wheel_test"})
        assert result.ok, result.to_dict()
        data = json.loads((Path(directory) / "project/project.json").read_text(encoding="utf-8"))
        assert data["profile"] == "ck3"
        assert (Path(directory) / "project" / data["asset_workflow"]).read_text(encoding="utf-8") == resources.read(
            "skills", "linn-modder/asset-pipeline/references/sourcing-and-psd.md")
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
        # Exercise the moved editor through the installed Service, not checkout imports.
        source = Path(directory) / "tk-source"
        source.mkdir()
        original = b'[{"id":"WJ1","name":"Fixture","force":"35"}]'
        (source / "Hero.json").write_bytes(original)
        for operation, arguments in (
            ("tk_project", {"source": str(source), "destination": "tk-project"}),
            ("tk_index", {"source": "tk-project", "catalog": "wheel"}),
        ):
            result = service.invoke(operation, arguments)
            assert result.ok, result.to_dict()
        edit = {"catalog": "wheel", "table": "Hero", "record_id": "WJ1", "changes": {"force": "50"}}
        preview = service.invoke("tk_patch", edit)
        assert preview.ok, preview.to_dict()
        applied = service.invoke("tk_patch", edit | {"apply": True, "expected_sha256": preview.data["confirmation"]})
        assert applied.ok and applied.data["applied"], applied.to_dict()
        assert json.loads((Path(directory) / "tk-project/Hero.json").read_text(encoding="utf-8"))[0]["force"] == "50"
        assert (source / "Hero.json").read_bytes() == original
        assert Path(applied.data["backup"]).read_bytes() == original
        service.close()
    print("Installed wheel: resources, PowerShell, projects, backups and TKEditor edit round trip passed.")


if __name__ == "__main__":
    main()
