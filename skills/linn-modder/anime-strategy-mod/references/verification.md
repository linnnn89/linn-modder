# Strategy-mod verification

Read when checking prepared assets, formats or runtime results. Follow the user's requested scope and validation level.

## Verification

Offline checks can establish file dimensions, alpha, encoding, manifest integrity,
descriptor structure and deterministic conversion round trips. Record those checks
in MODLOG.md. Record runtime verification separately; if no game was run, retain
`not-tested-in-game`. Never imply that a planning-only profile is a working loader.

## CK3 checks at completion

Choose checks for the changed behavior, not a fixed full-game checklist:

| Change | Offline evidence | Runtime evidence, when requested |
|---|---|---|
| Script/interaction | Defined IDs, correct scope, dependencies, one settlement path | Same target before/after; failure/cancel path if changed |
| History/lifecycle | Stable identities, family/employer/liege dates, shared generation source | New start or affected save migration; one rebuild without duplicates |
| Localization | UTF-8 BOM, matching filename/header, keys and placeholders | Actual language, tooltip and target context |
| 2D portraits/GUI | Identity mapping, actual widget references, crops/masks, override owners | A registered character and the affected ordinary/third-party branch |
| Dependency/DLC | Exact versions, load order and overridden objects | Only the supported combinations affected by this change |

If Tiger is already available and the task has game files, point it at the actual
mod descriptor. Its configuration can load parent mods via `load_mod`; a missing
dependency is not proof that all its references are wrong. Record tool/game versions.
An existing JSON baseline can focus the final check on new reports:

```powershell
ck3-tiger --suppress baseline.json "path/to/your/descriptor.mod"
```

Keep that baseline tied to its original revision. Review remaining relevant warnings;
do not generate a new baseline from broken output just to hide it. Tiger may lag game
updates or report false positives. It complements the target version's scripts/logs.
It is optional; this toolkit does not install or invoke it automatically.

## CK3 author sources

Read on **2026-10-12**, pinned for reproducibility; no third-party code was copied:

- [Tiger author README](https://github.com/amtep/tiger/blob/9e3d3b25c7524cdcc86d5f4190f3f8cffbc4d630/README.md)
  and [configuration](https://github.com/amtep/tiger/blob/9e3d3b25c7524cdcc86d5f4190f3f8cffbc4d630/ck3-tiger.conf):
  scope/reference/history checks, parent-mod context and report baselines. These are
  tool capabilities, not proof of this project's runtime compatibility.
- [Paradox Modding Toolkit author README](https://github.com/JDeffner/paradox-modding-toolkit/blob/d71163c4285267fa88c81e730dc8b9c3c2704432/README.md):
  preserve comments/source formatting, align localization filename/header/BOM,
  inspect dependency overrides and measure image requirements. Its compatibility
  migrations are marked experimental; no automatic migration is adopted here.

The Paradox forum diary and CK3 Wiki could not be read in this session; their search
snippets were not treated as verified syntax. Engine-specific project findings remain
in `knowledge/games/crusader-kings-iii/modding-playbook.md` with their original evidence
and version limits. No game or third-party validator was run for this documentation work.

## CK3 dynamic-description warning

For event descriptions or a startup stall, read the verified
[CK3 1.20.0.4 loading failure](ck3-dynamic-description-loading-failure.md).
In that build, `triggered_desc` accepts only `trigger` and `desc` as direct
children. A direct `first_valid` child caused repeated parser errors and blocked
startup despite passing brace, reference and package checks. Check the generated
event files as well as the generator; confirm that the actual game reaches its
main menu before marking startup verified. Main-menu success does not validate
the event's in-game display or gameplay effects.
