# 搜索定位、CK3 诊断过滤与 DDS 指南

2026-10-14；基线 `57fb14bd577e298c3dc7fe6e9f03623a2dfa5324`。

## 实施前固定的范围与目标

仅调整现有知识搜索、CK3 检查和按需素材文档。保持 24 个默认工具、单一 Service、
单一 SKILL.md；不新增运行依赖、验证器执行器、自动安装器或游戏解析器。

以下六个查询在实施前固定。`game` 使用笔记记录的名称，query 使用当前问题的关键词。

| 任务 | game | query | 预期章节 |
|---|---|---|---|
| CK3 普通人物 3D 外貌 | Crusader Kings III | 3D 外貌 | Gotchas 15 |
| CK3 旧档兼容 | Crusader Kings III | 旧档 | Gotchas 24 |
| CK3 DLC 解析问题 | Crusader Kings III | DLC 解析 | Gotchas 20 |
| Victoria II 地图 | Victoria 2 | map provinces.bmp | Map files |
| Victoria II 历史覆盖 | Victoria 2 | replace_path | History loading |
| Victoria II 本地化编码 | Victoria 2 | localisation cp1252 | Build steps |

验收目标：六题都能在前两个推荐章节中找到目标、按返回行号读取正确正文；指定游戏不混入
其他游戏专属笔记。对比旧版的“搜索 → 目录 → 背景 → 章节”与新版的“搜索 → 背景 → 章节”，
两边保留同一篇笔记的前 60 行作为首次版本/证据背景，适用流程的工具调用中位数至少减少 25%。
同时统计返回字符、UTF-8 字节和工具目录增加量，不能省略背景来提高数字。

诊断夹具固定为 500 条 warning 后接一条 fatal；默认页长 50。新版用严重程度过滤一次取得
fatal 的原始内容与全部位置，返回量比旧版顺序翻页减少至少 80%；全局 counts/total/passed
不受过滤影响。保留不传过滤参数时的原有结果合同。

这是可复现的工具工作流比较，不是模型自主选择工具的评测。没有模型 usage 或真实对话实验时，
不宣称 Token 账单、模型成功率或端到端开发时间改善。DDS 本轮仅文档纠偏，无转换吞吐指标。

## 依据

- [Anthropic 工具设计](https://www.anthropic.com/engineering/writing-tools-for-agents)：
  针对任务过滤、返回有效上下文、测量冗余调用。
- [Agent Skills 规范](https://agentskills.io/specification)：按需读取，避免冗长的引用链。
- [Tiger README](https://github.com/amtep/tiger/blob/9e3d3b25c7524cdcc86d5f4190f3f8cffbc4d630/README.md)：
  复用已有 consolidate/suppress 能力，不重新实现语法解析或报告抑制。
- [DirectXTex texconv](https://github.com/microsoft/DirectXTex/wiki/texconv) 与
  [texdiag](https://github.com/microsoft/DirectXTex/wiki/texdiag)：匹配目标 DDS 属性、色彩空间和数据通道。

以上原文在 2026-10-14 调研时读取。没有安装游戏、Tiger 或 DirectXTex。

## 备份与回退

远端与本地备份分支 `backup/pre-agent-usability-20261014` 固定在基线提交。
仓库外完整历史备份：`/workspace/linn-modder-backups/pre-agent-usability-20261014.bundle`，
23,276,180 bytes，SHA-256 `062695b65292572b3a1387a73d266e748d4fcfab2941b1aa627db952c1474d71`；
`git bundle verify` 已通过，声明包含完整历史。

可以从备份分支建立独立工作树使用旧版，或对本轮 squash 提交执行 `git revert` 后正常合入。
不强推主线，不迁移项目数据。回退时停止传入新参数并重启 MCP 客户端刷新 schema。

## 收尾结果

### 最终实现

- `knowledge_search` 增加可选 `game` 参数；复用已有名称过滤。命中项新增
  `game_version/date/platform` 与最多三个 `sections`。章节只按自身正文评分，避免父章节
  因包含全部子节而排到前面；同分优先较短的读取范围。保留原有结果字段和笔记级排序。
- `ck3_check(min_severity="error")` 同时返回 error/fatal。过滤页的 `matched_total`
  与全局 `total/counts/passed` 分开；不传参数时保留旧合同。没有新增诊断抑制器或报告执行器。
- DDS 按需指南明确参考格式、头、mip、色彩空间与 alpha 用途，并给出带适用条件的
  DirectXTex 配方。没有执行转换或把文档例子当作游戏兼容性验证。

### 成对工作流测量

同一 Python 3.12.14、MCP 1.30.0；用两个独立源码目录运行。
按 MCP JSON TextContent 的字符与 UTF-8 字节计量，不重复计算 structuredContent。

| 指标 | 修改前 | 修改后 | 变化 |
|---|---:|---:|---:|
| 六个知识查询调用总数 | 24 | 18 | 减少 25% |
| 六个知识查询返回字符 | 44,461 | 29,604 | 减少 33.42% |
| 六个知识查询 UTF-8 字节 | 55,840 | 37,337 | 减少 33.14% |
| 指定 Tiger 夹具定位 fatal 的调用数 | 11 | 1 | 减少 90.91% |
| 同一诊断流程返回字符/字节 | 189,362 | 1,038 | 减少 99.45% |
| 默认工具目录字符 | 43,474 | 43,946 | **增加 1.09%** |

六题均读取了与旧版完全相同的章节和前 60 行背景，目标章节排名为 1、1、1、1、2、1。
24 个工具和固定 AGENTS.md/SKILL.md 不变；只有 knowledge_search/ck3_check 两个 schema 改变。
合成报告中的 fatal 内容与全部位置未变；不加过滤时的 CK3 默认响应也与基线一致
（比较时仅归一化各次临时工作区绝对路径）。

**适用边界：** 调用数是固定流程的实际工具调用，不是模型自主行为统计；原来已知道行号、
使用本地 rg，或已读过目录的 agent 未必省下一次请求。诊断收益来自该噪声夹具，不外推所有
Tiger 报告。游戏过滤与章节元数据增加搜索本身的工作和单条命中大小；没有测量 CPU 加速、
网络延迟、真实模型 Token、生成质量或开发时间，也没有省略原始报告的检查范围。

[原始数据](benchmarks/agent-usability-20261014.json)保留源码摘要、版本、六题结果及目标判定。
测量发生于提交前，after 的 dirty 状态如实为 true。复现：

```sh
git worktree add --detach ../linn-usability-before backup/pre-agent-usability-20261014
uv run python scripts/benchmark_agent_usability.py --before ../linn-usability-before --output scratch/usability.json
```

### 验收

一次本地全套验收 **152 passed、2 skipped**；跳过项需要原生 Windows。收尾测量发现同分的
宽章节排在短章节之前，修正后仅复核相关检索/章节测试 **6 passed** 并重跑成对测量，全部目标通过。
用例覆盖游戏过滤、原文件行号、嵌套/代码块/无标题笔记、空过滤结果仍保持失败，以及
JSON CLI 和真实 stdio MCP 的一致性。文档结构、知识库索引和发布内容检查通过；
原有知识库 Gotchas 提示未改动。安装包检查和 Windows/Linux CI 结果见本次 PR。
sdist/wheel 构建通过；独立环境仅安装 wheel 及其核心依赖后，资源导出、搜索范围读取、
CK3 过滤和既有备份/编辑往返检查通过。未安装 MCP 作为该 wheel 检查的前置依赖。
