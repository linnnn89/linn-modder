"""Paired fixed retrieval workflows; measures calls and JSON volume, not autonomous agents.

Run once at acceptance with the same interpreter for both source checkouts.
Requires the optional MCP dependency for catalog measurement.
"""
import argparse
import asyncio
import datetime
import hashlib
import inspect
from importlib.metadata import version
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile


CK3 = "games/crusader-kings-iii/modding-playbook.md"
VIC2 = "games/victoria-2/south-central-gang-total-conversion.md"
# Fixed before implementation in docs/agent-usability-iteration.md.
TASKS = [
    ("ck3_3d", "Crusader Kings III", "3D 外貌", CK3, "15."),
    ("ck3_old_save", "Crusader Kings III", "旧档", CK3, "24."),
    ("ck3_dlc", "Crusader Kings III", "DLC 解析", CK3, "20."),
    ("vic2_map", "Victoria 2", "map provinces.bmp", VIC2, "Map files"),
    ("vic2_history", "Victoria 2", "replace_path", VIC2, "History loading"),
    ("vic2_localization", "Victoria 2", "localisation cp1252", VIC2, "Build steps"),
]


def encoded(value):
    return json.dumps(value, ensure_ascii=False)


def size(value):
    text = encoded(value)
    return {"characters": len(text), "utf8_bytes": len(text.encode("utf-8"))}


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def workflow(calls):
    return {"calls": len(calls), **{unit: sum(size(value)[unit] for value in calls)
                                    for unit in ("characters", "utf8_bytes")}}


def probe(root):
    sys.path.insert(0, str(root))
    from um import resources
    from um.mcp import create_server
    from um.service import Service
    assert Path(inspect.getfile(Service)).resolve().parent.parent == root
    with tempfile.TemporaryDirectory(prefix="linn-usability-") as temp:
        service = Service(temp)
        targeted = "game" in inspect.signature(service.knowledge_search).parameters
        async def catalog():
            return [t.model_dump(mode="json", exclude_none=True) for t in await create_server(service).list_tools()]
        output = {"catalog": asyncio.run(catalog()), "queries": {}}
        def call(name, args, calls):
            result = service.invoke(name, args)
            assert result.ok, result.to_dict()
            calls.append(result.to_dict())
            return result.data
        for name, game, query, path, heading in TASKS:
            calls = []
            args = {"query": query, "limit": 10}
            if targeted:
                args["game"] = game
            found = call("knowledge_search", args, calls)["matches"]
            match = next(row for row in found if row["path"] == path)
            read = {"collection": "knowledge", "path": path}
            if targeted:
                sections = match["sections"]
            else:
                sections = call("manual_read", read | {"outline": True}, calls)["sections"]
            rank, section = next((i + 1, s) for i, s in enumerate(sections) if s["heading"].startswith(heading))
            opening = call("manual_read", read | {"max_lines": 60}, calls)
            start, end = section["start_line"], section["end_line"]
            page = call("manual_read", read | {"start_line": start, "max_lines": end - start + 1}, calls)
            original = resources.read("knowledge", path)
            assert page["text"] == "".join(original.splitlines(keepends=True)[start - 1:end])
            output["queries"][name] = {"game": game, "query": query, "path": path,
                "section": section, "section_rank": rank if targeted else None,
                "matching_notes": len(found), "only_requested_game": all(row["game"] == game for row in found),
                "correct_section": True, "opening_sha256": digest(opening["text"]),
                "section_sha256": digest(page["text"]), "manual_sha256": digest(original),
                "workflow": workflow(calls)}

        mod = Path(temp) / "mod"
        mod.mkdir()
        (mod / "descriptor.mod").write_text('name="Synthetic fixture"\n', encoding="utf-8")
        def diagnostic(severity, key, line):
            return {"severity": severity, "key": key, "message": "Synthetic " + key,
                    "locations": [{"path": "events/test.txt", "linenr": line, "column": 1},
                                  {"path": "common/reference.txt", "linenr": 2, "column": 1}]}
        reports = [diagnostic("warning", "baseline-warning", 10) for _ in range(500)]
        reports.append(diagnostic("fatal", "target-fatal", 500))
        (Path(temp) / "tiger.json").write_text(encoded(reports), encoding="utf-8")
        args = {"source": "mod", "tiger_report": "tiger.json"}
        # Contract check is separate from the measured retrieval workflow.
        default = service.invoke("ck3_check", args).to_dict()
        default_hash = digest(encoded(default).replace(temp, "<WORKSPACE>"))
        if "min_severity" in inspect.signature(service.ck3_check).parameters:
            args["min_severity"] = "error"
        calls, fatal, offset = [], None, 0
        while fatal is None and offset is not None:
            page = call("ck3_check", args | {"offset": offset}, calls)
            fatal = next((d for d in page["diagnostics"] if d["severity"] == "fatal"), None)
            offset = page["next_offset"]
        assert fatal is not None and not page["passed"] and page["counts"] == {"warning": 500, "fatal": 1}
        output["diagnostics"] = {"workflow": workflow(calls), "counts": page["counts"], "total": page["total"],
            "passed": page["passed"], "fatal_sha256": digest(encoded(fatal)), "default_result_sha256": default_hash}
        service.close()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--before", type=Path)
    parser.add_argument("--after", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.worker:
        print(encoded(probe(args.worker.resolve())))
        return
    if not args.before or not args.output:
        parser.error("--before and --output are required")
    roots = {"before": args.before.resolve(), "after": args.after.resolve()}
    samples = {name: json.loads(subprocess.check_output([sys.executable, str(Path(__file__).resolve()), "--worker", str(root)],
                                                       cwd=root, text=True, encoding="utf-8"))
               for name, root in roots.items()}
    before, after = samples["before"], samples["after"]
    report = {"recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "python": sys.version, "mcp": version("mcp"), "sources": {}, "queries": {}, "catalog": {},
              "scope": "Fixed tool workflows, JSON TextContent counted once. No model usage, autonomous success rate or end-to-end timing measured."}
    for name, root in roots.items():
        report["sources"][name] = {
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
            "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root)),
            "implementation_sha256": {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in
                                      ("um/kb.py", "um/service.py", "um/resources.py", "um/editors/ck3/check.py", "um/mcp.py")}}
        report["catalog"][name] = size(samples[name]["catalog"]) | {"tools": len(samples[name]["catalog"])}
    def reduction(a, b):
        return {unit: round(100 * (1 - b[unit] / a[unit]), 2) for unit in ("calls", "characters", "utf8_bytes")}
    for name in after["queries"]:
        a, b = before["queries"][name], after["queries"][name]
        assert all(a[key] == b[key] for key in ("section", "opening_sha256", "section_sha256", "manual_sha256"))
        report["queries"][name] = {"before": a, "after": b, "reduction_pct": reduction(a["workflow"], b["workflow"])}
    a, b = before["diagnostics"], after["diagnostics"]
    assert a["fatal_sha256"] == b["fatal_sha256"] and a["default_result_sha256"] == b["default_result_sha256"]
    report["diagnostics"] = {"before": a, "after": b, "reduction_pct": reduction(a["workflow"], b["workflow"])}
    report["query_totals"] = {name: {unit: sum(q["workflow"][unit] for q in samples[name]["queries"].values())
                                  for unit in ("calls", "characters", "utf8_bytes")} for name in roots}
    report["query_total_reduction_pct"] = reduction(*report["query_totals"].values())
    report["catalog_growth_pct"] = round(100 * (report["catalog"]["after"]["characters"] / report["catalog"]["before"]["characters"] - 1), 2)
    old_tools, new_tools = [{t["name"]: t for t in sample["catalog"]} for sample in (before, after)]
    report["changed_tool_schemas"] = [name for name, tool in old_tools.items() if new_tools.get(name) != tool]
    report["targets"] = {
        "six_correct_sections_in_top_two": len(after["queries"]) == 6 and all(q["correct_section"] and q["section_rank"] <= 2 for q in after["queries"].values()),
        "game_filter_isolates_each_task": all(q["only_requested_game"] for q in after["queries"].values()),
        "median_query_calls_at_least_25_pct_less": statistics.median(q["reduction_pct"]["calls"] for q in report["queries"].values()) >= 25,
        "fatal_retrieved_in_one_call": b["workflow"]["calls"] == 1,
        "diagnostic_volume_at_least_80_pct_less": min(report["diagnostics"]["reduction_pct"][unit] for unit in ("characters", "utf8_bytes")) >= 80,
        "same_default_tools": old_tools.keys() == new_tools.keys(),
        "unrelated_tool_schemas_unchanged": set(report["changed_tool_schemas"]) <= {"knowledge_search", "ck3_check"},
        "fixed_context_unchanged": all((roots["before"] / path).read_bytes() == (roots["after"] / path).read_bytes()
                                       for path in ("AGENTS.md", "skills/linn-modder/SKILL.md")),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("query_total_reduction_pct", "diagnostics", "catalog", "catalog_growth_pct", "targets")}, indent=2))
    if not all(report["targets"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
