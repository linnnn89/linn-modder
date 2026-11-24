"""Cache replacement and CLI validation, using isolated folders and an offline HTTP adapter."""
import http.client
import json
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from um import kb


def test_sync_failure_preserves_cache_and_resolve_uses_it(tmp_path, monkeypatch, capsys):
    root = tmp_path / "knowledge"
    root.mkdir()
    (root / "old.md").write_bytes(b"previous usable note")
    (root / ".synced").write_text("invalid timestamp", encoding="utf-8")
    monkeypatch.setattr(kb, "cache_root", lambda: root)
    tree = {"sha": "a" * 40, "tree": [{"type": "blob", "path": "knowledge/new.md"}]}
    rename = Path.rename
    for failure in ("empty", "truncated", "json", "shape", "download", "publish"):
        def download(url, timeout):
            if "api.github.com" in url:
                if failure == "json":
                    return b"not json"
                if failure == "shape":
                    return b"[]"
                response = {"tree": []} if failure == "empty" else dict(tree, truncated=failure == "truncated")
                return json.dumps(response).encode()
            if failure == "download":
                raise http.client.IncompleteRead(b"partial")
            return b"new note"

        def publish(path, destination):
            if failure == "publish" and path.name == "knowledge" and path.parent.name.startswith("knowledge-sync-"):
                raise OSError("simulated publication failure")
            return rename(path, destination)

        monkeypatch.setattr(kb, "_download", download)
        monkeypatch.setattr(Path, "rename", publish)
        with pytest.raises(kb.SYNC_ERRORS):
            kb.sync(quiet=True)
        assert (root / "old.md").read_bytes() == b"previous usable note"
        assert sorted(path.name for path in tmp_path.iterdir()) == ["knowledge"]
    assert kb.resolve_root(remote=True) == root
    assert "using the stale cache" in capsys.readouterr().err


def test_sync_bounds_downloads_and_publishes_one_revision(tmp_path, monkeypatch, capsys):
    root = tmp_path / "knowledge"
    root.mkdir()
    (root / "old.md").write_bytes(b"previous")
    monkeypatch.setattr(kb, "cache_root", lambda: root)
    revision = "b" * 40
    files = {"knowledge/TEMPLATE.md": b"template", "knowledge/games/a.md": b"alpha", "knowledge/index.json": b"[]"}
    lock, barrier = threading.Lock(), threading.Barrier(2)
    active, peak, started = 0, 0, 0

    def download(url, timeout):
        nonlocal active, peak, started
        assert timeout == 2
        if "api.github.com" in url:
            return json.dumps({"sha": revision, "tree": [{"type": "blob", "path": path} for path in files]}).encode()
        assert f"/{revision}/" in url
        assert (root / "old.md").read_bytes() == b"previous"
        with lock:
            active += 1
            started += 1
            peak = max(peak, active)
            first_pair = started <= 2
        try:
            if first_pair:
                barrier.wait(timeout=5)
            return files[url.split(f"/{revision}/", 1)[1]]
        finally:
            with lock:
                active -= 1

    monkeypatch.setattr(kb, "_download", download)
    assert kb.sync(quiet=True, timeout=2, workers=2) == root
    assert peak == 2
    assert not (root / "old.md").exists()
    for path, content in files.items():
        assert (tmp_path / path).read_bytes() == content
    assert float((root / ".synced").read_text()) > 0
    assert sorted(path.name for path in tmp_path.iterdir()) == ["knowledge"]
    captured = capsys.readouterr()
    assert not captured.out and "3 files" in captured.err


def test_kb_check_rejects_missing_or_empty_inputs(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(kb, "local_root", lambda: None)
    empty = tmp_path / "empty"
    empty.mkdir()
    note = tmp_path / "valid.md"
    note.write_text("---\nkind: technique\ntitle: Fixture\ntags: [fixture]\ndate: 2026-11-13\nagents: [Fixture]\n---\n# Fixture\n", encoding="utf-8")
    for root, paths, index in [(None, [], False), (str(empty), [], False),
                                (str(tmp_path / "missing"), [], False), (None, [str(note)], True),
                                (None, [str(tmp_path / "missing.md")], False)]:
        with pytest.raises(SystemExit) as result:
            kb.main(SimpleNamespace(cmd="check", root=root, paths=paths, index=index))
        assert result.value.code == 1
        assert "PASS" not in capsys.readouterr().out
    with pytest.raises(SystemExit) as result:
        kb.main(SimpleNamespace(cmd="check", root=None, paths=[str(note)], index=False))
    assert result.value.code == 0
    assert "PASS: 1 notes checked" in capsys.readouterr().out
