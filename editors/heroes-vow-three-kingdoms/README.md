# 英雄立志传：三国志 — TKEditor Agent 工具

《英雄立志传：三国志》的 JSON 数据、检索、安全编辑和新增外部 CG 接口已集成到
Linn Modder 的共用 Service。MCP 和 JSON CLI 使用同一参数与错误结构。
不增加依赖：SQLite 来自 Python 标准库，图片处理复用 Pillow。
完整参数示例与防呆边界见[按需参考](../../skills/linn-modder/file-mod/references/tkeditor.md)。

## 文件位置

- 本目录：该游戏编辑器的使用入口及后续专属启动脚本、配置示例。
- [Python 实现](../../um/editors/heroes_vow/tkeditor.py)：与其他游戏隔离，共用 Service。
- [工作流测试](../../tests/editors/test_heroes_vow.py)：使用临时 JSON/SQLite/PNG。
- [全部游戏编辑器](../README.md)：统一目录与新增游戏约定。

原有 `tk_*` MCP/CLI 名称、`um.tkeditor` Python 导入和 `.um/tkeditor/` 数据路径保持兼容。
这是 Agent 的 MCP/CLI 编辑器，不是独立图形界面，也不包含官方 TKEditor 或游戏文件。

## 命令行使用

以下是本机已有安装的只读索引示例；更换机器时替换路径。
在仓库根目录使用已有 Python 环境执行，或在安装版本中将 `python -m um` 换成 `um`：

```powershell
$TkWorkspace = 'I:\linn-modder'
$TkModSource = 'D:\STEAM\steamapps\workshop\content\3020510\3473834101'
@{ source = $TkModSource; catalog = 'moezhan' } | ConvertTo-Json | Set-Content -Encoding utf8 index-args.json
python -m um tool call tk_index --workspace $TkWorkspace --game-root $TkModSource --args-file index-args.json
@{ catalog = 'moezhan'; table = 'Hero'; query = '芽衣'; fields = 'id,surname,name,icon'; limit = 5 } |
    ConvertTo-Json | Set-Content -Encoding utf8 query-args.json
python -m um tool call tk_query --workspace $TkWorkspace --game-root $TkModSource --args-file query-args.json
```

创建数据工程：调用 `tk_project`，将目录重新索引到 `edit`；随后调用 `tk_patch`。
默认只预览，应用需要预览的 `confirmation`，并且只能写入工作区独立工程。
创建新头像：调用 `tk_portraits`，默认 `new_option`；通过 `tk_portrait_options` 搜索生成的选项。
登记失败时保留已生成文件，按返回的 `data.recovery` 调用 `tk_portrait_register` 恢复登记，
无需重新生成或覆盖头像包。
具体 JSON 参数见上述参考，避免让 Agent 生成 Python/SQL/全表 JSON。

## MCP 使用

复用现有 `um mcp serve`。每个游戏/工坊目录用重复 `--game-root` 显式允许读取；
工具不会自行查找账户或改安装设置。可用工具筛选减少 schema 上下文：

仅新增头像（4 个工具）：将输入 PNG 放在 `$TkWorkspace` 中，无须允许读取游戏目录。
建议使用专用工作区，避免既有 `default` 索引触发与本任务无关的冲突校验。

```powershell
python -m um mcp serve --workspace $TkWorkspace --enable-tool manual_read --enable-tool tk_portraits --enable-tool tk_portrait_options --enable-tool tk_portrait_register
```

数据检索与安全编辑（7 个工具）：

```powershell
python -m um mcp serve --workspace $TkWorkspace --game-root $TkModSource --enable-tool manual_read --enable-tool tk_index --enable-tool tk_tables --enable-tool tk_query --enable-tool tk_read_field --enable-tool tk_project --enable-tool tk_patch
```

需要替换旧武将头像或混合任务时，使用完整 TKEditor 配置（10 个工具）：

```powershell
python -m um mcp serve --workspace $TkWorkspace --game-root $TkModSource --enable-tool manual_read --enable-tool tk_index --enable-tool tk_tables --enable-tool tk_query --enable-tool tk_read_field --enable-tool tk_project --enable-tool tk_patch --enable-tool tk_portraits --enable-tool tk_portrait_options --enable-tool tk_portrait_register
```

MCP-only Agent 先调用：

```json
{"collection":"skills","path":"linn-modder/file-mod/references/tkeditor.md","max_lines":40}
```

前 40 行包含四条最短流程和参数约定；先选查询、修改、新增头像或替换头像，
再用返回的 `data.next_line` 作为 `start_line` 按需续读细节和错误恢复表。
新增头像无需先检索旧武将；修改确认值须来自预览的 `data.confirmation`。
不预载全部游戏表或所有手册。客户端配置见[安装与接入](../../docs/setup.md)。
如果正在运行已安装的旧 wheel，需要更新到含本次代码的版本并重新启动对应 MCP；
本次开发不会自动覆盖客户端安装或配置。

MCP Schema 声明头像模式枚举、分页范围、索引名称规则和关键参数描述；
后端仍进行严格校验，CLI、MCP 和 Python `Service.invoke` 均不自动转换错误类型。
确定的恢复动作位于 `data.recovery`，包含 `tool` 与 `arguments`；索引过期、未知表和
修改确认值错误另外返回 `available`，表示恢复工具是否被当前服务启用。
`available:false` 时需要调整接入配置，不能绕过白名单。恢复动作只供调用方选择执行，
不会自动运行，也不会自动应用修改。无法确认来源的缺失/损坏索引不猜测重建路径。

## 验证范围

自动测试使用临时 JSON/SQLite/PNG：中文检索、字段投影、长文本分页、重复 ID 保留、
预览确认、原件保护、备份、PNG 三尺寸、默认新增选项、显式替换，以及真实 CLI/MCP stdio。
对本机“萌战无双星誓”进行只读索引和检索：82 张表，57356 行（2026-10-04快照）。
没有运行官方 TKEditor 或游戏来验证导入、显示及兼容性。

数据工程不附带原 MOD 的数 GB 资源包；新增 CG 包需要合并到游戏 Portraits 目录后，
在自建武将界面选择外部 CG。生成结果不会自动安装，不能把准备完成报告成游戏已启用。
