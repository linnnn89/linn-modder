# Linn Modder

Windows 优先的游戏 Mod 工具，支持 MCP、JSON CLI 和 Python 接口，方便不同
agent harness 复用同一套操作。Agent 负责规划和代码，工具负责检查、素材准备、
备份和窗口操作；技能文档按任务加载。

## 从这里开始

| 你要做什么 | 入口 |
|---|---|
| 安装工具、接入 MCP 或命令行 | [安装与接入](docs/setup.md) |
| 让 agent 选择当前任务的技能 | [技能导航](skills/README.md)；已知任务直接读对应 `SKILL.md` |
| 做二次元策略游戏 Mod | [anime-strategy-mod](skills/anime-strategy-mod/SKILL.md) · [工作流与支持范围](docs/anime-mods.md) |
| 开发或修改工具本身 | [开发指南](docs/development.md) · [架构](docs/architecture.md) |
| 查看效率实测、专用工具配置与回退方法 | [效率报告](docs/performance.md) |
| 查已有游戏经验 | [知识库索引](knowledge/INDEX.md) |

## Windows 快速开始

安装 Python 3.10+、Git 和 [uv](https://docs.astral.sh/uv/)，在 PowerShell 执行：

```powershell
uv tool install "linn-modder[mcp] @ git+https://github.com/linnnn89/linn-modder"
um doctor
New-Item -ItemType Directory -Force C:\Mods
um tool list --workspace C:\Mods
```

先用 `game_profiles` 查看支持范围，再按需调用工具。MCP 客户端使用
`um mcp serve --workspace C:\Mods`，完整配置见[安装与接入](docs/setup.md)。
扫描、知识库、项目脚手架和图片处理不需要生成服务的 API key。

## 当前可以做什么

- 同一服务提供严格参数校验、结构化错误和带 hash 的文件产物。
- 离线读取技能/知识库、创建项目、裁切透明 PNG、备份及预览恢复。
- Windows 窗口发现与捕获；输入控制需要明确启用和用户授权。
- 原有素材生成、精灵处理、3D 转帧和视频工具保留为 CLI 命令。

| 游戏 | 当前实现 | 适合的起点 |
|---|---|---|
| CK3 | 项目脚手架、descriptor、本地化占位文件 | 图标、事件图、文本与数据；主要肖像为 3D 流程 |
| Victoria II | `.mod` 和目录脚手架 | 旗帜、事件图与按版本核对编码的本地化 |
| 三国志 | 规划配置与素材工作区 | 明确作品、版本、PK 和头像导入方式 |
| 信长之野望 | 规划配置与素材工作区 | 按创造/大志/新生等具体作品确认格式 |

准备好的 PNG、格式检查和实机验证是三个不同阶段。当前没有通用归档导入器、
自动 Mod 构建/安装引擎或远程 PC 桥接。项目使用合成文件和 Windows CI 验证代码，
未安装或运行这些目标游戏。

## 文档如何加载

`AGENTS.md` 只保留项目边界与导航；`CLAUDE.md` 引用同一入口。技能发现只需要
简短的 `name`/`description`，匹配任务后才读 `SKILL.md`，执行某一步时才读
对应 `references/`。无需每次加载全部手册、命令样例或引擎知识。

MCP 提供 `um://guide` 导航和 `manual_read` 单文件读取。打包后的技能保持相同目录
结构；需要本地技能目录时可用 `manuals_export` 导出真实文件，避免依赖 Windows
符号链接。目录设计与维护规则见[技能文档设计](docs/skill-design.md)。

## 来源与许可

由 [Rehan 的 universal-modder](https://github.com/rehan-remade/universal-modder)
派生，保留 MIT 许可与上游版权；字体使用 SIL OFL。设计参考见[架构文档](docs/architecture.md)。
上游的 [Terraria](examples/terraria-tmodloader)、[AoE2](examples/aoe2-de-civ) 和
[Minecraft × GTA V](examples/minecraft-gta5-passthrough) 示例作为参考保留。
