---
name: linn-modder
description: >-
  用于已有离线游戏的 MOD 制作、修改与排错。当用户要找游戏/MOD/Steam 创意工坊目录、判断游戏能否改、安装或修复模组、更新后恢复兼容、换角色头像/立绘/皮肤/纹理/音效、制作二次元内容、改 HUD/菜单/布局/字体/汉化、调整配置/数据/脚本/存档数值、分析或解包回封资源、查找模组工具与教程、验证或打包发布 MOD 时使用；即使请求没有写出“MOD”也适用。根据游戏与版本选择路线，按需读取子文件夹，并联网查证工具和格式。
  Use for offline game modding, Steam Workshop paths, asset swaps, UI/localization, save edits, mod troubleshooting and packaging.
  ゲームMOD制作・導入、不具合修正、立ち絵差し替え、UI改造、日本語化。
---

# Linn Modder

帮助把游戏修改需求落到可编辑对象、合适工具、修改文件和验证结果。整个技能只有这个入口；
子文件夹中的 `GUIDE.md` 是任务指南，执行当前步骤时再读相关 reference。
以自有离线游戏为对象，保留原件与存档备份；发布包只包含可分发的 MOD 文件。

## 接到任务后

1. 从用户提供的游戏名称、版本、路径、文件或截图确定目标与期望变化。已有信息足够时直接进入对应指南；目标不明或路线未定时先做游戏识别。
2. 从下表选当前任务的主题。单项修改直接进入该主题；完整 MOD 用整体流程安排工作，随阶段切换资料，不一次读取所有指南。
3. 首次选择编辑器、loader、导入/回封工具，或遇到未知格式、版本差异、陌生错误时，读联网查证指南并打开当前原文。优先官方手册、维护者仓库和对应版本示例；按问题选英文、中文或日文免费资料。
4. 在工作区副本完成最小改动，检查格式和引用，再按任务验证目标效果。交付修改文件、验证结果与恢复方法；MOD 工作的证据和未决项写入 `MODLOG.md`。

## 按任务进入子文件夹

| 当前任务 | 读取 |
|---|---|
| 完整 MOD、跨阶段工作或路线未定 | [整体流程](mod-any-game/GUIDE.md) |
| “模组在哪”、Steam 创意工坊路径、安装排错、引擎与可行性 | [游戏识别](game-recon/GUIDE.md) |
| 查当前版本、工具、格式与英中日免费资料 | [联网查证](mod-research/GUIDE.md) |
| 改 HUD/菜单/布局、界面皮肤、字体、汉化与文字溢出 | [UI 修改](ui-mod/GUIDE.md) |
| TKEditor 检索/安全编辑/新增头像、配置/脚本/存档、资源解包回封 | [文件修改](file-mod/GUIDE.md) |
| 二次元策略 MOD 的角色、头像、阵营、内容映射与本地化 | [策略游戏内容](anime-strategy-mod/GUIDE.md) |
| 换立绘/表情、抠图、透明通道、PSD/Live2D、精灵与 3D 素材 | [素材制作](asset-pipeline/GUIDE.md) |
| 未知二进制格式、内部逻辑与读写验证 | [逆向分析](reverse-engineering/GUIDE.md) |
| 明确选择 fal 生成素材 | [fal 素材](fal-assets/GUIDE.md) |
| 截图、窗口输入与运行时观察 | [游戏操作](game-automation/GUIDE.md) |
| 融合多个游戏的玩法或模拟 | [玩法融合](mashup-mods/GUIDE.md) |
| 演示视频、预告片或蒙太奇 | [视频制作](showcase-video/GUIDE.md) |
| 打包与发布 MOD | [交付发布](publish-mod/GUIDE.md) |
| 查找、整理和贡献可复用经验 | [知识经验](share-field-notes/GUIDE.md) |

更新后 MOD 失效：定位加载/依赖问题时读游戏识别；出现文件格式或字段变化时读文件修改，
并通过联网查证确认当前版本差异。按识别结果选择[引擎手册目录](mod-any-game/references/engines/)中的相应文件。
需要工具操作时读[共享接口](references/tools.md)，按当前环境已有能力选择 MCP、JSON CLI 或文件工具。

## 读取方式

Linn Modder 是本项目的工具包名称，`um` 是其命令行入口；MCP 服务标识为 `linn-modder`，
客户端显示名称取决于配置。普通文件工具就能读取本技能及子文件夹；工具包操作按需使用。

- 文件客户端：以当前读到的本文件所在目录为技能根目录，解析相对链接；复制安装后也从该目录读取子文件夹。
- MCP：`um://guide` 和 `um://workflow` 提供本入口；用 `manual_read` 读取
  `{"collection":"skills","path":"linn-modder/ui-mod/GUIDE.md"}`，下一步可读取
  `linn-modder/ui-mod/references/layout-and-state.md`。
- JSON CLI/Python：使用同一个 `manual_read` 操作和路径。
- 经验：有工具包时用 `knowledge_search` 查找记录，再读取匹配的 `knowledge` 文件；只有文件工具时，在源码或导出的 `knowledge/` 目录搜索相关记录。网页由客户端联网工具读取。

工具包开发或安装时，从本项目源码仓库目录读取 `docs/development.md` 或 `docs/setup.md`；
这些文档不在复制安装的技能目录中。源码位置按安装记录或客户端配置查找。
