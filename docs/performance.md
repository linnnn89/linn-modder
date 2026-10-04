# 效率迭代、测量与回退

本轮以 `4e983f16aaa3c4e33b56d953472ec2d541d2c9fb` 为基线，先设目标，再实现与测量。
范围是工具启动和 agent 上下文交付；未安装或运行游戏，也未测量模型推理质量、费用或游戏帧率。

## 审核与第一性原理

一次操作的必要工作由请求决定。版本查询不需要构建所有子命令；读取游戏配置不需要
导入扫描和知识库后端；专用创作任务不必加载窗口控制 schema；只看文档开头不需要
返回全部正文。优化沿这些边界减少工作，保留真正需要的信息和约束。

| 发现 | 方案 | 预先设定的验收目标 |
|---|---|---|
| CLI 每次注册全部功能组 | 根入口保留短帮助，选中命令才加载完整 parser | 版本查询中位耗时减少 ≥50% |
| Service 提前导入未使用后端 | 对应操作执行时导入，使用 Python 原有模块缓存 | JSON 配置查询中位耗时减少 ≥20% |
| 专用 harness 仍获得全部工具 schema | 可重复的 `--enable-tool` 同时限制发现与调用 | 五工具创作配置 schema Token 减少 ≥50% |
| 长手册只能整篇返回 | 可选行范围和明确的续读位置 | 代表性长手册首次返回 Token 减少 ≥60% |

没有增加后台服务、通用命令执行器或自建缓存。原始 JSON 严格校验、只读游戏根目录、
备份校验与恢复撤销逻辑仍由共享服务负责。工具清单是启动配置，变更后需要重启；
它不替代操作系统权限隔离。分页控制返回文本，不承诺减少文件读取 I/O。

## 公开实践依据

查阅日期：2026-10-02。借鉴设计原则，没有复制实现代码。

- [Agent Skills specification](https://agentskills.io/specification)：发现元数据、任务正文、
  按需参考分层。上一轮已完成文档分层，本轮将按需原则延伸到运行时。
- [Click 8.2.1：Lazily Loading Subcommands](https://github.com/pallets/click/blob/8.2.1/docs/complex.rst)：
  延迟导入可降低大型 CLI 启动成本，同时应验证每个子命令的帮助入口。
  本项目沿用 argparse，测试全部 12 个功能组和真实操作。
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)：区分 CLI + Skills 与 MCP 的
  上下文成本，提供能力选择。本项目保留两种接口，允许专用任务选择工具。
- [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)：
  structured content 为兼容性应同时提供 JSON 文本。两份结果均保留，测量也将它们计入。

## 实测结果

[原始样本与环境](benchmarks/efficiency-2026-10-02.json)包含每次耗时、P95、依赖版本、
基线提交及工作树 Python 源码指纹。结果取自同一 Linux 主机、Python 3.12.14、
MCP 1.29.0、tiktoken 0.14.0。运行每项前预热 2 次，然后新建进程交替测量两个 checkout
各 25 次；计入进程启动成本，比较相同命令的 stdout。最终记录时没有同时运行测试。

| 测量项 | 迭代前 | 迭代后 | 减少 |
|---|---:|---:|---:|
| `um --version` 中位耗时 | 82.606 ms | 24.042 ms | 70.90% |
| JSON `game_profiles` 中位耗时 | 75.296 ms | 49.806 ms | 33.85% |
| 全部 14 工具 → 可选 5 工具 schema，cl100k | 4,366 tokens | 1,664 tokens | 61.89% |
| 同上，o200k | 4,606 tokens | 1,757 tokens | 61.85% |
| 215 行手册全文 → 首 40 行，cl100k | 7,770 tokens | 1,572 tokens | 79.77% |
| 同上，o200k | 7,712 tokens | 1,571 tokens | 79.63% |

五工具配置为 `game_profiles`、`manual_read`、`project_create`、`image_prepare`、
`backup_create`，适合项目创建和素材准备。它不包含恢复或扫描；这些任务应选入对应工具。
手册样本为已有的 `knowledge/games/gta-v/minecraft-passthrough.md`，选择它是因为它是
当前较长的真实笔记，而不是为了用填充文本扩大收益。

**边界和成本：**

- 耗时是此 Linux 环境的 CLI 新进程实测，不能外推为 Windows 速度、常驻 MCP 吞吐或游戏运行速度。
- Token 用 `cl100k_base`、`o200k_base` 对紧凑 MCP JSON 计数。harness 如何投影工具和结果、
  模型使用什么 tokenizer、是否缓存提示词，都会影响实际输入量；此数值不代表模型账单。
- 默认仍是 14 工具。新增分页参数使默认 schema 从 4,366 增至 4,405 cl100k tokens（约 +0.89%）；
  62% 的节省需要启用专用工具清单，不能宣称默认所有会话都自动省下这些 Token。
- 首次只读一页才得到约 80% 的节省。全文分六页读完为 8,546 cl100k / 8,502 o200k tokens，
  比一次全文多约 10%，还有额外往返。已知需要全文时直接整篇读取。
- 分页可能截断代码块；返回 `next_line` 供继续读取。测试确认逐页拼接与全文一致。

## 使用和复现

配置示例见[安装与接入](setup.md#专用任务的工具清单)，分页约定见[工具接口](../skills/linn-modder/references/tools.md#reading-a-long-manual)。

在完整 Git checkout 中，用同一个 Python 环境比较两棵代码树：

```powershell
git fetch origin backup/pre-efficiency-20261002
git worktree add --detach ../linn-modder-baseline 4e983f16aaa3c4e33b56d953472ec2d541d2c9fb
uv sync --extra mcp --extra dev
uv run --with tiktoken python scripts/benchmark_efficiency.py --before ../linn-modder-baseline --output efficiency-local.json --require-targets
```

默认 25 组样本，可用 `--runs` 调整。Token 计数需要 tiktoken；首次加载词表可能联网，
预先缓存词表后可离线测量。此环境从公开 tokenizer 镜像重建缓存，验证 SHA-256 与
tiktoken 官方 cl100k/o200k 词表哈希完全一致后使用。未用字符数估算 Token。
`--require-targets` 在任何收益目标不满足时退出非零。

脚本比较的是同一解释器下的 checkout，避免依赖环境变化混入结果。计时目标不放入
普通 CI 的硬门槛；不同 runner 的绝对耗时不可直接比较。CI 检查功能和协议回归，
本地成对基准负责评估收益。Windows 可运行同一脚本独立验证，不沿用 Linux 的耗时结论。

## 备份与回退

优化前版本：`4e983f16aaa3c4e33b56d953472ec2d541d2c9fb`。

- 远程保留 [backup/pre-efficiency-20261002](https://github.com/linnnn89/linn-modder/tree/backup/pre-efficiency-20261002)，本轮不会移动该备份分支。
- 工作区外保存 `pre-efficiency-20261002.bundle`，包含旧版本完整历史，大小 22,978,897 bytes。
  SHA-256：`884281f2be64d533c341dd25e76b371f0f7fc86372eba5608a6fa102bb8e3b7b`。
- 已从 bundle 独立克隆，验证 HEAD 为上述提交、tree 为 `0619b18487710f7dc9e43d346bcfda6678a22583`。
  初始浅克隆的 bundle 未通过实际恢复演练，补全历史后重新生成并成功恢复。
- 本轮不迁移用户项目或备份格式，旧程序可继续读取现有项目；没有真实游戏文件变更。

无需改变当前工作目录即可检查旧版本：

```powershell
git fetch origin backup/pre-efficiency-20261002
git worktree add --detach ../linn-modder-previous 4e983f16aaa3c4e33b56d953472ec2d541d2c9fb
```

已安装工具可重新安装固定提交：

```powershell
uv tool install --reinstall "linn-modder[mcp] @ git+https://github.com/linnnn89/linn-modder@4e983f16aaa3c4e33b56d953472ec2d541d2c9fb"
```

若已启用本轮新增配置，回退时同时移除 harness 启动参数中的 `--enable-tool NAME`，
将 `manual_read` 调用恢复为 `collection`、`path` 两个参数，并重启 MCP 客户端以刷新 schema。
原有默认配置无需变更。备份代码不会自动回退用户单独编辑的 harness 配置。

如需让主分支撤销整轮改动，对本轮 squash 合并提交执行 `git revert <合并提交SHA>`，
经检查后正常推送。这样保留改动历史和后续工作；不要用强制推送覆盖主分支。

## 后续优化方向

当前知识库规模小，尚无证据支持引入数据库或持久缓存。下一轮更值得测量真实的
批量头像处理：先用合成图片建立吞吐和内存基线，再决定是否增加批处理接口，避免
每张图片一次进程启动或模型往返。并发写入、任务队列和动态工具发现会增加状态管理
成本，应在实际工作量证明收益后再引入。

## 扫描与统一入口的后续测量

见 [2026-10-04 扫描与路由优化](scan-routing-performance.md)：相对 `ab8d478` 的单次安全遍历、严格扫描边界、入口 Token 成本与回退方法。
