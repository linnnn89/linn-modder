# CK3 技能整理与代码质量审核 — 2026-10-12

基线：`016f3b790d33334a4453cb2696d63e480971b20b`。最新 PR #11 已合并；
新增 CK3 经验是直接提交到 main 的文档更新，9 个文件，没有新增运行代码。
已同步该提交并确认其 Windows/Linux CI 成功。

## 审核结果与处理

这里按是否必要、可解释和有依据判断质量，不根据行文风格猜测作者是不是 AI。

| 发现 | 影响 | 处理 |
|---|---|---|
| 统一入口中 CK3 与策略任务重复指向同一指南 | 每次载入增加重复路由 | 合并为一行，保留 CK3 与中英任务词；发现元数据不变 |
| 指南要求查大型 CK3 经验档，但缺少简短设计步骤 | MCP 默认全文读取可能加载不相关案例 | 新增 [CK3 工作流](../skills/linn-modder/anime-strategy-mod/references/ck3-design.md)，经验档按问题分页 |
| 通用人物原则包含具体强化、阵营与配角性格偏好 | 其他项目容易误用；本项目偏好又不能丢 | 移至 [星誓萌战约定](../skills/linn-modder/anime-strategy-mod/references/ck3-moe-project.md)，继续该项目时读取 |
| 人物最小验收一律包含完整死亡重建 | 仅改属性也可能重复测试无关流程 | 按变更行为选择验收，保留生命周期改动所需检查 |

还人工抽查了 `um/service.py`、`resources.py`、`projects.py`、`contracts.py`、
`workspace.py`、`backup.py`、`common.py` 和知识库读取路径：共享服务、路径约束、
结构化错误、清理半成品、备份校验各有具体职责。本轮未找到足以删除这些保护或
引入新框架的证据；未修改运行模块。这不是对全仓每一行或实际 CK3 MOD 脚本的无缺陷保证。
本仓库不包含经验档所述本机 MOD 生成器和游戏产物，无法据此审计它们的实现。

## 吸收的制作经验

新工作流把玩家操作、目标 scope、结果状态、费用/AI 范围、持久性和验收放在一张功能卡中；
再选择历史、数据库、互动、事件、回调或 GUI。详细故障证据留在原知识库，原记录的版本、
用户实测与未验证边界保留。

读取了 Tiger 和 Paradox Modding Toolkit 作者的 README/配置，采用依赖上下文、
新增报告对比、本地化格式一致性、源文件局部修改和画像接口检查的方法。
固定来源提交及适用边界见 [验证资料](../skills/linn-modder/anime-strategy-mod/references/verification.md#ck3-author-sources)。
未复制第三方代码，也未增加运行依赖、MCP 工具、发现入口或自动迁移器。

## 阅读量对比

单位是 **Unicode 字符数**（包含 Markdown），不是 Token、模型账单或耗时。
`tiktoken` 分词表下载被当前网络代理拒绝；本轮没有可用的实际 Token 测量结果。
AGENTS.md、技能发现元数据和工具定义未变。各路线按文件顺序用一个换行连接后计数：

| 路线 | 之前 | 之后 | 减少 |
|---|---:|---:|---:|
| 统一 SKILL 入口 | 2,222 | 2,147 | 3.38% |
| 入口＋策略指南＋通用人物原则 | 8,214 | 7,589 | 7.61% |
| CK3 首轮设计：之前读取完整经验档，之后读取设计工作流 | 19,591 | 8,129 | 58.51% |
| 星誓萌战人物路线：之后额外读取项目约定 | 8,214 | 8,691 | -5.81% |

第三行只衡量**全文读取回退路径**的首轮成本；旧指南也允许按章节阅读，因此不能把
58.51% 宣称为所有 CK3 任务的节省率。深入故障排查仍需追加对应证据。
第四行有意保留增长：专用约定补入了经验档中的婚姻、孕期、旧档和素材边界，且多一个文件链接。
收益是首轮设计更聚焦、通用任务减少无关内容；本轮没有运行时增速结论。

在仓库根目录用 Python 可复现（不需第三方依赖）：

```python
import subprocess
from pathlib import Path

base = "016f3b790d33334a4453cb2696d63e480971b20b"
entry = "skills/linn-modder/SKILL.md"
guide = "skills/linn-modder/anime-strategy-mod/GUIDE.md"
refs = "skills/linn-modder/anime-strategy-mod/references/"
character = refs + "character-design-principles.md"
note = "knowledge/games/crusader-kings-iii/modding-playbook.md"
routes = {
    "entry": ([entry], [entry]),
    "character": ([entry, guide, character], [entry, guide, character]),
    "design/full-note": ([entry, guide, note], [entry, guide, refs + "ck3-design.md"]),
    "moe": ([entry, guide, character], [entry, guide, character, refs + "ck3-moe-project.md"]),
}
for name, (before, after) in routes.items():
    old = "\n".join(subprocess.check_output(["git", "show", f"{base}:{p}"]).decode("utf-8") for p in before)
    new = "\n".join(Path(p).read_text(encoding="utf-8") for p in after)
    print(name, len(old), len(new), round(100 * (1 - len(new) / len(old)), 2))
```

## 验收与回退

本地收尾：相关测试 24 项通过，文档结构、13 篇知识库索引、构建及独立安装 wheel 检查通过；
发布扫描 0 failures / 0 warnings。知识库另有一条既有的 Gotchas 编号格式警告，
该笔记实际使用编号子标题，未为消除提示改写其证据记录。
wheel 检查覆盖新参考的读取/导出及 CK3 经验档分页。没有新增“断言某句文案”的测试。
没有安装游戏、启动 CK3、下载角色素材或运行第三方验证器。

远端 [backup/pre-ck3-skill-20261012](https://github.com/linnnn89/linn-modder/tree/backup/pre-ck3-skill-20261012)
保留基线。回退时 revert 本次 squash 合并即可；没有项目数据迁移。
