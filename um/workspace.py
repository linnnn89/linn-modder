"""Explicit filesystem boundaries for agent-facing operations.

These checks prevent accidental traversal; they are not an OS sandbox against a
concurrent, hostile local process. Game roots are read-only through this API.
"""
from pathlib import Path
import stat

from um.contracts import ToolError


def is_link(path: Path) -> bool:
    """Include Windows junctions/reparse points on Python 3.10 and newer."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


class Workspace:
    def __init__(self, root: str | Path, game_roots: tuple[str | Path, ...] = ()):
        self.root = Path(root).expanduser().resolve()
        if not self.root.is_dir():
            raise ToolError("invalid_workspace", "Workspace must be an existing directory.")
        self.game_roots = tuple(Path(p).expanduser().resolve() for p in game_roots)
        if any(not p.is_dir() for p in self.game_roots):
            raise ToolError("invalid_game_root", "Each game root must be an existing directory.")

    def path(self, value: str | Path, *, write: bool = False, exists: bool = False) -> Path:
        p = Path(value).expanduser()
        p = (self.root / p if not p.is_absolute() else p).resolve()
        roots = (self.root,) if write else (self.root, *self.game_roots)
        if not any(p.is_relative_to(r) for r in roots):
            raise ToolError("path_outside_roots", "Path is outside the configured workspace/game roots.")
        if write and any(p.is_relative_to(r) for r in self.game_roots):
            raise ToolError("game_root_read_only", "Game roots are read-only; write to a staging project.")
        if exists and not p.exists():
            raise ToolError("not_found", f"Path does not exist: {p}")
        return p

    def check_tree(self, root: Path) -> None:
        """Reject symlinks/junctions escaping roots before recursive readers run."""
        import os
        for parent, dirs, files in os.walk(root, followlinks=False):
            for name in dirs + files:
                candidate = Path(parent) / name
                self.path(candidate, exists=True)
                if is_link(candidate):
                    raise ToolError("linked_tree", "Recursive operations require a tree without links/junctions.")
