---
name: linn-modder
description: >-
  用于已有离线游戏的 MOD 制作、修改与排错。当用户要找游戏/MOD/Steam 创意工坊目录、判断游戏能否改、安装或修复模组、更新后恢复兼容、换角色头像/立绘/皮肤/纹理/音效、制作二次元内容、改 HUD/菜单/布局/字体/汉化、调整配置/数据/脚本/存档数值、分析或解包回封资源、查找模组工具与教程、验证或打包发布 MOD 时使用；即使请求没有写出“MOD”也适用。根据游戏与版本选择路线，按需读取子文件夹，并联网查证工具和格式。
  Use for offline game modding, Steam Workshop paths, asset swaps, UI/localization, save edits, mod troubleshooting and packaging.
  ゲームMOD制作・導入、不具合修正、立ち絵差し替え、UI改造、日本語化。
---

# Linn Modder

Owned offline games: back up saves/config; edit workspace copies. Read one topic
and current reference; reuse loaded routes. Log evidence/unknowns in `MODLOG.md`:
prepared files, format checks and in-game verification are separate outcomes.

| Task / 任务 | Read |
|---|---|
| Whole mod / 路线未定 | [Workflow](mod-any-game/GUIDE.md) |
| Locate game/Workshop, install/debug mods / 目录与排错 | [Recon](game-recon/GUIDE.md) |
| Unknown tools/formats or version changes / 联网查证 | [Research](mod-research/GUIDE.md) |
| HUD, menus, fonts, localization / 界面汉化 | [UI](ui-mod/GUIDE.md) |
| TKEditor; config, scripts, saves, textures/audio, unpack/repack / 文件修改 | [Files](file-mod/GUIDE.md) |
| Anime strategy characters, factions / 二次元策略 | [Strategy](anime-strategy-mod/GUIDE.md) |
| Portraits, transparency, PSD/Live2D, sprites/3D / 素材 | [Assets](asset-pipeline/GUIDE.md) |
| Unknown binaries, internals, round trips / 逆向 | [Reverse](reverse-engineering/GUIDE.md) |
| Explicit fal generation | [fal](fal-assets/GUIDE.md) |
| Capture/input / 游戏操作 | [Automation](game-automation/GUIDE.md) |
| Cross-game mechanics / 玩法融合 | [Mashups](mashup-mods/GUIDE.md) |
| Trailer/video | [Video](showcase-video/GUIDE.md) |
| Package/release | [Publish](publish-mod/GUIDE.md) |
| Reuse/contribute findings | [Knowledge](share-field-notes/GUIDE.md) |

Research unfamiliar tools/formats and version changes first. Distribute mod files only.

Resolve links from this file's directory. MCP `um://guide` and `um://workflow` return
this entry; `manual_read` uses collection `skills` and path `linn-modder/<topic>/GUIDE.md`.
Tools, knowledge and installation: [interfaces](references/tools.md).
