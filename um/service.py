"""Shared application service. No MCP imports, shell parsing or stdout logging."""
import hashlib
import inspect
import mimetypes
import logging
import re
import subprocess
import threading
import uuid
from pathlib import Path

from um import backup, doctor, kb, projects, resources, scan
from um.contracts import Artifact, ErrorInfo, Result, ToolError
from um.workspace import Workspace


class Service:
    def __init__(self, workspace: str | Path, game_roots: tuple[str | Path, ...] = (),
                 allow_input: bool = False, windows=None):
        self.workspace = Workspace(workspace, game_roots)
        self.allow_input = allow_input
        self._windows = windows
        self._lock = threading.RLock()

    @property
    def windows(self):
        if self._windows is None:
            from um.windows_backend import WindowsBackend
            self._windows = WindowsBackend()
        return self._windows

    def tools(self) -> dict:
        names = ["environment_check", "game_profiles", "game_scan", "knowledge_search",
                 "manual_read", "manuals_export", "project_create", "image_prepare",
                 "backup_create", "backup_list", "backup_verify", "backup_restore", "windows_list", "window_capture"]
        if self.allow_input:
            names.append("window_input")
        return {name: getattr(self, name) for name in names}

    def invoke(self, name: str, arguments: dict | None = None) -> Result:
        try:
            fn = self.tools().get(name)
            if fn is None:
                raise ToolError("unknown_tool", "Tool is unknown or disabled in this configuration.")
            arguments = {} if arguments is None else arguments
            if not isinstance(arguments, dict):
                raise ToolError("invalid_arguments", "Arguments must be a JSON object.")
            try:
                bound = inspect.signature(fn).bind(**arguments)
            except TypeError as exc:
                raise ToolError("invalid_arguments", str(exc)) from exc
            for key, value in bound.arguments.items():
                expected = inspect.signature(fn).parameters[key].annotation
                if expected in (str, int, bool) and type(value) is not expected:
                    raise ToolError("invalid_arguments", f"{key} must be {expected.__name__}.")
            # Legacy modules contain mutable caches; serialize calls within one service.
            # MCP executes this on a worker thread so protocol handling stays responsive.
            with self._lock:
                return fn(**arguments)
        except ToolError as exc:
            return Result(False, error=ErrorInfo(exc.code, str(exc)))
        except (ValueError, TypeError) as exc:
            return Result(False, error=ErrorInfo("invalid_arguments", str(exc)))
        except subprocess.TimeoutExpired:
            return Result(False, error=ErrorInfo("timeout", "The external tool exceeded its time limit."))
        except (OSError, RuntimeError) as exc:
            return Result(False, error=ErrorInfo("operation_failed", str(exc)))
        except SystemExit as exc:
            # Legacy CLI helpers call die(); never let one terminate an MCP session.
            return Result(False, error=ErrorInfo("operation_failed", f"Legacy backend exited ({exc.code}); see stderr."))
        except Exception:
            logging.getLogger(__name__).exception("Unexpected failure in tool %s", name)
            return Result(False, error=ErrorInfo("internal_error", "Unexpected backend failure; see stderr."))

    def close(self):
        with self._lock:
            if self._windows is not None:
                self._windows.close()

    def _artifact(self, path: Path, role: str = "output") -> Artifact:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return Artifact(str(path), mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                        path.stat().st_size, digest.hexdigest(), role)

    def environment_check(self) -> Result:
        """Report dependency and platform capabilities without installing anything."""
        data = doctor.inspect_environment()
        data["workspace"] = str(self.workspace.root)
        data["input_enabled"] = self.allow_input
        return Result(True, data)

    def game_profiles(self) -> Result:
        """List game-specific routes, localization rules and current support levels."""
        return Result(True, {"profiles": projects.profiles()})

    def game_scan(self, path: str) -> Result:
        """Identify a game in the workspace or an explicitly configured read-only game root."""
        target = self.workspace.path(path, exists=True)
        if not target.is_dir():
            raise ToolError("invalid_path", "Game path must be a directory.")
        self.workspace.check_tree(target)
        return Result(True, scan.scan(str(target)))

    def knowledge_search(self, query: str, limit: int = 10) -> Result:
        """Search bundled field notes offline; no network synchronization occurs."""
        if not 1 <= limit <= 50:
            raise ToolError("invalid_limit", "Limit must be 1..50.")
        return Result(True, {"matches": kb.search(resources.root("knowledge"), query.split(), limit=limit)})

    def manual_read(self, collection: str, path: str) -> Result:
        """Read a bundled skill or field note; paths are relative to skills/ or knowledge/."""
        return Result(True, {"collection": collection, "path": path, "text": resources.read(collection, path)})

    def manuals_export(self, destination: str) -> Result:
        """Copy bundled skills and knowledge into a new workspace folder, without symlinks."""
        return Result(True, resources.export(self.workspace.path(destination, write=True)))

    def project_create(self, destination: str, profile: str, name: str, game_version: str = "unknown") -> Result:
        """Create an anime-mod staging project; game installation directories stay read-only."""
        path = self.workspace.path(destination, write=True)
        data = projects.create(path, profile, name, game_version)
        return Result(True, data, [self._artifact(path / "project.json")])

    def image_prepare(self, source: str, output: str, width: int, height: int,
                      mode: str = "contain", anchor: str = "center") -> Result:
        """Prepare an RGBA PNG with explicit dimensions/crop; does not claim engine-ready conversion."""
        src = self.workspace.path(source, exists=True)
        dst = self.workspace.path(output, write=True)
        data = projects.prepare_image(src, dst, width, height, mode, anchor)
        return Result(True, data, [self._artifact(dst)])

    def backup_create(self, source: str, name: str, note: str = "") -> Result:
        """Snapshot a bounded source folder into workspace/.um/backups with a manifest."""
        source_path = self.workspace.path(source, exists=True)
        if not source_path.is_dir():
            raise ToolError("invalid_path", "Backup source must be a directory.")
        self.workspace.check_tree(source_path)
        store = self._backup_store(name)
        # Avoid recursively snapshotting the store itself, including the workspace root.
        if store.is_relative_to(source_path):
            raise ToolError("recursive_backup", "Back up a specific subfolder, not an ancestor of .um.")
        path = backup.create(str(source_path), name, note, store=store, quiet=True)
        return Result(True, {"snapshot": str(path)}, [self._artifact(path)])

    def _backup_store(self, name: str) -> Path:
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", name):
            raise ToolError("invalid_name", "Backup ID must use 1..64 ASCII letters, digits, _ or -.")
        store = self.workspace.path(".um", write=True)
        self.workspace.path(backup._root(name, store), write=True)
        return store

    def _backup_snapshot(self, name: str, snapshot: str) -> Path:
        store = self._backup_store(name)
        if not snapshot:
            paths = backup.snapshots(name, store=store)
            if not paths:
                raise ToolError("not_found", f"No snapshots for {name}")
            snapshot = str(paths[-1])
        path = self.workspace.path(snapshot, exists=True)
        folder = self.workspace.path(backup._root(name, store), write=True)
        if not path.is_relative_to(folder) or not path.is_file():
            raise ToolError("invalid_snapshot", "Choose a snapshot inside this workspace's named backup store.")
        return path

    def backup_list(self, name: str) -> Result:
        """List snapshots for a backup ID in this workspace, without writing files."""
        store = self._backup_store(name)
        folder = self.workspace.path(backup._root(name, store), write=True)
        if folder.exists():
            self.workspace.check_tree(folder)
        return Result(True, {"snapshots": [
            {"path": str(path), "size": path.stat().st_size}
            for path in backup.snapshots(name, store=store)]})

    def backup_verify(self, name: str, snapshot: str = "") -> Result:
        """Verify all archive paths, sizes and checksums; default to the latest named snapshot."""
        path = self._backup_snapshot(name, snapshot)
        manifest = backup.verify_snapshot(path)
        return Result(True, {"snapshot": str(path), "files": len(manifest["files"]),
                             "bytes": sum(entry["size"] for entry in manifest["files"].values()), "valid": True})

    def backup_restore(self, name: str, target: str, snapshot: str = "",
                       clean: bool = False, apply: bool = False) -> Result:
        """Preview a workspace restore. Set apply=true to restore after reviewing; save an undo snapshot first."""
        path = self._backup_snapshot(name, snapshot)
        destination = self.workspace.path(target, write=True)
        store = self._backup_store(name)
        self._backup_store(name[:52] + "-pre-restore")
        if (store.is_relative_to(destination) or destination.is_relative_to(store)
                or any(root.is_relative_to(destination) for root in self.workspace.game_roots)):
            raise ToolError("invalid_target", "Restore target must not overlap the snapshot store or game roots.")
        if destination.exists():
            self.workspace.check_tree(destination)
        if not apply:
            return Result(True, backup.diff(name, str(destination), str(path), store=store)
                          | {"applied": False, "clean": clean})
        result = backup.restore(name, str(destination), str(path), clean=clean, yes=True, store=store, quiet=True)
        artifacts = [self._artifact(Path(result["undo_snapshot"]), "undo")] if result["undo_snapshot"] else []
        return Result(True, result | {"applied": True, "clean": clean}, artifacts)

    def windows_list(self) -> Result:
        """List visible Windows processes with exact process and window IDs."""
        return Result(True, {"windows": self.windows.list_windows()})

    def window_capture(self, hwnd: int) -> Result:
        """Capture one window; return a saved PNG plus a bounded preview suitable for vision agents."""
        if hwnd <= 0:
            raise ToolError("invalid_window", "Window handle must be positive.")
        from PIL import Image
        destination = self.workspace.path(f".um/captures/{uuid.uuid4().hex}.png", write=True)
        self.windows.capture(hwnd, destination)
        preview = destination.with_name(destination.stem + "_preview.png")
        with Image.open(destination) as im:
            im.thumbnail((1024, 1024))
            im.convert("RGB").save(preview, "PNG")
            size = list(im.size)
        return Result(True, {"hwnd": hwnd, "preview_size": size},
                      [self._artifact(destination), self._artifact(preview, "preview")])

    def window_input(self, pid: int, action: str, x: int = 0, y: int = 0,
                     key: str = "", text: str = "") -> Result:
        """Send one bounded action to an exact PID. Focus is explicit; automatic focus retry is disabled."""
        if not self.allow_input:
            raise ToolError("input_disabled", "Start the server with --allow-input after the user agrees.")
        if pid <= 0:
            raise ToolError("invalid_pid", "PID must be positive.")
        if action == "focus":
            command = "focus"
        elif action == "click" and 0 <= x <= 32767 and 0 <= y <= 32767:
            command = f"click {x} {y}"
        elif action == "key" and re.fullmatch(r"(?:0x[0-9a-fA-F]{1,2}|[0-9]{1,3})", key):
            if not 1 <= int(key, 16 if key.startswith("0x") else 10) <= 255:
                raise ToolError("invalid_key", "Virtual key must be 1..255.")
            command = f"key {key} tap"
        elif action == "type" and 0 < len(text) <= 256 and not any(ord(c) < 32 for c in text):
            command = "type " + text
        else:
            raise ToolError("invalid_action", "Use focus, click, key or type with bounded arguments.")
        reply = self.windows.input(pid, command)
        if reply != "ok":
            raise ToolError("input_failed", reply)
        return Result(True, {"pid": pid, "action": action})
