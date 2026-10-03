"""Local staging projects and deterministic 2D asset preparation.

Profiles describe support honestly. Engine texture conversion/import is a separate,
version-specific step; preparing PNGs does not claim a mod works in a game.
"""
import hashlib
import json
import re
import shutil
from pathlib import Path

from um.contracts import ToolError


def profiles() -> list[dict]:
    path = Path(__file__).parent / "data" / "game_profiles.json"
    return json.loads(path.read_text(encoding="utf-8"))["profiles"]


def profile(profile_id: str) -> dict:
    match = next((p for p in profiles() if p["id"] == profile_id), None)
    if match is None:
        raise ToolError("unknown_profile", f"Unknown game profile: {profile_id}")
    return match


def create(destination: Path, profile_id: str, name: str, game_version: str = "unknown") -> dict:
    spec = profile(profile_id)
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name):
        raise ToolError("invalid_name", "Project ID must start with a-z and use a-z, 0-9, _ or - (max 64).")
    if destination.exists():
        raise ToolError("already_exists", "Project destination must not already exist.")
    manifest = {"schema_version": 1, "name": name, "profile": profile_id,
                "game_version": game_version, "verification": "not-tested-in-game",
                "style": {"direction": "anime", "palette": [], "character_consistency": "Record references and variant rules in ART_DIRECTION.md"},
                "asset_manifest": "assets/manifest.json", "reference_manifest": "references/manifest.json",
                "asset_workflow": "ASSET_WORKFLOW.md", "support": spec["support"]}
    destination.mkdir(parents=True)
    try:
        for relative in ("assets/source", "assets/prepared", "assets/layers", "assets/editable", "references", "verification"):
            (destination / relative).mkdir(parents=True)
        (destination / "project.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        (destination / "assets/manifest.json").write_text('{"schema_version": 1, "assets": []}\n', encoding="utf-8")
        (destination / "references/manifest.json").write_text('{"schema_version": 1, "references": []}\n', encoding="utf-8")
        from um.resources import read
        (destination / "ASSET_WORKFLOW.md").write_text(
            read("skills", "linn-modder/asset-pipeline/references/sourcing-and-psd.md"), encoding="utf-8")
        (destination / "ART_DIRECTION.md").write_text(
            "# Art direction\n\nRecord the cast, palette, line style, lighting, costume rules, expressions and framing.\n"
            "Keep a stable character ID across crops and variants. Record authorship/license and generation provenance.\n"
            "Follow ASSET_WORKFLOW.md: official references first; available GPT Image for needed artwork; real layered export for PSD.\n"
            "Measure required sizes and formats in the exact target version before preparing assets.\n", encoding="utf-8")
        (destination / "MODLOG.md").write_text(
            f"# {name}\n\nGame profile: {profile_id}\nVersion: {game_version}\nVerification: not tested in game.\n\n"
            + "\n".join("- " + c for c in spec["constraints"]) + "\n", encoding="utf-8")
        if spec["support"] == "project-scaffold":
            mod = destination / "mod" / name
            mod.mkdir(parents=True)
            for relative in spec["scaffold_directories"]:
                folder = mod / relative
                folder.mkdir(parents=True, exist_ok=True)
                (folder / ".gitkeep").touch()
            descriptor = f'name="{name}"\n'
            (destination / "mod" / f"{name}.mod").write_text(descriptor + f'path="mod/{name}"\n', encoding="utf-8")
            if profile_id == "ck3":
                (mod / "descriptor.mod").write_text(descriptor, encoding="utf-8")
                # Comment-only files avoid inventing game IDs or overwriting vanilla localization.
                for language in ("english", "simp_chinese"):
                    (mod / "localization" / language / f"{name}_l_{language}.yml").write_text(
                        f"l_{language}:\n # Add namespaced localization keys here.\n", encoding="utf-8-sig")
        (destination / "README.md").write_text(
            f"# {name}\n\n{spec['name']} — {spec['support']}.\n\n"
            "This is a staging project. Confirm the exact game build and reference formats before installation.\n"
            "Prepared PNGs are intermediate art; engine-ready conversion and in-game verification are separate steps.\n",
            encoding="utf-8")
    except Exception:
        shutil.rmtree(destination)
        raise
    return manifest | {"path": str(destination), "constraints": spec["constraints"]}


def prepare_image(source: Path, output: Path, width: int, height: int,
                  mode: str = "contain", anchor: str = "center") -> dict:
    from PIL import Image, ImageOps
    if not (1 <= width <= 8192 and 1 <= height <= 8192 and width * height <= 16_777_216):
        raise ToolError("invalid_size", "Dimensions must be 1..8192, at most 16 megapixels.")
    if mode not in ("contain", "cover") or anchor not in ("center", "top"):
        raise ToolError("invalid_fit", "Use contain/cover and center/top.")
    if output.suffix.lower() != ".png":
        raise ToolError("invalid_format", "Prepared images must use .png; engine conversion is a separate step.")
    if output.exists():
        raise ToolError("already_exists", "Output already exists; choose a new filename.")
    with Image.open(source) as original:
        if original.width * original.height > 40_000_000:
            raise ToolError("image_too_large", "Input exceeds 40 megapixels.")
        im = ImageOps.exif_transpose(original).convert("RGBA")
        centering = (0.5, 0.0 if anchor == "top" else 0.5)
        if mode == "cover":
            result = ImageOps.fit(im, (width, height), Image.Resampling.LANCZOS, centering=centering)
        else:
            resized = ImageOps.contain(im, (width, height), Image.Resampling.LANCZOS)
            result = Image.new("RGBA", (width, height))
            result.paste(resized, ((width - resized.width) // 2,
                                  0 if anchor == "top" else (height - resized.height) // 2))
        output.parent.mkdir(parents=True, exist_ok=True)
        result.save(output, "PNG")
    return {"path": str(output), "width": width, "height": height, "mode": mode,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "engine_ready": False}
