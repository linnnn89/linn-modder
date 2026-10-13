# Paradox 制作路线与手册读取优化

2026-10-13；相对 `ddad4af106d027e77973097ca4bba7c4d5856852`。目标是减少选路和查资料的试错，不引入统一游戏解析器、自动安装器或新的验证框架。

## 从作者资料到实现

- Tiger 的游戏支持程度、依赖配置与错误基线；CWTools 的扩展、规则和原版缓存分开管理。
- Victoria 3 Co-op 的内容根与源目录分离，CMF 的真实依赖声明。
- Stellaris ACE 对关键覆盖块的处理，提炼为按对象核对冲突，保留旧版案例范围。
- CK3 继续按当前版本的原生样例与 scope 开发；Victoria II 单独处理旧启动器、CSV 本地化和真实游戏 exe。

作者资料、固定 commit 链接及适用范围集中在 [Paradox 指南](../skills/linn-modder/mod-any-game/references/engines/paradox.md)。CK3 的入口是 [设计与实现](../skills/linn-modder/anime-strategy-mod/references/ck3-design.md)。本次只读取资料、提炼方法，没有执行第三方脚本或引入其代码。无法取得正文的 Wiki 没有用作语法依据。

## 最小实现

1. 扫描沿用已有有界索引，识别根目录或 `game/` 下同级的 `common/` 与 `events/`。现代布局同时要求 launcher 配置；旧 Victoria II 要求根目录 `v2game.exe`。只有通用目录名或 exe 名不足以识别。路线指向专门的 Paradox 指南。
2. `manual_read(outline=True)` 返回 ATX 标题、级别和包含子节的行号范围。排除 YAML 与 fenced code 中的伪标题，用已有 `start_line/max_lines` 读取正文；默认读取合同不变。
3. 单一 `SKILL.md` 与固定 `AGENTS.md` 原样保留。细节放进当前步骤按需读取的参考资料；23 个默认工具不变，无新运行依赖。

这是轻量标题索引，不是完整 Markdown AST。没有 ATX 标题时返回空目录，继续使用普通分页；标题重名按行号区分。已知章节位置或短文直接读取更合适。文件或包版本变化后重新取得行号。

## 实测收益与代价

目标：四个固定知识库查询中，**目录 + 目标章节 + 首次版本背景**的返回量合计至少减少 40%；固定上下文不增长、工具数量不增长，四种合成目录均正确选路。

使用同一 Python 解释器，读取前后内容完全相同的知识文档。按 MCP `TextContent` 的实际 JSON 序列化口径计算字符数和 UTF-8 字节，不重复计入 `structuredContent`。首次背景保守计入开头 60 行；没有删掉版本、证据范围来获得更好数字。

| 查询 | 原整篇响应字符 | 目录 + 章节 + 前 60 行 | 字符减少 | UTF-8 字节减少 |
|---|---:|---:|---:|---:|
| CK3 普通人物 3D 外貌 | 15,128 | 6,602 | 56.36% | 71.48% |
| CK3 旧档兼容 | 15,128 | 6,596 | 56.40% | 71.25% |
| Victoria II 地图格式 | 15,077 | 6,410 | 57.48% | 57.48% |
| Victoria II Gotchas 整节 | 15,077 | 8,955 | 40.60% | 40.64% |
| 合计 | 60,410 | 28,563 | **52.72%** | **64.62%** |

- 默认 MCP 工具目录从 41,399 增到 41,476 字符，增加 **77 字符（约 0.19%）**，来自新增参数及描述；工具仍为 23 个。固定技能入口和项目规则逐字节不变。
- 合成扫描从 **1/4** 正确选路变为 **4/4**：保留根目录布局，补齐两种 `game/` + launcher 布局及旧 Victoria II。另有负例和 managed launcher 优先级测试。这个数字是指定夹具覆盖，不是对所有游戏的识别率。
- 新流程首次读取是三次调用（背景、目录、章节），整篇是一次。不能由字符减少推导网络延迟下降或开发速度翻倍；大段通读也不适合这个路径。读过背景或目录后可以复用；已有文件工具和 `rg` 的 agent 本就可以定位章节。
- 这是**知识读取量**对比，不是端到端上下文或 Token 账单。新增指南按问题读取，但其大小没有计入上述知识查询；未测模型 Token、生成质量、实际游戏性能或完整开发用时。

原始数据含源码/手册哈希、SDK 版本和目标结果：[JSON](benchmarks/paradox-workflow-20261013.json)。修改前代码在单独的只读基线工作树运行；修改后测量发生于提交前，`dirty: true` 如实保留。

复现（在开发环境已安装 MCP 依赖）：

```sh
git worktree add --detach ../linn-paradox-before backup/pre-paradox-workflow-20261013
python scripts/benchmark_paradox_workflow.py --before ../linn-paradox-before --output scratch/paradox-workflow.json
```

脚本比较默认全文合同与选中行的精确内容，并检查上述目标。不把绝对耗时加入 CI 门槛。

## 验收与回退

本地集中验收：137 passed、2 skipped；跳过项需要原生 Windows。覆盖 Service、JSON CLI、真实 stdio MCP、合成扫描目录、标题中的代码/元数据排除以及按范围读取。文档链接、知识库索引、发布内容、sdist/wheel 构建及独立安装 wheel 检查均通过；Windows/Python 矩阵由 CI 验证。本次未安装或运行游戏。

远端备份分支 **`backup/pre-paradox-workflow-20261013`** 固定在 `ddad4af`。需要旧版本时从该备份创建独立工作树；需要撤销主线改动时对本次 squash 提交执行 `git revert <提交号>`，通过普通 PR 合入，不强推或重置远端历史。未修改游戏文件、用户存档或外部工具配置。
