"""Bounded TKEditor JSON editing and external Portraits preparation.

No executable scripts, SQL from callers, bundle writer or game installation writes.
The SQLite catalog is a replaceable snapshot, never the source of truth for writes.
"""
import hashlib
import json
import os
import re
import shutil
import sqlite3
import tempfile
import uuid
from collections import Counter
from contextlib import closing
from pathlib import Path

from um.contracts import ToolError

MAX_FILE = 64 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
PORTRAITS = {"1000x1400": (1000, 1400), "1024x1024": (1024, 1024), "260x340": (260, 340)}
TEXT_FIELDS = {"name", "surname", "word", "description", "remark"}
STATS = {"rule", "force", "wise", "politics", "charm", "will"}
LABELS = {"id": "ID", "name": "名/名称", "surname": "姓", "word": "字", "icon": "头像资源引用（只读）",
          "description": "说明", "remark": "备注", "rule": "统率", "force": "武力", "wise": "智略",
          "politics": "政务", "charm": "魅力", "will": "意志"}
MARKER = ".tkeditor-project.json"
DISPLAY_NAME_LIMIT = 80
OPTION_NAME_LIMIT = DISPLAY_NAME_LIMIT + 20  # um_ + 16 hex digits + _


def fail(code, message):
    raise ToolError(code, message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("invalid_json", f"Duplicate JSON key: {key}")
        if isinstance(value, str) and any(ord(c) < 32 and c not in "\n\r\t" for c in value):
            fail("invalid_json", "Unsupported control character in JSON string.")
        result[key] = value
    return result


def load(raw):
    try:
        # Shipped TKEditor tables contain literal CR/LF inside quoted text. Accept
        # that observed dialect only; writes use standard escaped JSON strings.
        return json.loads(raw.decode("utf-8-sig"), strict=False, object_pairs_hook=object_pairs,
                          parse_constant=lambda value: fail("invalid_json", f"Non-finite number: {value}"))
    except (ValueError, UnicodeError, RecursionError) as exc:
        fail("invalid_json", str(exc))


def read(path):
    if not path.is_file() or path.stat().st_size > MAX_FILE:
        fail("file_limit", "Choose a JSON file of at most 64 MiB.")
    raw = path.read_bytes()
    if len(raw) > MAX_FILE:
        fail("file_limit", "JSON file exceeds 64 MiB.")
    return raw


def rows_from(raw):
    rows = load(raw)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        fail("unsupported_table", "Expected a JSON array of objects; no conversion was attempted.")
    if len(rows) > 100000:
        fail("row_limit", "At most 100000 rows per table.")
    for row in rows:
        if "id" in row:
            if not isinstance(row["id"], str) or not row["id"]:
                fail("invalid_id", "Record IDs must be nonempty strings.")
    # Relationship tables repeat an ID across stories/conditions. Preserve every
    # row, and refuse ID-only edits when more than one row matches.
    return rows


def identifier(value):
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", value):
        fail("invalid_name", "Catalog names use 1..64 ASCII letters, digits, _ or -.")
    return value


def catalog_path(ws, catalog, exists=False):
    return ws.path(f".um/tkeditor/catalogs/{identifier(catalog)}.sqlite", write=True, exists=exists)


def connect(ws, catalog):
    path = catalog_path(ws, catalog, True)
    con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA query_only=ON")
    if con.execute("PRAGMA user_version").fetchone()[0] not in (1, 2):
        con.close()
        fail("invalid_catalog", "Rebuild this catalog with tk_index.")
    return con


def source_files(ws, source):
    root = ws.path(source, exists=True)
    if not root.is_dir():
        fail("invalid_path", "Source must be a TKEditor JSON/Mod directory.")
    ws.check_tree(root)
    files = sorted(p for p in root.glob("*.json") if not p.name.startswith(("_", ".")))
    if not (root / "Hero.json").is_file():
        fail("unsupported_source", "Choose the directory containing Hero.json, not the game root.")
    if len(files) > 256 or sum(p.stat().st_size for p in files) > MAX_TOTAL:
        fail("source_limit", "At most 256 JSON files / 256 MiB per source.")
    return root, files


def editable(table, field):
    base = re.sub(r"(Tc|En|Jp|Kr|Other)$", "", field)
    return base in TEXT_FIELDS or (table == "Hero" and field in STATS)


def fingerprint(path):
    info = path.stat()
    return json.dumps([info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_dev, info.st_ino])


def index(ws, source, catalog):
    root, files = source_files(ws, source)
    destination = catalog_path(ws, catalog)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=destination.parent, suffix=".sqlite")
    os.close(fd)
    temp = Path(temporary)
    counts, skipped = {}, []
    try:
        with closing(sqlite3.connect(temp)) as con, con:
            con.executescript("""
                PRAGMA user_version=2;
                CREATE TABLE sources (name TEXT PRIMARY KEY, path TEXT, sha256 TEXT, schema_json TEXT, count INTEGER, duplicate_ids INTEGER, fingerprint TEXT);
                CREATE TABLE records (table_name TEXT, record_id TEXT, ordinal INTEGER, label TEXT, search TEXT, body TEXT,
                                      PRIMARY KEY(table_name,ordinal));
                CREATE INDEX record_ids ON records(table_name,record_id,ordinal);
            """)
            for path in files:
                stamp = fingerprint(path)
                raw = read(path)
                if fingerprint(path) != stamp:
                    fail("source_changed", "Source changed while indexing; rebuild the catalog.")
                try:
                    rows = rows_from(raw)
                except ToolError as exc:
                    if exc.code != "unsupported_table":
                        raise
                    skipped.append(path.name)
                    continue
                schema = {}
                for ordinal, row in enumerate(rows):
                    for field, value in row.items():
                        schema.setdefault(field, set()).add(type(value).__name__)
                    label = str(row.get("surname", "")) + str(row.get("name", ""))
                    # Chinese substring search works without language tokenizers. The
                    # database bounds table/ID access; callers never submit SQL.
                    search = (label + "\n" + "\n".join(
                        str(v)[:2048] for v in row.values() if isinstance(v, (str, int)))).casefold()
                    con.execute("INSERT INTO records VALUES (?,?,?,?,?,?)", (
                        path.stem, row.get("id", f"@{ordinal}"), ordinal, label, search,
                        json.dumps(row, ensure_ascii=False, allow_nan=False)))
                fields = {key: sorted(value) for key, value in schema.items()}
                duplicates = sum(count > 1 for count in Counter(row["id"] for row in rows if "id" in row).values())
                con.execute("INSERT INTO sources VALUES (?,?,?,?,?,?,?)", (
                    path.stem, str(path), digest(raw), json.dumps(fields), len(rows), duplicates, stamp))
                counts[path.stem] = len(rows)
        os.replace(temp, destination)
    finally:
        temp.unlink(missing_ok=True)
    return {"catalog": catalog, "source": str(root), "tables": len(counts),
            "records": sum(counts.values()), "skipped": skipped[:20], "skipped_count": len(skipped),
            "search_characters_per_field": 2048, "next": "tk_tables, then tk_query; request only needed fields"}


def table_source(ws, con, table, catalog, verify_content=False):
    entry = con.execute("SELECT * FROM sources WHERE name=?", (table,)).fetchone()
    if entry is None:
        raise ToolError("unknown_table", "Use tk_tables to select a table.",
                        recovery={"tool": "tk_tables", "arguments": {"catalog": catalog, "limit": 20}})
    path = ws.path(entry["path"], exists=True)
    # Read operations serve a snapshot while the source's filesystem identity and
    # timestamps match. Editing always verifies bytes, even if metadata matches.
    version = con.execute("PRAGMA user_version").fetchone()[0]
    if not verify_content and version == 2 and fingerprint(path) == entry["fingerprint"]:
        return entry, path, None
    raw = read(path)
    if digest(raw) != entry["sha256"]:
        raise ToolError("stale_catalog", "Source changed since indexing. Refresh, then query/preview again.",
                        recovery={"tool": "tk_index", "arguments": {"source": str(path.parent), "catalog": catalog}})
    return entry, path, raw


def page(limit, offset):
    if not 1 <= limit <= 50 or not 0 <= offset <= 100000:
        fail("invalid_page", "limit must be 1..50; offset must be 0..100000.")


def tables(ws, catalog, table, limit, offset):
    page(limit, offset)
    with closing(connect(ws, catalog)) as con:
        if table:
            entry, _, _ = table_source(ws, con, table, catalog)
            schema = json.loads(entry["schema_json"])
            fields = [{"field": k, "label": LABELS.get(k, k), "types": v, "editable": editable(table, k)}
                      for k, v in schema.items()]
            return {"table": table, "rows": entry["count"], "sha256": entry["sha256"],
                    "duplicate_ids": entry["duplicate_ids"],
                    "fields": fields[offset:offset + limit],
                    "next_offset": offset + limit if offset + limit < len(fields) else None}
        entries = con.execute("SELECT name,count FROM sources ORDER BY name LIMIT ? OFFSET ?", (limit + 1, offset)).fetchall()
        return {"tables": [{"table": row["name"], "rows": row["count"]} for row in entries[:limit]],
                "next_offset": offset + limit if len(entries) > limit else None, "snapshot": True}


def projection(fields, schema):
    selected = [f.strip() for f in fields.split(",") if f.strip()] if fields else [
        f for f in ("id", "surname", "name", "icon", "description") if f in schema]
    if not selected:
        selected = list(schema)[:5]
    if len(selected) > 8 or any(f not in schema for f in selected):
        fail("invalid_fields", "Select up to 8 existing fields using tk_tables; full-row dumps are disabled.")
    return selected


def query(ws, catalog, table, query_text, record_id, fields, limit, offset):
    page(limit, offset)
    if len(query_text) > 128 or len(record_id) > 128 or len(fields) > 512:
        fail("invalid_query", "Query/ID <=128 characters; fields <=512.")
    with closing(connect(ws, catalog)) as con:
        entry, _, _ = table_source(ws, con, table, catalog)
        selected = projection(fields, json.loads(entry["schema_json"]))
        sql = "SELECT record_id,ordinal,body FROM records WHERE table_name=?"
        parameters = [table]
        if record_id:
            sql += " AND record_id=?"
            parameters.append(record_id)
        if query_text:
            sql += " AND instr(search,?)>0"
            parameters.append(query_text.casefold())
        sql += " ORDER BY ordinal LIMIT ? OFFSET ?"
        entries = con.execute(sql, parameters + [limit + 1, offset]).fetchall()
        records, truncated, used = [], [], 0
        for entry_row in entries[:limit]:
            body = json.loads(entry_row["body"])
            record = {"record_id": entry_row["record_id"], "row_index": entry_row["ordinal"], "values": {}}
            for field in selected:
                value = body.get(field)
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                if isinstance(value, str) and len(value) > 512:
                    value = value[:512] + "…"
                    truncated.append({"record_id": entry_row["record_id"], "field": field})
                record["values"][field] = value
            size = len(json.dumps(record, ensure_ascii=False))
            if records and used + size > 12000:
                break
            records.append(record)
            used += size
        more = len(entries) > len(records)
        return {"table": table, "sha256": entry["sha256"], "records": records,
                "truncated": truncated[:400], "next_offset": offset + len(records) if more else None}


def project(ws, source, destination):
    root, files = source_files(ws, source)
    target = ws.path(destination, write=True)
    if target.exists() or root.is_relative_to(target) or target.is_relative_to(root):
        fail("invalid_target", "Choose a new, non-overlapping workspace directory.")
    # Validate everything before creating a project, including duplicate keys/IDs.
    for path in files:
        rows_from(read(path))
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(dir=target.parent, prefix=".tk-stage-"))
    try:
        for path in files:
            shutil.copyfile(path, temp / path.name)
        (temp / MARKER).write_text(json.dumps({"adapter": 1, "source": str(root),
            "assets_copied": False}, ensure_ascii=False), encoding="utf-8")
        temp.rename(target)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return {"project": str(target), "json_files": len(files), "assets_copied": False,
            "verification": "data-only-not-tested-in-editor-or-game",
            "next": "tk_index this project before editing. Import its JSON with TKEditor; retain original asset dependencies."}


def read_field(ws, catalog, table, record_id, field, start, max_chars, row_index):
    if not 0 <= start <= MAX_FILE or not 1 <= max_chars <= 2000 or row_index < -1:
        fail("invalid_range", "start >=0, max_chars 1..2000; row_index >=0 or -1 (unique ID).")
    with closing(connect(ws, catalog)) as con:
        table_source(ws, con, table, catalog)
        entries = con.execute("""SELECT body FROM records WHERE table_name=? AND record_id=?
            AND (?=-1 OR ordinal=?) LIMIT 2""", (table, record_id, row_index, row_index)).fetchall()
        if len(entries) != 1:
            fail("ambiguous_record" if entries else "unknown_record", "Choose one record; repeated IDs require row_index from tk_query.")
        body = json.loads(entries[0]["body"])
        if field not in body or not isinstance(body[field], str):
            fail("invalid_field", "Choose an existing text field with tk_tables.")
        value = body[field]
        if start > len(value):
            fail("invalid_range", "start exceeds the field's character count.")
        end = min(len(value), start + max_chars)
        return {"record_id": record_id, "field": field, "text": value[start:end], "start": start,
                "total_characters": len(value), "next_start": end if end < len(value) else None}


def validate_changes(table, row, changes):
    if not isinstance(changes, dict) or not 1 <= len(changes) <= 8:
        fail("invalid_changes", "Supply 1..8 explicit field/value changes for one existing record.")
    diffs = []
    for field, value in changes.items():
        if field not in row or not editable(table, field):
            fail("protected_field", "Only existing display text and Hero's six base stats are writable. IDs/references/code are protected.")
        if type(value) is not type(row[field]) or not isinstance(value, str):
            fail("invalid_value", "TKEditor writable fields require strings; numeric JSON values are not coerced.")
        if table == "Hero" and field in STATS:
            if not re.fullmatch(r"(?:0|[1-9][0-9]?|100)", value):
                fail("invalid_value", "Safety policy: Hero base stats must be integer strings in 0..100.")
        elif len(value) > (10000 if field.startswith("description") else 128) or '"' in value or any(
                ord(c) < 32 and c not in "\n\r\t" for c in value):
            fail("invalid_value", "Text exceeds its limit or contains quotes/control characters forbidden by the editor.")
        if value != row[field]:
            diffs.append({"field": field, "before": row[field][:512], "after": value[:512],
                          "before_length": len(row[field]), "after_length": len(value),
                          "truncated": len(row[field]) > 512 or len(value) > 512})
    return diffs


def patch(ws, catalog, table, record_id, changes, expected_sha256, apply):
    with closing(connect(ws, catalog)) as con:
        entry, path, raw = table_source(ws, con, table, catalog, verify_content=True)
    rows = rows_from(raw)
    matches = [row for row in rows if row.get("id") == record_id]
    if len(matches) != 1:
        fail("ambiguous_record" if matches else "unknown_record", "Select an existing ID with exactly one matching row. Repeated relationship IDs are read-only.")
    differences = validate_changes(table, matches[0], changes)
    change_hash = digest(json.dumps({"source": str(path), "source_sha256": entry["sha256"], "table": table,
        "record_id": record_id, "changes": changes}, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    data = {"table": table, "record_id": record_id, "source_sha256": entry["sha256"],
            "confirmation": change_hash, "changes": differences, "applied": False}
    if not apply or not differences:
        return data
    if expected_sha256 != change_hash:
        raise ToolError("confirmation_required", "Preview first, then use data.confirmation with identical changes.",
                        recovery={"tool": "tk_patch", "arguments": {"catalog": catalog, "table": table,
                            "record_id": record_id, "changes": changes, "apply": False}})
    ws.path(path, write=True)
    marker = ws.path(path.parent / MARKER, exists=True)
    if load(read(marker)).get("adapter") != 1:
        fail("invalid_project", "Apply only to a data project created by tk_project.")
    ws.check_tree(path.parent)
    matches[0].update(changes)
    new_raw = json.dumps(rows, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8") + b"\n"
    rows_from(new_raw)
    backup = ws.path(f".um/tkeditor/backups/{uuid.uuid4().hex}", write=True)
    backup.mkdir(parents=True)
    (backup / path.name).write_bytes(raw)
    (backup / "change.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".tk-edit-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(new_raw)
            stream.flush()
            os.fsync(stream.fileno())
        if digest(read(path)) != entry["sha256"]:
            fail("source_changed", "Source changed while preparing the patch; nothing was replaced.")
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return data | {"applied": True, "backup": str(backup / path.name), "output": str(path),
                   "sha256": digest(new_raw), "next": "tk_index to refresh before the next edit/query",
                   "verification": "json-roundtrip-not-tested-in-editor-or-game"}


def filename(name, limit=DISPLAY_NAME_LIMIT):
    if (not isinstance(name, str) or not 1 <= len(name) <= limit or name != name.strip() or name.endswith(".")
            or any(ord(c) < 32 or c in '<>:"/\\|?*' for c in name)
            or name.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *(
                f"{prefix}{n}" for prefix in ("COM", "LPT") for n in range(1, 10))}):
        fail("invalid_name", f"Portrait name must use 1..{limit} characters and be a safe Windows filename without extension.")
    return name


def option_store(ws):
    return ws.path(".um/tkeditor/portrait-options.sqlite", write=True)


def register_option(ws, manifest, target):
    store = option_store(ws)
    store.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(store)) as con, con:
        con.execute("""CREATE TABLE IF NOT EXISTS options (option_id TEXT PRIMARY KEY, name TEXT,
            display_name TEXT, intent TEXT, hero_id TEXT, path TEXT)""")
        values = (manifest["option_id"], manifest["name"], manifest["display_name"],
                  manifest["intent"], manifest["hero_id"], str(target))
        con.execute("INSERT OR IGNORE INTO options VALUES (?,?,?,?,?,?)", values)
        existing = con.execute("SELECT * FROM options WHERE option_id=?", (manifest["option_id"],)).fetchone()
        if tuple(existing) != values:
            fail("portrait_id_conflict", "This option ID already belongs to another pack; existing registration was preserved.")


def registration_result(ws, manifest, target):
    data = manifest | {"output": str(target)}
    try:
        register_option(ws, manifest, target)
    except (OSError, sqlite3.Error) as exc:
        return data | {"registered": False, "registration_error": str(exc)[:512],
                       "recovery": {"tool": "tk_portrait_register", "arguments": {"pack": str(target)}}}
    return data | {"registered": True}


def portrait_register(ws, pack):
    """Recover registration using only a verified existing workspace pack."""
    from PIL import Image
    target = ws.path(pack, write=True, exists=True)
    if not target.is_dir():
        fail("invalid_portrait_pack", "Choose a workspace portrait pack directory.")
    ws.check_tree(target)
    manifest = load(read(ws.path(target / "portrait-pack.json", exists=True)))
    if not isinstance(manifest, dict):
        fail("invalid_portrait_pack", "Invalid portrait pack manifest.")
    option_id = manifest.get("option_id")
    name, display_name, intent = (manifest.get(key) for key in ("name", "display_name", "intent"))
    if not isinstance(option_id, str) or not re.fullmatch(r"um_[a-f0-9]{16}", option_id):
        fail("invalid_portrait_pack", "Invalid portrait option ID.")
    filename(display_name)
    filename(name, OPTION_NAME_LIMIT if intent == "new_option" else DISPLAY_NAME_LIMIT)
    hero_id = manifest.get("hero_id")
    if (intent not in {"new_option", "replace"} or not isinstance(hero_id, str)
            or (intent == "new_option" and (hero_id or name != option_id + "_" + display_name))
            or (intent == "replace" and (not hero_id or name != display_name))):
        fail("invalid_portrait_pack", "Portrait identity does not match the declared intent.")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != 3:
        fail("invalid_portrait_pack", "Exactly three portrait files are required.")
    for entry, (folder, size) in zip(files, PORTRAITS.items()):
        expected = f"Portraits/{folder}/{name}.png"
        if not isinstance(entry, dict) or entry.get("path") != expected or entry.get("size") != list(size):
            fail("invalid_portrait_pack", "Portrait paths or dimensions do not match the contract.")
        path = ws.path(target / expected, exists=True)
        if path.stat().st_size > 32 * 1024 * 1024 or digest(path.read_bytes()) != entry.get("sha256"):
            fail("invalid_portrait_pack", "A portrait is oversized or its checksum changed; registration refused.")
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            if (im.format != "PNG" or im.size != size or getattr(im, "n_frames", 1) != 1
                    or im.getexif().get(274, 1) != 1):
                fail("invalid_portrait_pack", "Portrait pixels/orientation do not match the contract.")
            im.load()
    # Recovery never upgrades the original preparation into game verification.
    manifest.update(installed=False, engine_ready=False, verification="png-format-only-not-tested-in-game")
    return registration_result(ws, manifest, target)


def portrait_options(ws, query_text, intent, limit, offset):
    page(limit, offset)
    if len(query_text) > 128 or intent not in {"new_option", "replace", "all"}:
        fail("invalid_query", "query <=128 characters; intent is new_option, replace or all.")
    store = option_store(ws)
    if not store.exists():
        return {"options": [], "next_offset": None}
    with closing(sqlite3.connect(store.as_uri() + "?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("""SELECT * FROM options WHERE (?='all' OR intent=?)
            AND instr(lower(display_name || name || option_id),lower(?))>0
            ORDER BY rowid LIMIT ? OFFSET ?""", (intent, intent, query_text, limit + 1, offset)).fetchall()
        return {"options": [dict(row) | {"installed": False} for row in rows[:limit]],
                "next_offset": offset + limit if len(rows) > limit else None,
                "scope": "workspace packs; not the live game's installed/selected portraits"}


def portraits(ws, full, half, icon, name, destination, mode, catalog, hero_id, intent):
    from PIL import Image, ImageOps
    if mode not in {"strict", "contain", "cover"}:
        fail("invalid_mode", "Choose strict dimensions, contain (padding), or cover (center crop).")
    if intent not in {"new_option", "replace"}:
        fail("invalid_intent", "Choose new_option (default, additive) or replace (requires a Hero ID).")
    if (intent == "new_option" and hero_id) or (intent == "replace" and not hero_id):
        fail("invalid_intent", "New options never bind an existing Hero; replacement requires explicit intent=replace and hero_id.")
    option_id = "um_" + uuid.uuid4().hex[:16]
    display_name = name or "AI头像"
    if hero_id:
        with closing(connect(ws, catalog)) as con:
            table_source(ws, con, "Hero", catalog, verify_content=True)
            entries = con.execute("SELECT body FROM records WHERE table_name='Hero' AND record_id=? LIMIT 2", (hero_id,)).fetchall()
            if len(entries) != 1:
                fail("ambiguous_record" if entries else "unknown_record", "Select a Hero ID with exactly one matching record.")
            row = json.loads(entries[0][0])
            derived = row.get("surname", "") + row.get("name", "")
            if name and name != derived:
                fail("name_mismatch", "Historical replacement filename must match surname+name exactly.")
            name = derived
            if con.execute("SELECT count(*) FROM records WHERE table_name='Hero' AND label=?", (name,)).fetchone()[0] != 1:
                fail("ambiguous_name", "Several heroes share this name; external filename replacement is ambiguous.")
        display_name = name
    else:
        # A separate namespace makes a custom CG selectable without accidentally
        # matching a historical hero's surname+name or an existing numeric icon.
        filename(display_name)
        name = option_id + "_" + display_name
        if catalog_path(ws, catalog).exists():
            with closing(connect(ws, catalog)) as con:
                table_source(ws, con, "Hero", catalog)
                if con.execute("SELECT 1 FROM records WHERE table_name='Hero' AND label=?", (name,)).fetchone():
                    fail("name_collision", "New option would replace an existing hero; choose another name.")
                if any(json.loads(row[0]).get("icon") == name for row in con.execute(
                        "SELECT body FROM records WHERE table_name='Hero'")):
                    fail("name_collision", "New option would reuse an existing icon; choose another name.")
    filename(name, OPTION_NAME_LIMIT if intent == "new_option" else DISPLAY_NAME_LIMIT)
    target = ws.path(destination, write=True)
    if target.exists():
        fail("target_exists", "Portrait packs require a new folder; existing files are never overwritten.")
    images = []
    try:
        for source, size in zip((full, half, icon), PORTRAITS.values()):
            path = ws.path(source, exists=True)
            if not path.is_file() or path.stat().st_size > 32 * 1024 * 1024:
                fail("image_limit", "Source image must be a file <=32 MiB.")
            with Image.open(path) as im:
                if im.format != "PNG" or im.width * im.height > 16000000 or getattr(im, "n_frames", 1) != 1:
                    fail("invalid_image", "Use a single-frame PNG of at most 16 megapixels.")
                image = ImageOps.exif_transpose(im).convert("RGBA")
            if mode == "strict" and image.size != size:
                actual_size = image.size
                image.close()
                fail("invalid_dimensions", f"Required dimensions after orientation correction: {size}; got {actual_size}.")
            if mode == "contain":
                fitted = ImageOps.contain(image, size, Image.Resampling.LANCZOS)
                image.close()
                image = Image.new("RGBA", size)
                image.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
                fitted.close()
            elif mode == "cover":
                fitted = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
                image.close()
                image = fitted
            images.append(image)
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = Path(tempfile.mkdtemp(dir=target.parent, prefix=".tk-portraits-"))
        try:
            manifest = {"name": name, "display_name": display_name, "option_id": option_id,
                        "intent": intent, "hero_id": hero_id, "mode": mode, "files": [], "installed": False,
                        "verification": "png-format-only-not-tested-in-game", "engine_ready": False,
                        "installation": "Manually back up and copy Portraits into ThreeKingdom_Data/StreamingAssets/Portraits. "
                            "Custom heroes select external CG in game; historical replacement uses exact surname+name. "
                            "This is not an AssetBundle or a Workshop-ready mod. Large packs can exhaust game memory."}
            for (folder, size), image in zip(PORTRAITS.items(), images):
                if image.size != size:
                    fail("invalid_dimensions", "Prepared portrait size does not match its output slot.")
                path = temp / "Portraits" / folder / (name + ".png")
                path.parent.mkdir(parents=True)
                image.save(path, "PNG")
                with Image.open(path) as saved:
                    if saved.size != size:
                        fail("invalid_dimensions", "Saved PNG has incorrect dimensions.")
                    saved_size = list(saved.size)
                    saved.verify()
                manifest["files"].append({"path": path.relative_to(temp).as_posix(), "size": saved_size,
                                          "sha256": digest(path.read_bytes())})
            (temp / "portrait-pack.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            temp.rename(target)
        finally:
            if temp.exists():
                shutil.rmtree(temp)
    finally:
        for image in images:
            image.close()
    return registration_result(ws, manifest, target)
