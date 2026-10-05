# TKEditor：Agent 数据与新增头像接口

用于《英雄立志传：三国志》官方 TKEditor JSON 工程和外部 CG。使用 Linn Modder
已有 MCP、`um tool call` 或 Python Service，不需要启动编辑器、写代码或提供 SQL。
先查询再修改，不把原始 JSON 整表送入上下文。下面 JSON 都是工具参数。

## 先按意图选最短流程

| 用户要做什么 | 最短调用顺序 | 完成条件 |
|---|---|---|
| 查武将或资料 | 无可用索引时 `tk_index` → `tk_query`；未知表/字段才用 `tk_tables`；需要长文才用 `tk_read_field` | 找到所需字段即可停止 |
| 修改已有数据 | `tk_project` → 对新工程 `tk_index(catalog="edit")` → 查询 → `tk_patch` 预览 → 同参数应用 → 刷新该工程索引 | `data.applied:true`；已有可用工程可复用 |
| 新增头像选项 | 准备 PNG → `tk_portraits(intent="new_option")` → 查看产物；以后用 `tk_portrait_options` 搜索 | 包已生成并登记；仍未安装到游戏 |
| 替换旧武将头像 | 来源索引 → `tk_query` 取得唯一 Hero ID → `tk_portraits(intent="replace",hero_id=该ID,catalog=该索引)` | 替换包已准备；仍未部署 |

新增头像不需要创建武将、修改 `icon` 或先检索旧武将。`new_option` 无须预先建索引；
但指定名称的索引（省略时为 `default`）若已存在，会用于冲突检查，过期时须刷新。
只有用户明确要求替换旧头像时才能使用 `replace`，不要因新增失败自动切换模式。

参数约定：`catalog` 是索引名称（1..64 个英文字母、数字、`_`、`-`），不是路径或游戏名。
在同一工作区中复用相同索引名；原始来源可叫 `source`，可写工程用 `edit`，不要混用。
相对文件路径均以服务配置的工作区为基准；`source` 指向含 `Hero.json` 的目录；
`destination` 必须是工作区内的新目录。尖括号占位符须替换为真实路径或查询结果。

返回值先检查 `ok`，失败读取 `error.code`；业务数据在 `data`，产物路径在 `artifacts`。
不要把 `ok:false` 一律理解为“没有生成文件”：头像登记失败会保留包，按下文恢复。
复用已有索引，变化或写入后再刷新；先 `limit:5` 和必要字段，定位后改用精确 ID。
仅在需要更多候选时沿 `data.next_offset` 翻页；长字段用 `tk_read_field`，不要扩大整表输出。
初次可读取本页前 40 行选流程；细节按 `manual_read` 的 `data.next_line` 续读至相关节。

## 检索

1. `tk_index`：输入包含 `Hero.json` 的目录，不是游戏根目录。
   工坊 MOD、`MODProjects/<工程>`、`StreamingAssets/Json` 均可作为只读来源。
   SQLite 保存在工作区 `.um/tkeditor/catalogs/`。
2. `tk_tables`：默认只返回表名和条数；指定 `table` 后分页返回字段、类型、中文解释及可写状态。
3. `tk_query`：中文子串、完整姓名或精确 `record_id`，只投影指定字段。
4. 长文本用 `tk_read_field` 按 `next_start` 续读。

调用 `tk_index`：

```json
{"source":"<ABSOLUTE_MOD_DIRECTORY>","catalog":"source"}
```

调用 `tk_query`：

```json
{"catalog":"source","table":"Hero","query":"芽衣","fields":"id,surname,name,icon","limit":5}
```

需要长说明时调用 `tk_read_field`，ID 来自上一步 `data.records`：

```json
{"catalog":"source","table":"Hero","record_id":"<ID_FROM_QUERY>","field":"description","max_chars":1000}
```

`limit` 1..50，默认查询 10 条；字段最多 8 个，单个值最多 512 字符，记录区总预算
约 12000 字符，返回 `truncated` 和 `next_offset`。长字段单页最多 2000 字符。
子串检索每个字段的前 2048 字符；不保证命中更后面的文本。
SQLite 按表/ID建立索引，中文子串用数据库条件过滤；没有语义检索或远程模型调用。
精确 ID 查询直接使用表/ID复合索引。新索引的读取先检查源文件大小、纳秒时间戳和
文件标识，未变化时直接读取 SQLite 快照，不反复读取整个 JSON；元数据变化时退回
完整 SHA-256 校验。它不是对伪造文件元数据的检测机制。旧版索引仍可读取，但继续
使用完整哈希校验；重新 `tk_index` 后获得新索引性能。
关联表可以重复 ID，返回 `row_index` 区分；`tk_read_field` 可用该位置读取一行，
重复 ID 的修改会被拒绝。无 ID 的元数据行用 `@<位置>` 查询，仅供读取。

## 创建独立数据工程与安全修改

`tk_project` 复制 JSON 到新的工作区目录，保持原始 ID、标识符与全部未知字段。
不复制模型、声音、AssetBundle、RAR、工坊发布 ID 或其他非 JSON 内容。
这是数据工程，不是完整的可发布 MOD；原始资源依赖必须保留。

```json
{"source":"<ABSOLUTE_MOD_DIRECTORY>","destination":"projects/my-mod"}
```

随后 `tk_index(source="projects/my-mod", catalog="edit")`，再查询和预览：

```json
{"catalog":"edit","table":"Hero","record_id":"<ID_FROM_QUERY>","changes":{"force":"50"}}
```

上面的参数用于 `tk_patch` 预览（默认 `apply:false`）。以下仅展示成功响应的关键字段，
哈希占位符代表真实返回的字符串，此响应示例不能用作调用参数：

```json
{"ok":true,"data":{"source_sha256":"<SOURCE_FILE_HASH>","confirmation":"<PREVIEW_CONFIRMATION>","applied":false}}
```

读取 `data.changes` 确认目标和改动符合请求；若为空则没有变化，无须应用。
应用仍调用 `tk_patch`，复制相同的 `catalog/table/record_id/changes`：

```json
{"catalog":"edit","table":"Hero","record_id":"<ID_FROM_QUERY>","changes":{"force":"50"},"apply":true,"expected_sha256":"<PREVIEW_CONFIRMATION>"}
```

**`expected_sha256` 必须逐字复制预览的 `data.confirmation`，不能使用 `data.source_sha256`。**
若改变任一修改参数或来源内容，重新预览，不能复用旧确认值。
确认值绑定来源路径、来源 SHA-256、表、ID 和此次改动；它是防止误操作的机制，
不是人类审批或身份认证。

可写字段：已有的 `name/surname/word/description/remark` 及其语言版本；
`Hero` 的 `rule/force/wise/politics/charm/will` 六个基础属性。
属性必须是 0..100 的整数字符串，这是工具的保守安全策略，不宣称游戏的理论最大值。
其他 ID、`icon`、模型引用、父母关系、事件条件/效果、卡牌表达式均只读。
不能增删记录、批量清空或执行生成代码。双引号及不受支持的控制字符会被拒绝；
短文本最大 128 字符，说明最大 10000 字符。

应用只允许 `tk_project` 创建的工程。每次在 `.um/tkeditor/backups/<唯一ID>/`
保存原始完整 JSON 和改动信息，再原子替换目标 JSON；其余记录和字段的值不变。
输出格式化可能改变空白与转义表示。预览和应用始终完整校验源文件 SHA-256，
不走读取快路径；来源不一致时旧确认失效。成功编辑后也要刷新索引。完整原文件在返回的 `backup` 中，
需要恢复时可以在授权范围内复制回工作区工程，之后重新索引。

## 新增头像选项（默认）

`tk_portraits` 默认 `intent:"new_option"`。它创建一套独立外部 CG，而非新增武将，
也不修改旧武将的 `Hero.icon` 或原图。显示名称可以相同，真实文件名使用
`um_<随机标识>_<显示名称>`，避免命中官方的“同姓名替换历史武将”规则。
同一角色可以新增多套头像，在自建武将的外部 CG 入口选择。

```json
{"full":"art/full.png","half":"art/half.png","icon":"art/icon.png","destination":"portraits/new-hero","name":"新角色·制服","intent":"new_option"}
```

三张单帧 PNG 的规格来自本地官方 `Portraits/说明.txt`：

| 槽位 | 尺寸 | 输出目录 |
|---|---|---|
| `full` | 1000×1400 | `Portraits/1000x1400/` |
| `half` | 1024×1024 | `Portraits/1024x1024/` |
| `icon` | 260×340 | `Portraits/260x340/` |

默认 `mode:"strict"` 拒绝错误尺寸。需要工具调整时显式选择
`contain`（透明留白）或 `cover`（居中裁切），三个输入可指向同一张源 PNG。
有图片查看能力的 AI 应查看生成的三张图，检查人脸位置和裁切效果。
这组 TKEditor MCP 工具返回文件路径，不自动提供图片视觉输入；使用客户端的图片查看工具。
若客户端不能查看图片，明确报告“格式已验证，构图和裁切未检查”，交由用户查看产物，
不能声称视觉验收通过。格式通过不保证画面好看。来源最大 32 MiB、
16 百万像素，保留透明通道。三张图片全部通过后才发布新目录，已有输出目录不覆盖。
尺寸以 EXIF 方向校正后的像素为准，保存后再次验证。显示名称最多 80 个字符；
新增选项的实际文件名另保留 20 个字符给唯一前缀，不占用显示名称额度。
包内 `portrait-pack.json` 记录名称、独立选项 ID、三张图的 SHA-256 和安装说明。

成功准备的选项登记到工作区 `.um/tkeditor/portrait-options.sqlite`，可通过
`tk_portrait_options(query="制服", limit=5)` 分页搜索。索引重建不删除这些登记。
登记状态始终标明未由本工具安装；不推断游戏当前是否加载/选择了它。

若数据库登记失败，结果为 `ok:false`、`portrait_registration_failed`，但已生成的包
保留。`data.output`、`artifacts` 和 `data.recovery` 给出产物及恢复操作，不要重新生成
到同一目录。调用 `tk_portrait_register(pack="portraits/new-hero")` 会重新校验目录边界、
选项身份、三张 PNG 的固定路径、实际尺寸及 SHA-256，再登记到 SQLite。
重复恢复同一个包不会重复插入；同一选项 ID 对应不同包时拒绝覆盖。恢复不需要原始素材，
也不会修改包内文件。使用工具白名单时须同时启用 `tk_portrait_register`。

安装说明：先备份游戏现有 `Portraits`，再把生成包内的三种尺寸子目录合并到
`ThreeKingdom_Data/StreamingAssets/Portraits`，在游戏的自建武将中读取外部 CG。
工具不写游戏目录，因此此阶段交付的是新增选项包及导入步骤，不是已经出现在游戏中的选项。
无需创建新武将记录或改旧 `icon`；不会自动获得 AssetBundle 的内置头像编号。

如果明确要求替换，必须同时传 `intent:"replace"` 和检索得到的 `hero_id`。
工具用当前 `surname+name` 命名并拒绝同名歧义；新增模式拒绝绑定旧 `hero_id`。
替换前同时检查 ID 唯一性；同一个 ID 对应多条武将记录时也会拒绝。
替换结果同样只在工作区生成，游戏安装另外执行。

## 失败后下一步

先看 `error.code` 和 `error.message`，修正原因后再调用；不原样无限重试。
有 `data.recovery` 时优先使用其中的 `tool` 和 `arguments`，不要自行重组已确定的参数。
`stale_catalog` 返回原来源和索引名；`unknown_table` 返回表查询；
`confirmation_required` 返回同目标/改动的预览参数（`apply:false`），不会自动应用。
这些恢复动作的 `available:false` 表示当前白名单未启用该工具，应报告配置限制。
没有恢复动作时按下表处理，不推断自己获得了额外写入权限。

| 错误或状态 | 下一步 |
|---|---|
| `stale_catalog` / `invalid_catalog` | 用原来的来源目录和相同 `catalog` 重新 `tk_index`；写入前重新查询、预览 |
| `source_changed` | 来源在操作期间变化；确认写入者已结束后重新索引、查询；修改需重新预览 |
| `not_found` | 按错误消息区分缺文件、缺索引或缺工程标记；核对路径；缺索引才建索引，缺工程则用 `tk_project`，不伪造标记 |
| `unsupported_source` | 选择真正含 `Hero.json` 的目录，不传游戏根目录 |
| `unknown_table` / `invalid_fields` / `invalid_field` | 用 `tk_tables` 查真实表名和字段；不要猜名称或请求全部字段 |
| `unknown_record` | 在相同索引/表重新查询真实 ID，不编造记录 |
| `confirmation_required` | 重新预览，把 `data.confirmation` 放入 `expected_sha256`，其他修改参数保持一致 |
| `protected_field` / `invalid_project` / `path_outside_roots` / `game_root_read_only` | 遵守可写字段和工作区边界；需要时创建独立工程，不能改用 shell/SQL 绕过限制 |
| `ambiguous_record` | 读取可用查询返回的 `row_index`；修改或替换不能用它绕过 ID 歧义，停止该操作并报告 |
| `ambiguous_name` | 同名武将无法安全通过外部文件名定向替换，停止替换并报告 |
| `invalid_value` | 对照可写字段类型/范围修正，如属性用 `"50"` 而非数值 `50`；不静默改成其他目标值 |
| `invalid_dimensions` | 提供正确尺寸；需要缩放时按构图要求显式选择 `contain` 或 `cover`，然后检查产物 |
| `target_exists` / `invalid_target` | 使用新的工作区输出目录，不删除或覆盖旧目录；若是登记失败的已有包，走下面的恢复流程 |
| `portrait_registration_failed` | 包已经保留；使用 `data.recovery` 给出的工具/参数调用 `tk_portrait_register`，不要重生成 |
| `invalid_portrait_pack` / `portrait_id_conflict` | 报告校验或身份冲突，不编辑清单、伪造哈希或删除原登记来强行通过 |

遇到工具未出现在客户端列表中，检查 MCP 工具白名单及服务版本；不要猜另一个工具名。
其他未列出的失败按返回消息处理；原因不清楚时保留产物并报告实际错误。

## 能力与证据边界

本接口不运行 TKEditor、不编译 Unity AssetBundle、不编写模型/动画、不编辑复杂事件
表达式，也不做 Steam 发布或直接部署。外部 CG 不等于 AssetBundle/工坊模组。
官方提示大量外部图片占用内存，整包替换应走 AssetBundle；本工具不声称支持该编译流程。
官方 TKEditor 基本教程还提示不要启用开发者标记、字符串不要使用双引号。

本地 MOD 中存在 JSON 字符串内的未转义换行：读取兼容 CR/LF/Tab，仍拒绝重复键、
NaN/Infinity 和其他控制字符；输出使用标准 JSON 转义。读取/往返校验通过不等于
当前 TKEditor 导入或游戏加载已通过。

资料来源：随游戏提供的 `TKEditor使用说明.txt`、`---TKEditor基本教程---.pdf`、
`Portraits/说明.txt`（检查日期 2026-10-04）；
[Python 3.10 JSON 文档](https://docs.python.org/3.10/library/json.html)确认解析参数与重复键处理。
