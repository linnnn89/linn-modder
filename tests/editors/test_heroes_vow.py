"""Real temp JSON/SQLite/PNG workflows, with CLI and stdio MCP transport checks."""
import asyncio
import json
import subprocess
import sys
import os
import sqlite3
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from um.service import Service
from um import tkeditor


def fixture(tmp_path):
    game, work = tmp_path / "game", tmp_path / "work"
    game.mkdir()
    work.mkdir()
    rows = [{"id": "WJ100", "surname": "春原", "name": "芽衣", "icon": "0000",
             "force": "35", "description": "合成角色\n多行数据", "unknown": "retain/me;1"},
            {"id": "WJ101", "surname": "曹", "name": "操", "icon": "0001",
             "force": "70", "description": "x" * 20000, "unknown": "keep"}]
    (game / "Hero.json").write_bytes(json.dumps(rows, ensure_ascii=False).replace("\\n", "\n").encode("utf-8-sig"))
    (game / "DataInfo.json").write_text('[{"strProjectName":"fixture","strIDEnd":"7np1q"}]', encoding="utf-8")
    (game / "AssetBundlesImage").mkdir()
    (game / "AssetBundlesImage/image_fixture").write_bytes(b"not-a-real-bundle")
    return game, work, rows


def good(service, operation, **arguments):
    result = service.invoke(operation, arguments)
    assert result.ok, result.to_dict()
    return result


def test_agent_schema_constraints_keep_strict_dispatch(tmp_path):
    from um.mcp import create_server

    async def exercise():
        service = Service(tmp_path)
        server = create_server(service)
        tools = {t.name: t for t in await server.list_tools()}
        props = tools["tk_portraits"].inputSchema["properties"]
        assert props["mode"]["enum"] == ["strict", "contain", "cover"]
        assert props["intent"]["enum"] == ["new_option", "replace"]
        query = tools["tk_query"].inputSchema["properties"]
        assert query["limit"]["minimum"] == 1 and query["limit"]["maximum"] == 50
        assert query["catalog"]["pattern"] == "^[A-Za-z0-9_-]{1,64}$"
        assert "data.confirmation" in tools["tk_patch"].inputSchema["properties"]["expected_sha256"]["description"]
        for arguments, code in [({"table": "Hero", "limit": "5"}, "invalid_arguments"),
                                ({"table": "Hero", "limit": 51}, "invalid_page")]:
            result = await server.call_tool("tk_query", arguments)
            assert result.structuredContent["error"]["code"] == code
        service.close()
    asyncio.run(exercise())


def test_agent_recovery_round_trip_and_disabled_action(tmp_path):
    from um.mcp import create_server

    game, work, rows = fixture(tmp_path)
    service = Service(work, (game,))
    good(service, "tk_project", source=str(game), destination="project")
    good(service, "tk_index", source="project", catalog="edit")
    rows[0]["force"] = "36"
    (work / "project/Hero.json").write_text(json.dumps(rows), encoding="utf-8")
    result = service.invoke("tk_query", {"catalog": "edit", "table": "Hero"})
    recovery = result.data["recovery"]
    assert recovery == {"tool": "tk_index", "arguments": {"source": str(work / "project"), "catalog": "edit"}, "available": True}
    args_file = work / "query.json"
    args_file.write_text(json.dumps({"catalog": "edit", "table": "Hero"}), encoding="utf-8")
    cli = subprocess.run([sys.executable, "-m", "um", "tool", "call", "tk_query", "--workspace", str(work),
                          "--args-file", str(args_file)], capture_output=True, text=True, encoding="utf-8")
    assert cli.returncode == 1
    assert json.loads(cli.stdout)["data"]["recovery"] == recovery
    limited = Service(work, (game,), enabled_tools=("tk_query",))
    assert limited.invoke("tk_query", {"catalog": "edit", "table": "Hero"}).data["recovery"]["available"] is False
    limited.close()
    good(service, recovery["tool"], **recovery["arguments"])
    missing = service.invoke("tk_query", {"catalog": "edit", "table": "Unknown"})
    listing = missing.data["recovery"]
    assert any(row["table"] == "Hero" for row in good(service, listing["tool"], **listing["arguments"]).data["tables"])
    args = {"catalog": "edit", "table": "Hero", "record_id": "WJ100", "changes": {"force": "50"}}
    result = service.invoke("tk_patch", args | {"apply": True, "expected_sha256": "wrong"})
    recovery = result.data["recovery"]
    assert recovery["arguments"]["apply"] is False
    preview = good(service, recovery["tool"], **recovery["arguments"])
    good(service, "tk_patch", **args, apply=True, expected_sha256=preview.data["confirmation"])
    async def refresh():
        server = create_server(service)
        failed = await server.call_tool("tk_query", {"catalog": "edit", "table": "Hero"})
        action = failed.structuredContent["data"]["recovery"]
        assert failed.isError
        refreshed = await server.call_tool(action["tool"], action["arguments"])
        assert not refreshed.isError
    asyncio.run(refresh())
    assert good(service, "tk_query", catalog="edit", table="Hero", record_id="WJ100", fields="force").data["records"][0]["values"]["force"] == "50"
    denied = service.invoke("tk_patch", args | {"changes": {"icon": "changed"}})
    assert denied.error.code == "protected_field" and "recovery" not in denied.data
    assert json.loads((game / "Hero.json").read_text(encoding="utf-8-sig"), strict=False)[0]["force"] == "35"
    service.close()


def test_minimal_portrait_and_editing_toolsets(tmp_path):
    from um.mcp import create_server

    game, work, _ = fixture(tmp_path)
    portraits = ("manual_read", "tk_portraits", "tk_portrait_options", "tk_portrait_register")
    editing = ("manual_read", "tk_index", "tk_tables", "tk_query", "tk_read_field", "tk_project", "tk_patch")
    art = work / "art.png"
    Image.new("RGBA", (20, 30), (100, 80, 60, 255)).save(art)
    service = Service(work, enabled_tools=portraits)
    async def discover():
        listed = await create_server(service).list_tools()
        assert {tool.name for tool in listed} == set(portraits)
    asyncio.run(discover())
    pack = good(service, "tk_portraits", full="art.png", half="art.png", icon="art.png",
                mode="contain", destination="portrait", name="Fixture")
    assert pack.data["intent"] == "new_option" and pack.data["registered"]
    assert good(service, "tk_portrait_options").data["options"][0]["option_id"] == pack.data["option_id"]
    assert service.invoke("tk_patch", {}).error.code == "unknown_tool"
    service.close()
    service = Service(work, (game,), enabled_tools=editing)
    assert set(service.tools()) == set(editing)
    good(service, "tk_project", source=str(game), destination="edit")
    good(service, "tk_index", source="edit", catalog="edit")
    args = {"catalog": "edit", "table": "Hero", "record_id": "WJ100", "changes": {"force": "40"}}
    preview = good(service, "tk_patch", **args)
    assert good(service, "tk_patch", **args, apply=True, expected_sha256=preview.data["confirmation"]).data["applied"]
    assert service.invoke("tk_portraits", {}).error.code == "unknown_tool"
    service.close()


def test_index_stage_patch_and_real_transports(tmp_path):
    game, work, original = fixture(tmp_path)
    before = (game / "Hero.json").read_bytes()
    service = Service(work, (game,))
    good(service, "tk_index", source=str(game), catalog="source")
    assert good(service, "tk_tables", catalog="source").data["tables"] == [
        {"table": "DataInfo", "rows": 1}, {"table": "Hero", "rows": 2}]
    found = good(service, "tk_query", catalog="source", table="Hero", query="春原芽衣").data
    assert len(found["records"]) == 1
    assert found["records"][0]["record_id"] == "WJ100"
    long = good(service, "tk_query", catalog="source", table="Hero", record_id="WJ101").data
    assert len(long["records"][0]["values"]["description"]) == 513
    assert long["truncated"] == [{"record_id": "WJ101", "field": "description"}]
    text = good(service, "tk_read_field", catalog="source", table="Hero", record_id="WJ101", field="description").data
    assert text["text"] == "x" * 1000 and text["next_start"] == 1000
    ending = good(service, "tk_read_field", catalog="source", table="Hero", record_id="WJ101",
                  field="description", start=19000).data
    assert ending["text"] == "x" * 1000 and ending["next_start"] is None
    assert good(service, "tk_query", catalog="source", table="Hero", limit=1).data["next_offset"] == 1
    good(service, "tk_project", source=str(game), destination="project")
    assert not (work / "project/AssetBundlesImage").exists()
    good(service, "tk_index", source="project")
    args = dict(table="Hero", record_id="WJ100", changes={"force": "50", "name": "小芽衣"})
    preview = good(service, "tk_patch", **args).data
    assert not preview["applied"]
    assert (work / "project/Hero.json").read_bytes() == before
    result = good(service, "tk_patch", **args, apply=True, expected_sha256=preview["confirmation"])
    updated = json.loads((work / "project/Hero.json").read_text(encoding="utf-8"))
    assert updated == [original[0] | {"force": "50", "name": "小芽衣"}, original[1]]
    assert result.artifacts[1].role == "undo"
    assert (game / "Hero.json").read_bytes() == before
    assert open(result.data["backup"], "rb").read() == before
    assert service.invoke("tk_query", {"table": "Hero"}).error.code == "stale_catalog"

    # A real CLI subprocess must emit exactly one structured result with no data dump.
    cli = subprocess.run([sys.executable, "-m", "um", "tool", "call", "tk_query", "--workspace", str(work),
                          "--game-root", str(game), "--args", json.dumps({"catalog": "source", "table": "Hero",
                          "query": "芽衣", "fields": "id,name"})], capture_output=True, encoding="utf-8", check=True)
    assert json.loads(cli.stdout)["data"]["records"][0]["values"] == {"id": "WJ100", "name": "芽衣"}

    async def protocol():
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        parameters = StdioServerParameters(command=sys.executable, args=["-m", "um", "mcp", "serve",
            "--workspace", str(work), "--game-root", str(game)])
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                tools = {tool.name: tool for tool in (await client.list_tools()).tools}
                assert tools["tk_query"].annotations.readOnlyHint
                assert tools["tk_patch"].inputSchema["additionalProperties"] is False
                assert tools["tk_portrait_register"].inputSchema["required"] == ["pack"]
                invalid_pack = await client.call_tool("tk_portrait_register", {"pack": "../escape"})
                assert invalid_pack.isError
                assert invalid_pack.structuredContent["error"]["code"] == "path_outside_roots"
                query = await client.call_tool("tk_query", {"catalog": "source", "table": "Hero", "query": "芽衣"})
                assert not query.isError and len(query.structuredContent["data"]["records"]) == 1
                failed = await client.call_tool("tk_patch", {"catalog": "source", "table": "Hero", "record_id": "WJ100", "changes": []})
                assert failed.isError and failed.structuredContent["error"]["code"] == "invalid_changes"
                await client.send_ping()
    asyncio.run(asyncio.wait_for(protocol(), timeout=30))


def test_safety_boundaries_stale_sources_and_invalid_json(tmp_path):
    game, work, _ = fixture(tmp_path)
    service = Service(work, (game,))
    before = (game / "Hero.json").read_bytes()
    good(service, "tk_index", source=str(game))
    args = dict(table="Hero", record_id="WJ100", changes={"force": "50"})
    preview = good(service, "tk_patch", **args).data
    assert service.invoke("tk_patch", args | {"apply": True, "expected_sha256": preview["confirmation"]}).error.code == "path_outside_roots"
    assert service.invoke("tk_project", {"source": str(game), "destination": str(game / "project")}).error.code == "path_outside_roots"
    good(service, "tk_project", source=str(game), destination="project")
    good(service, "tk_index", source="project")
    assert service.invoke("tk_patch", args | {"apply": True}).error.code == "confirmation_required"
    # Identical JSON in another source cannot reuse a preview confirmation.
    assert service.invoke("tk_patch", args | {"apply": True, "expected_sha256": preview["confirmation"]}).error.code == "confirmation_required"
    for changes in ({"id": "oops"}, {"icon": "missing"}, {"unknown": "code()"}, {"force": "101"},
                    {"force": 50}, {"name": 'bad"quote'}, {"name": "x\x00"}, {"typo": "value"}):
        assert not service.invoke("tk_patch", args | {"changes": changes}).ok
    for arguments in ({"table": "Hero", "limit": True}, {"table": "Hero", "limit": 51},
                      {"table": "Hero", "fields": "*"}, {"table": "Hero;DROP TABLE records"},
                      {"table": "Hero", "catalog": "../escape"}):
        assert not service.invoke("tk_query", arguments).ok
    assert (work / "project/Hero.json").read_bytes() == before
    assert (game / "Hero.json").read_bytes() == before
    (work / "project/Hero.json").write_bytes(b'[{"id":"1","id":"2"}]')
    assert service.invoke("tk_index", {"source": "project"}).error.code == "invalid_json"
    assert service.invoke("tk_query", {"table": "Hero"}).error.code == "stale_catalog"
    (work / "project/Hero.json").write_bytes(b'[{"id":"1"},{"id":"1"}]')
    good(service, "tk_index", source="project", catalog="relationships")
    duplicated = good(service, "tk_query", table="Hero", catalog="relationships", record_id="1").data
    assert len(duplicated["records"]) == 2
    assert [row["row_index"] for row in duplicated["records"]] == [0, 1]
    assert service.invoke("tk_patch", {"table": "Hero", "catalog": "relationships", "record_id": "1", "changes": {"name": "test"}}).error.code == "ambiguous_record"
    (work / "project/Hero.json").write_bytes(before)
    assert good(service, "tk_query", table="Hero").data["records"]  # Failed rebuild preserved the previous DB.


def test_portrait_triplet_roundtrip_crop_names_and_no_overwrite(tmp_path):
    game, work, _ = fixture(tmp_path)
    service = Service(work, (game,))
    good(service, "tk_index", source=str(game))
    sizes = [(1000, 1400), (1024, 1024), (260, 340)]
    for slot, size in zip(("full", "half", "icon"), sizes):
        Image.new("RGBA", size, (255, 30, 80, 127)).save(work / (slot + ".png"))
    sources = dict(full="full.png", half="half.png", icon="icon.png")
    before = (work / "full.png").read_bytes()
    result = good(service, "tk_portraits", **sources, destination="pack", hero_id="WJ100", intent="replace")
    assert result.data["name"] == "春原芽衣" and not result.data["engine_ready"]
    for artifact, size in zip(result.artifacts, sizes):
        with Image.open(artifact.path) as im:
            assert im.format == "PNG" and im.size == size and im.getpixel((0, 0))[3] == 127
    assert (work / "full.png").read_bytes() == before
    assert service.invoke("tk_portraits", sources | {"destination": "pack", "name": "custom"}).error.code == "target_exists"
    assert service.invoke("tk_portraits", sources | {"destination": "other", "name": "wrong", "hero_id": "WJ100", "intent": "replace"}).error.code == "name_mismatch"
    assert service.invoke("tk_portraits", sources | {"destination": "other", "hero_id": "WJ100"}).error.code == "invalid_intent"
    game_before = (game / "Hero.json").read_bytes()
    additive = good(service, "tk_portraits", **sources, destination="new-option", name="春原芽衣")
    assert additive.data["intent"] == "new_option" and additive.data["hero_id"] == ""
    assert additive.data["name"].startswith("um_") and additive.data["name"] != "春原芽衣"
    assert not any(path.name == "春原芽衣.png" for path in (work / "new-option").rglob("*.png"))
    assert (game / "Hero.json").read_bytes() == game_before
    options = good(service, "tk_portrait_options", query="春原芽衣").data["options"]
    assert len(options) == 1 and options[0]["option_id"] == additive.data["option_id"]
    assert not options[0]["installed"]
    for name in ("../escape", "CON", "COM1", "bad.", "../", "x/y"):
        assert not service.invoke("tk_portraits", sources | {"destination": "bad", "name": name}).ok
    wrong = dict(full="icon.png", half="icon.png", icon="icon.png", destination="bad", name="custom")
    assert service.invoke("tk_portraits", wrong).error.code == "invalid_dimensions"
    assert not (work / "bad").exists()
    padded = good(service, "tk_portraits", **(wrong | {"destination": "padded", "mode": "contain"}))
    with Image.open(padded.artifacts[0].path) as im:
        assert im.size == (1000, 1400) and im.getpixel((0, 0))[3] == 0
    cropped = good(service, "tk_portraits", **(wrong | {"destination": "cropped", "mode": "cover"}))
    with Image.open(cropped.artifacts[0].path) as im:
        assert im.size == (1000, 1400) and im.getpixel((0, 0))[3] == 127


def test_portrait_normalized_dimensions_identity_and_name_limits(tmp_path):
    game, work, rows = fixture(tmp_path)
    service = Service(work, (game,))
    good(service, "tk_index", source=str(game))
    sources = dict(full="full.png", half="half.png", icon="icon.png", name="a" * 80)
    for slot, size in zip(("full", "half", "icon"), ((1000, 1400), (1024, 1024), (260, 340))):
        Image.new("RGBA", size, (10, 20, 30, 127)).save(work / (slot + ".png"))
    exif = Image.Exif()
    exif[274] = 6
    Image.new("RGBA", (1000, 1400)).save(work / "full.png", exif=exif)
    rejected = service.invoke("tk_portraits", sources | {"destination": "bad-size"})
    assert rejected.error and rejected.error.code == "invalid_dimensions"
    assert not (work / "bad-size").exists()
    Image.new("RGBA", (1400, 1000)).save(work / "full.png", exif=exif)
    result = good(service, "tk_portraits", **sources, destination="normalized")
    assert result.data["display_name"] == "a" * 80
    for artifact, item in zip(result.artifacts, result.data["files"]):
        with Image.open(artifact.path) as im:
            assert list(im.size) == item["size"]
            assert im.getexif().get(274, 1) == 1
    assert not service.invoke("tk_portraits", sources | {"destination": "too-long", "name": "a" * 81}).ok
    rows[1]["id"] = rows[0]["id"]
    (game / "Hero.json").write_text(json.dumps(rows), encoding="utf-8")
    good(service, "tk_index", source=str(game))
    ambiguous = service.invoke("tk_portraits", sources | {
        "destination": "ambiguous", "name": "", "intent": "replace", "hero_id": "WJ100"})
    assert ambiguous.error and ambiguous.error.code == "ambiguous_record"
    assert not (work / "ambiguous").exists()


def test_portrait_registration_failure_can_recover_without_recreating_files(tmp_path):
    _, work, _ = fixture(tmp_path)
    service = Service(work)
    for slot, size in zip(("full", "half", "icon"), ((1000, 1400), (1024, 1024), (260, 340))):
        Image.new("RGBA", size).save(work / (slot + ".png"))
    original_connect = sqlite3.connect

    class CommitFailure(sqlite3.Connection):
        def __exit__(self, exc_type, exc, tb):
            if exc_type is None:
                self.rollback()
                raise sqlite3.OperationalError("simulated commit failure")
            return super().__exit__(exc_type, exc, tb)

    def fail_commit(*args, **kwargs):
        kwargs["factory"] = CommitFailure
        return original_connect(*args, **kwargs)

    with patch.object(tkeditor.sqlite3, "connect", side_effect=fail_commit):
        failed = service.invoke("tk_portraits", dict(full="full.png", half="half.png", icon="icon.png",
                                                     destination="pack", name="可恢复头像"))
    assert not failed.ok and failed.error.code == "portrait_registration_failed"
    assert failed.data["recovery"] == {"tool": "tk_portrait_register", "arguments": {"pack": str(work / "pack")}}
    assert (work / "pack/portrait-pack.json").is_file()
    before = {p: p.read_bytes() for p in (work / "pack").rglob("*.png")}
    result = good(service, "tk_portrait_register", pack="pack")
    assert result.data["registered"]
    good(service, "tk_portrait_register", pack="pack")  # Idempotent recovery after an uncertain result.
    assert len(good(service, "tk_portrait_options").data["options"]) == 1
    assert before == {p: p.read_bytes() for p in before}
    changed = next(iter(before))
    changed.write_bytes(b"damaged")
    rejected = service.invoke("tk_portrait_register", {"pack": "pack"})
    assert rejected.error and rejected.error.code == "invalid_portrait_pack"
    changed.write_bytes(before[changed])
    manifest_path = work / "pack/portrait-pack.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"][0]["path"] = "../full.png"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert service.invoke("tk_portrait_register", {"pack": "pack"}).error.code == "invalid_portrait_pack"


def test_index_read_fast_path_keeps_strict_write_verification(tmp_path):
    game, work, _ = fixture(tmp_path)
    service = Service(work, (game,))
    good(service, "tk_project", source=str(game), destination="project")
    good(service, "tk_index", source="project")
    original_read = Path.read_bytes
    read_paths = []

    def observed_read(path):
        read_paths.append(path)
        return original_read(path)

    with patch.object(Path, "read_bytes", observed_read):
        data = good(service, "tk_query", table="Hero", record_id="WJ100").data
        good(service, "tk_read_field", table="Hero", record_id="WJ100", field="description")
    assert data["records"][0]["record_id"] == "WJ100" and read_paths == []
    target = work / "project/Hero.json"
    saved_stat = target.stat()
    baseline = target.read_bytes()
    args = dict(table="Hero", record_id="WJ100", changes={"force": "50"})
    preview = good(service, "tk_patch", **args).data
    target.write_bytes(baseline.replace(b'"35"', b'"36"'))
    os.utime(target, ns=(saved_stat.st_atime_ns, saved_stat.st_mtime_ns))
    result = service.invoke("tk_patch", args | {"apply": True, "expected_sha256": preview["confirmation"]})
    assert result.error and result.error.code == "stale_catalog"
    assert b'"36"' in target.read_bytes()
    # The previous catalog remains readable after restoring unchanged contents.
    target.write_bytes(baseline)
    assert good(service, "tk_query", table="Hero", record_id="WJ100").data["records"]
    # Old catalogs retain strict hash checks instead of requiring a destructive migration.
    old = tkeditor.catalog_path(service.workspace, "legacy")
    with sqlite3.connect(tkeditor.catalog_path(service.workspace, "default")) as source_con:
        with sqlite3.connect(old) as legacy:
            source_con.backup(legacy)
            legacy.execute("PRAGMA user_version=1")
    with patch.object(Path, "read_bytes", observed_read):
        read_paths.clear()
        good(service, "tk_query", table="Hero", catalog="legacy", record_id="WJ100")
    assert target in read_paths


def test_oversized_patch_preserves_project_and_index(tmp_path):
    source = tmp_path / 'source'; source.mkdir()
    original = b'[{"id":"1","name":"A","description":"x"}]'
    (source / 'Hero.json').write_bytes(original)
    service = Service(tmp_path)
    good(service, 'tk_project', source='source', destination='project')
    good(service, 'tk_index', source='project')
    args = dict(table='Hero', record_id='1', changes={'description': 'x' * 600})
    preview = good(service, 'tk_patch', **args)
    with patch.object(tkeditor, 'MAX_FILE', 512):
        failed = service.invoke('tk_patch', args | {'apply': True, 'expected_sha256': preview.data['confirmation']})
    assert failed.error.code == 'file_limit'
    assert (tmp_path / 'project/Hero.json').read_bytes() == original
    assert not (tmp_path / '.um/tkeditor/backups').exists()
    assert good(service, 'tk_query', table='Hero').data['records'][0]['values']['description'] == 'x'
    service.close()


def test_long_ids_rejected_at_index_and_in_legacy_catalog(tmp_path):
    source = tmp_path / 'source'; source.mkdir()
    path = source / 'Hero.json'
    path.write_text(json.dumps([{'id': 'x' * 200000, 'name': 'fixture'}]), encoding='utf-8')
    service = Service(tmp_path)
    assert service.invoke('tk_index', {'source': 'source'}).error.code == 'invalid_id'
    path.write_text(json.dumps([{'id': 'x' * 128, 'name': 'fixture'}]), encoding='utf-8')
    good(service, 'tk_index', source='source')
    assert good(service, 'tk_query', table='Hero', record_id='x' * 128).data['records']
    with sqlite3.connect(tkeditor.catalog_path(service.workspace, 'default')) as con:
        con.execute('UPDATE records SET record_id=?', ('x' * 200000,))
    result = service.invoke('tk_query', {'table': 'Hero', 'fields': 'name'})
    assert result.error.code == 'invalid_id'
    assert len(json.dumps(result.to_dict())) < 1000
    service.close()


def test_query_budget_includes_metadata_and_pages_without_missing_rows(tmp_path):
    source = tmp_path / 'source'; source.mkdir()
    fields = [f'text{i}' for i in range(8)]
    rows = [{'id': str(i), **dict.fromkeys(fields, '界' * 1000)} for i in range(20)]
    (source / 'Hero.json').write_text(json.dumps(rows), encoding='utf-8')
    service = Service(tmp_path)
    good(service, 'tk_index', source='source')
    offset, found = 0, []
    while offset is not None:
        data = good(service, 'tk_query', table='Hero', fields=','.join(fields), limit=50, offset=offset).data
        assert len(json.dumps(data, ensure_ascii=False)) <= 12000
        ids = [row['record_id'] for row in data['records']]
        assert ids
        assert all(item['record_id'] in ids for item in data['truncated'])
        found.extend(ids)
        next_offset = data['next_offset']
        assert next_offset is None or next_offset > offset
        offset = next_offset
    assert found == [str(i) for i in range(20)]
    service.close()


def test_first_query_record_cannot_bypass_budget(tmp_path):
    source = tmp_path / 'source'; source.mkdir()
    fields = [f'number{i}' for i in range(8)]
    # Numeric values are not text-truncated but still count toward the budget.
    rows = [{'id': '1', **dict.fromkeys(fields, 10 ** 2000)}]
    (source / 'Hero.json').write_text(json.dumps(rows), encoding='utf-8')
    service = Service(tmp_path)
    good(service, 'tk_index', source='source')
    result = service.invoke('tk_query', {'table': 'Hero', 'fields': ','.join(fields)})
    assert result.error.code == 'output_limit'
    assert good(service, 'tk_query', table='Hero', fields=fields[0]).data['records']
    service.close()
