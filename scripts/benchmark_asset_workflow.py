"""Measure existing per-image CLI vs a single Python Service session on synthetic PNGs.

This is a workflow comparison, not a new batch API or a before/after code speedup.
No network, model generation, PSD editing or game installation is involved.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

WORKER = """
import json, sys
from pathlib import Path
from um.service import Service
service = Service(sys.argv[1])
try:
    results = [service.invoke('image_prepare', job).to_dict()
               for job in json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))]
    assert all(r['ok'] for r in results), results
    print(json.dumps(results))
finally: service.close()
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=16)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.count <= 64 or args.runs < 3:
        parser.error("Use count 1..64 and at least 3 paired runs.")
    from PIL import Image, ImageDraw
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
    samples = {"per_image_cli": [], "one_service_process": []}
    with tempfile.TemporaryDirectory() as temp:
        workspace = Path(temp)
        for i in range(args.count):
            image = Image.new("RGBA", (256, 512), (i * 3, 80, 120, 0))
            draw = ImageDraw.Draw(image)
            draw.rectangle((30, 20, 225, 490), fill=(40 + i, 170, 220 - i, 150 + i))
            draw.ellipse((70, 50, 180, 160), fill=(220, 40 + i, 90, 255))
            image.save(workspace / f"source-{i}.png")
        for run in range(args.runs + 1):  # first pair warms imports/filesystem caches
            modes = list(samples)
            if run % 2: modes.reverse()
            hashes = {}
            for mode in modes:
                jobs = [{"source": f"source-{i}.png", "output": f"{run}/{mode}/{i}.png",
                         "width": 192, "height": 256, "mode": "contain", "anchor": "top"}
                        for i in range(args.count)]
                manifest = workspace / "jobs.json"
                manifest.write_text(json.dumps(jobs), encoding="utf-8")
                start = time.perf_counter()
                if mode == "per_image_cli":
                    results = []
                    for job in jobs:
                        output = subprocess.run([sys.executable, "-m", "um", "tool", "call", "image_prepare",
                            "--workspace", str(workspace), "--args", json.dumps(job)], cwd=root, env=env,
                            check=True, capture_output=True)
                        results.append(json.loads(output.stdout))
                else:
                    output = subprocess.run([sys.executable, "-c", WORKER, str(workspace), str(manifest)],
                        cwd=root, env=env, check=True, capture_output=True)
                    results = json.loads(output.stdout)
                elapsed = (time.perf_counter() - start) * 1000
                if run: samples[mode].append(elapsed)
                assert all(r["ok"] for r in results)
                hashes[mode] = []
                for result in results:
                    path = Path(result["artifacts"][0]["path"])
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    assert digest == result["artifacts"][0]["sha256"]
                    hashes[mode].append(digest)
            assert hashes["per_image_cli"] == hashes["one_service_process"]
    medians = {mode: statistics.median(values) for mode, values in samples.items()}
    report = {"recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "platform": platform.platform(), "python": sys.version,
              "pillow": Image.__version__, "count": args.count, "runs": args.runs,
              "input_size": [256, 512], "output_size": [192, 256],
              "method": "One warmup pair, alternating mode order, fresh process(es) for each pair; identical synthetic inputs and settings.",
              "median_ms": {k: round(v, 3) for k, v in medians.items()},
              "samples_ms": {k: [round(v, 3) for v in values] for k, values in samples.items()},
              "reduction_pct": round((1 - medians["one_service_process"] / medians["per_image_cli"]) * 100, 2),
              "byte_identical_outputs": True,
              "scope": "Same code, existing Service.invoke in both modes. Persistent MCP already reuses a process; no MCP speedup or Token savings measured."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
