---
name: linn-modder
description: 制作和修改离线游戏 MOD，按任务读取游戏识别、二次元素材、UI、文件、逆向、验证和发布资料。Offline game modding, assets, UI, files and research. ゲームMOD制作・改造。
---

# Linn Modder

这是统一技能入口。先确认任务和目标版本，从下表选一个主题子文件夹，读它的 `GUIDE.md`；
执行当前步骤时，再读该主题的相关 reference。主题目录存放按需资料。

## 按任务进入子文件夹

| 当前任务 | 读取 |
|---|---|
| 完整 MOD、跨阶段工作或路线未定 | [整体流程](mod-any-game/GUIDE.md) |
| 找安装/MOD 位置、识别引擎、判断可行性 | [游戏识别](game-recon/GUIDE.md) |
| 查当前版本、工具、格式与英中日免费资料 | [联网查证](mod-research/GUIDE.md) |
| HUD、菜单、皮肤、字体和界面汉化 | [UI 修改](ui-mod/GUIDE.md) |
| 配置、数据、脚本、纹理或容器文件 | [文件修改](file-mod/GUIDE.md) |
| 二次元策略游戏角色、头像与本地化 | [策略游戏内容](anime-strategy-mod/GUIDE.md) |
| 立绘、表情、PSD、Live2D、精灵与 3D 素材 | [素材制作](asset-pipeline/GUIDE.md) |
| 未知二进制格式、内部逻辑与读写验证 | [逆向分析](reverse-engineering/GUIDE.md) |
| 明确选择 fal 生成素材 | [fal 素材](fal-assets/GUIDE.md) |
| 截图、窗口输入与运行时观察 | [游戏操作](game-automation/GUIDE.md) |
| 融合多个游戏的玩法或模拟 | [玩法融合](mashup-mods/GUIDE.md) |
| 演示视频、预告片或蒙太奇 | [视频制作](showcase-video/GUIDE.md) |
| 打包与发布 MOD | [交付发布](publish-mod/GUIDE.md) |
| 查找、整理和贡献可复用经验 | [知识经验](share-field-notes/GUIDE.md) |

已知任务直接读对应主题。跨阶段任务随工作推进切换主题，每次只读当前需要的资料。
游戏引擎手册按扫描结果选择；工具操作见[共享接口](references/tools.md)。
首次选工具、未知格式、版本变化或陌生错误时，通过联网查证主题核对当前原文。

## 读取方式

- 文件客户端：链接相对本文件解析。
- MCP：`um://guide` 和 `um://workflow` 提供本入口；用 `manual_read` 读取
  `{"collection":"skills","path":"linn-modder/ui-mod/GUIDE.md"}`，下一步可读取
  `linn-modder/ui-mod/references/layout-and-state.md`。
- JSON CLI/Python：使用同一个 `manual_read` 操作和路径。
- 经验：先 `knowledge_search`，再读取匹配的 `knowledge` 文件；网页由客户端联网工具读取。

输出与检查按用户任务选择：staged 文件、格式结果、运行证据或发布产物。
工具开发读取 checkout 的 `docs/development.md`；安装与客户端接入读取 `docs/setup.md`。
