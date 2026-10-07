# Target games and editions

Read when choosing a profile or import route. Follow the user's requested scope and validation level.

## Establish the target

Record the exact title, version, language, store, expansion/PK edition and existing
mod dependencies. A series name is enough for a planning project but not for an
archive importer. If a version or format is unknown, record it as unknown.

Use these profile IDs:

- `ck3`: project scaffold; native mod descriptor, additive data and UTF-8 BOM YAML
  localization. Main character portraits use a 3D model/material/animation pipeline.
- `victoria2`: project scaffold; legacy .mod and semicolon CSV localization.
  Preserve language columns and verify encoding against the target build/patch.
- `romance-of-the-three-kingdoms`: planning only; select the exact title and edition
  before choosing built-in portrait import, an editor, or a resource adapter.
- `nobunagas-ambition`: planning only; Souzou, Taishi and Shinsei formats must be
  treated independently, including expansion editions.

## Victoria II prior work

Search `knowledge_search` for `Victoria 2` or `South Central`, then read
`manual_read(collection="knowledge",path="games/victoria-2/south-central-gang-total-conversion.md")`.
The imported upstream report covers HoD 3.04 map formats, non-recursive
`replace_path`, event pictures and icon strips. Preserve its version and original
verification context; it does not establish compatibility for another build.
