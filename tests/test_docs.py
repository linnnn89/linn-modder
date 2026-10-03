"""Discovery regressions that would prevent agents from finding bounded entries."""
from scripts.check_docs import check_skill_tree


def test_skill_checker_catches_orphans_invalid_metadata_and_unspaced_entry_growth(tmp_path):
    folder = tmp_path / "sample"
    folder.mkdir()
    (folder / "references").mkdir()
    (folder / "references/task.md").write_text("detail", encoding="utf-8")
    entry = folder / "SKILL.md"
    text = '---\nname: sample\ndescription: Sample task\n---\n[Task](references/task.md)\n'
    entry.write_text(text, encoding="utf-8")
    index = tmp_path / "README.md"
    index.write_text("# Router\n", encoding="utf-8")
    assert any("missing from routing index" in problem for problem in check_skill_tree(tmp_path))
    index.write_text("[Sample](sample/SKILL.md)\n", encoding="utf-8")
    assert check_skill_tree(tmp_path) == []
    entry.write_text(text + "界" * 3001, encoding="utf-8")
    assert any("3000 characters" in problem for problem in check_skill_tree(tmp_path))
    entry.write_text(text.replace("description:", "metadata: [invalid]\ndescription:"), encoding="utf-8")
    assert any("metadata must map" in problem for problem in check_skill_tree(tmp_path))
    entry.write_text(text.replace("description:", "metadata: [\ndescription:"), encoding="utf-8")
    assert any("invalid YAML" in problem for problem in check_skill_tree(tmp_path))
