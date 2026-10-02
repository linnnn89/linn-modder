# Linn Modder

Windows 优先、与 agent harness 解耦的游戏 Mod 工具。由
[universal-modder](https://github.com/rehan-remade/universal-modder) 派生，
保留其 Python CLI、素材工具和知识库，并增加共享服务层、JSON 接口和 MCP stdio server。

当前关注 CK3、维多利亚 2、三国志和信长之野望的二次元化 Mod。
**CK3/Victoria II 提供项目脚手架；光荣系列提供规划配置，尚无通用归档导入器。**

- [项目结构与设计参考](docs/architecture.md)
- [二次元 Mod 工作流与游戏支持范围](docs/anime-mods.md)
- [已有游戏实战知识库](knowledge/INDEX.md)

## 安装：原生 Windows，不需要 WSL

需要 Python 3.10+、Git 和 [uv](https://docs.astral.sh/uv/)。
在 PowerShell 执行（代码合并到默认分支后使用此安装地址）：

```powershell
uv tool install "linn-modder[mcp] @ git+https://github.com/linnnn89/linn-modder"
um --version
um doctor
```

在当前 checkout 中开发：

```powershell
uv sync --extra mcp --extra dev
uv run um doctor
.\bin\um.cmd tool list
```

安装包同时提供 `um` 和 `linn-modder` 两个入口。只需 CLI 时可不安装
`mcp` extra。FFmpeg、Blender 和 fal key 按功能需要配置；扫描、知识库、
项目脚手架和本地图片处理不需要 fal key。

`um win setup` 可下载 Windows 截图所需的 FFmpeg 并放置 PowerShell 工具。
`um doctor` 只检查环境，不安装依赖。窗口捕获需要带 `gfxcapture` 的 FFmpeg。

## 接入 agent harness

### MCP

先创建工作目录。在支持 stdio MCP 的客户端中添加以下 server；顶层配置键可能
因客户端不同而变化，使用绝对路径避免工作目录歧义：

```json
{
  "mcpServers": {
    "linn-modder": {
      "command": "um",
      "args": [
        "mcp", "serve",
        "--workspace", "C:\\Mods",
        "--game-root", "D:\\Games"
      ]
    }
  }
}
```

客户端需能在 PATH 找到已安装的 `um`；也可填写 `um.exe` 的绝对路径。
只有在用户同意桌面控制后才添加 `--allow-input`。默认工具列表不含输入操作。
`--game-root` 可重复指定，通过服务层始终只读。远端 agent 需要额外的认证桥接，
本项目当前提供本机 stdio 接入。

| 工具 | 用途 |
|---|---|
| `environment_check` | 平台、依赖与能力诊断 |
| `game_profiles` / `game_scan` | 游戏适配范围、安装目录指纹 |
| `knowledge_search` / `manual_read` | 离线知识库、引擎与操作手册 |
| `manuals_export` | 将完整 Skills 与知识库复制到工作区 |
| `project_create` | 按游戏创建二次元 Mod 开发项目 |
| `image_prepare` | 图片裁切、缩放、透明 PNG 中间产物 |
| `backup_create` / `backup_list` / `backup_verify` | 工作区快照、列表及完整性校验 |
| `backup_restore` | 预览恢复差异，执行恢复并保存撤销快照 |
| `windows_list` / `window_capture` | 窗口发现、截图和原生 MCP 图片预览 |
| `window_input` | 可选的按 PID 控制，显式聚焦 |

每个工具有独立参数 schema。结果包含 `ok`、`data`、`artifacts` 和 `error`；
文件产物附带路径、类型、大小和 SHA-256。MCP 错误同时设置 `isError`。

### CLI 与 Python SDK

能执行命令的 harness 使用相同服务层：

```powershell
um tool list --workspace C:\Mods
um tool call game_profiles --workspace C:\Mods
um tool call project_create --workspace C:\Mods --args-file create-project.json
```

参数文件避免 PowerShell 对内联 JSON 引号的不同处理：

```json
{"destination":"projects/anime_ck3","profile":"ck3","name":"anime_ck3","game_version":"unknown"}
```

参数文件支持 UTF-8，包含 Windows PowerShell 5.1 常用的 BOM。MCP、JSON CLI
与 Python 服务使用相同的严格参数校验；未知参数和错误类型返回结构化错误。

备份默认存放在工作区的 `.um/backups/<name>/`。使用 `backup_restore` 时必须
指定工作区内的 `target`，默认仅预览差异：

```json
{"name":"anime-saves","target":"saves","clean":false,"apply":false}
```

检查结果后设置 `apply:true` 执行恢复。工具先验证整个快照的路径、大小和校验和，
再暂存解压文件；覆盖前将当前目录保存到 `<name>-pre-restore`，结果中的
`undo_snapshot` 可用于撤销。`clean:true` 会删除目标中快照未包含的文件。
服务层的恢复目标保持在工作区内，游戏目录仍只读。旧 CLI 通过相同存储位置访问：

```powershell
um backup list anime-saves --store C:\Mods\.um
um backup diff anime-saves C:\Mods\saves --store C:\Mods\.um
```

```python
from um.service import Service

service = Service(r"C:\Mods", game_roots=(r"D:\Games",))
try:
    result = service.invoke("game_profiles", {})
    print(result.to_dict())
finally:
    service.close()
```

Skills 和知识库随 wheel 一同发布，可离线读取，无需依赖 Windows 符号链接。
原有各厂商插件清单保留了上游接入方式；本 fork 推荐使用这里的 MCP 或 CLI 配置。

## 保留的底层工具

原有 `um scan`、`fal`、`sprite`、`render3d`、`video`、`win`、`backup`、
`publish` 和 `kb` 命令仍可使用，每组有 `--help`。
生成素材可选用 fal；3D 转精灵图依赖 Blender；视频处理依赖 FFmpeg。
这些直接 CLI 命令不继承新 Service 的目录限制。

上游的 [Terraria](examples/terraria-tmodloader)、
[AoE2](examples/aoe2-de-civ) 和
[Minecraft × GTA V](examples/minecraft-gta5-passthrough) 实例作为参考保留。
它们不构成本 fork 对新目标游戏的实机验证。

## 开发与验证

```powershell
uv run --extra mcp --extra dev pytest -q tests
uv run um kb check --index
uv run um publish check .
uv run --extra dev python -m build
```

CI 覆盖 Ubuntu/Windows 和 Python 3.10/3.12，并验证独立安装的 wheel。
测试使用模拟游戏目录、合成图片/存档、fake Windows backend 和真实 MCP stdio
会话。Windows CI 编译 WinDrive，但不安装或控制真实游戏。

当前服务层没有通用的 Mod 编译/安装引擎，也未提供持久后台任务、远程 HTTP
控制或光荣资源包回写。对应扩展边界见 [architecture.md](docs/architecture.md)。

## Credits and license

Fork of [Rehan's universal-modder](https://github.com/rehan-remade/universal-modder).
MIT licensed; upstream copyright and [LICENSE](LICENSE) are retained.
Bundled Space Grotesk and JetBrains Mono fonts use SIL OFL.
Design references and adopted patterns are documented in [architecture.md](docs/architecture.md).
