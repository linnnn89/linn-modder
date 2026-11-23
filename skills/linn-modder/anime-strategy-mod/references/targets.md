# Target games and editions

Read when choosing a profile or import route. Follow the user's requested scope and validation level.

## Establish the target

Record the exact title, version, language, store, expansion/PK edition and existing
mod dependencies. A series name is enough for a planning project but not for an
archive importer. If a version or format is unknown, record it as unknown.

Use these profile IDs:

- `ck3`: project scaffold; native mod descriptor, additive data and UTF-8 BOM YAML
  localization. Main character portraits use a 3D model/material/animation pipeline.
  Follow the [CK3 workflow](ck3-design.md); a 2D portrait framework needs its own GUI/identity integration.
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

## 群星与其他游戏案例

《群星》萌化物种、领袖或原版头像：用 `manual_read(collection="knowledge", path="games/stellaris/anime-species-portraits.md")` 读取 DDS、立绘组、物种集合与建国器分类的对应关系。

在 `knowledge_search` 中按下表搜索；返回的 `path` 可交给 `manual_read` 离线读取。

| 当前任务 | 搜索词 |
|---|---|
| 从另一部作品移入完整势力 | 幕府将军 2 |
| 用原版战役抉择招募其他势力领主 | 战锤 3 招降 |
| 跨作品角色随机开局与章节平衡 | 幻想少女大战 |
| 大型 CPK 修改、回封与卸载回退 | 虚空幻界 |
| 阵营专属国策与本地化 | 阿尔巴尼亚 |
| 浏览全部 11 个上游示例工程 | 示例工程 |
