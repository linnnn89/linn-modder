# Linn Modder 技能

统一入口：[linn-modder/SKILL.md](linn-modder/SKILL.md)。客户端发现一个技能，
AI 按入口中的任务表进入主题子文件夹，读取 `GUIDE.md` 和当前步骤的 reference。

完整目录随插件和 wheel 提供；`manuals_export` 导出相同的真实目录。
MCP 的 `um://guide` 与 `um://workflow` 都读取统一入口。

主题资料、英中日网页入口和知识经验按需读取。工具开发与接入方式分别见 checkout
的 `docs/development.md` 和 `docs/setup.md`。
