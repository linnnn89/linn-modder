"""Compare MCP discovery volume and existing schemas across two source checkouts."""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys


WORKER = r'''
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from um import resources
from um.mcp import create_server
from um.service import Service
async def main():
    service = Service('.')
    tools = await create_server(service).list_tools()
    report = {"default": [t.model_dump(mode="json", exclude_none=True) for t in tools], "toolsets": {}}
    folder = resources.root("skills") / "linn-modder/references/toolsets"
    for path in sorted(folder.glob("*.json")):
        args = json.loads(path.read_text())["mcpServers"]["linn-modder"]["args"]
        names = tuple(args[i + 1] for i, value in enumerate(args) if value == "--enable-tool")
        selected = Service('.', enabled_tools=names)
        tools = await create_server(selected).list_tools()
        assert {t.name for t in tools} == set(names)
        report["toolsets"][path.stem] = [t.model_dump(mode="json", exclude_none=True) for t in tools]
        selected.close()
    service.close()
    print(json.dumps(report, ensure_ascii=False))
asyncio.run(main())
'''


def measure(tools):
    text = json.dumps(tools, ensure_ascii=False)
    return {"tools": len(tools), "characters": len(text), "utf8_bytes": len(text.encode("utf-8"))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    roots = {"before": args.before.resolve(), "after": args.after.resolve()}
    probes = {k: json.loads(subprocess.check_output([sys.executable, "-c", WORKER, str(root)], cwd=root))
              for k, root in roots.items()}
    before, after = probes["before"], probes["after"]
    schemas = [{t["name"]: t for t in p["default"]} for p in (before, after)]
    preserved = all(schemas[1].get(name) == schema for name, schema in schemas[0].items())
    report = {"python": sys.version, "mcp": version("mcp"), "sources": {},
              "default": {k: measure(p["default"]) for k, p in probes.items()}, "toolsets": {},
              "existing_schemas_unchanged": preserved,
              "scope": "Serialized MCP catalog only; no model tokens, task completion time or game behavior measured."}
    for key, root in roots.items():
        digest = hashlib.sha256()
        for path in sorted((root / "um").rglob("*.py")):
            digest.update(path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes())
        report["sources"][key] = {
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
            "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root)),
            "python_sources_sha256": digest.hexdigest(),
        }
    for name, tools in after["toolsets"].items():
        value = measure(tools)
        value["names"] = [t["name"] for t in tools]
        value["reduction_vs_before_default_pct"] = round(100 * (1 - value["characters"] / report["default"]["before"]["characters"]), 2)
        report["toolsets"][name] = value
    report["fixed_context_unchanged"] = all((roots["before"] / path).read_bytes() == (roots["after"] / path).read_bytes()
        for path in ("AGENTS.md", "skills/linn-modder/SKILL.md"))
    report["targets"] = {
        "three_task_configs": set(report["toolsets"]) == {"ck3", "paradox", "tkeditor"},
        "each_config_at_least_40_pct_smaller_than_before_default": all(
            v["reduction_vs_before_default_pct"] >= 40 for v in report["toolsets"].values()),
        "preserve_existing_schemas": preserved,
        "fixed_context_unchanged": report["fixed_context_unchanged"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not all(report["targets"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
