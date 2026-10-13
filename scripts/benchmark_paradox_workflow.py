"""Compare manual response volume and synthetic Paradox routing between two checkouts.

Measures JSON characters/UTF-8 bytes, not model tokens, latency or in-game behavior.
Both checkouts use the same interpreter. Requires the optional MCP dependency.
"""
import argparse
import datetime
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys


WORKER = r'''
import asyncio, inspect, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from um import scan
from um.mcp import create_server
from um.service import Service

with tempfile.TemporaryDirectory() as temp:
    service = Service(temp)
    async def catalog():
        return [t.model_dump(mode="json", exclude_none=True) for t in await create_server(service).list_tools()]
    report = {"catalog": asyncio.run(catalog()), "manuals": {}, "scans": {}}
    cases = [("ck3_portrait", "games/crusader-kings-iii/modding-playbook.md", "15."),
             ("ck3_old_save", "games/crusader-kings-iii/modding-playbook.md", "24."),
             ("vic2_map", "games/victoria-2/south-central-gang-total-conversion.md", "Map files"),
             ("vic2_gotchas", "games/victoria-2/south-central-gang-total-conversion.md", "Gotchas")]
    def read(args):
        result = service.invoke("manual_read", args)
        assert result.ok, result.to_dict()
        return result.to_dict()
    for name, path, heading in cases:
        args = {"collection": "knowledge", "path": path}
        entry = {"full": read(args)}
        if "outline" in inspect.signature(service.manual_read).parameters:
            outline = read(args | {"outline": True})
            section = next(s for s in outline["data"]["sections"] if s["heading"].startswith(heading))
            start, end = section["start_line"], section["end_line"]
            page = read(args | {"start_line": start, "max_lines": end - start + 1})
            assert page["data"]["text"] == "".join(entry["full"]["data"]["text"].splitlines(keepends=True)[start - 1:end])
            entry.update(section=section, outline=outline, page=page, opening=read(args | {"max_lines": 60}))
        report["manuals"][name] = entry
    scan.all_games = lambda: []
    scan.win_folders = lambda: {}
    for name, directories, files in (
        ("root_layout", ("common", "events"), ("launcher-settings.json",)),
        ("game_layout_root_launcher", ("game/common", "game/events"), ("launcher-settings.json",)),
        ("game_layout_nested_launcher", ("game/common", "game/events"), ("launcher/launcher-settings.json",)),
        ("legacy_vic2", ("common", "events"), ("v2game.exe",)),
    ):
        folder = Path(temp) / name
        for directory in directories:
            (folder / directory).mkdir(parents=True, exist_ok=True)
        for file in files:
            path = folder / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fixture")
        result = service.invoke("game_scan", {"path": name})
        assert result.ok, result.to_dict()
        report["scans"][name] = result.data["engine"]["key"]
    service.close()
print(json.dumps(report, ensure_ascii=False))
'''


def size(value):
    # Same serialization as MCP TextContent; do not count structuredContent a second time.
    text = json.dumps(value, ensure_ascii=False)
    return {"characters": len(text), "utf8_bytes": len(text.encode("utf-8"))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    roots = {"before": args.before.resolve(), "after": args.after.resolve()}
    probes = {key: json.loads(subprocess.check_output([sys.executable, "-c", WORKER, str(root)], cwd=root))
              for key, root in roots.items()}
    report = {"recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "python": sys.version, "mcp": version("mcp"),
              "unit": "JSON characters and UTF-8 bytes; no Token or timing estimate",
              "sources": {}, "fixed_context": {}, "manuals": {}, "catalog": {}, "scans": {}}
    for key, root in roots.items():
        report["sources"][key] = {
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
            "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root)),
            "implementation_sha256": {path: hashlib.sha256((root / path).read_bytes()).hexdigest()
                                      for path in ("um/resources.py", "um/service.py", "um/scan.py", "um/mcp.py")},
        }
        report["catalog"][key] = size(probes[key]["catalog"]) | {"tools": len(probes[key]["catalog"])}
        report["scans"][key] = probes[key]["scans"]
    for path in ("AGENTS.md", "skills/linn-modder/SKILL.md"):
        before, after = [(root / path).read_bytes() for root in roots.values()]
        report["fixed_context"][path] = {"unchanged": before == after, "utf8_bytes": len(after)}
    for name, after in probes["after"]["manuals"].items():
        before = probes["before"]["manuals"][name]
        assert before["full"] == after["full"], "Compare identical manual content and default response contracts"
        full = size(before["full"])
        warm = {unit: sum(size(after[part])[unit] for part in ("outline", "page")) for unit in full}
        cold = {unit: warm[unit] + size(after["opening"])[unit] for unit in full}
        report["manuals"][name] = {
            "path": after["full"]["data"]["path"], "section": after["section"],
            "manual_sha256": hashlib.sha256(after["full"]["data"]["text"].encode()).hexdigest(),
            "full": full, "outline_and_section": warm, "plus_first_60_lines": cold,
            "cold_reduction_pct": {unit: round(100 * (1 - cold[unit] / full[unit]), 2) for unit in full},
        }
    cases = report["manuals"].values()
    reductions = {unit: round(100 * (1 - sum(c["plus_first_60_lines"][unit] for c in cases) /
                                            sum(c["full"][unit] for c in cases)), 2)
                  for unit in ("characters", "utf8_bytes")}
    report["aggregate_cold_reduction_pct"] = reductions
    report["targets"] = {
        "cold_responses_at_least_40_pct_smaller_in_both_units": min(reductions.values()) >= 40,
        "fixed_context_unchanged": all(v["unchanged"] for v in report["fixed_context"].values()),
        "same_tool_count": report["catalog"]["before"]["tools"] == report["catalog"]["after"]["tools"],
        "all_four_layouts_routed": all(v == "clausewitz" for v in report["scans"]["after"].values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"aggregate_cold_reduction_pct": reductions, "catalog": report["catalog"],
                      "scans": report["scans"], "targets": report["targets"]}, indent=2))
    if not all(report["targets"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
