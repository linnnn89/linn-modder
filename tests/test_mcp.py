"""Protocol integration through the official client, including a real stdio subprocess."""
import asyncio
import base64
import json
import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("mcp")
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from um.mcp import create_server
from um.service import Service
from test_service import FakeWindows


def test_tools_have_named_arguments_and_structured_output(tmp_path):
    async def exercise():
        service = Service(tmp_path, windows=FakeWindows())
        server = create_server(service)
        tools = {t.name: t for t in await server.list_tools()}
        assert "window_input" not in tools
        assert all(t.outputSchema for t in tools.values())
        assert tools["project_create"].inputSchema["required"] == ["destination", "profile", "name"]
        failed = await server.call_tool("project_create", {"destination": "../bad", "profile": "ck3", "name": "test"})
        assert failed.isError
        assert failed.structuredContent["error"]["code"] == "path_outside_roots"
        shot = await server.call_tool("window_capture", {"hwnd": 42})
        assert not shot.isError
        image = next(c for c in shot.content if c.type == "image")
        assert base64.b64decode(image.data).startswith(b"\x89PNG")
        assert shot.structuredContent["artifacts"][1]["role"] == "preview"
        service.close()
    asyncio.run(exercise())


def test_stdio_session_survives_tool_errors_and_reads_resources(tmp_path):
    async def exercise():
        env = dict(os.environ)
        root = str(Path(__file__).resolve().parents[1])
        env["PYTHONPATH"] = root + os.pathsep + env.get("PYTHONPATH", "")
        params = StdioServerParameters(command=sys.executable,
                                      args=["-m", "um", "mcp", "serve", "--workspace", str(tmp_path)], env=env)
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                listed = await client.list_tools()
                assert "project_create" in [t.name for t in listed.tools]
                result = await client.call_tool("project_create", {"destination": "project", "profile": "ck3", "name": "anime"})
                assert not result.isError
                assert result.structuredContent["ok"]
                failed = await client.call_tool("project_create", {"destination": "project", "profile": "ck3", "name": "anime"})
                assert failed.isError
                profiles = await client.call_tool("game_profiles", {})
                assert len(profiles.structuredContent["data"]["profiles"]) == 4
                resource = await client.read_resource("um://workflow")
                assert "Linn Modder" in resource.contents[0].text
                guide = await client.read_resource("um://guide")
                assert resource.contents[0].text == guide.contents[0].text
                assert "anime-strategy-mod/GUIDE.md" in guide.contents[0].text
                topic = await client.call_tool("manual_read", {"collection": "skills",
                    "path": "linn-modder/ui-mod/GUIDE.md"})
                assert not topic.isError
                assert "references/layout-and-state.md" in topic.structuredContent["data"]["text"]
                reference = await client.call_tool("manual_read", {"collection": "skills",
                    "path": "linn-modder/anime-strategy-mod/references/targets.md"})
                assert not reference.isError
                assert "planning only" in reference.structuredContent["data"]["text"]
                # The new drawers remain readable through the same portable MCP contract.
                for path in ("linn-modder/mod-research/references/engine-and-file-sources.md",
                             "linn-modder/ui-mod/references/layout-and-state.md",
                             "linn-modder/file-mod/references/text-and-data.md"):
                    drawer = await client.call_tool("manual_read", {"collection": "skills", "path": path})
                    assert not drawer.isError
                    assert drawer.structuredContent["data"]["text"] == (
                        Path(root) / "skills" / path).read_text(encoding="utf-8")
                await client.send_ping()
    asyncio.run(asyncio.wait_for(exercise(), timeout=30))


def test_stdio_validation_matches_service_for_raw_json_arguments(tmp_path):
    async def exercise():
        service = Service(tmp_path)
        params = StdioServerParameters(command=sys.executable,
                                      args=['-m', 'um', 'mcp', 'serve', '--workspace', str(tmp_path)])
        cases = [('knowledge_search', {'query': 'terraria', 'limit': value})
                 for value in (True, '5', 5.0, None)]
        cases += [('project_create', {}), ('game_profiles', {'typo': True}),
                  ('game_scan', {'path': 7})]
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                tools = await client.list_tools()
                assert all(t.inputSchema['additionalProperties'] is False for t in tools.tools)
                for name, arguments in cases:
                    expected = service.invoke(name, arguments)
                    result = await client.call_tool(name, arguments)
                    assert result.isError, (name, arguments)
                    assert result.structuredContent == expected.to_dict(), (name, arguments)
                valid = await client.call_tool('game_profiles', {})
                assert valid.structuredContent == service.invoke('game_profiles').to_dict()
        service.close()
    asyncio.run(asyncio.wait_for(exercise(), timeout=30))


def test_stdio_allowlist_and_paged_manuals(tmp_path):
    async def exercise():
        params = StdioServerParameters(command=sys.executable,
            args=['-m', 'um', 'mcp', 'serve', '--workspace', str(tmp_path),
                  '--enable-tool', 'manual_read', '--enable-tool', 'game_profiles'])
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                listed = await client.list_tools()
                assert {t.name for t in listed.tools} == {'manual_read', 'game_profiles'}
                assert (await client.call_tool('project_create', {})).isError
                args = {'collection': 'knowledge', 'path': 'games/gta-v/minecraft-passthrough.md'}
                full = await client.call_tool('manual_read', args)
                first = await client.call_tool('manual_read', args | {'max_lines': 40})
                data = first.structuredContent['data']
                assert data['next_line'] == 41
                assert full.structuredContent['data']['text'].startswith(data['text'])
                assert json.loads(first.content[0].text) == first.structuredContent
                invalid = await client.call_tool('manual_read', args | {'max_lines': True})
                assert invalid.structuredContent['error']['code'] == 'invalid_arguments'
                await client.send_ping()
    asyncio.run(asyncio.wait_for(exercise(), timeout=30))
