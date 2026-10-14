"""Game-scoped retrieval with original-file section ranges, not prose assertions."""
import asyncio
import json
import subprocess
import sys

from um import kb, resources
from um.service import Service


def test_search_filters_game_and_reads_exact_nested_sections(tmp_path, monkeypatch):
    text = "\n".join([
        "---", "game: Victoria 2", 'game_version: "3.04"', "date: 2026-10-14", "platform: windows", "---",
        "# Victoria II", "Evidence applies only to the reported build.", "## Setup", "paths",
        "## Map files", "provinces.bmp uses distinct colours.", "### Details", "```text",
        "## Example, not a heading", "```", "tail", "## Map files", "unrelated second section",
    ])
    (tmp_path / "vic2.md").write_text(text, encoding="utf-8")
    (tmp_path / "bannerlord.md").write_text('---\ngame: "Mount & Blade II"\n---\n# Map files\nprovinces.bmp\n', encoding="utf-8")
    monkeypatch.setattr(resources, "root", lambda _: tmp_path)
    service = Service(tmp_path)
    result = service.invoke("knowledge_search", {"query": "map provinces.bmp", "game": "Victoria 2"})
    assert result.ok, result.to_dict()
    assert [row["path"] for row in result.data["matches"]] == ["vic2.md"]
    match = result.data["matches"][0]
    assert match["game_version"] == "3.04" and match["date"] == "2026-10-14" and match["platform"] == "windows"
    assert (match["sections"][0]["start_line"], match["sections"][0]["end_line"]) == (11, 17)
    for section in match["sections"]:
        args = {"collection": "knowledge", "path": match["path"], "start_line": section["start_line"],
                "max_lines": section["end_line"] - section["start_line"] + 1}
        page = service.invoke("manual_read", args)
        assert page.ok and page.data["text"] == "".join(text.splitlines(keepends=True)[section["start_line"] - 1:section["end_line"]])
    assert all("Example" not in s["heading"] for s in match["sections"])
    assert service.invoke("knowledge_search", {"query": "map", "game": "absent game"}).data["matches"] == []
    assert service.invoke("knowledge_search", {"query": "map", "game": 2}).error.code == "invalid_arguments"


def test_search_uses_parent_own_text_and_keeps_headingless_notes(tmp_path):
    (tmp_path / "nested.md").write_text('---\ngame: Fixture\ngames_also: [Second Game]\n---\n'
        '# Fixture\n## Issues\n### First\nrare_token\n### Second\nother\n', encoding="utf-8")
    row = kb.search(tmp_path, ["rare_token"], game="Second Game")[0]
    assert row["sections"] == [{"heading": "First", "level": 3, "start_line": 7, "end_line": 8}]
    assert row["game_version"] is None and row["date"] is None and row["platform"] is None
    (tmp_path / "plain.md").write_text("plain unique_token\n", encoding="utf-8")
    plain = kb.search(tmp_path, ["unique_token"])[0]
    assert plain["sections"] == [] and plain["hits"] == ["plain unique_token"]
    (tmp_path / "ties.md").write_text("# Notes\n## Broad\ntie_token\nextra\ncontext\n## Focused\ntie_token\n", encoding="utf-8")
    ranked = kb.search(tmp_path, ["tie_token"])[0]["sections"]
    assert [s["heading"] for s in ranked] == ["Focused", "Broad"]
    # Existing keys and JSON serialization still work when dates are YAML date objects.
    assert {"score", "path", "title", "game", "engine", "route", "status", "hits"} <= row.keys()
    json.dumps(row)


def test_search_cli_and_mcp_share_filter_and_ranges(tmp_path):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    args = {"query": "Victoria II localisation", "game": "Victoria 2", "limit": 2}
    service = Service(tmp_path)
    expected = service.invoke("knowledge_search", args).to_dict()
    assert len(expected["data"]["matches"]) == 1
    args_file = tmp_path / "args.json"
    args_file.write_text(json.dumps(args), encoding="utf-8-sig")
    run = subprocess.run([sys.executable, "-m", "um", "tool", "call", "knowledge_search", "--workspace", str(tmp_path),
                          "--args-file", str(args_file)], capture_output=True, text=True, encoding="utf-8")
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout) == expected
    async def exercise():
        params = StdioServerParameters(command=sys.executable, args=["-m", "um", "mcp", "serve", "--workspace", str(tmp_path),
                                                                  "--enable-tool", "knowledge_search", "--enable-tool", "manual_read"])
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                result = await client.call_tool("knowledge_search", args)
                assert result.structuredContent == expected
                match = expected["data"]["matches"][0]
                section = match["sections"][0]
                read_args = {"collection": "knowledge", "path": match["path"], "start_line": section["start_line"],
                             "max_lines": section["end_line"] - section["start_line"] + 1}
                page = await client.call_tool("manual_read", read_args)
                assert page.structuredContent == service.invoke("manual_read", read_args).to_dict()
    asyncio.run(asyncio.wait_for(exercise(), timeout=30))
