"""Paired scan timings and actual routing Token counts; no installed game needed.

Requires tiktoken for both encodings. Timing acceptance belongs on the same
machine with idle runners, not as an absolute cross-platform CI threshold.
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

PROBE = '''
import json, sys, time
from pathlib import Path
from um import scan
from um.service import Service
scan.all_games = lambda: []  # isolate game indexing from machine/store discovery
root = Path(sys.argv[1])
service = Service(root)
start = time.perf_counter()
result = service.invoke('game_scan', {'path': '.'})
seconds = time.perf_counter() - start
assert result.ok, result.to_dict()
service.close()
# Additive diagnostics are intentionally different; engine and other results must agree.
report = dict(result.data)
report.pop('entries_visited', None)
report.pop('index_truncation_reasons', None)
print(json.dumps({'seconds': seconds, 'report': report}, sort_keys=True))
'''
ENTRY = Path('skills/linn-modder/SKILL.md')
GUIDE = Path('skills/linn-modder/asset-pipeline/GUIDE.md')


def probe(root, fixture):
    env = dict(os.environ)
    env['PYTHONPATH'] = str(root) + os.pathsep + env.get('PYTHONPATH', '')
    result = subprocess.run([sys.executable, '-c', PROBE, str(fixture)], cwd=root,
                            env=env, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def identify(root):
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    paths = sorted((root / 'um').rglob('*.py')) + [root / ENTRY, root / GUIDE]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(root).as_posix().encode() + b'\0' + path.read_bytes())
    dirty = subprocess.check_output(['git', 'diff', 'HEAD', '--', 'um', str(ENTRY), str(GUIDE)], cwd=root)
    return {'commit': commit, 'measured_sources_dirty': bool(dirty),
            'measured_sources_sha256': digest.hexdigest()}


def reduction(before, after):
    return round(100 * (1 - after / before), 2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--runs', type=int, default=15)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--require-targets', action='store_true')
    args = parser.parse_args()
    if args.runs < 3:
        parser.error('--runs must be at least 3')
    roots = {'before': args.before.resolve(), 'after': args.after.resolve()}
    samples = {key: [] for key in roots}
    with tempfile.TemporaryDirectory(prefix='linn-scan-') as directory:
        fixture = Path(directory)
        for d in range(20):
            folder = fixture / f'assets-{d}'; folder.mkdir()
            for f in range(250):
                (folder / f'{f}.dat').touch()
        (fixture / 'UnityPlayer.dll').write_bytes(b'MZ')
        data = fixture / 'Game_Data'; data.mkdir()
        (data / 'GlobalGameManagers').write_bytes(b'2022.3.21f1')
        (data / 'App.Info').write_text('Studio\nFixture', encoding='utf-8')
        expected = probe(roots['before'], fixture)['report']
        assert probe(roots['after'], fixture)['report'] == expected
        for i in range(args.runs):
            for label in (('before', 'after') if i % 2 == 0 else ('after', 'before')):
                sample = probe(roots[label], fixture)
                assert sample['report'] == expected, 'scan output changed'
                samples[label].append(sample['seconds'] * 1000)
    medians = {key: statistics.median(values) for key, values in samples.items()}
    import tiktoken
    import yaml
    texts = {key: (root / ENTRY).read_text(encoding='utf-8') for key, root in roots.items()}
    # Discovery triggers must not be lost to meet the active-context target.
    assert yaml.safe_load(texts['before'].split('---', 2)[1]) == yaml.safe_load(texts['after'].split('---', 2)[1])
    tokens = {}
    for name in ('cl100k_base', 'o200k_base'):
        encoding = tiktoken.get_encoding(name)
        entry = {key: len(encoding.encode(text)) for key, text in texts.items()}
        asset = {key: len(encoding.encode(text + (roots[key] / GUIDE).read_text(encoding='utf-8')))
                 for key, text in texts.items()}
        tokens[name] = {'entry': entry, 'asset_route': asset,
                        'entry_reduction_pct': reduction(entry['before'], entry['after']),
                        'asset_route_reduction_pct': reduction(asset['before'], asset['after'])}
    speedup = reduction(medians['before'], medians['after'])
    targets = {'scan_at_least_25_pct_faster': speedup >= 25,
               'cl100k_asset_route_at_least_40_pct_smaller': tokens['cl100k_base']['asset_route_reduction_pct'] >= 40,
               'both_entries_at_least_45_pct_smaller': all(t['entry_reduction_pct'] >= 45 for t in tokens.values()),
               'cl100k_entry_at_most_900_tokens': tokens['cl100k_base']['entry']['after'] <= 900}
    report = {'date_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'platform': platform.platform(), 'python': sys.version, 'tiktoken': tiktoken.__version__,
              'sources': {key: identify(root) for key, root in roots.items()},
              'fixture': {'files': 5003, 'directories': 21, 'store_discovery': 'stubbed'},
              'scan': {'samples_ms': samples, 'median_ms': medians, 'reduction_pct': speedup,
                       'equivalent_existing_report_fields': True}, 'tokens': tokens, 'targets': targets}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'medians_ms': medians, 'scan_reduction_pct': speedup, 'tokens': tokens, 'targets': targets}, indent=2))
    if args.require_targets and not all(targets.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
