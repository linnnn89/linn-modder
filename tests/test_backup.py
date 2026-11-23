"""Snapshot round trips and invalid archives; no game files or desktop control."""
import hashlib
import json
import os
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from um import backup
from um.contracts import ToolError
from um.service import Service


def archive(path, target, files, *, metadata=None, symlink=None):
    entries = metadata or {name: {'size': len(content), 'sha1': hashlib.sha1(content).hexdigest()}
                           for name, content in files.items()}
    with zipfile.ZipFile(path, 'w') as z:
        for name, content in files.items():
            if name == symlink:
                info = zipfile.ZipInfo(name)
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(info, content)
            else:
                z.writestr(name, content)
        z.writestr(backup.MANIFEST, json.dumps({'source': str(target), 'files': entries}))
    return path


@pytest.mark.parametrize('name', ['../escaped.txt', '/escaped.txt', 'C:/escaped.txt',
                                 'C:escaped.txt', r'..\escaped.txt', 'save:stream',
                                 'NUL.txt', 'dir./save.dat', 'dir /save.dat'])
def test_unsafe_archive_paths_leave_target_unchanged(tmp_path, name):
    target = tmp_path / 'target'; target.mkdir()
    (target / 'save.dat').write_bytes(b'current')
    snapshot = archive(tmp_path / 'invalid.zip', target, {name: b'payload'})
    with pytest.raises(ToolError, match='Unsafe'):
        backup.restore('fixture', str(target), str(snapshot), yes=True, store=tmp_path / 'store', quiet=True)
    assert (target / 'save.dat').read_bytes() == b'current'
    assert sorted(p.name for p in tmp_path.iterdir()) == ['invalid.zip', 'target']


def test_corruption_is_detected_before_any_file_is_replaced(tmp_path):
    target = tmp_path / 'target'; target.mkdir()
    (target / 'first.dat').write_bytes(b'current')
    files = {'first.dat': b'old', 'second.dat': b'corrupt'}
    metadata = {name: {'size': len(data), 'sha1': hashlib.sha1(data).hexdigest()} for name, data in files.items()}
    metadata['second.dat']['sha1'] = '0' * 40
    snapshot = archive(tmp_path / 'invalid.zip', target, files, metadata=metadata)
    with pytest.raises(ToolError, match='Checksum'):
        backup.restore('fixture', str(target), str(snapshot), yes=True, store=tmp_path / 'store', quiet=True)
    assert (target / 'first.dat').read_bytes() == b'current'
    assert not (target / 'second.dat').exists()
    assert not (tmp_path / 'store').exists()


@pytest.mark.parametrize('files,symlink', [({'save.dat': b'one', 'SAVE.dat': b'two'}, None),
                                         ({'dir': b'one', 'dir/save.dat': b'two'}, None),
                                         ({'link': b'../outside'}, 'link')])
def test_archive_collisions_and_links_are_rejected(tmp_path, files, symlink):
    snapshot = archive(tmp_path / 'invalid.zip', tmp_path / 'target', files, symlink=symlink)
    with pytest.raises(ToolError):
        backup.verify_snapshot(snapshot)
    assert not (tmp_path / 'target').exists()


def test_workspace_restore_preview_apply_and_undo(tmp_path, monkeypatch):
    monkeypatch.setenv('UM_HOME', str(tmp_path / 'user-store'))
    work = tmp_path / 'work'; work.mkdir()
    saves = work / 'saves'; saves.mkdir()
    (saves / 'save.dat').write_bytes(b'original')
    service = Service(work)
    created = service.invoke('backup_create', {'source': 'saves', 'name': 'fixture'})
    assert created.ok, created.to_dict()
    listed = service.invoke('backup_list', {'name': 'fixture'})
    assert listed.data['snapshots'][0]['path'] == created.data['snapshot']
    assert service.invoke('backup_verify', {'name': 'fixture'}).data['valid']
    (saves / 'save.dat').write_bytes(b'edited')
    (saves / 'extra.dat').write_bytes(b'extra')
    args = {'name': 'fixture', 'target': 'saves', 'clean': True}
    preview = service.invoke('backup_restore', args)
    assert preview.ok and not preview.data['applied']
    assert preview.data['changed'] == ['save.dat'] and preview.data['added'] == ['extra.dat']
    assert (saves / 'save.dat').read_bytes() == b'edited'
    restored = service.invoke('backup_restore', args | {'apply': True})
    assert restored.ok, restored.to_dict()
    assert (saves / 'save.dat').read_bytes() == b'original'
    assert not (saves / 'extra.dat').exists()
    assert Path(restored.data['undo_snapshot']).is_file()
    undo = service.invoke('backup_restore', {'name': 'fixture-pre-restore', 'target': 'saves', 'apply': True,
                                          'snapshot': restored.data['undo_snapshot'], 'clean': True})
    assert undo.ok, undo.to_dict()
    assert (saves / 'save.dat').read_bytes() == b'edited'
    assert (saves / 'extra.dat').read_bytes() == b'extra'
    # Legacy CLI can discover service snapshots using the same explicit store.
    assert backup.snapshots('fixture', store=work / '.um') == [Path(created.data['snapshot'])]
    cli = subprocess.run([sys.executable, '-m', 'um', 'backup', 'list', 'fixture',
                          '--store', str(work / '.um')], capture_output=True, text=True, encoding='utf-8')
    assert cli.returncode == 0, cli.stderr
    assert Path(created.data['snapshot']).name in cli.stdout
    assert not (tmp_path / 'user-store').exists()


def test_restore_game_roots_and_store_stay_read_only(tmp_path):
    (tmp_path / 'saves').mkdir(); (tmp_path / 'game').mkdir()
    (tmp_path / 'saves/save.dat').write_bytes(b'original')
    service = Service(tmp_path, (tmp_path / 'game',))
    assert service.invoke('backup_create', {'source': 'saves', 'name': 'fixture'}).ok
    for target in ('game', '.', '.um', '.um/backups/fixture'):
        result = service.invoke('backup_restore', {'name': 'fixture', 'target': target, 'apply': True})
        assert not result.ok, target
    assert not list((tmp_path / 'game').iterdir())


def test_read_only_backup_operations_do_not_create_store(tmp_path):
    service = Service(tmp_path)
    assert service.invoke('backup_list', {'name': 'missing'}).data['snapshots'] == []
    assert service.invoke('backup_verify', {'name': 'missing'}).error.code == 'not_found'
    assert not (tmp_path / '.um').exists()


def test_restore_rejects_target_links(tmp_path):
    target = tmp_path / 'target'; target.mkdir()
    outside = tmp_path / 'outside'; outside.mkdir()
    try:
        (target / 'linked').symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip('Symlink creation requires privilege on this Windows host')
    snapshot = archive(tmp_path / 'fixture.zip', target, {'linked/save.dat': b'original'})
    with pytest.raises(ToolError, match='links'):
        backup.restore('fixture', str(target), str(snapshot), yes=True, store=tmp_path / 'store', quiet=True)
    assert not list(outside.iterdir())


def test_duplicate_archive_entries_are_rejected(tmp_path):
    snapshot = archive(tmp_path / 'duplicate.zip', tmp_path / 'target', {'save.dat': b'original'})
    with zipfile.ZipFile(snapshot, 'a') as z:
        with pytest.warns(UserWarning, match='Duplicate'):
            z.writestr('save.dat', b'other')
    with pytest.raises(ToolError, match='duplicate'):
        backup.verify_snapshot(snapshot)


def test_reserved_source_filename_does_not_create_a_broken_backup(tmp_path):
    saves = tmp_path / 'saves'; saves.mkdir()
    (saves / backup.MANIFEST).write_text('user data')
    result = Service(tmp_path).invoke('backup_create', {'source': 'saves', 'name': 'fixture'})
    assert result.error.code == 'reserved_path'
    assert not (tmp_path / '.um').exists()


def test_store_inside_source_is_rejected_by_legacy_backup(tmp_path):
    with pytest.raises(ToolError, match='inside'):
        backup.create(str(tmp_path), 'fixture', store=tmp_path / '.um', quiet=True)
    assert not list(tmp_path.iterdir())


def test_filesystem_failure_reports_a_verified_undo_snapshot(tmp_path, monkeypatch):
    target = tmp_path / 'saves'; target.mkdir()
    (target / 'a.dat').write_bytes(b'current-a')
    (target / 'b.dat').write_bytes(b'current-b')
    snapshot = archive(tmp_path / 'fixture.zip', target, {'a.dat': b'old-a', 'b.dat': b'old-b'})
    replace = backup.os.replace
    def fail_second(source, destination):
        if Path(destination).name == 'b.dat':
            raise OSError('simulated disk failure')
        return replace(source, destination)
    monkeypatch.setattr(backup.os, 'replace', fail_second)
    store = tmp_path / 'store'
    with pytest.raises(ToolError, match='undo snapshot') as error:
        backup.restore('fixture', str(target), str(snapshot), yes=True, store=store, quiet=True)
    assert error.value.code == 'restore_failed'
    undo = backup.snapshots('fixture-pre-restore', store=store)[0]
    assert str(undo) in str(error.value)
    backup.verify_snapshot(undo)
    with zipfile.ZipFile(undo) as z:
        assert z.read('a.dat') == b'current-a'
        assert z.read('b.dat') == b'current-b'
    assert not list(target.glob('.um-restore-*'))


@pytest.mark.parametrize('clean', [False, True])
@pytest.mark.parametrize('previous', [b'snapshot', b'edited'])
def test_restore_nested_spelling_uses_target_filesystem(tmp_path, previous, clean):
    source = tmp_path / 'source/Profiles'
    target = tmp_path / 'target'
    original = target / 'profiles/save.dat'
    desired = target / 'Profiles/Save.dat'
    extra = target / 'extra.dat'
    source.mkdir(parents=True)
    (source / 'Save.dat').write_bytes(b'snapshot')
    original.parent.mkdir(parents=True)
    original.write_bytes(previous)
    extra.write_bytes(b'extra')
    aliases = desired.exists() and desired.samefile(original)
    service = Service(tmp_path)
    assert service.invoke('backup_create', {'name': 'fixture', 'source': 'source'}).ok
    args = {'name': 'fixture', 'target': 'target', 'clean': clean}
    preview = service.invoke('backup_restore', args)
    assert preview.ok, preview.to_dict()
    assert preview.data['added'] == (['extra.dat'] if aliases else ['extra.dat', 'profiles/save.dat'])
    assert preview.data['removed'] == ([] if aliases else ['Profiles/Save.dat'])
    assert preview.data['changed'] == (['Profiles/Save.dat'] if aliases and previous != b'snapshot' else [])
    assert original.read_bytes() == previous and extra.is_file()

    result = service.invoke('backup_restore', args | {'apply': True})
    assert result.ok, result.to_dict()
    for key in ('added', 'removed', 'changed'):
        assert result.data[key] == preview.data[key]
    assert desired.read_bytes() == b'snapshot'
    assert extra.exists() == (not clean)
    if not aliases:
        assert original.exists() == (not clean)
        if not clean:
            assert original.read_bytes() == previous
    if clean:
        undo = service.invoke('backup_restore', args | {'apply': True, 'name': 'fixture-pre-restore',
                                                        'snapshot': result.data['undo_snapshot']})
        assert undo.ok, undo.to_dict()
        assert original.read_bytes() == previous
        assert extra.read_bytes() == b'extra'
        if not aliases:
            assert not desired.exists()


def test_restore_clean_removes_independent_hard_link(tmp_path):
    target = tmp_path / 'target'
    target.mkdir()
    saved = target / 'Save.dat'
    extra = target / 'copy.dat'
    saved.write_bytes(b'edited')
    os.link(saved, extra)
    snapshot = archive(tmp_path / 'fixture.zip', target, {'Save.dat': b'snapshot'})
    result = backup.restore('fixture', str(target), str(snapshot), clean=True, yes=True,
                            store=tmp_path / 'store', quiet=True)
    assert result['added'] == ['copy.dat']
    assert result['changed'] == ['Save.dat']
    assert saved.read_bytes() == b'snapshot'
    assert not extra.exists()


def test_restore_rejects_ambiguous_alias_with_hard_links(tmp_path):
    target = tmp_path / 'target'
    target.mkdir()
    saved = target / 'save.dat'
    saved.write_bytes(b'edited')
    if not (target / 'Save.dat').exists():
        pytest.skip('requires a case-insensitive target directory')
    os.link(saved, target / 'copy.dat')
    snapshot = archive(tmp_path / 'fixture.zip', target, {'Save.dat': b'snapshot'})
    with pytest.raises(ToolError, match='uniquely match'):
        backup.restore('fixture', str(target), str(snapshot), clean=True, yes=True,
                       store=tmp_path / 'store', quiet=True)
    assert saved.read_bytes() == b'edited'
    assert saved.samefile(target / 'copy.dat')
    assert not (tmp_path / 'store').exists()


@pytest.mark.parametrize('existing', [False, True])
def test_two_snapshot_paths_cannot_claim_one_target_entry(tmp_path, monkeypatch, existing):
    target = tmp_path / 'target'
    first, second = target / 'first', target / 'second'
    first.mkdir(parents=True)
    second.mkdir()
    saved = first / 'save.dat'
    if existing:
        saved.write_bytes(b'current')
    snapshot = archive(tmp_path / 'fixture.zip', target,
                       {'first/save.dat': b'one', 'second/save.dat': b'two'})
    file_id = backup._file_id

    def lookup(path):
        # Model a native lookup where both parent spellings resolve to 'first'.
        if path.is_relative_to(second):
            path = first / path.relative_to(second)
        return file_id(path)

    monkeypatch.setattr(backup, '_file_id', lookup)
    store = tmp_path / 'store'
    for operation in (backup.diff, backup.restore):
        args = {'clean': True, 'yes': True, 'quiet': True} if operation is backup.restore else {}
        with pytest.raises(ToolError) as error:
            operation('fixture', str(target), str(snapshot), store=store, **args)
        assert error.value.code == 'invalid_target'
        assert not store.exists()
        if existing:
            assert saved.read_bytes() == b'current'
        else:
            assert not saved.exists()


@pytest.mark.parametrize('fault', ['alias', 'unavailable'])
def test_cleanup_checks_every_candidate_before_unlink(tmp_path, monkeypatch, fault):
    target = tmp_path / 'target'
    target.mkdir()
    for name in ('keep.dat', 'a-extra.dat', 'z-extra.dat'):
        (target / name).write_bytes(b'current')
    snapshot = archive(tmp_path / 'fixture.zip', target, {'keep.dat': b'snapshot'})
    file_id = backup._file_id

    def lookup(path):
        if path.name == 'z-extra.dat':
            if fault == 'unavailable':
                raise OSError('file identity unavailable')
            return file_id(target / 'keep.dat')
        return file_id(path)

    monkeypatch.setattr(backup, '_file_id', lookup)
    store = tmp_path / 'store'
    with pytest.raises(ToolError, match='undo snapshot') as error:
        backup.restore('fixture', str(target), str(snapshot), clean=True, yes=True, store=store, quiet=True)
    assert error.value.code == 'restore_failed'
    assert (target / 'keep.dat').read_bytes() == b'snapshot'
    for name in ('a-extra.dat', 'z-extra.dat'):
        assert (target / name).read_bytes() == b'current'
    undo, = backup.snapshots('fixture-pre-restore', store=store)
    assert str(undo) in str(error.value)
    with zipfile.ZipFile(undo) as z:
        assert z.read('keep.dat') == b'current'
