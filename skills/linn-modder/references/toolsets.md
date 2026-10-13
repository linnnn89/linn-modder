# 按任务选择本地工具

用于配置 MCP 或减少无关工具说明。下面是现有 `--enable-tool` 的配置示例，不增加安装器、工具注册机制或新的权限。已有会话满足任务时不必重配。

| 任务 | 可复制的 MCP JSON | 覆盖范围 |
|---|---|---|
| CK3 制作与排错 | [ck3.json](toolsets/ck3.json) | 扫描、知识/手册、项目、图片、备份与 `ck3_check`；12 个工具 |
| 其他 P 社游戏 | [paradox.json](toolsets/paradox.json) | 同上但无 CK3 专属检查；11 个工具。项目脚手架仍只支持已实现的 profile |
| TKEditor 数据与头像 | [tkeditor.json](toolsets/tkeditor.json) | 环境、手册、9 个 TKEditor 操作；11 个工具，包含索引刷新和头像登记恢复 |

把 `<ABSOLUTE_WORKSPACE>` 换成现有工作目录；需要读取游戏文件时在 `args` 添加 `--game-root` 与实际游戏目录。游戏目录保持只读。客户端不采用 `mcpServers` 顶层键时，照搬其中 `command` 和 `args` 到它的 server 配置。

需要其他工具时追加 `--enable-tool` 和准确工具名，重启 server。桌面输入仍需 `--allow-input`。这些配置不包含远程控制桥接、通用文件编辑器、自动安装或素材生成器；脚本编写、官方参考检索和 GPT Image 使用 harness 已有能力。

默认仍公开全部操作（现在为 24 个）；不要求每个 harness 更换配置。JSON CLI 默认的 `um tool list` 保持简短，需要字段范围/枚举和使用提示时才用 `um tool list --details`。其中 `parameter_hints` 是与 MCP 共用的参数说明；Python 可用 `Service.parameter_hints(name)`。真正执行时仍由后端校验，不会把字符串自动转换成数字或布尔值。

安装位置与客户端设置见当前工具安装记录。技能复制后，这些 JSON 与文档仍在同一目录树；MCP-only 客户端可用 `manual_read(collection="skills", path="linn-modder/references/toolsets/ck3.json")` 获取配置文本。
