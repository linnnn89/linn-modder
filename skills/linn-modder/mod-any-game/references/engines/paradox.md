# Paradox：按游戏和版本选择制作路线

用于 CK3、Victoria II/3、Stellaris、HOI4、EU4 与 Imperator 的数据/脚本 MOD。扫描只识别引擎线索；相似目录不代表共享接口或保存格式。已有工程先用其清单和生成源，按当前问题读取下节。

## 先排除选路错误

| 游戏 | 先确认的入口与差异 | 可选的辅助检查 |
|---|---|---|
| **CK3** | 原生 `.mod` 注册文件与 `descriptor.mod`；`localization/` 的语言文件。人物/文化/头衔 scope 不可混用；原生 3D 与框架 2D 肖像分开。 | Tiger：引用、scope、历史关系；具体设计见 [CK3 工作流](../../../anime-strategy-mod/references/ck3-design.md)。 |
| **Victoria 3** | Co-op 模板的内容入口是 `mod/.metadata/metadata.json`，不要安装整个仓库或照搬 CK3 descriptor。确认本版 state/country 等对象与文件。 | `vic3-tiger` 接收 MOD 目录；依赖配置字段与 CK3 不完全相同，读对应样例。 |
| **Victoria II** | 旧 `.mod` 与 `localisation/` 分号 CSV；按目标语言/汉化包确认编码，保留列数。真实游戏是 `v2game.exe`，`.NET` 启动器不是脚本 API。 | 原生日志、已有合成检查及本版样例；CWTools 有旧规则仓库，不能据此承诺完整支持。 |
| **Stellaris / HOI4 / EU4** | 各自 MOD 描述、`localisation/`、事件和数据库；目录/对象的覆盖规则逐项核对。不要复制 CK3 回调或数值字段。 | CWTools 对应游戏规则；选定 tag/commit 后核对游戏版本。Tiger 的 HOI4 支持仍标为未完成。 |
| **Imperator: Rome** | 对照该游戏的描述文件、对象 scope 与版本，不能直接套用 CK3 的人物作用域。 | `imperator-tiger`；CWTools 作者将其支持标为过时。 |

`game_profiles` 的现有 P 社脚手架只有 `ck3`、`victoria2`；本表不新增其他游戏适配器。使用 UTF-8 BOM、某个 YAML 文件名或某个 `.mod` 片段前，先核对本游戏样例。文件后缀相同也不意味着可由标准 YAML/JSON 格式化器随意重写。

## 一个问题的最短闭环

1. **确认载入对象。** 记录游戏 build、启用 DLC、MOD/依赖版本、播放集顺序、描述文件指向的内容目录和本轮存档。先查文件与启动器信息，可查到的内容不重复问用户；版本号不能替代产物哈希。
2. **读一条适用证据。** 在本版 `.info`、原生调用者、已导出的脚本文档或对应工具规则里找同功能实例。知识库先搜游戏和错误；长文用 `manual_read(..., outline=True)` 找章节，再按行号读取。首次使用还需确认开头的版本和证据范围。
3. **做一个小改动。** 保留自己的命名空间，优先新增文件；有必要覆盖原对象时列出对象键、来源文件和保留内容。共享效果、框架或生成器有实际复用需求时再接入。
4. **一次收尾验收。** 检查本次改动的编码、引用、作用域与生成结果；已有外部验证器则加载正确原版与依赖。实际游戏验证按授权和变更范围进行，静态成功不升级为游戏验证。
5. **保留可复用结果。** `MODLOG.md` 写实际原因、来源版本、修法和验收；未解决的问题保留下一步证据需求。工作源、待安装产物和发布包分开，避免发布参考图、脚本缓存或整个依赖 MOD。

## 按症状缩小范围

| 现象 | 先检查 | 避免的无效尝试 |
|---|---|---|
| MOD 不出现/修改无效 | 描述格式、实际内容根、启用播放集、是否重载了本次产物 | 来回复制同一个旧 ZIP；把仓库根当内容根 |
| 验证器报大量未知引用 | 游戏规则版本、原版缓存、父 MOD 和 DLC 上下文 | 逐个“修复”依赖本来提供的符号；屏蔽整类错误 |
| 事件可显示却无效果 | root/保存的目标、触发与执行条件、成本是否重复扣除、显示值与实际值 | 猜命令名；以菜单出现代替状态写入验证 |
| 文本键或乱码 | 对应游戏的目录名、编码、语言头/文件名、CSV 列、本地化占位符 | 全项目自动转 UTF-8；把 Victoria II 当 Victoria 3 |
| 更新后某机制失效 | 被覆盖对象的新旧差异、依赖版本、对象是否保存进旧档 | 只提高 supported version 字段；整包覆盖原版 |
| 游戏变慢/日志猛增 | 新增重复错误、回调频率、目标集合、每次遍历数量 | 每个角色回调内再扫全世界；先归咎于图片数量 |
| 新局正常，旧档异常 | 已保存的规则/对象/队列、稳定 ID、是否需要明确迁移 | 反复重启期待重跑历史；重置全部变量或清空人物 |

## 验证器与兼容补丁

**工具须带正确上下文。** Tiger 的 CK3 配置用 `load_mod` 中的 `modfile` 指向依赖描述文件；Victoria 3 示例用 `mod` 指向依赖目录。按该版本样例配置，不发明一套跨游戏统一命令。已有错误基线可用于只看新增报告；保存原基线，不能在改坏后重新生成以掩盖错误。

CWTools 的扩展版本、游戏规则版本和原版缓存是三件事。Stellaris 规则作者区分 `stable` tag、`latest` commit 与手动规则目录；更新游戏后刷新适用缓存并核对规则。编辑器的错误提示是线索，目标游戏的接口和实际日志仍需核验。无需为读这份指南自动安装工具。

**声明真实依赖。** Victoria 3 CMF 将依赖写进 metadata 的 `relationships`，发布时还需对应 Workshop 必需项目。仅当使用其接口时接入；不为一个小事件强加框架。保留父 MOD，兼容修改写入自有补丁和记录。

**按对象合并。** Stellaris ACE 的作者明确要求保留其关键 AI 块语义，并区分不同覆盖方式。可复用的方法是审查冲突对象和调用链，而不是统一添加文件名前缀或宣称“排到最后就兼容”。该案例来自旧版本，只作为方法依据。

**先缩小、再测量。** 定时逻辑优先通知或已登记对象/待办队列。记录调用次数、扫描对象数和新增错误量，再决定是否缓存或降低频率；不要自动添加会改变玩法的冷却与条件。二分排除 MOD 时保留必需依赖，并记录每次启用集合。

## 版本化来源

以下作者资料在 **2026-10-13** 读取；只提炼方法，未安装工具、运行 MOD 或复制其代码。

| 来源 | 使用范围 |
|---|---|
| [Tiger README](https://github.com/amtep/tiger/blob/9e3d3b25c7524cdcc86d5f4190f3f8cffbc4d630/README.md)、[CK3 配置](https://github.com/amtep/tiger/blob/9e3d3b25c7524cdcc86d5f4190f3f8cffbc4d630/ck3-tiger.conf)、[Victoria 3 配置](https://github.com/amtep/tiger/blob/9e3d3b25c7524cdcc86d5f4190f3f8cffbc4d630/vic3-tiger.conf) | 支持状态、依赖字段、增量报告；作者说明会有误报与版本滞后。 |
| [CWTools README](https://github.com/cwtools/cwtools-vscode/blob/364beae5e3c1edfd6fe2f7e5701e8df93c9e45c5/README.md)、[HOI4 规则](https://github.com/cwtools/cwtools-hoi4-config/blob/297dd69c42aabe10078a8b7ab7f2d07ee631d4ef/README.md)、[Stellaris 规则](https://github.com/cwtools/cwtools-stellaris-config/blob/99147efe8072b331005b50536762dcc0b8573224/README.md) | 分游戏检查、规则渠道和缓存；规则存在不证明最新 build 全覆盖。 |
| [Victoria 3 Mod Template](https://github.com/Victoria-3-Modding-Co-op/Mod-Template/blob/317ed30aa0cee6b655cc2c89fa1ec495aed6c70c/README.md)、[metadata 示例](https://github.com/Victoria-3-Modding-Co-op/Mod-Template/blob/317ed30aa0cee6b655cc2c89fa1ec495aed6c70c/mod/.metadata/metadata.json) | 内容根、源/发布目录分离；不复制其版本占位符、自动抑制警告或默认建立 junction。 |
| [Victoria 3 CMF](https://github.com/Victoria-3-Modding-Co-op/Community-Mod-Framework/blob/5eaa4c0212895ab2b0924358ccb99850a8ecb78d/README.md) | 框架接口和依赖声明；不是本工具的新依赖。 |
| [Stellaris ACE 作者说明](https://github.com/OldEnt/stellaris-aggressive-crisis-engine/blob/714bde4ad07e68e61f8c16ba7fc7adaee40de8e6/steam_description.txt) | 最小关键覆盖与合并语义；旧版案例不作为当前 Stellaris 兼容声明。 |

CK3 与 Victoria II 的项目证据在 knowledge 集合的 `games/crusader-kings-iii/modding-playbook.md`、`games/victoria-2/south-central-gang-total-conversion.md`。用 `knowledge_search` 选条目，确认原作者版本及未验证事项。Victoria II 报告中的 `.NET` 扫描结果来自旧工具；当前扫描还检查数据目录与真实游戏 exe。CK3 Wiki 本次未能取得正文，未将搜索摘要当作语法依据。
