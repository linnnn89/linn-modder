# CK3 与二次元策略游戏 MOD

新做 CK3 功能或尚未确定实现路线时，先读[设计与实现](references/ck3-design.md)。已有工程的局部维护直接选下表，不必重建脚手架，也不必为脚本修改进入素材流程。Victoria II、光荣系列等游戏先查[目标游戏](references/targets.md)，不套用 CK3 接口。

## 开始与收尾

先确认用户要设计、诊断、修改还是安装，再从现有工程核对游戏版本、依赖、实际加载路径和目标开局或存档。新项目可用 `game_profiles` 选择路线、`project_create` 建立工作区；已有项目沿用清单、生成器和稳定 ID。

把一次玩家操作或一名人物做完整，再扩展同类内容。人物设计查原作，脚本接口查目标版本的原生说明和调用；本地依据不足时按[研究路线](../mod-research/GUIDE.md)查证。素材任务另行记录来源、处理输入与游戏成品，不能用一张 PNG 代替画像接入。

修改在工作区完成，游戏根保持只读。安装、游戏操作和发布按现有授权分别处理。收尾交付本轮变更及相关检查，在 `MODLOG.md` 区分离线验证、安装结果与游戏表现；没有运行游戏就保留 `not-tested-in-game`。

## 按任务读取

| 当前问题 | 参考 |
|---|---|
| CK3 新机制、脚本、规则或兼容设计 | [设计与实现](references/ck3-design.md) |
| 分封、飞地、首府、法理、书签或历史日期 | [历史、领国与开局](references/ck3-history-and-realms.md) |
| 2D 立绘、头像不显示、衣柜与生成器维护 | [画像绑定与衣柜](references/ck3-portraits-and-wardrobe.md) |
| 卡顿、重复维护、原生替代或活动生命周期 | [运行维护与活动优化](references/ck3-runtime-performance.md) |
| 人物属性、能力、阵营或轮回 | [人物设计原则](references/character-design-principles.md) |
| 人物素材、旗帜、来源或首个样本 | [人物与素材](references/cast-and-assets.md) |
| 官方参考、素材制作或分层 PSD | [素材与 PSD](../asset-pipeline/references/sourcing-and-psd.md)；同时遵循当前工程的素材规则 |
| 表情、Live2D、3D 或成品 MOD 研究 | [二次元素材接入](../asset-pipeline/references/anime-assets.md) |
| 编码、生成结果、安装或游戏验收 | [验证与交付](references/verification.md) |
| descriptor、本地化格式或已有 Tiger 诊断 | [CK3 文件检查](references/ck3-check.md) |
| 启动卡死，反复出现 triggered_desc 解析错误 | [动态描述故障案例](references/ck3-dynamic-description-loading-failure.md) |
| 决议 widget 加载时访问冲突 | [控制器故障案例](references/ck3-decision-widget-startup-crash.md) |
| 容器解包、修改与回封 | [往返验证](../reverse-engineering/references/archive-roundtrip.md) |
| 工具参数或仅能通过 MCP 读取手册 | [工具接口](../references/tools.md) |
