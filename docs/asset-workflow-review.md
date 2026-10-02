# 素材流程审核与下一步优化

基线：`13fb283fdf5315144cdfaf514a58040da1a0fb6e`。本轮围绕官方参考、GPT Image、
素体 PSD 和批量图片处理，使用合成图片验证代码，没有下载角色图片、调用生成模型或安装游戏。

## 已落地的调整

通用素材指南原先仍有“需要素材就用 fal”的默认路径。本轮改为：先取得并检查官方
参考，已有素材足够时直接复用；需要新图或编辑时，Codex 使用可用的 GPT Image。
fal 保留为可选提供方，发布文案记录实际使用的工具和来源。

新项目包含：

- `references/manifest.json`：初始为空，用于记录官方页面、原图 URL、版本、hash 和核验结果。
- `ASSET_WORKFLOW.md`：从唯一的[素材流程文档](../skills/asset-pipeline/references/sourcing-and-psd.md)复制，避免项目模板与技能要求不一致。
- `assets/layers/`、`assets/editable/`：透明部件与可编辑母版，和源图、游戏输出分开保存。

创建项目只创建结构，不会自动检索、生成图片或改写旧项目。GPT Image 提供光栅图像，
真正的 PSD 由可用的编辑器/写入器组装，并重新打开检查图层可编辑性。仓库本身目前
没有原生 GPT Image API 客户端、参考图下载器或 PSD 组装器；这些能力由 harness 提供，
缺失时如实报告交付状态。完整来源与验证要求见[二次元工作流](anime-mods.md)。

固定入口 `AGENTS.md`、`CLAUDE.md` 不变，MCP 工具名称/参数/schema 不变。
11 个技能的 name/description 合并为紧凑 JSON 后，cl100k 和 o200k 均由 439 增至
445 tokens（+6），用于增加官方参考、GPT Image 和 PSD 的发现入口；详细流程按需加载。
此计数描述元数据本身，实际 harness 包装和提示缓存另计。

## 实测发现：复用已有 Service 进程

用 16 张不同的合成 RGBA 图片，执行相同的 `image_prepare` 参数，比较逐张启动
JSON CLI 与单个 Python 进程连续使用 `Service.invoke`。两种方式使用完全相同的现有实现，
均保持工作区边界、严格参数校验与输出 hash；这里没有新批处理 API。

| 方式 | 16 张图的中位总耗时 | Python 进程数 |
|---|---:|---:|
| 每张图启动一次 CLI | 1,149.920 ms | 16 |
| 一个 Service 进程连续处理 | 150.780 ms | 1 |

耗时减少 **86.89%**，产物逐文件 SHA-256 完全一致。环境为 Linux / Python 3.12.14 /
Pillow 12.3.0；输入 256×512，输出 192×256，1 轮预热后交替运行 5 组。
见[原始数据](benchmarks/asset-workflow-2026-10-02.json)与[基准脚本](../scripts/benchmark_asset_workflow.py)。

这是同版本两种调用方式的差异，不是本轮代码带来的统一加速。常驻 MCP 已复用进程，
不能声称它也因此快了 87%；大型图片的缩放/编码占比更高，比例也会不同。未测量模型
Token、图片生成时间、Windows 耗时或 PSD 性能，不对这些指标作收益承诺。

复现：

```powershell
uv run python scripts/benchmark_asset_workflow.py --count 16 --runs 5 --output asset-workflow-local.json
```

有 Python 执行能力的 harness 可以复用现有 Service。下面的 `jobs.json` 是一组
`image_prepare` 参数对象，和项目的素材来源清单是不同文件：

```python
import json
from pathlib import Path
from um.service import Service

jobs = json.loads(Path("jobs.json").read_text(encoding="utf-8-sig"))
service = Service(r"C:\Mods")
try:
    for job in jobs:
        result = service.invoke("image_prepare", job)
        print(json.dumps(result.to_dict(), ensure_ascii=False))
        if not result.ok:
            raise RuntimeError(result.error.message)
finally:
    service.close()
```

这是顺序处理，失败时之前成功的输出仍保留，不是整批事务。输出采用新文件名并记录
清单，重跑时只处理未完成项。MCP-only harness 继续使用常驻服务的逐项调用。

## 仍有价值的优化方向

| 优先级 | 优化方向 | 为什么值得做 | 实施前的验收条件 |
|---|---|---|---|
| 1 | 素材清单校验和复用判断 | 发现重复下载、过期参考、缺失文件和同角色不一致变体 | 离线检测路径/hash/角色映射；有效缓存重复运行不发下载请求 |
| 2 | 可选 PSD 组装器 | 把对外部编辑器的依赖变为可测试、可重现的交付 | 独立读取器验证真实图层、alpha、命名、合成预览和失败后旧母版可用 |
| 3 | 批量素材任务清单与恢复 | 大量头像能减少重复调用和中断后的重做 | 混合成功/失败可恢复，结果与单图一致；同时测量总耗时和峰值内存 |
| 4 | 具体游戏版本的封包适配器 | 将准备好的素材变成可导入产物 | 明确目标样本；先证明无修改回封，再验证单项修改和未改资源不变 |

先采用现有单进程能力，再根据真实工作量决定是否新增批量 MCP 工具，避免为了减少
一次调用而常驻更多工具 schema。官方参考优先与出处记录已经进入流程，但尚未实现
自动下载缓存；目前没有依据给它报告下载耗时或 Token 节省百分比。

## 备份与兼容性

[backup/pre-asset-workflow-20261002](https://github.com/linnnn89/linn-modder/tree/backup/pre-asset-workflow-20261002)
保留基线版本，工作区外另有 `pre-asset-workflow-20261002.bundle`，已独立克隆验证。
本轮不迁移旧项目、改变现有操作参数或删除已有功能。新模板为 manifest 增加两个路径字段；
保留 schema_version 1 与原有字段，旧文件不会被就地覆盖。

需要回退时，可对本轮 squash 合并提交执行 `git revert`，或按固定基线 SHA 安装。
已创建的新项目和其中的素材应独立保留；回退工具代码不等于删除用户产物。
