"""Versioned manuals available both from a checkout and an installed wheel."""
from pathlib import Path
import shutil

from um.contracts import ToolError

KINDS = ("skills", "knowledge")


def root(kind: str) -> Path:
    if kind not in KINDS:
        raise ToolError("invalid_resource", f"Unknown resource collection: {kind}")
    packaged = Path(__file__).parent / "data" / kind
    checkout = Path(__file__).resolve().parent.parent / kind
    for candidate in (packaged, checkout):
        if candidate.is_dir():
            return candidate
    raise ToolError("missing_resources", "Reinstall linn-modder: bundled manuals are missing.")


def read(kind: str, name: str) -> str:
    base = root(kind).resolve()
    path = (base / name).resolve()
    if not path.is_relative_to(base) or path.suffix not in (".md", ".json"):
        raise ToolError("invalid_resource", "Choose a Markdown or JSON file inside the collection.")
    if kind == "skills" and not path.is_file():
        # Existing MCP/CLI callers can still read the former topic paths.
        relative = path.relative_to(base)
        if relative.parts and relative.parts[0] != "linn-modder":
            candidate = base / "linn-modder" / relative
            if candidate.name == "SKILL.md":
                candidate = candidate.with_name("GUIDE.md")
            candidate = candidate.resolve()
            if not candidate.is_relative_to(base):
                raise ToolError("invalid_resource", "Choose a file inside the collection.")
            path = candidate
    if not path.is_file():
        raise ToolError("not_found", f"Resource not found: {name}")
    if path.stat().st_size > 256 * 1024:
        raise ToolError("resource_too_large", "Resource exceeds 256 KiB.")
    return path.read_text(encoding="utf-8")


def export(destination: Path) -> dict:
    if destination.exists():
        raise ToolError("already_exists", "Export destination must not already exist.")
    sources = {kind: root(kind) for kind in KINDS}
    destination.mkdir(parents=True)
    try:
        for kind, source in sources.items():
            shutil.copytree(source, destination / kind)
    except Exception:
        shutil.rmtree(destination)
        raise
    return {"path": str(destination), "collections": list(KINDS)}
