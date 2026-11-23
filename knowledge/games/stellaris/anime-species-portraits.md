---
kind: game
title: "群星萌化 MOD：新建二次元物种立绘包，或替换原版外观"
game: Stellaris
game_version: "3.12 立绘注册改版，4.2.4 静态样例，4.3 系列外观替换系统；目标 4.6 待游戏验证"
platform: windows
engine: clausewitz
route: data
status: in-progress
date: 2026-11-23
agents: [Codex]
tags: [群星, 萌化, 二次元, 物种, 领袖, 肖像, 静态立绘, DDS, portrait_sets, portrait_categories]
links:
  - https://store.steampowered.com/news/app/281990/view/5766372999943272862
  - https://forum.paradoxplaza.com/forum/developer-diary/stellaris-dev-diary-414b-portrait-substitution-system.1915204/
  - https://github.com/Xen-Shuto/species_portrait_template/tree/c84a397599ea57a65b62bdecbd19fa6dbe49b36f
  - https://steamcommunity.com/sharedfiles/filedetails/?id=3241789640
  - https://store.steampowered.com/news/app/281990/view/1849827110441822
---

# 群星萌化：从一张静态立绘做到一个可选物种

## Setup — 先定萌化范围与版本

想在建国时选择自己的动漫种族，先做一套**新增静态生物立绘**，挂到已有类人类别（HUM）。想让原版银河里已有物种也换脸，则先调查**外观替换**。两者的验收点分别是“建国器中多了一个选项”和“原物种在启用替换模式后显示新外观”。两条路线都可以先用一张图做样本。

记录启动器里的游戏版本、所用 DLC 和播放集。2026-11-23 发布的免费更新是 4.6；下面的文件样例来自作者以 4.2.4 为编辑说明背景的仓库。在 4.6 开工时，先从本机原版找一套仍能在建国器选中的立绘，核对类别、集合、角色上下文。 [4.6 官方公告](https://store.steampowered.com/news/app/281990/view/1849827110441822) · [静态立绘模板原文](https://github.com/Xen-Shuto/species_portrait_template/tree/c84a397599ea57a65b62bdecbd19fa6dbe49b36f)

## Route — 新增一个二次元物种立绘组选项

1. 用启动器创建本地 Mod，先为一张半身立绘制作透明底图。已有 IP 人物优先查官方设定图作参考，并记录来源与可用范围；原创素体可用 GPT Image 制作，保留分层 PSD 或独立图层。输出 DDS 时对照选定的游戏样本检查透明边缘、尺寸、压缩和 mipmap。
2. 给类别、集合、立绘组、图片键加自己的命名前缀。按下表从界面往回追一遍，每个引用都应指向自己定义的键或已确认存在的原版键。为建国器显示的类别名补上当前语言的本地化，例如简体中文的 `localisation/simp_chinese/`。
3. 第一版让建国预览、物种、人口、领袖及统治者都取到同一张图。接线通了，再按脸型、服装或职位拆角色池。若目标是“银河随机遭遇这些种族”，另测 AI 随机生成，记录哪些形象只供玩家选择。

| 查哪里 | 查什么 |
|---|---|
| `common/portrait_categories/` | 建国器展示的分类。其 `sets` 引用立绘集合。 |
| `common/portrait_sets/` | `species_class` 对应哪种物种类别，`portraits` 列了哪些立绘或立绘组。3.12 改动前的老教程常把清单放在物种类别里。 |
| `gfx/portraits/portraits/` | 静态样例用 `portrait_groups` 分配 `default`、`game_setup`、`species`、`pop`、`leader`、`ruler`，再通过 `portraits` 内的 `texturefile` 找到 DDS。 |
| `gfx/models/` 下的自有目录 | 对照定义读取实际贴图。已读样例的一张生物立绘是 360 × 360、DXT1、1 个 mip 层；换画风、半透明发丝或换目标版本时重新选取合适样本。 |

Paradox 说明了类别与集合怎样配合。作者模板的生物集合直接使用 `species_class = HUM`。单纯追加形象可以从这里开始；若要独立的机械或石质种族，再核对相应类别、特质与 DLC 条件。 [开发日志 #343](https://store.steampowered.com/news/app/281990/view/5766372999943272862) · [作者模板中的生物集合](https://github.com/Xen-Shuto/species_portrait_template/blob/c84a397599ea57a65b62bdecbd19fa6dbe49b36f/MOD/portrait_Template/common/portrait_sets/00_Template_portrait_sets_01_bio.txt)

想看静态萌化包的实际设计，可以对照 Xen-Shuto 发布的三套物种立绘：原创 Aigis、晶龙娘与 Daedalus 型。作者使用同一模板制作不同题材，适合比较角色池如何按物种组织。其授权限制改作再分发，本项目只索引设计和来源。 [作者的三套成品](https://github.com/Xen-Shuto/Stellaris_PortraitsMOD/tree/97051bc47de4848ba3d293b9f4e7c5b40293f51e)

### 如果目标是替换原版外观

开发日志 #414b 展示了 `portrait_substitution_mode`，用 `substitutions` 把原头像键映射到替代键。先挑一个原版头像和一张已能显示的新图，核对当前版本示例、设置菜单中的替换模式，以及开启与关闭时同一物种的显示。保留相应 DLC 的使用条件。大规模萌化前分别抽查生物、机械、特殊阶段及其他 Mod 增加的头像，记录覆盖范围。 [开发日志 #414b](https://forum.paradoxplaza.com/forum/developer-diary/stellaris-dev-diary-414b-portrait-substitution-system.1915204/)

## Verification — 分清已经核实和需要进游戏确认的部分

编写时对照了开发日志、作者模板里的类别／集合／立绘定义，并读取了一张样例 DDS 的文件头。作者记录了自己环境下成功新增立绘。本项目尚未在 4.6 启动游戏验证。首个样本可依次核对：

- **离线**：类别 → 集合 → 立绘组 → 图片键 → DDS 全部可解析，贴图可回读，透明区与头部裁切符合目标框。
- **建国器**：在指定分类选中形象，查看物种与统治者预览，再保存并重新打开这个帝国。
- **新开局**：查看物种列表、人口和一名新招募领袖。若只替换视觉，顺手核对原版其他物种的显示和当前播放集的错误日志。

## Gotchas — 三种常见故障

1. **旧预设里有图，建国器里找不到。** 3.12 迁移案例中，贴图已加载，但新界面缺少类别和集合注册。先查这两层的键和值。[作者的修复说明](https://steamcommunity.com/sharedfiles/filedetails/?id=3241789640)
2. **物种预览正确，领袖空白或总是同一张脸。** 查 `leader`、`ruler` 的候选池、条件和默认图，再查对应的纹理路径。用单张图覆盖各上下文，可以减少第一次定位所需的变量。
3. **透明半身像在某个面板被截头或有白边。** 同一角色用建国、领袖和外交窗口的实际取景对照。先回读 DDS 的 alpha，再调整素体画布与人物位置，最后批量导出其余角色。
