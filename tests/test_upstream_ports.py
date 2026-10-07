"""Focused upstream regressions; synthetic files and platform adapters only."""
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from contextlib import nullcontext
from types import SimpleNamespace

import pytest
from PIL import Image

from um import backup, common, doctor, kb, publish, scan, sprite, win


def test_sprite_placement_keeps_partial_alpha():
    image = Image.new('RGBA', (8, 8), (200, 100, 50, 128))
    fitted = sprite.fit(image, 8, 8)
    sheet = sprite.sheet([image, image], cols=2)
    frames = sprite.simple_frames(image, n=3, kind='squash')
    assert fitted.getpixel((4, 4)) == (200, 100, 50, 128)
    assert sheet.getpixel((12, 4)) == (200, 100, 50, 128)
    assert all(frame.getpixel((4, 4)) == (200, 100, 50, 128) for frame in frames)


def test_powershell_locator_shares_path_fallback(tmp_path, monkeypatch):
    exe = tmp_path / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    exe.parent.mkdir(parents=True); exe.touch()
    monkeypatch.setenv('SystemRoot', str(tmp_path))
    monkeypatch.setattr(common, 'is_wsl', lambda: False)
    monkeypatch.setattr(common.shutil, 'which', lambda _: None)
    assert win.ps_exe() == scan.ps_exe() == common.ps_exe() == str(exe)
    monkeypatch.setattr(doctor, 'is_windows', lambda: True)
    monkeypatch.setattr(doctor, 'is_wsl', lambda: False)
    monkeypatch.setattr(doctor, 'find_ffmpeg', lambda **_: None)
    assert doctor.inspect_environment()['dependencies']['powershell'] == str(exe)
    assert doctor.inspect_environment()['capabilities']['windows_input']
    monkeypatch.setattr(common.shutil, 'which', lambda _: 'on-path-powershell')
    assert common.ps_exe() == 'on-path-powershell'
    monkeypatch.setattr(common.shutil, 'which', lambda _: None)
    monkeypatch.setattr(common, 'is_wsl', lambda: True)
    monkeypatch.setattr(common.os.path, 'exists', lambda p: p == '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe')
    assert common.ps_exe() == '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'


def test_steam_registry_discovery_without_default_install(tmp_path, monkeypatch):
    root = tmp_path / 'custom-steam'; (root / 'steamapps').mkdir(parents=True)
    fake_registry = SimpleNamespace(HKEY_CURRENT_USER=1, HKEY_LOCAL_MACHINE=2,
        OpenKey=lambda *_: nullcontext('key'), QueryValueEx=lambda *_: (str(root), 1))
    monkeypatch.setitem(sys.modules, 'winreg', fake_registry)
    monkeypatch.setattr(scan, 'is_windows', lambda: True)
    monkeypatch.setattr(scan, 'is_wsl', lambda: False)
    assert scan.steam_registry_root() == root
    assert root in scan.steam_roots()


def test_steam_registry_discovery_under_wsl(monkeypatch):
    monkeypatch.setattr(scan, 'is_windows', lambda: False)
    monkeypatch.setattr(scan, 'is_wsl', lambda: True)
    monkeypatch.setattr(common, 'is_wsl', lambda: True)
    monkeypatch.setattr(scan.subprocess, 'run', lambda *a, **kw: subprocess.CompletedProcess(a, 0,
        '    SteamPath    REG_SZ    D:\\Steam\n', ''))
    assert scan.steam_registry_root() == Path('/mnt/d/Steam')


@pytest.mark.parametrize('name, playbook', [('Slay the Spire', 'misc-engines.md'),
                                          ('Slay the Spire 2', 'godot.md')])
def test_specific_game_routes(tmp_path, monkeypatch, name, playbook):
    game = tmp_path / name; game.mkdir()
    monkeypatch.setattr(scan, 'all_games', lambda: [])
    assert scan.scan(str(game))['routes'][0]['playbook'] == playbook


def test_online_only_names_do_not_block_offline_titles():
    for name in ['Rusty Lake', 'Battlefield 1942', 'Call of Duty Modern Warfare 2']:
        assert scan.online_only(name) is None
    assert scan.online_only('Rust')
    assert scan.online_only("Tom Clancy's Rainbow Six® Siege")


def test_invalid_yaml_date_returns_a_note_error(tmp_path):
    note = tmp_path / 'bad.md'
    note.write_text('---\nkind: technique\ndate: 2026-09-31\n---\nBody', encoding='utf-8')
    assert '_yaml_error' in kb.parse(note)[0]
    fails, _ = kb.check_note(note)
    assert any('front matter is not valid YAML' in item for item in fails)


def test_knowledge_search_word_starts_keep_cjk_and_punctuation(tmp_path):
    for stem, title in [('rust', 'Rust and rusty tools'), ('trust', 'Trust and frustum'),
                        ('esp', 'plugin.esp'), ('portrait', '角色立绘替换')]:
        (tmp_path / f'{stem}.md').write_text(f'---\ntitle: {title}\n---\n{title}\n', encoding='utf-8')
    assert [r['path'] for r in kb.search(tmp_path, ['rust'])] == ['rust.md']
    assert [r['path'] for r in kb.search(tmp_path, ['.esp'])] == ['esp.md']
    assert [r['path'] for r in kb.search(tmp_path, ['立绘'])] == ['portrait.md']


def test_publish_check_recognizes_current_key_formats(tmp_path):
    # Synthetic patterns, never real credentials.
    (tmp_path / 'config.txt').write_text('sk-proj-' + 'a_' * 20 + '\ngithub_pat_' + 'b_' * 35)
    assert publish.check(str(tmp_path)) > 0


def test_backup_roundtrip_with_old_file_timestamp(tmp_path):
    source = tmp_path / 'source'; source.mkdir()
    (source / 'save.dat').write_bytes(b'old fixture')
    os.utime(source / 'save.dat', (315360000, 315360000))  # before 1980, still representable on Windows
    store = tmp_path / 'store'
    snapshot = backup.create(str(source), 'fixture', store=store, quiet=True)
    assert backup.verify_snapshot(snapshot)['files']['save.dat']['size'] == len(b'old fixture')
    with zipfile.ZipFile(snapshot) as archive:
        assert archive.read('save.dat') == b'old fixture'
