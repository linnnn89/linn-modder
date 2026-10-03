---
name: ui-mod
description: 制作或修改离线游戏的 UI MOD、HUD、菜单皮肤、图标、字体和界面本地化。Use for game UI changes, not general website design or character-only artwork. UI改造、フォント、メニュー。
---

# 游戏 UI MOD

1. 确认游戏/build、UI 技术和要修改的页面。区分贴图皮肤、布局、文本/字体与交互逻辑；找原有控件或资源的稳定 ID。
2. 首次选择修改路线、遇到未知属性或版本差异时，按[联网查证](../mod-research/SKILL.md)打开官方或维护者原文。不能把通用网页设计经验直接套到游戏打包 UI。
3. 先完成一个有真实状态的控件/页面，在独立 workspace 输出，保留原始纹理和配置。
4. 结合目标验证缩放、文字溢出、正常/悬停/按下/禁用/焦点状态及输入区域。游戏交互在已授权范围执行；仅做工具代码或资源准备时，明确运行时未验证。
5. 交付修改文件、资源/控件映射、验证范围与恢复方法。静态效果图不能证明实际 UI 可用。

## 选择抽屉

| 当前任务 | 读取 |
|---|---|
| HUD、菜单、九宫格、图集、手柄与鼠标 | [布局与状态](references/layout-and-state.md) |
| 汉化、日文、字体、长文本与插值参数 | [字体与本地化](references/fonts-and-localization.md) |
| 需要原画/图片转换 | [素材流程](../asset-pipeline/SKILL.md) |
| 编辑配置、脚本或打包文件 | [文件修改](../file-mod/SKILL.md) |
| 英中日官方教程入口 | [UI 资料](../mod-research/references/art-and-ui-sources.md) |

本技能提供操作经验，不新增 UI 注入器或通用编辑接口。Codex 和其他 harness 都按自身工具能力执行。
