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

## 按制作问题查上游案例

| 当前任务 | 可借鉴的做法与证据 |
|---|---|
| 把一个作品的势力移入另一个战略游戏 | 《全面战争：幕府将军 2》用法国替换大友氏，同时迁移兵种、单位卡、旗帜、文本和战役开局。策划三国志或信长题材时，可用一名武将和一个势力核对这些引用。原作者实测的是经典版 build 6262。 [法国阵营移植记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/total-war-shogun-2/shogun-2-napoleon-france-faction-port.md) |
| 给二次元角色加专属招降事件 | 《全面战争：战锤 3》用现成的阿查战役抉择为瓦尔基娅实现招降。设计 CK3 事件时，先找原版中相似的抉择，核对谁触发、谁成为附庸、谁进入招募池，再决定需要新增哪些效果。原作者在新战役中验证了两条触发路线。 [招降事件记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/total-war-warhammer-iii/valkia-khorne-subjugation-reusing-archaon-dilemmas.md) |
| 做跨作品角色随机开局 | 《幻想少女大战》以种子打乱友军和领队，敌人与首领则按章节调整。设计阵容时，把“抽到了谁”和“这一章能否打过”作为两个可验证的问题。该 GameMaker 案例仍在开发中。 [随机模式记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/fantasy-maiden-wars-dream-of-the-stray-dreamer/randomizer-mode-gml-via-undertalemodtool-cli-run-with-game-s.md) |
| 修改大型单文件封包，只交付自己的改动 | 《刀剑神域：虚空幻界》的经验值补丁记录了如何识别原版 CPK、备份改动及按字节核对卸载结果。遇到光荣游戏封包时，可借鉴回退验收方法，读写格式仍须按具体作品与版本取样。 [CPK 修改与还原记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/sword-art-online-hollow-realization/zero-exp-patcher-cri-cpk-append.md) |
| 给 P 社游戏做阵营专属内容 | 《钢铁雄心 IV》1.19.3 的阿尔巴尼亚国策树把国家选择条件、本地化和国策奖励放在一个最小例子里。作者只做了发布检查，开局能否选中该树、完成国策能否获得奖励仍待游戏验证。 [国策树记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/hearts-of-iron-iv/creating-a-national-focus-for-albania.md) |
