# CK3 启动卡死案例：triggered_desc 的非法直接子项

**已验证版本：CK3 1.20.0.4 / Crozier。记录日期：2026-10-09。**

> 在本版本中，`triggered_desc` 的直接子项只能是 `trigger` 和 `desc`。不要直接放入 `first_valid`。括号配对、本地化引用和安装包检查通过，仍可能在真实加载时反复报错并卡住。

这是本机星誓萌战的实际故障，不是推测。该写法来自 0.1.2 的名册状态页，0.1.3 扩充时沿用；用户在 0.1.3 报告读条无法进入主菜单。0.1.3.1 修正后，原五包组合实际进入主菜单。版本变化后仍须重新核验，不把本例当成所有 CK3/Jomini 版本的完整语法规范。

## 症状和定位证据

- 游戏可以显示加载画面，却始终进不了主菜单；不能仅凭进程存在或“未响应”状态判断是正常加载、死循环还是崩溃。
- 当次 `error.log` 达到 17,111,314 字节，下面同一条错误重复 **99,175 次**，指向 `events/mz_ss_status_events.txt` 第 37 行、事件 `mz_ss.111`。

```text
The body of triggered_desc can only take desc and/or trigger.
```

生成器把相同错误复制到了 21 名角色的状态页。错误在加载事件定义时就触发，因此即使没有打开名册，也会影响启动。不能先归咎于人物数量、图片体积、显卡或其他 MOD；也不能把单条其他警告直接认定为卡死原因，应检查重复模式、定位文件和修复前后的实际启动结果。

## 错误写法

以下是故障结构的缩写；外层 `desc` 本身不是问题。

```text
desc = {
    triggered_desc = {
        trigger = { has_global_variable = mz_ss_misaki_pending }
        first_valid = { # 错误：triggered_desc 不接受这个直接子项
            triggered_desc = {
                trigger = { has_global_variable = mz_ss_misaki_queued_date }
                desc = mz_ss.status.dates
            }
            desc = mz_ss.status.legacy_dates
        }
    }
}
```

这段文本括号完整、本地化键存在，看起来也符合一般的条件分支思路，但不符合本版引擎对该节点的具体合同。`first_valid` 并非全局禁用：本版原生事件在外层动态描述中使用它。**错误是它直接位于 `triggered_desc` 内。**

## 已验证的替代结构

将原先的条件选择拆为外层 `desc` 下两个互斥的 `triggered_desc`。保留共同前提，并以“日期变量存在/不存在”区分，避免同时显示两段文字或遗漏旧档提示。

```text
desc = {
    triggered_desc = {
        trigger = {
            NOT = { mz_ss_slot_alive_trigger = { KEY = misaki } }
            has_global_variable = mz_ss_misaki_pending
            has_global_variable = mz_ss_misaki_queued_date
        }
        desc = mz_ss.status.dates
    }
    triggered_desc = {
        trigger = {
            NOT = { mz_ss_slot_alive_trigger = { KEY = misaki } }
            has_global_variable = mz_ss_misaki_pending
            NOT = { has_global_variable = mz_ss_misaki_queued_date }
        }
        desc = mz_ss.status.legacy_dates
    }
}
```

示例中的 `mz_ss_*` 为本项目定义的辅助触发器、变量与本地化键，不是 CK3 内建接口。其他 MOD 复用结构时使用自己的已定义键。此修复只改变描述结构，不清空轮回队列、不重置冷却，也不删除角色。

## 修复和防回归要求

1. **先保留失败证据。** 备份日志、安装文件和相关生成器，记录游戏精确版本、启用组合和文件哈希；检查进程状态后再替换文件。清空日志不是修复。
2. **核对同版接口。** 本次依据是实际引擎报错与本机 1.20.0.4 原生事件 `game/events/lifestyles/intrigue_lifestyle/intrigue_temptation_events_2.txt`。精确错误联网检索没有找到有用结果，未用无关搜索结果或版本不明的旧教程替代。
3. **修正生成源和生成结果。** 本次修改 `build_status.py` 并重新生成状态事件；不能只修安装目录，下次构建又覆盖回错误写法。
4. **新增针对真实错误的检查。** 按层级扫描生成事件中每个 `triggered_desc` 的直接子项，只接受 `trigger`、`desc`，不误判内部 `trigger` 的条件键。先确认旧产物因 `first_valid` 失败，再确认新产物通过。单纯统计括号或全文禁止 `first_valid` 都不合适。
5. **用原故障流程验收。** 保持原启用组合，实际启动，确认重复错误消失且主菜单可见。日志停止增长、进程存活、包哈希一致或测试全绿，均不能单独替代这一项。
6. **区分启动与玩法。** 到达主菜单只能证明本次启动阻塞解除；动态日期显示、事件条件、旧档迁移和死亡轮回仍需各自的实际流程验证。运行中未执行的项目不得顺手标为通过。

## 本次结果与可追溯材料

- 旧写法被新增回归检查准确拦住；修复后该检查及既有检查共 **9 项通过**。
- 只修状态页结构后，原五包组合的启动日志记录 **14.034346 秒**完成启动；窗口截图确认主菜单已显示，相关动态描述解析错误 **0 次**。
- 当时主菜单前景为用户协议窗口；没有代用户接受协议，也没有载入或推进存档。此结果不证明新局、21 名角色或轮回已经全部验收。
- 最终交付为 **0.1.3.1**。旧 0.1.3 包保留为失败基线，不再作为推荐安装版本。

本机项目材料位于工作区 `scratch/ck3-moe-design-20261009/`：

| 材料 | 项目内相对路径 |
|---|---|
| 故障次数、日志哈希和备份位置 | `verification/loading_failure.json` |
| 修复后的启动日志、截图和结果 | `verification/loading_fix_0131/` |
| 针对直接子项的回归检查 | `tools/test_dynamic_description_regression.py` |
| 安装文件、版本与配置核对 | `verification/loading_fix_deployment.json` |
| 完整过程与验证边界 | `MODLOG.md` |

这些是被 Git 忽略的本机证据，并非手册读者必须具备的仓库文件。手册保留可复用的错误结构、修正方法和验证要求，不随仓库提交游戏日志、图片或提取素材。
