# 安装与 agent 接入

按需要选择 MCP、JSON CLI 或 Python；三种接口使用同一个 `Service`。
以下命令以 Windows PowerShell 为例；目录由使用者选择，不预设盘符或安装位置。
详细操作见[工具接口](../skills/references/tools.md)。

## 安装

需要 Python 3.10+、Git 和 [uv](https://docs.astral.sh/uv/)。在 PowerShell 执行：

```powershell
uv tool install "linn-modder[mcp] @ git+https://github.com/linnnn89/linn-modder"
um --version
um doctor
```

只用 CLI 时可以去掉 `[mcp]`。安装同时提供 `um` 和 `linn-modder` 两个入口。
开发 checkout 用 `uv sync --extra mcp --extra dev`，通过 `uv run um` 或
`.\bin\um.cmd` 执行，详见[开发指南](development.md)。

按功能配置依赖：扫描、手册、项目和本地图片处理不需要 fal；3D 渲染需要 Blender，
视频处理需要 FFmpeg。`um win setup` 可下载带 `gfxcapture` 的 Windows FFmpeg。
`um doctor` 只检查环境；诊断和截图按相同规则选择 FFmpeg：`UM_FFMPEG_WIN`、
工具下载目录、Windows PATH。

## MCP：本机 stdio

先创建工作目录。在客户端添加以下 server；顶层配置键可能因 harness 而不同。
使用绝对路径，并确保客户端能在 PATH 找到安装的 `um`，或填写 `um.exe` 的完整路径。
下方 `<ABSOLUTE_WORKSPACE>` 和 `<ABSOLUTE_GAME_ROOT>` 是需要替换的占位符，
不是工具会自动展开的变量；JSON/TOML 中 Windows 反斜杠需要按各自语法转义。
游戏目录应由使用者指定或通过安装元数据确认，仅使用手册时可省略 `--game-root`。

PowerShell 命令示例使用以下变量，可将其改为自己的工作目录：

```powershell
$ModWorkspace = Join-Path (Get-Location) 'mod-workspace'
New-Item -ItemType Directory -Force $ModWorkspace
```

```json
{
  "mcpServers": {
    "linn-modder": {
      "command": "um",
      "args": ["mcp", "serve", "--workspace", "<ABSOLUTE_WORKSPACE>", "--game-root", "<ABSOLUTE_GAME_ROOT>"]
    }
  }
}
```

Codex 的同一配置可写为：

```toml
[mcp_servers.linn-modder]
command = "um"
args = ["mcp", "serve", "--workspace", "<ABSOLUTE_WORKSPACE>", "--game-root", "<ABSOLUTE_GAME_ROOT>"]
```

`--game-root` 可重复指定，服务层保持这些目录只读。只有桌面输入已获授权时，
才加入 `--allow-input`；默认没有输入工具。远端/cloud harness 需要独立的认证桥接，
stdio 配置本身不提供远程 PC 访问。

Codex 已发现技能时按任务描述选择一个；MCP 需要选择任务时读 `um://guide`。
知道任务时直接用 `manual_read` 读取对应技能。例如：

```json
{"collection":"skills","path":"anime-strategy-mod/SKILL.md"}
```

将这组参数传给 `manual_read`。技能中的 `references/targets.md` 是相对链接，下一次
读取使用 `anime-strategy-mod/references/targets.md`。只读取当前步骤需要的文件。

长手册可以传 `start_line:1,max_lines:40`，按返回的 `next_line` 续读；`next_line:null`
表示已读完。默认参数仍返回全文。分页可减少首次上下文，全文必读时直接读取全文更省调用。

仅有本项目 MCP 的 harness 还需自己的文件编辑能力，才能编写 Mod 脚本、本地化和
清单。Linn Modder 当前不提供通用文件读写工具。

### 专用任务的工具清单

通用配置默认暴露全部 14 个工具；`--allow-input` 额外启用输入工具。
专用 harness 可以重复传 `--enable-tool NAME`，只加载当前任务所需的 schema，例如：

```powershell
um mcp serve --workspace $ModWorkspace --enable-tool game_profiles --enable-tool manual_read --enable-tool project_create --enable-tool image_prepare --enable-tool backup_create
```

这是项目创建和素材准备配置；需要扫描、恢复或窗口操作时，将对应工具加入配置并重启
server。`--enable-tool` 不会自动启用桌面输入；选入 `window_input` 仍需 `--allow-input`。
未知工具名在启动时失败，避免配置错误被忽略。JSON CLI 接受相同选项，Python 使用
`Service(..., enabled_tools=("game_profiles", "manual_read"))`。

筛选同时作用于工具发现与 `Service.invoke`。它是工具配置，不是操作系统权限隔离；
只读 MCP 导航资源仍可读取。实测收益、适用范围与复现方法见[效率报告](performance.md)。

## JSON CLI

有 shell 的 harness 可用相同服务层。参数文件避免 PowerShell 的 JSON 引号差异，
支持带 BOM 的 UTF-8：

```powershell
um tool list --workspace $ModWorkspace
um tool call game_profiles --workspace $ModWorkspace
um tool call project_create --workspace $ModWorkspace --args-file create-project.json
```

`create-project.json`：

```json
{"destination":"projects/anime_ck3","profile":"ck3","name":"anime_ck3","game_version":"unknown"}
```

每次调用只在 stdout 输出一个 JSON 结果。失败返回非零退出码和结构化 `error`。
产物包含路径、类型、大小和 SHA-256；结果字段详见[工具接口](../skills/references/tools.md)。

## Python

```python
from pathlib import Path
from um.service import Service

workspace = Path("mod-workspace").resolve()
workspace.mkdir(parents=True, exist_ok=True)
service = Service(workspace)
try:
    result = service.invoke("game_profiles", {})
    print(result.to_dict())
finally:
    service.close()
```

## 本地技能与兼容入口

Codex 优先复用仓库 `AGENTS.md` 和现有插件中的 `skills/`。本地自动发现需要真实的
`.agents/skills/<name>/SKILL.md` 目录或有效符号链接；Windows checkout 中内容为
`../skills` 的普通指针文件不等于符号链接，也不会自行变成可发现的技能目录。
先检查文件类型，再选择插件、MCP 按需读取或导出，不能仅凭指针存在声称安装成功。

Windows checkout 未启用符号链接时，使用 MCP 的 `manual_read`，或调用
`manuals_export` 导出真实目录，再将其 `skills/` 按客户端规范放入技能搜索路径。
导出只是文件准备，不需要将所有文件塞进每轮提示词。

例如通过服务调用 `manuals_export`，参数为 `{"destination":"manuals"}`（工作区内
尚不存在的目录），得到 `manuals/skills/` 和 `manuals/knowledge/`。需本地自动发现时，
按客户端安装规则使用这份真实 `skills/` 目录，保留 `references/`、共享引用和
`agents/openai.yaml`。已有目录不要整目录覆盖；更换位置后检查新会话的技能列表，
或显式指向 `SKILL.md` 验证可读取。插件发现和实际模型选择仍由客户端负责。

新任务可直接指定 `$mod-research`、`$ui-mod` 或 `$file-mod`（技能已被客户端发现时），
也可让 agent 读取仓库内对应文件。MCP-only 用 `manual_read` 读取同一个路径；
不支持 `$skill` 的客户端仍按自然语言任务路由。联网使用 harness 自带的搜索/网页
能力，图像任务使用已有 provider；阅读资料、文件检查和 UI 经验学习不依赖 fal key。

| 入口 | 兼容约定 |
|---|---|
| `AGENTS.md` | Codex/Agents 共用项目边界与导航 |
| `plugin.json` + `mcp.json` | 保留 Agent Plugins 根清单与 `streamable-http` 格式 |
| `.codex-plugin/plugin.json` | 保留已有 Codex 兼容清单，skills/MCP 路径相对插件根；不另建插件 |
| `.codex/config.toml` | 可选 fal HTTP MCP，以 `FAL_KEY` 环境变量认证；不是本地 um MCP |
| `.claude-plugin/` + `.mcp.json` | 保留 Claude 插件与 HTTP MCP 格式 |
| `.cursor-plugin/` | 保留 Cursor 市场/插件元数据 |
| `gemini-extension.json` | `contextFileName` 指向 `AGENTS.md`，保留 Gemini 接入 |
| 可选 `CLAUDE.md` / `GEMINI.md` | 如启用，分别用 `@AGENTS.md` 单行导入 / 普通文字要求读取 `AGENTS.md`；文件缺失时不假定它们被加载 |

官方依据（2026-10-03 阅读）：[Codex 技能发现与渐进加载](https://learn.chatgpt.com/docs/build-skills)、
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、
[插件打包和兼容清单](https://developers.openai.com/plugins/build/plugins)。
保留已有 `universal-modder` 标识，避免把内容更新变成重新安装/迁移。

上游插件保留 `universal-modder` 标识及可选 fal 配置，以兼容已有安装；其简短描述用于
发现；仓库/安装地址指向本 fork，元数据版本与工具包一致。Claude 的 SessionStart hook 只设置 PATH，不向上下文注入手册。原生 Windows
推荐上面的安装入口，Bash hook 依赖对应 shell。需要 fal 时再读取
[fal-assets](../skills/fal-assets/SKILL.md)。

## 备份恢复

`backup_create/list/verify/restore` 共用工作区的 `.um`。恢复需要工作区内的目标，默认
仅预览；检查差异后，用 `apply:true` 执行已授权的恢复。`clean:true` 删除快照中没有的
文件。覆盖前保存撤销快照，结果给出 `undo_snapshot`。

```json
{"name":"anime-saves","target":"saves","clean":false,"apply":false}
```

旧 CLI 可查询同一存储：

```powershell
um backup list anime-saves --store (Join-Path $ModWorkspace '.um')
um backup diff anime-saves (Join-Path $ModWorkspace 'saves') --store (Join-Path $ModWorkspace '.um')
```

更多恢复边界见[工具接口](../skills/references/tools.md)。原有 `um win`、`backup`、
`fal` 等直接 CLI 命令保持原接口，不继承 Service 的工作区限制。
