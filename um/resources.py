"""Versioned manuals available both from a checkout and an installed wheel."""
from pathlib import Path
import re
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


def outline(text: str) -> list[dict]:
    """ATX Markdown sections with inclusive source lines; ignore YAML and fenced code."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].lstrip("\ufeff").strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
        if end is not None:
            start = end + 1
    sections, parents = [], []
    fence = None
    for index in range(start, len(lines)):
        line = lines[index]
        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*", line):
                fence = None
            continue
        marker = re.match(r" {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker and not (marker[1][0] == "`" and "`" in marker[2]):
            fence = (marker[1][0], len(marker[1]))
            continue
        heading = re.match(r" {0,3}(#{1,6})(?:[ \t]+(.*)|$)", line)
        if heading is None:
            continue
        level = len(heading[1])
        while parents and parents[-1]["level"] >= level:
            parents.pop()["end_line"] = index
        section = {"heading": re.sub(r"(?:^|[ \t]+)#+[ \t]*$", "", heading[2] or "").strip(),
                   "level": level, "start_line": index + 1, "end_line": len(lines)}
        sections.append(section)
        parents.append(section)
    return sections


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
