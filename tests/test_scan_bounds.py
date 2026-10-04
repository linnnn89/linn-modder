"""Streaming limits and read boundaries, using synthetic trees only."""
import os
from pathlib import Path

import pytest

from um import scan
from um.service import Service
from um.workspace import Workspace


def test_large_directory_stops_at_limit_without_materializing_it(tmp_path, monkeypatch):
    for i in range(250):
        (tmp_path / f'{i}.dat').touch()
    monkeypatch.setattr(scan, 'MAX_ENTRIES', 2)
    original = os.scandir
    yielded = []

    class CountedEntries:
        def __enter__(self):
            self.entries = original(tmp_path)
            return self

        def __exit__(self, *args):
            self.entries.close()

        def __iter__(self):
            for entry in self.entries:
                yielded.append(entry.name)
                yield entry

    monkeypatch.setattr(scan.os, 'scandir', lambda _: CountedEntries())
    ix = scan.Index(tmp_path)
    assert len(ix.files) == ix.entries_visited == 2
    assert ix.truncated and ix.truncation_reasons == {'max_entries'}
    assert len(yielded) == 3  # one lookahead, not all 250 entries


@pytest.mark.parametrize('count, truncated', [(0, False), (2, False), (3, True)])
def test_exact_file_limit(tmp_path, monkeypatch, count, truncated):
    for i in range(count):
        (tmp_path / str(i)).touch()
    monkeypatch.setattr(scan, 'MAX_ENTRIES', 2)
    ix = scan.Index(tmp_path)
    assert len(ix.files) == min(count, 2)
    assert ix.truncated is truncated


def test_empty_directories_share_the_entry_budget(tmp_path, monkeypatch):
    for i in range(20):
        (tmp_path / str(i)).mkdir()
    monkeypatch.setattr(scan, 'MAX_ENTRIES', 2)
    ix = scan.Index(tmp_path)
    assert ix.entries_visited == len(ix.dirs) == 2
    assert not ix.files
    assert ix.truncation_reasons == {'max_entries'}


def test_depth_limit_keeps_boundary_files_and_reports_omissions(tmp_path, monkeypatch):
    (tmp_path / 'one' / 'two').mkdir(parents=True)
    (tmp_path / 'one' / 'Visible.dat').touch()
    (tmp_path / 'one' / 'two' / 'hidden.dat').touch()
    monkeypatch.setattr(scan, 'MAX_DEPTH', 1)
    monkeypatch.setattr(scan, 'all_games', lambda: [])
    result = Service(tmp_path).invoke('game_scan', {'path': '.'})
    assert result.ok
    assert result.data['files_indexed'] == 1
    assert result.data['index_truncated']
    assert result.data['index_truncation_reasons'] == ['max_depth']
    assert 'max_depth' in scan.format_report(result.data)


def test_boundary_directory_without_children_is_complete(tmp_path, monkeypatch):
    (tmp_path / 'one').mkdir()
    (tmp_path / 'one' / 'visible.dat').touch()
    monkeypatch.setattr(scan, 'MAX_DEPTH', 1)
    assert not scan.Index(tmp_path).truncated


@pytest.mark.parametrize('directory', [False, True])
def test_scan_rejects_links_before_binary_reads(tmp_path, monkeypatch, directory):
    work = tmp_path / 'work'; work.mkdir()
    outside = tmp_path / 'outside'
    if directory:
        outside.mkdir()
    else:
        outside.write_bytes(b'MZ')
    try:
        (work / 'linked.exe').symlink_to(outside, target_is_directory=directory)
    except OSError:
        pytest.skip('symlink creation needs Windows privilege or developer mode')
    monkeypatch.setattr(scan, 'all_games', lambda: [])
    monkeypatch.setattr(scan, 'detect', lambda _: pytest.fail('must reject before binary reads'))
    result = Service(work).invoke('game_scan', {'path': '.'})
    assert not result.ok and result.error.code == 'linked_tree'


def test_scan_reads_each_directory_once_and_preserves_original_case(tmp_path, monkeypatch):
    data = tmp_path / 'Game_Data'; data.mkdir()
    (tmp_path / 'UnityPlayer.dll').write_bytes(b'MZ')
    (data / 'GlobalGameManagers').write_bytes(b'2022.3.21f1')
    (data / 'App.Info').write_text('Studio\nFixture', encoding='utf-8')
    original = os.scandir
    visited = []

    def counted(path):
        visited.append(Path(path))
        return original(path)

    monkeypatch.setattr(scan.os, 'scandir', counted)
    monkeypatch.setattr(scan, 'all_games', lambda: [])
    monkeypatch.setattr(Workspace, 'check_tree', lambda *_: pytest.fail('duplicate prewalk'))
    result = Service(tmp_path).invoke('game_scan', {'path': '.'})
    assert result.ok
    assert result.data['engine']['version'] == '2022.3.21f1'
    assert result.data['engine']['product'] == 'Fixture'
    assert visited == [tmp_path, data]
    assert result.data['index_truncation_reasons'] == []


def test_unreadable_tree_is_an_error_not_a_complete_report(tmp_path, monkeypatch):
    def denied(_):
        raise PermissionError('synthetic access denied')
    monkeypatch.setattr(scan, 'all_games', lambda: [])
    monkeypatch.setattr(scan.os, 'scandir', denied)
    result = Service(tmp_path).invoke('game_scan', {'path': '.'})
    assert not result.ok and result.error.code == 'operation_failed'
