"""Snapshot folders before touching them (saves, profiles, config, the game's data folder).

    um backup create "C:\\Users\\me\\Documents\\My Games\\Terraria" --name terraria-saves
    um backup list [name]
    um backup diff terraria-saves "C:\\Users\\me\\Documents\\My Games\\Terraria"     # what changed since the last snapshot
    um backup restore terraria-saves [--to DIR] [--snapshot FILE] [--yes]

Snapshots are zip files + a manifest (size + sha1 per file) in ~/.universal-modder/backups/<name>/.
restore first snapshots the current state (so a restore can itself be undone), then puts every file
back and removes files that weren't in the snapshot only with --clean.
Habit that saved the Terraria showcase: keep a pristine copy of any world/scenario a scripted take
destroys, and restore it before each take.
"""
from __future__ import annotations

import hashlib
import json
import re
import os
import stat
import shutil
import tempfile
from contextlib import ExitStack
from datetime import datetime
import zipfile
from pathlib import Path

from um.common import data_dir, die, to_posix
from um.contracts import ToolError
from um.workspace import is_link


def _root(name: str, store: Path | None = None) -> Path:
    _relative(name)
    if '/' in name:
        raise ToolError('invalid_name', 'Backup name must be one directory name.')
    return (store if store is not None else data_dir()) / 'backups' / name


MANIFEST = '_um_manifest.json'
MAX_BYTES = 20 << 30
MAX_FILES = 100_000


def _relative(name: str) -> str:
    """Portable paths: reject traversal, Windows aliases/streams and device names."""
    if not isinstance(name, str) or not name:
        raise ToolError('invalid_snapshot', 'Snapshot paths must be nonempty strings.')
    for part in name.split('/'):
        if (part in ('', '.', '..') or part.endswith((' ', '.'))
                or re.search(r'[\\:\x00-\x1f<>"|?*]', part)
                or re.fullmatch(r'(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', part)):
            raise ToolError('invalid_snapshot', f'Unsafe snapshot path: {name!r}')
    return name


def _scan(src: Path) -> dict:
    files, total = {}, 0
    if is_link(src):
        raise ToolError('linked_tree', 'Snapshot folders must not contain links/junctions.')
    def walk_error(error):
        raise error
    for parent, dirs, names in os.walk(src, followlinks=False, onerror=walk_error):
        for name in dirs + names:
            if is_link(Path(parent) / name):
                raise ToolError('linked_tree', 'Snapshot folders must not contain links/junctions.')
        for name in sorted(names):
            p = Path(parent) / name
            if not p.is_file():
                continue
            relative = _relative(p.relative_to(src).as_posix())
            if relative.casefold() == MANIFEST.casefold():
                raise ToolError('reserved_path', f'{MANIFEST} is reserved for snapshot metadata.')
            total += p.stat().st_size
            if total > MAX_BYTES or len(files) >= MAX_FILES:
                raise ToolError('snapshot_too_large', 'Snapshot exceeds 20 GiB or 100000 files.')
            h = hashlib.sha1()
            with p.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1 << 20), b''):
                    h.update(chunk)
            files[relative] = dict(size=p.stat().st_size, sha1=h.hexdigest())
    return files


def create(src: str, name: str | None = None, note: str = '', *, store: Path | None = None, quiet: bool = False) -> Path:
    s = Path(to_posix(src)).expanduser().resolve()
    if not s.is_dir():
        raise ToolError('invalid_path', f'Not a folder: {s}')
    name = name or s.name.replace(' ', '-').lower()
    folder = _root(name, store)
    if folder.resolve().is_relative_to(s):
        raise ToolError('recursive_backup', 'Snapshot store must not be inside the source folder.')
    files = _scan(s)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / f'{stamp}.zip'
    created = False
    try:
        with zipfile.ZipFile(out, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            created = True
            for rel in files:
                z.write(s / rel, rel)
            z.writestr(MANIFEST, json.dumps(dict(source=str(s), created=stamp, note=note, files=files), indent=1))
        verify_snapshot(out)  # Reject source changes between hashing and archive creation.
    except Exception:
        if created:
            out.unlink(missing_ok=True)
        raise
    if not quiet:
        print(f'{out}  ({len(files)} files, {sum(f["size"] for f in files.values()) / 2**20:.1f} MB)')
    return out


def snapshots(name: str, *, store: Path | None = None) -> list[Path]:
    return sorted(_root(name, store).glob('*.zip'))


def _select(name: str, snapshot: str | None, store: Path | None) -> Path:
    zp = Path(to_posix(snapshot)) if snapshot else (snapshots(name, store=store) or [None])[-1]
    if zp is None:
        raise ToolError('not_found', f'No snapshots for {name}')
    return zp


def _metadata(z: zipfile.ZipFile) -> dict:
    entries = z.infolist()
    if len(entries) > MAX_FILES + 1 or len({i.filename for i in entries}) != len(entries):
        raise ToolError('invalid_snapshot', 'Too many or duplicate archive entries.')
    info = z.getinfo(MANIFEST)
    if info.file_size > 8 << 20:
        raise ToolError('invalid_snapshot', 'Snapshot manifest exceeds 8 MiB.')
    m = json.loads(z.read(info))
    if not isinstance(m, dict) or not isinstance(m.get('files'), dict) or not isinstance(m.get('source'), str):
        raise ToolError('invalid_snapshot', 'Invalid snapshot manifest.')
    total, seen = 0, set()
    for rel, entry in m['files'].items():
        _relative(rel)
        if rel.casefold() == MANIFEST.casefold() or not isinstance(entry, dict):
            raise ToolError('invalid_snapshot', 'Invalid snapshot file metadata.')
        if type(entry.get('size')) is not int or entry['size'] < 0 or not re.fullmatch(r'[0-9a-f]{40}', str(entry.get('sha1', ''))):
            raise ToolError('invalid_snapshot', 'Invalid snapshot size or checksum.')
        folded = rel.casefold()
        if folded in seen:
            raise ToolError('invalid_snapshot', 'Case-insensitive filename collision.')
        seen.add(folded)
        total += entry['size']
    for rel in seen:
        if any('/'.join(rel.split('/')[:n]) in seen for n in range(1, len(rel.split('/')))):
            raise ToolError('invalid_snapshot', 'Conflicting file and directory paths.')
    if total > MAX_BYTES or len(seen) > MAX_FILES:
        raise ToolError('snapshot_too_large', 'Snapshot exceeds size/file limits.')
    if {i.filename for i in entries} != set(m['files']) | {MANIFEST}:
        raise ToolError('invalid_snapshot', 'Archive entries do not match the manifest.')
    for i in entries:
        if i.is_dir() or stat.S_IFMT(i.external_attr >> 16) not in (0, stat.S_IFREG) or i.flag_bits & 1:
            raise ToolError('invalid_snapshot', 'Archive must contain regular files only.')
    return m


def _manifest(zp: Path) -> dict:
    try:
        with zipfile.ZipFile(zp) as z:
            return _metadata(z)
    except (zipfile.BadZipFile, KeyError, ValueError) as exc:
        raise ToolError('invalid_snapshot', 'Invalid snapshot archive or manifest.') from exc


def verify_snapshot(zp: Path, *, staging: Path | None = None) -> dict:
    """Validate every member before restore touches a target; optionally stage verified files."""
    try:
        with zipfile.ZipFile(zp) as z:
            m = _metadata(z)
            for rel, entry in m['files'].items():
                if z.getinfo(rel).file_size != entry['size']:
                    raise ToolError('invalid_snapshot', f'Size mismatch: {rel}')
                h, size = hashlib.sha1(), 0
                with ExitStack() as stack:
                    source = stack.enter_context(z.open(rel))
                    destination = None
                    if staging is not None:
                        p = staging / rel
                        p.parent.mkdir(parents=True, exist_ok=True)
                        destination = stack.enter_context(p.open('xb'))
                    for chunk in iter(lambda: source.read(1 << 20), b''):
                        size += len(chunk)
                        h.update(chunk)
                        if destination is not None:
                            destination.write(chunk)
                if size != entry['size'] or h.hexdigest() != entry['sha1']:
                    raise ToolError('invalid_snapshot', f'Checksum mismatch: {rel}')
            return m
    except (zipfile.BadZipFile, KeyError, ValueError) as exc:
        raise ToolError('invalid_snapshot', 'Invalid snapshot archive or manifest.') from exc


def _target(value: str) -> Path:
    t = Path(to_posix(value)).expanduser().absolute()
    for p in (t, *t.parents):
        if is_link(p):
            raise ToolError('linked_tree', 'Restore target must not traverse links/junctions.')
    if t.exists() and not t.is_dir():
        raise ToolError('invalid_path', 'Restore target must be a directory.')
    return t


def _diff(zp: Path, m: dict, t: Path) -> dict:
    now = _scan(t) if t.is_dir() else {}
    old = m['files']
    return dict(snapshot=str(zp), target=str(t),
                added=sorted(set(now) - set(old)), removed=sorted(set(old) - set(now)),
                changed=sorted(k for k in set(now) & set(old) if now[k]['sha1'] != old[k]['sha1']))


def diff(name: str, target: str | None = None, snapshot: str | None = None, *, store: Path | None = None) -> dict:
    zp = _select(name, snapshot, store)
    m = verify_snapshot(zp)
    return _diff(zp, m, _target(target or m['source']))


def restore(name: str, to: str | None = None, snapshot: str | None = None, clean: bool = False, yes: bool = False,
            *, store: Path | None = None, quiet: bool = False) -> dict:
    zp = _select(name, snapshot, store)
    with tempfile.TemporaryDirectory(prefix='um-restore-') as directory:
        staging = Path(directory)
        m = verify_snapshot(zp, staging=staging)
        t = _target(to or m['source'])
        folder = _root(name, store).resolve()
        if folder.is_relative_to(t) or t.is_relative_to(folder) or zp.resolve().is_relative_to(t):
            raise ToolError('recursive_backup', 'Restore target must not overlap its snapshot store.')
        d = _diff(zp, m, t)
        for rel in m['files']:
            p = t / rel
            if p.exists() and not p.is_file() or any(parent.exists() and not parent.is_dir() for parent in p.parents if parent != t):
                raise ToolError('invalid_path', f'Restore file conflicts with a directory: {rel}')
        if not quiet:
            print(f"restore {zp.name} -> {t}: {len(d['changed'])} changed, {len(d['removed'])} missing, {len(d['added'])} new since")
        if not yes:
            die('re-run with --yes to do it')
        undo = create(str(t), name[:52] + '-pre-restore', note=f'automatic, before restoring {zp.name}', store=store, quiet=quiet) if t.is_dir() else None
        t.mkdir(parents=True, exist_ok=True)
        try:
            for rel in m['files']:
                p = t / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                # Same-directory replace avoids truncating an existing file on a failed copy.
                with tempfile.NamedTemporaryFile(dir=p.parent, delete=False, prefix='.um-restore-') as tmp:
                    temporary = Path(tmp.name)
                try:
                    shutil.copyfile(staging / rel, temporary)
                    os.replace(temporary, p)
                finally:
                    temporary.unlink(missing_ok=True)
            if clean:
                for rel in d['added']:
                    (t / rel).unlink()
        except OSError as exc:
            raise ToolError('restore_failed', f'Restore incomplete; undo snapshot: {undo}. {exc}') from exc
        if not quiet:
            print('restored', len(m['files']), 'files')
        return d | {'restored': len(m['files']), 'undo_snapshot': str(undo) if undo else None}

def main(a):
    store = Path(to_posix(a.store)).expanduser().resolve() if a.store else None
    try:
        if a.cmd == "create":
            create(a.src, a.name, a.note or "", store=store)
        elif a.cmd == "list":
            root = (store if store is not None else data_dir()) / "backups"
            names = [a.name] if a.name else sorted(p.name for p in root.glob("*") if p.is_dir()) if root.exists() else []
            for n in names:
                for zp in snapshots(n, store=store):
                    m = _manifest(zp)
                    print(f"{n:28} {zp.name}  {len(m['files']):5} files  {m['source']}  {m.get('note', '')}")
        elif a.cmd == "diff":
            print(json.dumps(diff(a.name, a.target, a.snapshot, store=store), indent=1))
        elif a.cmd == "restore":
            restore(a.name, a.to, a.snapshot, a.clean, a.yes, store=store)
    except ToolError as exc:
        die(str(exc))


def register(sub):
    import argparse
    p = sub.add_parser("backup", help="snapshot / diff / restore save folders before you touch them",
                       description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")
    q = cs.add_parser("create", help="snapshot a folder")
    q.add_argument("src")
    q.add_argument("--name")
    q.add_argument("--note")
    q.set_defaults(func=main)
    q = cs.add_parser("list", help="list snapshots")
    q.add_argument("name", nargs="?")
    q.set_defaults(func=main)
    q = cs.add_parser("diff", help="what changed since the latest snapshot")
    q.add_argument("name")
    q.add_argument("target", nargs="?")
    q.add_argument("--snapshot")
    q.set_defaults(func=main)
    q = cs.add_parser("restore", help="restore the latest (or --snapshot) snapshot")
    q.add_argument("name")
    q.add_argument("--to")
    q.add_argument("--snapshot")
    q.add_argument("--clean", action="store_true", help="also delete files created after the snapshot")
    q.add_argument("--yes", action="store_true")
    q.set_defaults(func=main)
    for command in cs.choices.values():
        command.add_argument("--store", help="state root containing backups/ (use WORKSPACE/.um for service snapshots)")
