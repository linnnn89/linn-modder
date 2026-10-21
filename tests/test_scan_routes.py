"""Route decisions from synthetic installs, through the public service contract."""
import struct

import pytest

from um import resources, scan
from um.service import Service


def pe(managed=False):
    data = bytearray(1024)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 0x3C, 0x80)
    data[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<H', data, 0x84, 0x14C)
    struct.pack_into('<H', data, 0x98, 0x10B)
    struct.pack_into('<I', data, 0x98 + 96 + 14 * 8, 0x2000 if managed else 0)
    return bytes(data)


def inspect(root, files, monkeypatch):
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    monkeypatch.setattr(scan, 'all_games', lambda: [])
    monkeypatch.setattr(scan, 'save_hints', lambda *_: [])
    result = Service(root).invoke('game_scan', {'path': '.'})
    assert result.ok, result.to_dict()
    report = result.data
    assert resources.read('skills', report['playbook'].removeprefix('skills/'))
    assert report['index_truncation_reasons'] == []
    return report


@pytest.mark.parametrize('files, expected, ambiguous', [
    ({'bin/Game.exe': pe(), 'Forgotten Construction Set.exe': pe(True),
      'OgreMain_x64.dll': b'fixture'}, 'native', False),
    ({'bin/Game.exe': pe(), 'Editor.exe': pe(True),
      'Editor.runtimeconfig.json': b'{}', 'Editor.dll': pe(True)}, 'native', False),
    ({'bin/Game.exe': pe(True)}, 'dotnet', False),
    ({'bin/Game.exe': pe(), 'bin/Game.dll': pe(True),
      'bin/Game.runtimeconfig.json': b'{}'}, 'dotnet', False),
    ({'Game.dll': pe(True), 'Game.runtimeconfig.json': b'{}'}, 'dotnet', False),
    ({'Game.runtimeconfig.json': b'{}', '_CommonRedist/setup.exe': pe(True),
      '_Support/helper.jar': b'fixture'}, 'native', False),
    ({'Game.exe': pe(), 'Companion.exe': pe(True)}, 'dotnet', True),
])
def test_game_execution_model_does_not_follow_auxiliary_tools(tmp_path, monkeypatch, files, expected, ambiguous):
    report = inspect(tmp_path, files, monkeypatch)
    assert report['engine']['key'] == expected
    assert any('both native and managed' in w for w in report['warnings']) is ambiguous
    if ambiguous:
        assert report['engine']['confidence'] == 35
    assert not report['executable_probe_truncated']
    for name in files:
        if name.endswith('.exe'):
            assert name.lower() in report['executables']


@pytest.mark.parametrize('files, expected, version', [
    ({'bin/Win64_Shipping_Client/TaleWorlds.MountAndBlade.dll': b'fixture',
      'Modules/Native/SubModule.xml': b'<Module/>',
      'bin/Win64_Shipping_Client/Version.xml': b'<Version><Singleplayer Value="v1.2.9"/></Version>'}, 'bannerlord', 'v1.2.9'),
    ({'bin/Gaming.Desktop.x64_Shipping_Client/TaleWorlds.MountAndBlade.dll': b'fixture',
      'Modules/Native/SubModule.xml': b'<Module/>',
      'bin/Gaming.Desktop.x64_Shipping_Client/Version.xml': b'<Version Value="v1.3.0"/>'}, 'bannerlord', 'v1.3.0'),
    ({'bin/Win64_Shipping_Client/TaleWorlds.MountAndBlade.dll': b'fixture',
      'Modules/Native/SubModule.xml': b'<Module/>',
      'bin/Win64_Shipping_Client/Version.xml': b'not xml'}, 'bannerlord', None),
    ({'bin/Win64_Shipping_Client/TaleWorlds.MountAndBlade.dll': b'fixture'}, 'native', None),
    ({'System/Gothic2.exe': pe(), 'Data/Gothic.vdf': b'fixture'}, 'zengin', None),
    ({'System/Gothic2.exe': pe()}, 'native', None),
    ({'nativePC/rom/test.arc': b'fixture'}, 'mt-framework', None),
    ({'test.arc': b'fixture'}, 'native', None),
    ({'disk/stage.arl': b'fixture', 'disk/stage.ar.00': b'fixture'}, 'hedgehog', None),
    ({'disk/stage.arl': b'fixture'}, 'native', None),
])
def test_engine_routes_require_correlated_install_evidence(tmp_path, monkeypatch, files, expected, version):
    report = inspect(tmp_path, files, monkeypatch)
    assert report['engine']['key'] == expected
    assert report['engine'].get('version') == version
    if expected != 'native':
        assert report['routes'][0]['why'].startswith('engine:')


def test_probe_budget_prioritizes_game_and_surfaces_incomplete_evidence(tmp_path, monkeypatch):
    files = {f'Editor{i}.exe': pe(True) for i in range(14)}
    files['bin/Game.exe'] = pe(True)
    report = inspect(tmp_path, files, monkeypatch)
    assert report['engine']['key'] == 'dotnet'
    assert len(report['executables']) == 12
    assert 'bin/game.exe' in report['executables']
    assert report['executable_probe_truncated']
    assert not report['index_truncated']  # file enumeration and binary probes have separate budgets
    assert 'PE inspection limited' in scan.format_report(report)
