"""MCP stdio transport using the official Python SDK (optional `mcp` extra)."""
import base64
import inspect
import json
from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from typing import Annotated

from um.contracts import Result
from um.service import Service


def create_server(service: Service):
    import anyio
    from mcp.server.fastmcp import FastMCP
    from mcp.types import CallToolResult, ImageContent, TextContent, ToolAnnotations

    @asynccontextmanager
    async def lifespan(_):
        try:
            yield {}
        finally:
            await anyio.to_thread.run_sync(service.close)

    async def execute(name, arguments):
        result = await anyio.to_thread.run_sync(partial(service.invoke, name, arguments))
        value = result.to_dict()
        content = [TextContent(type="text", text=json.dumps(value, ensure_ascii=False))]
        for artifact in result.artifacts:
            if artifact.role == "preview" and artifact.media_type == "image/png" and artifact.size <= 4 * 1024 * 1024:
                content.append(ImageContent(type="image", mimeType="image/png",
                                            data=base64.b64encode(Path(artifact.path).read_bytes()).decode("ascii")))
        return CallToolResult(content=content, structuredContent=value, isError=not result.ok)

    class ModderMCP(FastMCP):
        async def call_tool(self, name, arguments):
            # Preserve raw JSON types/unknown fields. FastMCP's default dispatch
            # coerces values before our strict, transport-independent validation.
            return await execute(name, arguments)

        async def list_tools(self):
            listed = await super().list_tools()
            for tool in listed:
                tool.inputSchema["additionalProperties"] = False
            return listed

    server = ModderMCP(
        "linn-modder", lifespan=lifespan,
        instructions="Read the unified entry at um://guide or um://workflow, then the relevant topic GUIDE.md "
                     "and current reference via manual_read when enabled. Game roots are read-only. "
                     "Report prepared art, format validation and in-game verification separately.")

    def adapt(name, fn):
        async def call(**arguments):
            return await execute(name, arguments)

        call.__name__ = name
        call.__doc__ = inspect.getdoc(fn)
        # Preserve each operation's named parameters: no opaque run(command) tool.
        call.__signature__ = inspect.signature(fn).replace(return_annotation=Annotated[CallToolResult, Result])
        return call

    read_only = {"environment_check", "game_profiles", "game_scan", "knowledge_search", "manual_read",
                 "backup_list", "backup_verify", "windows_list"}
    for name, fn in service.tools().items():
        server.tool(name=name, structured_output=True,
                    annotations=ToolAnnotations(readOnlyHint=name in read_only,
                                                destructiveHint=name in {"window_input", "backup_restore"},
                                                openWorldHint=False))(adapt(name, fn))

    @server.resource("um://profiles", mime_type="application/json")
    def profiles_resource() -> str:
        return json.dumps(service.game_profiles().data, ensure_ascii=False)

    @server.resource("um://workflow", mime_type="text/markdown")
    def workflow_resource() -> str:
        from um.resources import read
        return read("skills", "linn-modder/SKILL.md")

    @server.resource("um://guide", mime_type="text/markdown")
    def guide_resource() -> str:
        """Unified skill entry; topic guides and references are loaded on demand."""
        from um.resources import read
        return read("skills", "linn-modder/SKILL.md")

    return server


def main(args):
    from um.common import die
    from um.tool import make_service
    try:
        import mcp  # noqa: F401
    except ImportError:
        die('MCP support is optional. Install this checkout with: pip install ".[mcp]"; see README for uv tool installation.')
    service = make_service(args)
    try:
        create_server(service).run(transport="stdio")
    finally:
        service.close()


def register(sub):
    from um.tool import options
    p = sub.add_parser("mcp", help="serve tools over MCP stdio")
    commands = p.add_subparsers(dest="command", required=True)
    serve = commands.add_parser("serve")
    options(serve)
    serve.set_defaults(func=main)
