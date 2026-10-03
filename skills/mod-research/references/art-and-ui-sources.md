# 二次元美术与 UI：免费文字资料入口

下列正文于 2026-10-03 通过网页读取工具核对。免费指文档阅读；不表示编辑器、模型、字体、声音或角色授权可以免费使用。只加载当前素材/引擎对应的资料。

| 资料与语言 | 值得学习的内容 | 使用注意 |
|---|---|---|
| [Unity 9 切片精灵](https://docs.unity3d.com/cn/2022.3/Manual/9SliceSprites.html) · 中文 | 固定边角、拉伸区域、边框设置 | 2022.3 HTML；SpriteRenderer 示例不等于 UGUI Image API，使用前识别组件 |
| [Unity Canvas Scaler](https://docs.unity3d.com/Packages/com.unity.ugui@1.0/manual/script-CanvasScaler.html) · EN | 参考分辨率、缩放模式与宽高匹配 | UGUI 1.0 官方正文；不能直接套到 UI Toolkit 或私有 UI |
| [Godot Using Containers](https://docs.godotengine.org/en/stable/tutorials/ui/gui_containers.html) · EN | 容器布局、最小尺寸与尺寸策略 | 官方 HTML；容器控制子节点时不要只靠手改坐标 |
| [Godot 游戏国际化](https://docs.godotengine.org/zh-cn/4.x/tutorials/i18n/internationalizing_games.html) · 中文 | 翻译、语言切换与本地化流程 | 官方中文 HTML；4.x 与 3.x 有区别 |
| [Unity スプライトアトラス](https://docs.unity3d.com/ja/2021.3/Manual/class-SpriteAtlas.html) · 日本語 | 图集打包、旋转、padding、过滤和纹理设置 | 固定 2021.3 官方日文页；检查目标引擎和图集 UV 约定 |
| [Live2D テクスチャアトラス編集](https://docs.live2d.com/cubism-editor-manual/texture-atlas-edit/) · 日本語 | 部件图集布局、未放入部件和纹理空间 | 官方日文 HTML；Cubism 版本和 SDK 兼容性需另查；贴图不是完整可动模型 |
| [VRM の特徴・内容](https://vrm.dev/vrm/vrm_features/) · 日本語 | 人形模型、表情、材质与模型使用条件的概念 | 官方日文 HTML；VRM 0.x/1.0 和游戏私有骨架不能混用 |
| [Krita PSD 支持](https://docs.krita.org/en/general_concepts/file_formats/file_psd.html) · EN | PSD 跨编辑器能力与局限 | 免费官方 HTML；保存后重开查图层，不假设所有 Photoshop 特性无损 |
| [Ren'Py Screens](https://www.renpy.org/doc/html/screens.html) · EN | 屏幕、交互控件、显示与动作 | 官方 HTML；先确认实际 Ren'Py 版本与源码是否可编辑 |
| [Ren'Py Translation](https://www.renpy.org/doc/html/translation.html) · EN | 对话、界面字符串与翻译机制 | 官方 HTML；字符串 ID 与替换参数要保留 |

## 跨资料得到的实施规则

- UI 皮肤不只是换 PNG：还要保留图集矩形、边框、pivot 和交互状态，并在目标缩放下观察。
- 二次元角色要区分平面立绘、分层表情、Live2D 参数模型和骨骼 3D；导出的纹理正确并不代表动作/表情正确。
- 字体与翻译必须一起检查：覆盖中文/日文字符、参数替换、换行、缺字回退及实际菜单宽度。
- 编辑器手册提供制作方法；游戏自己的加载合同、原生样本与官方 mod SDK 才决定怎样接入。不要据此宣称 Linn Modder 有新格式导入器。

遇到失效链接按[检索与证据](search-and-evidence.md)处理。三语词表用来补查疑点，不是要求每个任务读三份相同手册。
