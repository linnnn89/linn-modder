# 游戏编辑器

这里统一收纳自己制作的游戏编辑器。每个游戏一个稳定的英文目录名，中文名称和
Steam AppID 写在说明里；同一游戏的多个工具放在同一目录下。

| 游戏 | 目录 | 现有能力 | 验证边界 |
|---|---|---|---|
| 英雄立志传：三国志 / Heroes' Vow: Three Kingdoms（3020510） | [heroes-vow-three-kingdoms](heroes-vow-three-kingdoms/README.md) | TKEditor JSON 分页检索、安全编辑、外部 CG 选项包；MCP / JSON CLI / Python | 工具工作流验证；官方编辑器导入和游戏显示未验证 |

## 新游戏放在哪里

- `editors/<game-slug>/`：使用说明、该游戏专属的启动脚本与配置示例（有需要再添加）。
- `um/editors/<game_module>/`：需要共享 MCP/CLI 的 Python 实现，由现有 Service 调用，随 wheel 分发。
- `tests/editors/`：按游戏命名的合成数据工作流测试。
- `skills/linn-modder/`：保留唯一技能入口；Agent 操作参考继续按主题归档，供安装版按需读取。

实际工程、索引、备份和生成素材放在独立工作区；临时开发产物可放在已忽略的
`scratch/<game-slug>/`。不提交游戏本体、官方编辑器、提取资源、存档、私人配置或构建产物。

已部署到游戏旁的工具是独立安装副本；整理此仓库不会自动搬迁或升级它们。
安装与更新方式见[接入说明](../docs/setup.md)。
