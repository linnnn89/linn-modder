---
name: file-mod
description: 安全修改离线游戏的配置、JSON/CSV、本地化、脚本、纹理和容器文件，保留编码、ID、引用和可恢复性。Use for known file edits; route unknown binary formats to reverse-engineering. ファイル編集、設定変更。
---

# 游戏文件修改

1. 确认目标 build、文件用途、magic/编码、读取者与写入者；扩展名不等于格式。先区分游戏本体、Workshop 下载、官方编辑器工程、模组输出和存档。
2. 优先官方编辑器/SDK 或已有可靠 writer。未知格式、工具兼容性、版本变更及陌生错误必须先[联网查证](../mod-research/SKILL.md)。
3. 原件只读，在 workspace 保存基线 hash 和待改副本，限定文件/ID/字段；安装、覆盖存档或本体另按已有授权执行。
4. 用一个最小改动验证读 → 写 → 再读；比较未改数据、跨文件引用和目标内容。失败保留原件与最后成功产物，不尝试盲目批量修复。
5. 交付输出、精确改动清单、依赖与恢复步骤。不要把能解析/能导出称为游戏可用。

## 按格式打开

| 当前对象 | 抽屉 |
|---|---|
| JSON、CSV、YAML、INI、XML、脚本和本地化 | [文本与数据](references/text-and-data.md) |
| 纹理、音频、模型、二进制、归档和存档 | [二进制与资源](references/binary-and-assets.md) |
| 未知格式/不确定能否写回 | [逆向调查](../reverse-engineering/SKILL.md) |
| 官方工具/格式规范 | [免费文件资料](../mod-research/references/engine-and-file-sources.md) |

本工具包没有通用游戏文件写入/回封接口；用当前环境真实存在的编辑能力，不编造服务工具。三次失败的修改验证后停止盲改，重新收集证据。
