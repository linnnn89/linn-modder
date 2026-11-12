# CK3 启动卡死案例：triggered_desc 的非法直接子项

**案例版本：CK3 1.20.0.4 / Crozier。** 示例使用中性名称，说明该版本的解析故障与修正方法。

> 在本版本中，`triggered_desc` 的直接子项只能是 `trigger` 和 `desc`。不要直接放入 `first_valid`。括号配对、本地化引用和安装包检查通过，仍可能在真实加载时反复报错并卡住。

该版本的故障案例中，修正这种嵌套结构后，原启用组合成功进入主菜单。版本变化后仍须重新核验，不把本例当成所有 CK3/Jomini 版本的完整语法规范。

## 症状和定位证据

- 游戏可以显示加载画面，却始终进不了主菜单；不能仅凭进程存在或“未响应”状态判断是正常加载、死循环还是崩溃。
- `error.log` 中同一条解析错误反复出现，并指向生成的事件文件与具体事件。

```text
The body of triggered_desc can only take desc and/or trigger.
```

生成器可能把相同错误复制到多个事件。错误在加载定义时就触发，因此即使没有打开相关菜单，也会影响启动。不能先归咎于人物数量、图片体积、显卡或其他 MOD；应检查重复模式、定位文件和修复前后的实际启动结果。

## 错误写法

以下是故障结构的缩写；外层 `desc` 本身不是问题。

```text
desc = {
    triggered_desc = {
        trigger = { has_global_variable = example_actor_pending }
        first_valid = { # 错误：triggered_desc 不接受这个直接子项
            triggered_desc = {
                trigger = { has_global_variable = example_actor_queued_date }
                desc = example_status.dates
            }
            desc = example_status.legacy_dates
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
            NOT = { example_slot_alive_trigger = { KEY = actor_a } }
            has_global_variable = example_actor_pending
            has_global_variable = example_actor_queued_date
        }
        desc = example_status.dates
    }
    triggered_desc = {
        trigger = {
            NOT = { example_slot_alive_trigger = { KEY = actor_a } }
            has_global_variable = example_actor_pending
            NOT = { has_global_variable = example_actor_queued_date }
        }
        desc = example_status.legacy_dates
    }
}
```

示例中的 `example_*`、`example_status.*` 和 `actor_a` 为占位标识；辅助触发器、变量与本地化键需要由具体工程定义。这里仅展示描述分支的结构，修正时保留实际玩法条件及已有状态。

## 修复和防回归要求

1. **先保留失败证据。** 备份日志、安装文件和相关生成器，记录游戏精确版本、启用组合和文件哈希；检查进程状态后再替换文件。清空日志不是修复。
2. **核对同版接口。** 本次依据是实际引擎报错与本机 1.20.0.4 原生事件 `game/events/lifestyles/intrigue_lifestyle/intrigue_temptation_events_2.txt`。精确错误联网检索没有找到有用结果，未用无关搜索结果或版本不明的旧教程替代。
3. **修正生成源和生成结果。** 修改对应生成器并重新生成受影响事件；不能只修安装目录，下次构建又覆盖回错误写法。
4. **新增针对真实错误的检查。** 按层级扫描生成事件中每个 `triggered_desc` 的直接子项，只接受 `trigger`、`desc`，不误判内部 `trigger` 的条件键。先确认旧产物因 `first_valid` 失败，再确认新产物通过。单纯统计括号或全文禁止 `first_valid` 都不合适。
5. **用原故障流程验收。** 保持原启用组合，实际启动，确认重复错误消失且主菜单可见。日志停止增长、进程存活、包哈希一致或测试全绿，均不能单独替代这一项。
6. **区分启动与玩法。** 到达主菜单只能证明本次启动阻塞解除；动态日期显示、事件条件、旧档迁移和死亡轮回仍需各自的实际流程验证。运行中未执行的项目不得顺手标为通过。

## 证据与适用边界

回归检查能保护节点结构，实际启动才验证解析故障是否解除。版本、启用组合、错误日志和运行结果应保留在使用者自己的工程中；公共手册不包含私人项目路径或游戏素材。完整验收仍按本轮行为选择，见[验证与交付](verification.md)。
