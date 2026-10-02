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

    server = FastMCP(
        "linn-modder", lifespan=lifespan,
        instructions="Use game_profiles and manual_read before planning a mod. Game roots are read-only. "
                     "Projects and prepared images are staging artifacts; report in-game verification separately.")

    def adapt(name, fn):
        async def call(**arguments):
            result = await anyio.to_thread.run_sync(partial(service.invoke, name, arguments))
            value = result.to_dict()
            content = [TextContent(type="text", text=json.dumps(value, ensure_ascii=False))]
            for artifact in result.artifacts:
                if artifact.role == "preview" and artifact.media_type == "image/png" and artifact.size <= 4 * 1024 * 1024:
                    content.append(ImageContent(type="image", mimeType="image/png",
                                                data=base64.b64encode(Path(artifact.path).read_bytes()).decode("ascii")))
            return CallToolResult(content=content, structuredContent=value, isError=not result.ok)

        call.__name__ = name
        call.__doc__ = inspect.getdoc(fn)
        # Preserve each operation's named parameters: no opaque run(command) tool.
        call.__signature__ = inspect.signature(fn).replace(return_annotation=Annotated[CallToolResult, Result])
        return call

    read_only = {"environment_check", "game_profiles", "game_scan", "knowledge_search", "manual_read", "windows_list"}
    for name, fn in service.tools().items():
        server.tool(name=name, structured_output=True,
                    annotations=ToolAnnotations(readOnlyHint=name in read_only,
                                                destructiveHint=name == "window_input",
                                                openWorldHint=False))(adapt(name, fn))

    @server.resource("um://profiles", mime_type="application/json")
    def profiles_resource() -> str:
        return json.dumps(service.game_profiles().data, ensure_ascii=False)

    @server.resource("um://workflow", mime_type="text/markdown")
    def workflow_resource() -> str:
        from um.resources import read
        return read("skills", "mod-any-game/SKILL.md")

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
