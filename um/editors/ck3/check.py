"""Read-only CK3 format checks and Tiger JSON report import; no script parser or runner."""
import codecs
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re

from um.contracts import ToolError
from um.workspace import is_link

MAX_FILE = 16 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_ENTRIES = 10000


def input_hints() -> dict:
    return {
        "source": {"description": "CK3 content directory containing descriptor.mod, e.g. project/mod/my_mod; not the staging or game root."},
        "tiger_report": {"description": "Optional existing UTF-8 JSON array from ck3-tiger --json. Paths in it are labels only; freshness/version are not verified."},
        "limit": {"minimum": 1, "maximum": 100},
        "offset": {"minimum": 0},
    }


def _read(ws, path: Path) -> bytes:
    if is_link(path):
        raise ToolError("linked_tree", "CK3 checks require files without links/junctions.")
    path = ws.path(path, exists=True)
    if not path.is_file():
        raise ToolError("invalid_path", "Expected a file.")
    with path.open("rb") as stream:
        raw = stream.read(MAX_FILE + 1)
    if len(raw) > MAX_FILE:
        raise ToolError("file_too_large", "CK3 check input exceeds 16 MiB; select a smaller input.")
    return raw


def _localization_files(root: Path):
    if is_link(root):
        raise ToolError("linked_tree", "Localization directory must not be a link/junction.")
    if not root.exists():
        return
    if not root.is_dir():
        raise ToolError("invalid_path", "localization must be a directory.")
    count = 0
    def denied(error):
        raise error
    for parent, dirs, files in os.walk(root, onerror=denied):
        dirs.sort()
        for name in sorted(dirs + files):
            count += 1
            if count > MAX_ENTRIES:
                raise ToolError("check_too_large", "Localization tree exceeds 10,000 entries.")
            if is_link(Path(parent) / name):
                raise ToolError("linked_tree", "Localization tree must not contain links/junctions.")
        for name in sorted(files):
            path = Path(parent) / name
            if path.suffix.lower() in (".yml", ".yaml"):
                yield path


def _tiger_reports(raw: bytes) -> list[dict]:
    try:
        reports = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(reports, list):
            raise ValueError("expected an array")
        result = []
        for report in reports:
            severity = report["severity"]
            if severity not in ("fatal", "error", "warning", "untidy", "tips"):
                raise ValueError("unknown severity")
            if not all(isinstance(report[key], str) for key in ("key", "message")):
                raise ValueError("expected key/message strings")
            pointers = report["locations"]
            if not isinstance(pointers, list):
                raise ValueError("expected locations array")
            locations = []
            for pointer in pointers:
                if not isinstance(pointer["path"], str):
                    raise ValueError("expected location path")
                for key in ("linenr", "column"):
                    value = pointer.get(key)
                    if value is not None and (type(value) is not int or value < 1):
                        raise ValueError("expected a positive location or null")
                locations.append({"path": pointer["path"], "line": pointer.get("linenr"),
                                  "column": pointer.get("column"), "from": pointer.get("from"),
                                  "fullpath": pointer.get("fullpath"), "tag": pointer.get("tag")})
            result.append({"source": "tiger", "severity": severity, "code": report["key"],
                           "message": report["message"], "locations": locations,
                           "info": report.get("info"), "confidence": report.get("confidence")})
        return result
    except (ValueError, KeyError, TypeError) as exc:
        raise ToolError("invalid_tiger_report", f"Expected a UTF-8 ck3-tiger --json report array: {exc}") from exc


def check(ws, source: str, tiger_report: str, limit: int, offset: int) -> dict:
    if not 1 <= limit <= 100 or offset < 0:
        raise ToolError("invalid_page", "limit must be 1..100; offset must be >=0.")
    root = ws.path(source, exists=True)
    if not root.is_dir():
        raise ToolError("invalid_path", "source must be the CK3 content directory containing descriptor.mod.")
    diagnostics = []
    checked, total_bytes = 0, 0

    def issue(path, code, message, line=None, severity="error"):
        diagnostics.append({"source": "local", "severity": severity, "code": code, "message": message,
                            "locations": [{"path": path.relative_to(root).as_posix(), "line": line, "column": None}]})

    def read_text(path):
        nonlocal checked, total_bytes
        raw = _read(ws, path)
        checked += 1
        total_bytes += len(raw)
        if total_bytes > MAX_TOTAL:
            raise ToolError("check_too_large", "Checked text exceeds 128 MiB.")
        try:
            return raw, raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            issue(path, "invalid_utf8", "Save this CK3 file as UTF-8; localization also requires BOM.",
                  exc.object[:exc.start].count(b"\n") + 1)
            return raw, None

    descriptor = root / "descriptor.mod"
    if not descriptor.exists():
        issue(descriptor, "missing_descriptor", "Select the content root or add its descriptor.mod; external .mod registration is a separate file.")
    else:
        _, text = read_text(descriptor)
        if text is not None and not any(line.strip() and not line.lstrip().startswith("#") for line in text.splitlines()):
            issue(descriptor, "empty_descriptor", "descriptor.mod contains no settings.", 1)
    if (root / "localisation").is_dir():
        issue(root / "localisation", "localization_directory", "CK3 uses localization/, not localisation/; check the intended content root.", severity="warning")
    for path in _localization_files(root / "localization"):
        raw, text = read_text(path)
        if text is None:
            continue
        if not raw.startswith(codecs.BOM_UTF8):
            issue(path, "missing_bom", "Save localization as UTF-8 with BOM.", 1)
        name = re.fullmatch(r".+_l_([A-Za-z][A-Za-z0-9_]*)\.yml", path.name)
        if name is None:
            issue(path, "localization_filename", "Use <name>_l_<language>.yml; .yaml is not the CK3 localization suffix.")
        first = next(((i, line.strip()) for i, line in enumerate(text.splitlines(), 1)
                      if line.strip() and not line.lstrip().startswith("#")), (1, ""))
        header = re.fullmatch(r"l_([A-Za-z][A-Za-z0-9_]*):\s*(?:#.*)?", first[1])
        if header is None:
            issue(path, "localization_header", "First non-comment line must be l_<language>:.", first[0])
        elif name is not None and name[1] != header[1]:
            issue(path, "localization_language", f"Filename selects {name[1]}, but header selects {header[1]}.", first[0])

    tiger = {"status": "not-provided", "freshness": "not-verified"}
    if tiger_report:
        report_path = ws.path(tiger_report, exists=True)
        raw = _read(ws, report_path)
        diagnostics.extend(_tiger_reports(raw))
        tiger.update(status="imported", path=str(report_path), sha256=hashlib.sha256(raw).hexdigest())
    counts = dict(Counter(item["severity"] for item in diagnostics))
    end = min(offset + limit, len(diagnostics))
    return {"source": str(root), "passed": not any(counts.get(s) for s in ("error", "fatal")),
            "verification": "not-tested-in-game", "files_checked": checked,
            "checks": ["descriptor_presence_utf8_nonempty", "localization_filename_bom_header"],
            "not_checked": ["descriptor_syntax_and_registration", "script_semantics", "runtime_behavior"],
            "tiger": tiger, "counts": counts, "total": len(diagnostics),
            "diagnostics": diagnostics[offset:end], "next_offset": end if end < len(diagnostics) else None}
