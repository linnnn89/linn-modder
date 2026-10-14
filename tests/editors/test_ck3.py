"""CK3 checks on synthetic text and author-format Tiger JSON; no validator or game."""
import asyncio
import codecs
import json
import subprocess
import sys

import pytest

from um import resources
from um.service import Service


def write(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8-sig"))
    return path


def check(service, **arguments):
    result = service.invoke("ck3_check", {"source": "mod"} | arguments)
    assert result.ok, result.to_dict()
    return result.data


def test_scaffold_and_replace_localization_round_trip(tmp_path):
    service = Service(tmp_path)
    assert service.invoke("project_create", {"destination": "project", "profile": "ck3", "name": "example"}).ok
    root = tmp_path / "project/mod/example"
    write(root, "localization/replace/test_l_simp_chinese.yml", '\n# note\nl_simp_chinese: # header\n test:0 "你好"')
    before = {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    result = check(service, source="project/mod/example")
    assert result["passed"] and result["total"] == 0
    assert result["files_checked"] == 4
    assert result["verification"] == "not-tested-in-game"
    assert result["tiger"]["status"] == "not-provided"
    assert before == {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_reports_all_local_faults_with_exact_lines_and_pagination(tmp_path):
    root = tmp_path / "mod"
    write(root, "descriptor.mod", "# only comments\n")
    write(root, "localization/a_l_english.yml", b'l_english:\n a:0 "Hello"\n')
    write(root, "localization/b_l_english.yml", '# note\nl_simp_chinese:\n b:0 "Hi"')
    write(root, "localization/c_l_english.yml", '\n# comment\n missing:0 "Header"')
    write(root, "localization/d_l_english.yaml", 'l_english:\n d:0 "Suffix"')
    write(root, "localization/e_l_english.yml", codecs.BOM_UTF8 + b'l_english:\n\xff')
    service = Service(tmp_path)
    first = check(service, limit=2)
    assert not first["passed"] and first["counts"] == {"error": 6}
    items = first["diagnostics"]
    offset = first["next_offset"]
    while offset is not None:
        page = check(service, limit=2, offset=offset)
        assert page["total"] == 6 and not page["passed"]
        items.extend(page["diagnostics"])
        offset = page["next_offset"]
    assert [(d["code"], d["locations"][0]["line"]) for d in items] == [
        ("empty_descriptor", 1), ("missing_bom", 1), ("localization_language", 2),
        ("localization_header", 3), ("localization_filename", None), ("invalid_utf8", 2)]
    assert all((root / d["locations"][0]["path"]).is_file() for d in items)
    write(root, "descriptor.mod", 'name="Fixed"')
    for name in ("a", "b", "c", "e"):
        write(root, f"localization/{name}_l_english.yml", f'l_english:\n {name}:0 "Fixed"')
    (root / "localization/d_l_english.yaml").rename(root / "localization/d_l_english.yml")
    assert check(service)["passed"]


def test_tiger_levels_multiple_locations_and_old_report_status(tmp_path):
    write(tmp_path, "mod/descriptor.mod", 'name="Fixture"')
    reports = [{"severity": severity, "key": "test-fixture", "message": "Synthetic diagnostic",
                "confidence": "strong", "info": "Context", "locations": [
                    {"path": "events/test.txt", "linenr": 12, "column": 3, "line": "not a line number",
                     "from": "mod", "tag": "first definition", "fullpath": "C:/fixture/events/test.txt"},
                    {"path": "../never-read.txt", "linenr": None, "column": None, "from": "base"}]}
               for severity in ("fatal", "warning", "tips")]
    write(tmp_path, "report.json", json.dumps(reports))
    data = check(Service(tmp_path), tiger_report="report.json", limit=1)
    assert not data["passed"] and data["counts"] == {"fatal": 1, "warning": 1, "tips": 1}
    assert data["total"] == 3 and data["next_offset"] == 1
    diag = data["diagnostics"][0]
    assert diag["source"] == "tiger" and diag["confidence"] == "strong"
    assert diag["locations"][0]["line"] == 12 and diag["locations"][0]["tag"] == "first definition"
    assert diag["locations"][1]["path"] == "../never-read.txt"
    assert data["tiger"]["freshness"] == "not-verified" and len(data["tiger"]["sha256"]) == 64
    write(tmp_path, "report.json", "[]")
    empty = check(Service(tmp_path), tiger_report="report.json")
    assert empty["passed"] and empty["tiger"]["freshness"] == "not-verified"
    assert "script_semantics" in empty["not_checked"]


def test_severity_filter_preserves_global_failure_and_pages_only_matches(tmp_path):
    write(tmp_path, "mod/descriptor.mod", "# empty: one local error")
    reports = [{"severity": severity, "key": severity, "message": "Synthetic diagnostic", "locations": [
                    {"path": "events/test.txt", "linenr": i + 1, "column": 3},
                    {"path": "common/other.txt", "linenr": None, "column": None}]}
               for i, severity in enumerate(("tips", "untidy", "warning", "error", "fatal"))]
    write(tmp_path, "report.json", json.dumps(reports))
    service = Service(tmp_path)
    all_data = check(service, tiger_report="report.json")
    assert "matched_total" not in all_data and "min_severity" not in all_data
    for threshold in ("tips", "untidy", "warning", "error", "fatal"):
        levels = ("tips", "untidy", "warning", "error", "fatal")
        expected = [d for d in all_data["diagnostics"] if levels.index(d["severity"]) >= levels.index(threshold)]
        actual, offset = [], 0
        while offset is not None:
            page = check(service, tiger_report="report.json", min_severity=threshold, limit=1, offset=offset)
            assert page["min_severity"] == threshold and page["matched_total"] == len(expected)
            assert page["counts"] == all_data["counts"] and page["total"] == 6 and not page["passed"]
            actual.extend(page["diagnostics"])
            offset = page["next_offset"]
        assert actual == expected  # includes every original location and info field
    write(tmp_path, "report.json", "[]")
    empty = check(service, tiger_report="report.json", min_severity="fatal")
    assert empty["matched_total"] == 0 and empty["diagnostics"] == [] and empty["next_offset"] is None
    assert empty["counts"] == {"error": 1} and not empty["passed"]
    assert check(service, min_severity="error", offset=50)["diagnostics"] == []
    invalid = service.invoke("ck3_check", {"source": "mod", "min_severity": "errors"})
    assert invalid.error.code == "invalid_severity"


@pytest.mark.parametrize("raw", [b"", b"{}", b"[{\"severity\":\"unknown\"}]", "[]".encode("utf-16")])
def test_invalid_tiger_output_never_becomes_a_clean_report(tmp_path, raw):
    write(tmp_path, "mod/descriptor.mod", 'name="Fixture"')
    write(tmp_path, "report.json", raw)
    result = Service(tmp_path).invoke("ck3_check", {"source": "mod", "tiger_report": "report.json"})
    assert not result.ok and result.error.code == "invalid_tiger_report"


def test_read_only_roots_and_bounded_inputs(tmp_path, monkeypatch):
    from um.editors.ck3 import check as backend
    work = tmp_path / "work"
    work.mkdir()
    game = tmp_path / "game"
    path = write(game, "descriptor.mod", 'name="Fixture"')
    service = Service(work, (game,))
    assert check(service, source=str(game))["passed"]
    assert service.invoke("ck3_check", {"source": str(tmp_path)}).error.code == "path_outside_roots"
    assert service.invoke("ck3_check", {"source": str(game), "limit": True}).error.code == "invalid_arguments"
    monkeypatch.setattr(backend, "MAX_FILE", 4)
    assert service.invoke("ck3_check", {"source": str(game)}).error.code == "file_too_large"
    assert path.read_text(encoding="utf-8-sig") == 'name="Fixture"'


def test_missing_descriptor_and_localization_links(tmp_path):
    root = tmp_path / "mod"
    root.mkdir()
    service = Service(tmp_path)
    assert check(service)["diagnostics"][0]["code"] == "missing_descriptor"
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (root / "localization").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation needs Windows developer mode or privilege")
    assert service.invoke("ck3_check", {"source": "mod"}).error.code == "linked_tree"


def test_ck3_cli_and_real_stdio_using_packaged_configuration(tmp_path):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    write(tmp_path, "mod/descriptor.mod", "# empty: local error")
    arguments = {"source": "mod", "min_severity": "fatal"}
    write(tmp_path, "args.json", json.dumps(arguments))
    result = subprocess.run([sys.executable, "-m", "um", "tool", "call", "ck3_check", "--workspace", str(tmp_path),
                             "--args-file", str(tmp_path / "args.json")], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    expected = Service(tmp_path).invoke("ck3_check", arguments).to_dict()
    assert json.loads(result.stdout) == expected
    config = json.loads(resources.read("skills", "linn-modder/references/toolsets/ck3.json"))
    server_args = [str(tmp_path) if v == "<ABSOLUTE_WORKSPACE>" else v for v in config["mcpServers"]["linn-modder"]["args"]]
    async def exercise():
        params = StdioServerParameters(command=sys.executable, args=["-m", "um", *server_args])
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                tools = {t.name: t for t in (await client.list_tools()).tools}
                assert not any(name.startswith("tk_") for name in tools)
                assert tools["ck3_check"].annotations.readOnlyHint
                assert tools["ck3_check"].inputSchema["properties"]["min_severity"]["enum"] == ["", "tips", "untidy", "warning", "error", "fatal"]
                response = await client.call_tool("ck3_check", arguments)
                assert response.structuredContent == expected
    asyncio.run(asyncio.wait_for(exercise(), timeout=30))
