# Linn Modder

Windows-first mod toolkit; MCP, JSON CLI and Python share one service.
Follow the user's requested scope. Toolkit/code work uses synthetic fixtures;
a real game installation, gameplay test or showcase is required only when requested.

## Load on demand
- Modding task: read the single entry `skills/linn-modder/SKILL.md`, then the matching topic's `GUIDE.md` and current reference.
- Topic folders are on-demand documents. Keep one discoverable `SKILL.md`; do not preload all guides.
- Toolkit code/integration: read `docs/development.md`; read `docs/architecture.md` when changing service boundaries.
- Installation or harness configuration: read `docs/setup.md`.
- Reuse prior game findings: search the knowledge base; read only relevant matches.
- Verify unfamiliar formats, tool choices and version changes online through the `mod-research` topic.

## Always keep
- Use owned offline games; no protected online-client modification or protection bypasses.
- Stage changes in the workspace; service game roots remain read-only. Back up affected saves/config first.
- Never commit game files, extracted assets, decompiled dumps or secrets; kill processes by exact PID.
- Desktop input, installation/registry changes and publication need user authorization; reuse authorization already given.
- Keep evidence/unknowns in `MODLOG.md` for mod work; distinguish prepared art, format validation and game verification.
- Keep MCP/JSON stdout clean and operational errors structured. State unsupported formats honestly.

## 验证范围与预算

- 局部修改只验证受影响文件、直接调用链及相关测试；生成、打包、安装、交付各阶段不得反复全项目枚举、读取、哈希或比对。
- 默认使用写入路径白名单、变更清单、受影响文件备份及安装前后定向核对。不得为证明无关文件未变，或因现有脚本默认全量校验而扩大范围，应改用定向入口。
- 仅用户明确要求全项目审计，或具体异常无法定向定位时扩大范围；同一未变化状态最多建立一次必要全量基线并复用。
- 相关内容未变且无新失败证据时，不重复已通过检查。保留任务要求的存档保护核对，但不扩大为全项目核对。

## Harness compatibility

`AGENTS.md` 为规范入口；客户端格式见 `docs/setup.md`，共享流程放在 `skills/`，不按客户端重复。
Windows 的 `../skills` 文本指针不能自动发现技能；复用现有插件、MCP 手册读取或导出的实体目录。
保留兼容清单，不创建空的平台技能目录。
