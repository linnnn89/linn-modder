# 引擎与文件：免费文字资料入口

2026-10-03 用网页读取工具确认下列页面返回正文，均为公开文档或作者仓库，无需付费账号。可访问状态会变化；每次只读与目标版本有关的页面。`master`、`stable` 和默认分支是移动目标，使用时选择游戏对应的版本/tag。

| 资料与语言 | 用来回答什么 | 读取与适用边界 |
|---|---|---|
| [BepInEx 安装分流](https://docs.bepinex.dev/master/articles/user_guide/installation/index.html) · EN | Mono、IL2CPP 和其他运行时的安装路线 | HTML；master 不等于稳定版，按运行时选择子页 |
| [BepInEx 作者仓库](https://github.com/BepInEx/BepInEx) · EN | 兼容范围、releases、维护者问题反馈 | README/源码；先核对版本，不能把某个预发布包当所有 Unity 游戏通用包 |
| [AssetRipper](https://github.com/AssetRipper/AssetRipper) · EN | Unity 资源分析与导出 | README/源码；导出能力不证明能够原包回封 |
| [UABEA](https://github.com/nesrak1/UABEA) · EN | Unity bundle/asset 编辑工具入口 | README/源码；核对维护状态、工具建议及目标 Unity 版本，再做无修改往返 |
| [UAssetGUI](https://github.com/atenfyr/UAssetGUI) · EN | Unreal 资产检查/修改与版本选择 | README/源码；单个 uasset 的支持不能证明整个 pak/IoStore 可写 |
| [Kaitai Struct](https://kaitai.io/) · EN | 用声明式结构描述二进制、寻找格式规格 | HTML/格式源码；必须另证 writer 能力，解析器不是通用打包器 |
| [DDS 文件布局](https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dds-file-layout-for-textures) · EN | DDS 头、压缩纹理、mipmap 数据布局 | 官方 HTML；与实际渲染器、目标平台格式一起核对 |
| [Python JSON](https://docs.python.org/3/library/json.html) · EN | 字符控制、重复键、数值与编解码选项 | 官方 HTML；选择本机 Python 版本；宽松读取不能证明游戏解析规则 |
| [Python CSV](https://docs.python.org/3/library/csv.html) · EN | dialect、引号、换行与字符串字段 | 官方 HTML；CSV 不是可直接用逗号拆开的文本 |
| [Fabric 开发者指南](https://docs.fabricmc.net/zh_cn/develop/) · 中文 | Minecraft 模组的版本化开发与资源流程 | 官方中文 HTML；选对 Minecraft、Loader、API 和映射版本 |
| [Fabric デベロッパガイド](https://docs.fabricmc.net/ja_jp/develop/) · 日本語 | 同一生态的日文检索入口 | 官方日文 HTML；译文覆盖范围可能不同 |

从这些页面继续导航到当前任务的精确 API/格式，不要把整份仓库克隆当作默认研究步骤。美术/UI 的英中日入口在另一份[资料抽屉](art-and-ui-sources.md)。
