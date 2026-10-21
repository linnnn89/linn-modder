# Cast consistency and asset staging

Read when preparing a character set, portraits, flags or illustrations. Follow the user's requested scope and validation level.

For gameplay attributes, personality, faction placement and persistent identity,
read [Character design principles](character-design-principles.md). An existing
portrait or imported roster is not evidence that its stats or relationships match canon.

## Build a consistent cast

Retrieve official character references first and record source URLs/hashes in
`references/manifest.json`; follow [sourcing and PSD](../../asset-pipeline/references/sourcing-and-psd.md)
for Codex GPT Image generation and genuine layered masters. Write ART_DIRECTION.md before batch generation. Record stable character IDs,
reference sheets, palette, line style, lighting, costumes, expressions and crop
rules. Maintain the same identity across face, bust, full-body and event variants.
Do not invent mandatory texture dimensions from memory: record measured target
sizes, alpha behavior, compression, mipmaps and resource IDs from known samples.

Keep source assets in `assets/source`, intermediate artwork in `assets/prepared`
and provenance/character mappings in `assets/manifest.json`. `image_prepare`
supports alpha-preserving PNG output, contain/cover fitting and center/top anchors.
Its output includes source and output hashes; copy those to the asset manifest.
Use Codex's available GPT Image tool for needed bases/edits, or another selected and
configured provider. Existing `um fal` commands are one option. Local PNG preparation
does not require a provider; PSD assembly requires an actual PSD-capable writer.

## Stage a small slice

Start with one character, one event illustration or one flag family. In CK3,
prefer a namespaced data/UI/event slice before undertaking 3D portrait replacement.
In Victoria II, preserve all required political flag variants and localization
columns. In Koei games, prefer a supported portrait importer when available.
Do not assume a prepared PNG can be copied directly into a game's archive.

Keep generated changes in the project workspace. Game roots exposed to the shared
service are read-only. A future engine adapter must validate format round trips
and produce an installation plan before changing an installed game.

## CK3 二维立绘与独立小头像：制作及审查参考

2026-10-17 核对二向箔核心库 / Anime Core Lib 的本机 Workshop 教程、当前生成脚本，以及下列网络原文。此节适用于借用二向箔纸片模型的 CK3 MOD；通用美术经验不等于 CK3 引擎限制。更新后仍应读取实际安装的教程、mesh、portrait types、GUI 与遮罩，不凭本节宣称版本兼容。

### 一手资料与适用范围

| 资料 | 可采用的规则 | 适用边界 |
|---|---|---|
| [Anime Core Lib 作者页](https://steamcommunity.com/workshop/filedetails/?id=2975613539)；安装包内 `README.md`、`upgrade_guide.md`、`animecorelib.py` | 使用依赖、专用身份和种族注册；追踪模板至素材；按作者实际样例绑定 | 作者页要求阅读包内教程，网页本身不是完整接口手册。本机教程与脚本于 2026-10-17 只读核对，未执行作者脚本 |
| [GENSEKI 立ち絵ガイドライン](https://img.genseki.me/images/compes/202209/tachie.pdf) | 脸靠横向中心、统一人物尺度、检查三人并排、衣服不在边界突兀截断、小屏幕检查可读性 | 是特定服务的投稿规范；其大腿以上构图、画布和线宽要求不可直接作为 CK3 强制规则 |
| [Konado 作者文档：立ち絵規約](https://godothub.com/oss/konado/ja/latest/tutorial/actor-coordinate-and-scaling.html) | 透明背景、边缘余量、主体可见区、锚点及下方 UI 避让 | 适用于其 Godot 对话系统；CK3 锚点必须回到真实模型与骨骼核对 |
| [Ren'Py 官方 Transform Properties](https://renpy.org/doc/html/transform_properties.html#transform-property-fit) | 区分等比容纳 `contain`、等比铺满裁切 `cover` 与拉伸 `fill` | 用于解释图像处理方式，不代表 CK3 支持同名配置 |

### 将图片、绑定与控件分开检查

1. **主立绘。** 本次二向箔教程推荐 1024×1024，默认 mesh 焦点约为 `(0.5W, 0.2H)`；头部应落在上中区域。方形画布不表示把人物撑成正方形。作者附带脚本使用 `scale = 1.6`，accessory 绑定 `node = "ground_joint"`。这些是该 mesh 的合同；换 mesh 或节点要重新验证，不能仅因立绘偏移就给全部人物改节点或 scale。
2. **身份绑定。** 按角色稳定 key 核对：身份特质 → portrait modifier → gene/template/index → accessory → entity → pdxmesh → texture；历史人物和新建人物同时核对 `anime_ethnicity`。检查重名、重复索引、缺失贴图和错误交叉引用。接线完整只说明代码对应一致，不证明图片画的就是该角色；身份仍须对照来源。
3. **独立小头像。** 从完整面部或可靠源头像取景，另存裁框和眼部坐标。发饰、武器、翅膀、透明留白不应决定脸的位置。保留原作遮眼、闭眼和面具，不将这些特征误报为裁坏，也不自行补画。
4. **实际调用。** 检查当前播放集中同名 GUI 的定义和优先级，确认小、普通、地图、肩部、躯干等控件分别走 bitmap 或模型镜头。独立 DDS 正常，不能证明控件实际使用了它；部分自定义窗口可能直接调用 `Character.GetPortrait`。

**索引的版本差异：** 二向箔附带脚本仍可见按 255 个模板切组的旧写法，但 [CK3 1.20.0 官方更新说明](https://store.steampowered.com/oldnews/?appgroupname=crusader+kings+iii&appids=1158310&enddate=1790838000&feed=steam_community_announcements) 已将 accessory gene index 上限从 255 扩展至 2,147,483,647。不能仅凭索引超过 255 就判为当前版本绑定错误；也不能把模板索引与 DNA 中其他 0–255 数值混为一谈。旧版兼容仍须按旧引擎另验。

### 构图审查规则

- **宽度以有效人物区域判断。** 测量 alpha 边界，并将主体与武器、坐骑、翅膀、背景特效分开理解。横向有效边界宽高比大于 1 可用于排查，但不是自动判废线；大特效会同时造成身体缩小、脸偏离中心。优先使用姿势集中、竖向完整单人彩图，不靠压扁人物或截掉肢体凑比例。已有正常素材按用户范围保留。
- **身体等比，脸部独立定位。** `contain` 能保全图片，但不能保证脸对准镜头；`cover` 会裁切，`fill` 会改变宽高比例。先对照原图，再判断过宽是原构图、不等比缩放、画布留白还是镜头所致。大立绘与小头像可以使用不同取景。
- **比较同一个控件中的人物尺度。** 大头半身照、完整站姿、蹲姿、斜躺、多人合图不应在同一模板下宣称已适配。检查头部、脚底或主体锚点；三人并排检查遮挡。
- **小头像看脸，不看头发中心。** 在实际显示尺寸查看双眼、鼻口、下巴及表情可读性，检查左右偏移、上下留白、旋转、放大模糊及底部好感/数值条。需要试做样张时，可从眼线位于画布高度约 35%–45%、下巴高于底部约 20% 的范围起步，再按原画和真实遮罩调整；这是审查建议，不是引擎标准或批量自动修正公式。
- **用实际遮罩检查多个尺寸。** 本项目常用 256×320 DDS 在部分小控件显示为 80×100，也有地图与其他比例控件。检查遮罩本身 alpha 和控件最终宽高，不只检查未遮罩大预览。离线模拟数值条必须标作示意，不能当游戏截图。
- **元数据须跟随实际处理。** 改用眼部仿射变换后，旧 `face_bbox` / `crop_bbox` 若不再描述输出，应注明已废弃或更新；不能用失效框证明居中，也不能据其自动判错。

### 验证与证据边界

按授权范围只读扫描一次涉及的画像链，复用角色清单、指标和缩略图；后续只回读异常项原图。审查表分别记录“静态接线异常”“图片目视问题”“几何筛查候选”和“游戏内未确认”，不要把 alpha 接边、原作遮眼、阈值命中全部算成缺陷。

最终实机验收应覆盖人物主面板、最小关系头像、配偶/廷臣列表、肩部/躯干窗口，有涉及再检查地图、事件与宫廷；同时观察普通角色回退、点击、悬停、死亡与囚禁遮罩。仅在用户授权后启动或操作游戏。图片准备、格式/绑定检查、离线目视、实际游戏 UI、人工验收是不同证据层，必须分别说明。
