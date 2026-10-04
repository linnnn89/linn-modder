# Linn Modder

Windows 优先的游戏 Mod 工具，支持 MCP、JSON CLI 和 Python 接口，方便不同
agent harness 复用同一套操作。Agent 负责规划和代码，工具负责检查、素材准备、
备份和窗口操作；技能文档按任务加载。

## 从这里开始

| 你要做什么 | 入口 |
|---|---|
| 安装工具、接入 MCP 或命令行 | [安装与接入](docs/setup.md) |
| 让 agent 选择当前任务的资料 | [统一技能入口](skills/linn-modder/SKILL.md)，再进入对应主题子文件夹 |
| 做二次元策略游戏 Mod | [anime-strategy-mod](skills/linn-modder/anime-strategy-mod/GUIDE.md) · [工作流与支持范围](docs/anime-mods.md) |
| 二次元立绘、表情、Live2D/3D 的制作注意事项 | [二次元素材抽屉](skills/linn-modder/asset-pipeline/references/anime-assets.md) |
| UI MOD、HUD、菜单皮肤、字体或汉化 | [UI MOD](skills/linn-modder/ui-mod/GUIDE.md) |
| 修改配置、数据、脚本、资源与打包文件 | [文件修改](skills/linn-modder/file-mod/GUIDE.md) |
| 联网查证版本、工具和英中日免费学习资料 | [MOD 联网查证](skills/linn-modder/mod-research/GUIDE.md) |
| 学习完整内容 MOD 的组织方式 | [资源分层、稳定标识与交付边界](knowledge/techniques/content-mod-design.md) |
| 找不到 Steam 已下载 MOD | [工坊位置发现方法](skills/linn-modder/game-recon/references/steam-workshop.md) |
| TKEditor 检索、受限编辑和新增头像选项 | [Agent 工具与使用](docs/tkeditor.md) |
| 找官方素材参考、用 GPT Image 制作底图或准备 PSD | [素材流程](skills/linn-modder/asset-pipeline/references/sourcing-and-psd.md) |
| 开发或修改工具本身 | [开发指南](docs/development.md) · [架构](docs/architecture.md) |
| 查看效率实测、专用工具配置与回退方法 | [效率报告](docs/performance.md) |
| 查看素材流程审核与批量处理建议 | [素材优化报告](docs/asset-workflow-review.md) |
| 查已有游戏经验 | [知识库索引](knowledge/INDEX.md) |

## Windows 快速开始

如需让 Agent 自动安装，请先指定电脑上的项目安装路径，让 Agent 将本项目安装到该位置、把完整的 `skills/linn-modder/` 目录安装到客户端技能目录，并在安装后的 `SKILL.md` 中写明项目的实际安装路径，指引 Agent 到该位置查找本项目文件和按需资料，同时按[安装与接入](docs/setup.md)配置所需的 MCP 启动命令、工作区和游戏目录。

安装 Python 3.10+、Git 和 [uv](https://docs.astral.sh/uv/)，在 PowerShell 执行：

```powershell
uv tool install "linn-modder[mcp] @ git+https://github.com/linnnn89/linn-modder"
um doctor
$ModWorkspace = Join-Path (Get-Location) 'mod-workspace'
New-Item -ItemType Directory -Force $ModWorkspace
um tool list --workspace $ModWorkspace
```

先用 `game_profiles` 查看支持范围，再按需调用工具。MCP 客户端使用
`um mcp serve --workspace $ModWorkspace`，完整配置见[安装与接入](docs/setup.md)。
扫描、知识库、项目脚手架和图片处理不需要生成服务的 API key。

## 当前可以做什么

- 同一服务提供严格参数校验、结构化错误和带 hash 的文件产物。
- 离线读取技能/知识库、创建项目、裁切透明 PNG、备份及预览恢复。
- Windows 窗口发现与捕获；输入控制需要明确启用和用户授权。
- 原有素材生成、精灵处理、3D 转帧和视频工具保留为 CLI 命令。
- TKEditor JSON 的 SQLite 分页检索、独立数据工程、带备份和预览确认的受限编辑；
  三尺寸外部 CG 默认新增可选头像，独立命名并可通过数据库搜索，不修改旧武将头像。

| 游戏 | 当前实现 | 适合的起点 |
|---|---|---|
| CK3 | 项目脚手架、descriptor、本地化占位文件 | 图标、事件图、文本与数据；主要肖像为 3D 流程 |
| Victoria II | `.mod` 和目录脚手架 | 旗帜、事件图与按版本核对编码的本地化 |
| 英雄立志传：三国志 / TKEditor | JSON 检索与受限编辑、外部 CG 选项包 | 默认新增头像；数据工程不包含原 MOD 资源，导入与游戏显示尚未验证 |
| 三国志 | 规划配置与素材工作区 | 明确作品、版本、PK 和头像导入方式 |
| 信长之野望 | 规划配置与素材工作区 | 按创造/大志/新生等具体作品确认格式 |

准备好的 PNG、格式检查和实机验证是三个不同阶段。当前没有通用归档导入器、
自动 Mod 构建/安装引擎或远程 PC 桥接。项目使用合成文件和 Windows CI 验证代码，
未安装或运行这些目标游戏。

## 文档如何加载

`AGENTS.md` 保留项目边界与导航；客户端只发现一个 `linn-modder` 技能。
AI 读取统一 `SKILL.md` 后，按任务表进入主题子文件夹，读 `GUIDE.md`，
再读当前步骤需要的 `references/`。14 个主题共用一个技能入口。

Codex 使用 `$linn-modder`；MCP 的 `um://guide` 与 `um://workflow` 读取同一个统一入口，
再用 `manual_read` 读取主题文件。
JSON CLI 与 Python 复用相同读取操作。打包后的技能保持相同目录
结构；需要本地技能目录时可用 `manuals_export` 导出真实文件，避免依赖 Windows
符号链接。目录设计与维护规则见[技能文档设计](docs/skill-design.md)。

统一入口附带一份 `agents/openai.yaml` 展示名称和示例提示。
英中日学习资料按引擎/文件、美术/UI 分抽屉；第一次选工具、
遇到未知格式或版本变化要联网查正文，普通本地修改可复用已验证结论。
这些是技能和经验扩充，不代表工具包新增了 UI 注入器、通用回封器或游戏支持 profile。
共享经验按设计问题组织，不依赖维护者的安装目录或某个成品包；运行时路径由使用者
的配置与环境确定。案例只用于来源追溯，不能成为通用技能的默认目标。

## 来源与许可

由 [Rehan 的 universal-modder](https://github.com/rehan-remade/universal-modder)
派生，保留 MIT 许可与上游版权；字体使用 SIL OFL。设计参考见[架构文档](docs/architecture.md)。
上游的 [Terraria](examples/terraria-tmodloader)、[AoE2](examples/aoe2-de-civ) 和
[Minecraft × GTA V](examples/minecraft-gta5-passthrough) 示例作为参考保留。
