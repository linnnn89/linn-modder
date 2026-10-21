# CK3 启动崩溃案例：决议 widget 未显式初始化 controller

**故障版本：CK3 1.20.1.1；记录日期：2026-10-17。** 萌战 MOD 0.6.10-rc1 已安装定向修复；用户随后确认“成功了。我已经成功进入游戏、并且开始游玩”。启动及进入游玩已获用户确认，竞技场、温泉筹备界面尚未单独验收。

## 原因与证据

游戏在加载阶段发生 `C0000005 / EXCEPTION_ACCESS_VIOLATION`。本次 minidump 的故障线程同时保留了：

- 脚本：`common/decisions/mz_ar_arena.txt`。
- 决议：`mz_ar_host_decision`；自定义 GUI：`mz_ar_planner`。
- 控制器指针：对象偏移 `+0x40` 为 `0`；故障时 `RCX = 0`。
- 故障指令：`mov rax,[rcx]`，读取空地址；相对 ck3.exe 的故障地址为 `0x261a879`，首个调用者返回地址为 `0x3112603`。

决议的 `widget` 只指定了 `gui`，没有显式声明 `controller`。同版引擎的解析路径在处理 `controller` 时创建控制器对象；本次缺失该字段的对象保持为空，后续加载直接访问它而崩溃。温泉决议 `mz_sp_host_decision` 存在同样遗漏，属于同根因预防性修正；本次捕获的致命线程指向竞技场。

本机同版 `game/common/decisions/_decisions.info` 将控制器默认值写为 `default`，并列出其数据上下文为 `EventWindowWidget`。**文档中的默认值不能替代这次运行证据：维护本项目时必须显式声明需要的控制器。** 不据此推断所有 CK3 版本都会因省略该字段崩溃，也不把任意 `C0000005` 都归为此问题。

决议会在启动阶段加载，尚未点击该决议并不能隔离这种错误。日志末尾的人物特质本地化警告不等于致命原因；应结合异常线程、脚本对象和故障指令判断。

## 错误写法与正确方式

本次导致空控制器的写法：

```text
widget = { gui = "mz_ar_planner" }
```

不需要专用行为的自定义筹备界面，显式使用默认控制器：

```text
widget = {
    controller = default
    gui = "mz_ar_planner"
}
```

对应 GUI 文件应位于 `gui/decision_view_widgets/mz_ar_planner.gui`，文件名与 `gui` 值一致。温泉同理使用 `controller = default` 和 `gui = "mz_sp_planner"`。

若界面需要选项列表、头衔或其他专用控制器，应按当前版本 `_decisions.info` 及原生示例显式选择匹配的控制器；不要一律替换成 `default`。新增步骤、`show_from_start` 和相应按钮字段也应分别遵守本版合同。

## 修复和防回归

1. 保留本次 crash 文件夹、精确版本、启用组合和受影响脚本。异常堆栈缺少函数名时，转储中的对象名和空指针可以缩小范围；不要仅凭最后一条日志批量改脚本或归咎于图片、硬件。
2. 同步修正生成源、工作区生成结果与实际安装副本。本次仅改竞技场、温泉两份决议及其生成器，不重建人物、头像、活动或整个 MOD。
3. 在生成结果的具体 `widget` 块上检查控制器声明与 GUI 路径。先确认旧结果失败，再确认修复结果通过；括号检查或整文件出现一个 `controller` 字符串均不足以保护调用点。
4. 备份受影响文件，使用路径白名单定向安装，保留原存档与配置；安装前后核对受保护文件。不要把存档打入 MOD 包。
5. 复验保持相同启用组合，确认进入主菜单并检查新一轮日志；随后验证竞技场和温泉筹备入口、按钮可用性及原生活动页面。到达主菜单不证明活动、AI、旅行或存读流程全部通过。用户接管测试后停止自动化。

## 本次完成状态与本机材料

- 一项新增回归检查先在两处旧写法上失败；修复后连同竞技场、温泉既有六项检查，合计 **7 项通过**。
- 两份决议已定向安装，候选、工作区与安装副本哈希一致；安装前后 **20 份存档、24 个受保护文件哈希一致**。
- 用户选择“只修复安装，由我启动验证”，随后确认成功进入游戏并开始游玩。启动与进入游玩的验收依据是用户反馈，代理未执行自动启动；竞技场、温泉筹备按钮和完整活动流程尚未单独确认。**静态检查、安装校验与用户实测分别记录，不扩大验收范围。**

本机项目为 `scratch/ck3-starseal-anime-batch-20261010/`，证据位于 `verification/startup-crash-20261017/`：`dump-findings.json`、`installation.json` 和 `crash-evidence/`。生成源为 `tools/build_arena.py`、`tools/build_hot_springs.py`；回归检查为 `tools/test_decision_controller_startup.py`，从 `tools` 目录运行 `python -m unittest test_decision_controller_startup test_arena test_hot_springs -v`。完整过程见项目 `MODLOG.md`。这些本机材料不随公共手册提交游戏转储、日志、素材或存档。
