"""JSON CLI over the same operations exported through MCP."""
import inspect
import json
from pathlib import Path

from um.contracts import ErrorInfo, Result, ToolError
from um.service import Service


def options(parser):
    parser.add_argument("--workspace", default=".", help="existing writable staging workspace")
    parser.add_argument("--game-root", action="append", default=[], help="additional read-only game directory (repeatable)")
    parser.add_argument("--allow-input", action="store_true", help="enable Windows input after user consent")
    parser.add_argument("--enable-tool", action="append", default=None, metavar="NAME",
                        help="expose only named service tools (repeatable); default: all enabled tools")


def make_service(args) -> Service:
    return Service(args.workspace, tuple(args.game_root), allow_input=args.allow_input,
                   enabled_tools=None if args.enable_tool is None else tuple(args.enable_tool))


def main(args):
    service = None
    try:
        service = make_service(args)
        if args.command == "list":
            result = Result(True, {"tools": [{"name": name, "description": inspect.getdoc(fn),
                                               "signature": str(inspect.signature(fn))}
                                              for name, fn in service.tools().items()]})
        else:
            raw = Path(args.args_file).read_text(encoding="utf-8-sig") if args.args_file else args.args
            result = service.invoke(args.name, json.loads(raw))
    except (ValueError, OSError, ToolError) as exc:
        result = Result(False, error=ErrorInfo(getattr(exc, "code", "invalid_arguments"), str(exc)))
    finally:
        if service is not None:
            service.close()
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    if not result.ok:
        raise SystemExit(1)


def register(sub):
    p = sub.add_parser("tool", help="agent-neutral structured JSON interface")
    commands = p.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="list enabled service operations")
    options(listing)
    listing.set_defaults(func=main)
    call = commands.add_parser("call", help="call a service operation")
    call.add_argument("name")
    group = call.add_mutually_exclusive_group()
    group.add_argument("--args", default="{}", help="JSON object; use --args-file to avoid shell quoting")
    group.add_argument("--args-file", help="UTF-8 JSON argument file")
    options(call)
    call.set_defaults(func=main)
