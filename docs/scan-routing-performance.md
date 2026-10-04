# 扫描与技能路由优化（2026-10-04）

基线：`ab8d4789ff374179fca23f73ce3e73997e55d299`。保留单技能、14 个按需主题，
不改变发现描述、工具名称、用户项目和备份格式。没有安装真实游戏。

## 验收目标与结果

同一 Linux / Python 3.12 环境，预热后交替运行前后版本各 15 次。
原始样本、源码摘要与环境见 [JSON 记录](benchmarks/scan-routing-20261004.json)。
测量时修改后版本尚未提交，`commit` 为工作分支基点；`measured_sources_dirty`
和 `measured_sources_sha256` 区分实际测量的代码与入口内容。

| 指标 | 基线 | 修改后 | 减少 |
|---|---:|---:|---:|
| 合成目录完整 `Service.game_scan` 耗时中位数 | 403.55 ms | 254.63 ms | 36.90% |
| 入口全文，cl100k | 1,733 | 778 tokens | 55.11% |
| 入口 + 素材指南，cl100k | 2,142 | 1,187 tokens | 44.58% |
| 入口全文，o200k | 1,361 | 696 tokens | 48.86% |
| 入口 + 素材指南，o200k | 1,770 | 1,105 tokens | 37.57% |

达到完整扫描至少快 25%、cl100k 素材路由至少省 40%、两种编码的入口至少省 45%、
入口不超过 900 cl100k tokens 的目标。发现元数据未改，不宣称本轮减少固定发现成本。

扫描夹具为 20 个目录内 5,000 个空文件，加 Unity 识别文件共 5,003 文件、21 目录。
计时包括安全检查、索引、引擎识别和报告，不包括解释器启动；两版都禁用本机商店枚举，
避免已安装游戏和网络盘影响结果。逐次比较既有报告字段，识别结果一致。
这不是 Windows 磁盘或真实安装目录的性能结论；原始样本可用于观察波动。

Token 用 tiktoken 0.14.0 的 `cl100k_base` / `o200k_base` 实际编码文本，包含 frontmatter。
素材路由为入口加未修改的素材指南；下一步所需的格式手册、接口资料并未计入。
需要工具时仍需读取接口文档，不能把每个任务都视为省下相同 Token。
未计 MCP 包装、提示缓存和模型输出，也不等同于账单或实际模型理解能力。

## 实现与边界

- 使用流式 `os.scandir` 一次完成链接检查和索引，不先完整遍历目录。
- 80,000 上限约束所有访问条目，包括目录，防止空目录树绕过预算；最多额外看一个条目来区分
  “恰好到上限”和“还有内容未扫描”。深度为六，最深层文件仍可收录，更深目录不进入。
- `index_truncated` 保留；新增 `index_truncation_reasons` 和 `entries_visited`。
  截断原因是 `max_entries` 或 `max_depth`，文本输出也显示原因。
- 进入目录/读取二进制前拒绝遇到的符号链接及 Windows reparse points，包括 junction；
  保存已检查文件的原始大小写路径，后续读取不再逐层枚举目录。
- 未进入的截断子树和忽略的 `.git`、`__pycache__`、`shadercache` 不属于安全检查结果。
  遍历访问错误直接失败，不输出貌似完整的报告。备份操作的完整检查未修改。
- 不把这些检查称作 OS 隔离：恶意进程并发替换文件的竞态仍不在保证范围内。
- 流式深度优先顺序取决于文件系统；有限预算下不能保证所有引擎标记都被收录，应结合截断标记
  扫描明确子目录。目录也占用预算，因此大树可能比旧版更早截断。

回归夹具覆盖超大单目录、恰好到限、空目录预算、深度边界、大小写读取、链接拒绝、
访问错误和单次目录枚举；Windows CI 额外验证真实 junction。

## 路由审阅样例

以下是对压缩前后导航的静态审阅样例，不是跨 harness 的模型准确率测试。
三个语言列各 14 个请求，都能映射到保留的主题；自动文档检查另外验证所有链接可达。
发现描述的中英日文本保持原样；入口正文使用简短英文和中文任务标签。

| 中文请求 | English request | 日本語リクエスト | 首读主题 |
|---|---|---|---|
| 从零制作完整 MOD | Plan a complete mod | MOD全体を制作 | mod-any-game |
| 创意工坊模组在哪，为什么加载失败 | Locate Workshop mods; fix loading | Workshopの場所と導入失敗 | game-recon |
| 核对新版工具和格式 | Verify current tools/formats | 最新のツールと形式を確認 | mod-research |
| 菜单字体太小，汉化溢出 | Fix menu font/localization overflow | UIのフォントと日本語のはみ出し | ui-mod |
| 改存档数值、解包并回封 | Edit saves; unpack/repack | セーブ値変更と再パック | file-mod |
| CK3 二次元角色与阵营映射 | Map anime characters/factions | 二次元キャラと勢力の対応 | anime-strategy-mod |
| 做头像、透明立绘和 PSD | Make portraits and layered PSD | 立ち絵とレイヤーPSD | asset-pipeline |
| 分析未知二进制结构 | Reverse unknown binary internals | 未知バイナリの構造解析 | reverse-engineering |
| 明确用 fal 生成图片 | Generate with fal | falで生成 | fal-assets |
| 截图并操作游戏窗口 | Capture and control a game window | ゲーム画面の撮影と操作 | game-automation |
| 融合两个游戏的玩法 | Combine two games' mechanics | 二つのゲームの仕組みを融合 | mashup-mods |
| 制作 MOD 预告片 | Produce a mod trailer | MODの紹介動画 | showcase-video |
| 打包发布 MOD | Package and release a mod | MODの配布パッケージ | publish-mod |
| 查找并贡献已验证经验 | Reuse and contribute findings | 検証済みの知見を検索・共有 | share-field-notes |

涉及多个阶段时逐步切换主题；未知格式和版本变化仍需联网查证。素材指南仍保留
官方参考优先、可用 GPT Image 制作底图、真实 PSD 写入器组装并重新打开验证的要求。

## 复现与回退

在完整 checkout 中使用同一解释器和依赖环境：

```powershell
git fetch origin backup/pre-scan-routing-20261004
git worktree add --detach ../linn-scan-before ab8d4789ff374179fca23f73ce3e73997e55d299
uv run --with tiktoken python scripts/benchmark_scan_routing.py --before ../linn-scan-before --output scan-routing-local.json --require-targets
```

脚本输出每次计时和实际 Token 数，不对不同 CI runner 设置绝对耗时门槛。
Tokenizer 首次加载可能联网；缓存后可离线运行。Windows 可使用同一脚本独立测量。

优化前的远端分支为 [backup/pre-scan-routing-20261004](https://github.com/linnnn89/linn-modder/tree/backup/pre-scan-routing-20261004)。
可用上述 worktree 检查原版，或重新安装固定基线提交；合并后要整体撤销时，对本轮 squash
提交执行 `git revert <合并提交SHA>`，检查后正常推送，不强制覆盖主分支。
本轮没有项目数据迁移，也不要求修改 harness 参数。
