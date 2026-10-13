# 工具发现与 CK3 检查：架构迭代记录

2026-10-13；基线 `fdb3a53cc4f3014cb7f528548690c6fa27a73744`。保留单体工具库、共享 Service、一个技能入口和现有调用方式。目标是减少无关工具说明与重复排错，不增加插件注册框架、调度队列或统一游戏解析器。

## 实现与边界

- **选择工具。** 三个可复制的 [MCP 配置](../skills/linn-modder/references/toolsets.md) 复用已有 `--enable-tool`，随手册打包。默认配置仍兼容原调用，新增 `ck3_check` 后为 24 个工具；精简配置需主动选用。
- **参数说明归游戏模块。** TKEditor 的枚举、范围与提示从 MCP 移到 `um/editors/heroes_vow/metadata.py`。`Service.parameter_hints` 筛选实际存在且启用的参数；MCP 和可选的 `um tool list --details` / Python 共用。默认 CLI 列表的字段不变，CLI 不依赖 MCP；后端校验保持原样。
- **CK3 检查闭环。** `um/editors/ck3/check.py` 检查 descriptor 存在/UTF-8/非空，以及本地化文件名/BOM/语言头。一次调用汇总问题并分页，提供准确文件和行号。只遍历 `localization/`，不扫描全部图片资源。
- **复用 Tiger。** 可导入已有 JSON 数组，保留 error/fatal/warning/tips/untidy、多位置与置信度。报告路径只是诊断标签，不据此读外部文件。报告格式来自作者固定版本的 [JSON writer 与级别定义](../skills/linn-modder/anime-strategy-mod/references/ck3-check.md)。没有引入第三方代码或运行依赖。

`ok` 表示操作完成；检查是否有 error/fatal 看 `data.passed`。本地检查不解析完整 descriptor、本地化正文或脚本语义，也不检查启动器是否注册成功。Tiger 由使用者已有环境运行，本工具只读报告；报告没有足够的输入版本/哈希和执行状态，因此保留 `freshness:not-verified`。空报告不升级为脚本或实机验证。全过程无自动安装、执行外部程序或写入游戏。

## 效率与兼容性

预先目标：三套配置相对旧默认工具目录均减少至少 40%；固定上下文逐字节不变；原工具 schema 不变。用同一 Python 3.12.14 / MCP 1.29.0 获取完整工具目录，以 `json.dumps(..., ensure_ascii=False)` 计算实际字符/UTF-8 字节；本次目录内容为 ASCII，两者相同。

| 配置 | 工具数 | 目录字符 | 相对旧默认减少 |
|---|---:|---:|---:|
| 修改前默认 | 23 | 41,476 | 基线 |
| 修改后默认 | 24 | 43,474 | 增加 1,998（4.82%） |
| CK3 专用 | 12 | 18,699 | **54.92%** |
| 其他 P 社专用 | 11 | 16,701 | **59.73%** |
| TKEditor 专用 | 11 | 23,655 | **42.97%** |

三个目标配置均达标。23 个旧工具的完整 MCP schema/说明/注解逐项保持一致，`AGENTS.md` 与 `SKILL.md` 原样保留。收益来自选择适用工具，旧版本其实已经具备白名单能力；本次把它落实为可复制、可验证的配置。没有声称默认模式变小，也没有把字符数当 Token、网络耗时或完整任务完成时间。

检查效果用合成工程验证：`ck3_check` 定位 **6 类同时存在的问题**（空 descriptor、缺 BOM、语言不一致、缺语言头、错误后缀、非法 UTF-8），报告包含具体位置，分页仍保留全局错误统计。按报告修正后复查通过。另验证已有 Tiger 多位置诊断、损坏/非 UTF-8 报告拒绝、空报告时效标记、只读根与真实 CLI/MCP 调用。此结果不代表真实 MOD 错误检出率。

原始记录：[architecture-toolsets-20261013.json](benchmarks/architecture-toolsets-20261013.json)。其中保留基线提交、提交前 dirty 状态、Python 源码摘要和目标结果。复现：

```sh
git worktree add --detach ../linn-architecture-before backup/pre-architecture-20261013
python scripts/benchmark_toolsets.py --before ../linn-architecture-before --output scratch/toolsets.json
```

## 验收与回退

本地集中测试 **148 passed、2 skipped**；跳过项需原生 Windows。包含无 site-packages 的 JSON CLI 参数发现，证明该路径不要求 MCP。文档结构、知识库索引、发布内容、构建和独立安装 wheel 检查均通过；Windows/Linux CI 结果见本次 PR。没有安装游戏、运行 Tiger 或开展实机验证。

远端备份 **`backup/pre-architecture-20261013`** 指向 `fdb3a53`。可从该分支建立独立工作树使用旧版，或对本次 squash 提交执行 `git revert <提交号>` 后正常合入。无需强推远端历史；已有工具名、参数与工作区数据位置保留。
