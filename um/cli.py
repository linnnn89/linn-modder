"""`um` command line: one entry point for every tool, so skills can say `um <group> <cmd>`."""
from __future__ import annotations

import argparse
import importlib
import sys
import os

from um import __doc__ as DOC, __version__

# Keep discovery cheap; the selected group still owns its complete parser.
GROUPS = {
    "scan": "find installed games; fingerprint engine, anti-cheat, loaders, saves, routes",
    "fal": "generate assets with fal (sprites, textures, 3D, rigs, audio, video)",
    "sprite": "cut out, fit, pixelate, recolor and pack 2D sprites",
    "render3d": "render a GLB into sprite frames from a game's camera (Blender)",
    "video": "compile styled showcase videos, contact sheets, trim, mux",
    "win": "Windows/WSL: screenshots, recording with game-only audio, input, processes",
    "backup": "snapshot / diff / restore save folders before you touch them",
    "publish": "lint a mod folder before sharing (game files, decompiled code, secrets)",
    "kb": "knowledge base of how games were modded: search, write, check, PR",
    "doctor": "report dependencies and platform capabilities as JSON",
    "tool": "agent-neutral structured JSON interface",
    "mcp": "serve tools over MCP stdio",
}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    selected = argv[0] if argv and argv[0] in GROUPS else None
    # Redirected Windows stdio otherwise depends on the user's ANSI codepage.
    if os.name == "nt":
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="um", description=DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"linn-modder {__version__}")
    sub = ap.add_subparsers(dest="group", metavar="<group>")
    for group, help_text in GROUPS.items():
        if group == selected:
            importlib.import_module(f"um.{group}").register(sub)
        else:
            sub.add_parser(group, help=help_text)
    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        # a group without a command: show that group's help
        if args.group:
            ap.parse_args([args.group, "--help"])
        ap.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
