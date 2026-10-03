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
    entry.write_text(text.replace("Sample task", "界" * 512), encoding="utf-8")
    assert check_skill_tree(tmp_path) == []
    entry.write_text(text.replace("Sample task", "界" * 513), encoding="utf-8")
    assert any("1..512 characters" in problem for problem in check_skill_tree(tmp_path))
    entry.write_text(text + "界" * 3001, encoding="utf-8")
    assert any("3000 characters" in problem for problem in check_skill_tree(tmp_path))
    entry.write_text(text.replace("description:", "metadata: [invalid]\ndescription:"), encoding="utf-8")
    assert any("metadata must map" in problem for problem in check_skill_tree(tmp_path))
    entry.write_text(text.replace("description:", "metadata: [\ndescription:"), encoding="utf-8")
    assert any("invalid YAML" in problem for problem in check_skill_tree(tmp_path))


def test_single_entry_checker_rejects_nested_skills_and_unrouted_topics(tmp_path):
    folder = tmp_path / "sample"
    topic = folder / "ui-mod"
    topic.mkdir(parents=True)
    entry = folder / "SKILL.md"
    entry.write_text('---\nname: sample\ndescription: Modding\n---\nreferences/\n', encoding="utf-8")
    (tmp_path / "README.md").write_text('[Entry](sample/SKILL.md)\n', encoding="utf-8")
    (topic / "GUIDE.md").write_text('UI workflow\n', encoding="utf-8")
    assert any("topic missing" in problem for problem in check_skill_tree(tmp_path))
    with entry.open('a', encoding='utf-8') as stream:
        stream.write('[UI](ui-mod/GUIDE.md)\n')
    assert check_skill_tree(tmp_path) == []
    (topic / "SKILL.md").write_text('---\nname: ui-mod\ndescription: UI\n---\nreferences/\n', encoding="utf-8")
    problems = check_skill_tree(tmp_path)
    assert any("exactly one" in problem for problem in problems)
    assert any("nested SKILL.md" in problem for problem in problems)
