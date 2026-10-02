"""Compare two checkouts on one interpreter; no game or model-provider calls.

Run with --require-targets to accept only measured improvements. Timing thresholds
are for a controlled comparison, not a CI gate across unrelated runner machines.
"""
import argparse
import datetime
import hashlib
import json
import math
from importlib.metadata import version
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

AUTHORING = ["game_profiles", "manual_read", "project_create", "image_prepare", "backup_create"]
NOTE = "games/gta-v/minecraft-passthrough.md"
PROBE = r'''
import asyncio, json, sys, tempfile
from um.service import Service
from um.mcp import create_server
async def run():
    with tempfile.TemporaryDirectory() as workspace:
        service = Service(workspace, **({'enabled_tools': tuple(json.loads(sys.argv[2]))} if sys.argv[2] else {}))
        try:
            server = create_server(service)
            tools = await server.list_tools()
            args = {'collection': 'knowledge', 'path': sys.argv[3]}
            if sys.argv[1] == 'page': args['max_lines'] = 40
            result = await server.call_tool('manual_read', args)
            assert not result.isError
            pages = [result]
            if sys.argv[1] == 'page':
                while pages[-1].structuredContent['data']['next_line'] is not None:
                    args['start_line'] = pages[-1].structuredContent['data']['next_line']
                    page = await server.call_tool('manual_read', args)
                    assert not page.isError
                    pages.append(page)
                original = service.invoke('manual_read', {'collection': 'knowledge', 'path': sys.argv[3]})
                assert ''.join(p.structuredContent['data']['text'] for p in pages) == original.data['text']
            print(json.dumps({'catalog': [t.model_dump(mode='json', exclude_none=True) for t in tools],
                              'manual': result.model_dump(mode='json', exclude_none=True),
                              'pages': [p.model_dump(mode='json', exclude_none=True) for p in pages]}, ensure_ascii=False))
        finally: service.close()
asyncio.run(run())
'''


def run_at(root, args):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run([sys.executable, *args], cwd=root, env=env, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def revision(root):
    def git(*args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True).stdout
    diff = git("diff", "HEAD", "--", "um")
    digest = hashlib.sha256()
    for path in sorted((root / "um").rglob("*.py")):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes())
    return {"commit": git("rev-parse", "HEAD").decode().strip(),
            "runtime_diff_sha256": hashlib.sha256(diff).hexdigest(), "runtime_dirty": bool(diff),
            "python_sources_sha256": digest.hexdigest()}


def size(value, encodings):
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return {"utf8_bytes": len(text.encode("utf-8")),
            "tokens": {name: len(enc.encode(text, disallowed_special=())) for name, enc in encodings.items()}}


def reduction(before, after):
    return round((1 - after / before) * 100, 2)


def benchmark(before, after, runs, encodings):
    report = {"recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "platform": platform.platform(), "python": sys.version,
              "dependencies": {name: version(name) for name in ("mcp", "tiktoken") if name != "tiktoken" or encodings},
              "before": revision(before), "after": revision(after), "runs": runs,
              "method": "Fresh subprocesses, 2 warmups, alternating checkout order; same interpreter and workspace. "
                        "Token counts use compact MCP JSON, including compatibility text and structured results. "
                        "Opt-in comparisons change catalog/page scope; full behavior is also measured.",
              "timings": {}, "payloads": {}, "targets": {}}
    with tempfile.TemporaryDirectory() as workspace:
        cases = {"version": ["-m", "um", "--version"],
                 "game_profiles": ["-m", "um", "tool", "call", "game_profiles", "--workspace", workspace]}
        for name, args in cases.items():
            for root in (before, after):
                for _ in range(2): run_at(root, args)
            samples = {"before": [], "after": []}
            outputs = {}
            for n in range(runs):
                order = [("before", before), ("after", after)]
                if n % 2: order.reverse()
                for label, root in order:
                    start = time.perf_counter()
                    result = run_at(root, args)
                    samples[label].append((time.perf_counter() - start) * 1000)
                    outputs[label] = result.stdout
            if outputs["before"] != outputs["after"]:
                raise RuntimeError(f"{name}: output compatibility changed")
            stats = {label: {"median_ms": round(statistics.median(values), 3),
                             "p95_ms": round(sorted(values)[math.ceil(len(values) * .95) - 1], 3),
                             "samples_ms": [round(v, 3) for v in values]}
                     for label, values in samples.items()}
            gain = reduction(stats["before"]["median_ms"], stats["after"]["median_ms"])
            report["timings"][name] = stats | {"median_reduction_pct": gain, "stdout_identical": True}
            minimum = 50 if name == "version" else 20
            report["targets"][name] = {"minimum_reduction_pct": minimum, "actual_pct": gain, "passed": gain >= minimum}

    def probe(root, mode="full", names=None):
        return json.loads(run_at(root, ["-c", PROBE, mode, json.dumps(names) if names else "", NOTE]).stdout)
    old, new, scoped = probe(before), probe(after), probe(after, "page", AUTHORING)
    if old["manual"] != new["manual"]:
        raise RuntimeError("Default full manual response changed")
    for key, previous, current in (("default_catalog", old["catalog"], new["catalog"]),
                                   ("authoring_catalog", old["catalog"], scoped["catalog"]),
                                   ("manual_first_page", old["manual"], scoped["manual"])):
        a, b = size(previous, encodings), size(current, encodings)
        gains = {name: reduction(a["tokens"][name], b["tokens"][name]) for name in encodings}
        report["payloads"][key] = {"before": a, "after": b, "token_reduction_pct": gains,
                                  "byte_reduction_pct": reduction(a["utf8_bytes"], b["utf8_bytes"])}
        if key != "default_catalog":
            minimum = 50 if key == "authoring_catalog" else 60
            report["targets"][key] = {"minimum_reduction_pct": minimum, "actual_pct": gains,
                                      "passed": bool(gains) and all(v >= minimum for v in gains.values())}
    report["scope"] = {"default_tools_before": len(old["catalog"]), "default_tools_after": len(new["catalog"]),
                       "authoring_tools": AUTHORING, "manual": NOTE, "first_page_lines": 40,
                       "total_lines": scoped["manual"]["structuredContent"]["data"]["total_lines"],
                       "default_manual_identical": True, "pages_to_read_all": len(scoped["pages"])}
    page_sizes = [size(page, encodings) for page in scoped["pages"]]
    report["payloads"]["manual_all_pages_total"] = {
        "utf8_bytes": sum(p["utf8_bytes"] for p in page_sizes),
        "tokens": {name: sum(p["tokens"][name] for p in page_sizes) for name in encodings},
        "note": "Reading every page costs more requests and repeated metadata than one full read."}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--runs", type=int, default=25)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-targets", action="store_true")
    args = parser.parse_args()
    if args.runs < 5: parser.error("Use at least 5 samples; 25 recommended.")
    encodings = {}
    try:
        import tiktoken
        encodings = {name: tiktoken.get_encoding(name) for name in ("cl100k_base", "o200k_base")}
    except ImportError:
        if args.require_targets: parser.error("Token targets require tiktoken: uv run --with tiktoken ...")
    report = benchmark(args.before.resolve(), args.after.resolve(), args.runs, encodings)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"targets": report["targets"], "report": str(args.output)}, indent=2))
    if args.require_targets and not all(t["passed"] for t in report["targets"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
