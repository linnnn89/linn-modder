"""Explicit filesystem boundaries for agent-facing operations.

These checks prevent accidental traversal; they are not an OS sandbox against a
concurrent, hostile local process. Game roots are read-only through this API.
"""
from pathlib import Path

from um.contracts import ToolError


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
                if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
                    raise ToolError("linked_tree", "Recursive operations require a tree without links/junctions.")
