"""Section discovery followed by existing range reads, including examples to ignore."""
import json
import subprocess
import sys

from um import resources
from um.service import Service


def test_outline_selects_exact_sections_without_example_or_metadata_headings(tmp_path, monkeypatch):
    lines = [
        "---", "# YAML comment", "title: Fixture", "---", "# 手册", "intro",
        "## Duplicate ###", "first", "### Detail", "````python", "# code",
        "```", "## still code", "~~~~", "````", "    # indented code",
        "~~~", "## tilde example", "~~~", "## Duplicate", "last", "# End",
    ]
    text = "\n".join(lines)  # no trailing newline
    (tmp_path / "note.md").write_text(text, encoding="utf-8")
    monkeypatch.setattr(resources, "root", lambda _: tmp_path)
    service = Service(tmp_path)
    args = {"collection": "knowledge", "path": "note.md"}
    result = service.invoke("manual_read", args | {"outline": True})
    assert result.ok, result.to_dict()
    assert "text" not in result.data
    assert result.data["total_lines"] == len(lines)
    sections = result.data["sections"]
    assert [(s["heading"], s["level"], s["start_line"], s["end_line"]) for s in sections] == [
        ("手册", 1, 5, 21), ("Duplicate", 2, 7, 19), ("Detail", 3, 9, 19),
        ("Duplicate", 2, 20, 21), ("End", 1, 22, 22),
    ]
    for section in sections:
        start, end = section["start_line"], section["end_line"]
        page = service.invoke("manual_read", args | {"start_line": start, "max_lines": end - start + 1})
        assert page.ok
        assert page.data["text"] == "".join(text.splitlines(keepends=True)[start - 1:end])
    assert service.invoke("manual_read", args).data == args | {"text": text}
    for extra in ({"max_lines": 10}, {"start_line": 2}, {"outline": "true"}, {"outline": 1}):
        invalid = service.invoke("manual_read", args | {"outline": True} | extra)
        assert invalid.error.code == "invalid_arguments"
    escaped = service.invoke("manual_read", args | {"outline": True, "path": "../outside.md"})
    assert escaped.error.code == "invalid_resource"


def test_outline_empty_plain_and_unclosed_examples():
    for text in ("", "plain\ntext", "```\n# unfinished example"):
        assert resources.outline(text) == []
    assert resources.outline("\ufeff---\n# metadata\n...\n## ###") == [
        {"heading": "", "level": 2, "start_line": 4, "end_line": 4}]


def test_outline_json_cli(tmp_path):
    args = {"collection": "skills", "path": "linn-modder/mod-any-game/references/engines/paradox.md", "outline": True}
    arguments = tmp_path / "args.json"
    arguments.write_text(json.dumps(args), encoding="utf-8-sig")
    result = subprocess.run([sys.executable, "-m", "um", "tool", "call", "manual_read",
                             "--workspace", str(tmp_path), "--args-file", str(arguments)],
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == Service(tmp_path).invoke("manual_read", args).to_dict()
