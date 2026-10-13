"""TKEditor parameter guidance shared by MCP, JSON CLI and Python discovery."""


def input_hints(name: str) -> dict:
    """Advertise existing backend constraints; raw dispatch still validates every call."""
    common = {
        "catalog": {"pattern": "^[A-Za-z0-9_-]{1,64}$", "description": "Index name, not a path. Reuse the same workspace/catalog."},
        "limit": {"minimum": 1, "maximum": 50},
        "offset": {"minimum": 0, "maximum": 100000},
        "source": {"description": "Allowed directory containing Hero.json, not the game root."},
        "destination": {"description": "New directory inside configured workspace; never overwrite existing output."},
    }
    specific = {
        "tk_query": {
            "query": {"maxLength": 128}, "record_id": {"maxLength": 128},
            "fields": {"maxLength": 512, "description": "Comma-separated existing fields, at most 8; e.g. id,surname,name,icon."}},
        "tk_read_field": {
            "start": {"minimum": 0, "maximum": 64 * 1024 * 1024},
            "max_chars": {"minimum": 1, "maximum": 2000}, "row_index": {"minimum": -1}},
        "tk_patch": {
            "changes": {"minProperties": 1, "maxProperties": 8, "additionalProperties": {"type": "string"},
                        "description": "Existing allowed display fields or Hero stats; stats must be integer strings 0..100."},
            "expected_sha256": {"description": "Copy preview data.confirmation, NOT data.source_sha256; keep edit arguments identical."},
            "apply": {"description": "False previews; true requires confirmation and an indexed tk_project."}},
        "tk_portraits": {
            "mode": {"enum": ["strict", "contain", "cover"]},
            "intent": {"enum": ["new_option", "replace"]},
            "hero_id": {"description": "Omit for new_option. Replacement requires an exact unique ID from this catalog's Hero table."},
            "full": {"description": "Single-frame PNG; strict requires 1000x1400 after orientation correction."},
            "half": {"description": "Single-frame PNG; strict requires 1024x1024 after orientation correction."},
            "icon": {"description": "Single-frame PNG; strict requires 260x340 after orientation correction."}},
        "tk_portrait_options": {"intent": {"enum": ["new_option", "replace", "all"]}, "query": {"maxLength": 128}},
        "tk_portrait_register": {"pack": {"description": "Existing workspace pack directory from data.recovery, not the manifest file."}},
    }
    return common | specific.get(name, {})
