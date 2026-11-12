# CK3 参考资料的组织与复核

公共参考围绕实现问题组织，具体工程的角色安排、素材偏好、目录和验收材料留在工程内。示例使用中性名称；游戏版本和原生接口名保留，以便判断技术结论的适用范围。

## 资料如何分工

| 资料 | 主要内容 |
|---|---|
| [设计与实现](../skills/linn-modder/anime-strategy-mod/references/ck3-design.md) | 玩家操作、目标 scope、状态变化、数据层与兼容范围 |
| [人物原则](../skills/linn-modder/anime-strategy-mod/references/character-design-principles.md) | 身份、能力、关系、阵营与生命周期的设计方法 |
| [历史与领国](../skills/linn-modder/anime-strategy-mod/references/ck3-history-and-realms.md) | 日期回放、分封、法理、首府和地图邻接 |
| [画像与衣柜](../skills/linn-modder/anime-strategy-mod/references/ck3-portraits-and-wardrobe.md) | 绑定、选择器、默认图条件、裁框和共享生成器 |
| [验证与交付](../skills/linn-modder/anime-strategy-mod/references/verification.md) | 静态检查、安装落位、游戏验收与回退 |

新机制先读设计入口，已知故障直接选对应参考。知识库按问题提供更详细的解释，不要求每次全文载入。

## 复核重点

先检查路径、参数和接口是否真实存在，再看示例是否能说明问题。公开示例应保持语义完整，并明确哪些键需要由使用者定义；匿名化不能将自定义触发器写成引擎内建能力。

人物属性、脚本、画像与轮回采用不同验收流程，只有涉及持久状态时才展开相应存读档检查。局部修改检查受影响文件及直接调用链，不为统一流程重复全项目验证。

变更入口或文件路径后，检查相对链接、目录定位、分页读取和打包资源。文字变化不需要增加逐句断言测试；相关开发检查见[开发说明](development.md)。

工具作者资料及固定修订见[验证资料](../skills/linn-modder/anime-strategy-mod/references/verification.md#ck3-author-sources)。静态工具、脚本模拟与实际游戏结果分别记录，不将其中一种视为其他阶段已经通过。
