# SAM 3 / 3.1 本地抠图：AI 执行手册

适用于用户已选定图片、希望去背景或提取指定人物/物体的任务。先读本页再执行；不要自行下载模型、安装节点、升级环境、换素材或补绘。只需抠图时不启动游戏，不修改安装中的 MOD。

## 0. 先确认任务

- 原图是什么，保留谁，以及兔耳、发饰、武器等是否也要保留？用户已提供时直接使用，不重复提问。
- 默认保留原图 RGB、方向和画布尺寸，仅改变透明通道；不重画、瘦身、换衣、自动裁切或填补被遮挡的身体。
- 原图已有可用透明通道时先检查并复用。简单纯色背景可用[现有 sprite cutout](sprites.md)，复杂背景再使用 SAM。
- 全程写新目录，原图与原始权重不覆盖。只核对本轮涉及的图片、权重和输出，不扫描或哈希整个项目。

## 1. 找到四个路径，不要猜环境

| 变量 | 必须指向什么 | 常见错误 |
|---|---|---|
| `$ComfyRoot` | 含 `main.py`、`comfy/`、`comfy_extras/` 的 ComfyUI 源码目录 | 指到外层便携包目录 |
| `$ComfyPython` | 这份 ComfyUI 实际使用的 Python | 使用系统 Python、Forge Python 或项目 `.venv` |
| `$Checkpoint` | 用户已提供的本地 SAM 权重文件 | 把仓库 URL 当本地文件；重复下载 |
| `$SourceImage` | 用户选定的原图 | 擅自改用缩略图、截图或生成替代素材 |

Windows 可只读解析用户的 ComfyUI 快捷方式、启动脚本或正在运行进程的命令行。
典型便携包的解释器在外层 `python_embeded/python.exe`，源码在内层 `ComfyUI/`；以实际文件为准。
未知安装路径时先查这些入口，不从整块磁盘递归搜索。

本手册配套的 [comfy_sam3_cutout.py](../scripts/comfy_sam3_cutout.py) 随技能目录一起分发。
它直接调用现有 ComfyUI 原生节点，不需要启动服务器，不导入自定义节点，不提供新 `um` 或 MCP 操作。
在仓库中，其路径为 `skills/linn-modder/asset-pipeline/scripts/comfy_sam3_cutout.py`；导出技能后按相同相对位置定位，不能依赖 `scratch/`。
保留同目录的 `sam3_geometry.py`、`sam3_encoding_cache.py` 和 `sam3_matting.py`；不要只复制主脚本而漏掉配套文件。SAM 仍使用本机原生节点；matting 直接调用已有 PyMatting，不导入自动下载权重的自定义节点。

## 2. 预检：只检查，不安装

若当前仓库根目录存在 `.um/sam3-local.json`，先用下面的本机配置入口，避免重复查找和用错解释器。
这是不入库的本机路径记录；移动目录或换机器后须重新核实，不能把其他机器路径当默认值。
从仓库根目录执行：

```powershell
$RepoRoot = (Get-Location).Path
$ConfigPath = Join-Path $RepoRoot '.um/sam3-local.json'
if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) { throw '没有本机路径记录：按第 1 节定位，不自动安装' }
$LocalSam = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
$ComfyRoot = $LocalSam.comfy_root
$ComfyPython = $LocalSam.comfy_python
$Checkpoint = $LocalSam.checkpoint
$Runner = Join-Path $RepoRoot $LocalSam.runner_relative
$Output = Join-Path $RepoRoot ('scratch/sam3-cutout-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
```

然后将 `$SourceImage` 设为本次用户提供的原图绝对路径；不要从旧配置推断本次目标图。
先设置上面的四个绝对路径，以及 `$Runner`（配套脚本）和 `$Output`（新的输出目录）。
下列命令直接复制使用；变量值必须来自已核实的文件，而不是照抄其他机器路径。

```powershell
@($ComfyPython, $Checkpoint, $SourceImage, $Runner,
  (Join-Path $ComfyRoot 'main.py'),
  (Join-Path $ComfyRoot 'comfy_extras/nodes_sam3.py')) |
  ForEach-Object { if (-not (Test-Path -LiteralPath $_ -PathType Leaf)) { throw "缺少文件：$_" } }
if (Test-Path -LiteralPath $Output) { throw "输出目录已存在，请换一个新目录：$Output" }
& $ComfyPython -s -c "import torch, safetensors; print(torch.__version__); print('CUDA:',torch.cuda.is_available()); assert torch.cuda.is_available(), 'CUDA unavailable'"
if ($LASTEXITCODE -ne 0) { throw 'ComfyUI 环境预检失败；保留错误，不自动安装依赖' }
```

CUDA 显示 False，或缺少原生 SAM 节点时停止 GPU 运行。先报告实际环境和缺项，再决定是否需要用户授权安装/升级；不静默改用另一个 Python。
SAM 推理只实现 CUDA 路线，不承诺其他显卡或所有 ComfyUI 版本可用；第4.4节的已有蒙版 matting 可只用 CPU，跳过 SAM/CUDA 与模型加载。

## 3. 默认：Bbox 框选指定主体

先看完整原图，确定包含人物及所需兔耳、尾巴、头发、双手、武器等配件的矩形。
坐标为 **左上角 X1、Y1，右下角 X2、Y2**，单位为原图像素；不得使用缩略图坐标，也不能把宽高当 X2/Y2。
默认必须提供 `--box`。未提供框且未显式指定 `--prompt` 时，脚本在加载模型和创建输出目录前报错；不会回退 `person`，也不会自动用全画布框代替主体框。

正式脚本默认先将非方图居中补白为正方形，保留人物长宽比，再交给原生节点缩放。
**不要自行先把竖图/横图拉伸成方图。** 不需要新增命令参数，也不需要手工制作补边图。
分割后自动去掉补边，只把还原到原尺寸的蒙版应用到原图；RGB、原画布大小和取景保持不变。
方图不增加补边。此默认行为同时适用于文字、框选和 `--compare-raw`。

```powershell
& $ComfyPython -s $Runner --comfy $ComfyRoot --checkpoint $Checkpoint `
  --image $SourceImage --output $Output --box $X1 $Y1 $X2 $Y2
if ($LASTEXITCODE -ne 0) { throw '分割失败：检查原始错误；不要把已有文件当作成功结果' }
```

- `--box` 使用纯 SAM 解码器框选路线，不编码文字、不加载文字编码器；即使同时传入 `--prompt`，也由框选优先。
- 脚本自动将框平移到补边坐标；调用者不得自行加补边偏移。输出检测框还原到原图坐标并裁到原画布，完全落在补边区的检测框会被丢弃。
- 框选不是裁图，框内配件也不保证自动全部保留；必须回看原图检查。框选报告的 `boxes` 可以为空，不代表分割失败，实际模式看 `selection_mode` 与 `input_box`。
- 当前脚本合成一张蒙版；多人图只框本次目标，不把所有人物合并交付。
- 不机械地用 `(0,0,宽,高)` 充当更精确的框选；全画布框会记录 `full_canvas_box` 提示。人物触边时仍须保留完整目标，不为消除提示而裁掉发饰或肢体。
- 模型只识别可见像素，不会恢复缺失的兔耳尖、被挡住的手臂或画面之外的身体。

## 4. 质量不好：同框诊断，再考虑显式文字对照

### 4.1 原始蒙版和细化蒙版对照

出现脸部、头发或衣服大面积透明孔洞时，不要立刻认定是解释器错误、颜色相近或 FP8 精度不足。
先在新目录对同一原图、同一主体框做对照，一次加载模型即可：

```powershell
$DiagnosticOutput = Join-Path (Split-Path $Output -Parent) ('sam3-diagnostic-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
& $ComfyPython -s $Runner --comfy $ComfyRoot --checkpoint $Checkpoint `
  --image $SourceImage --output $DiagnosticOutput --box $X1 $Y1 $X2 $Y2 `
  --refine-iterations 2 --compare-raw
if ($LASTEXITCODE -ne 0) { throw '诊断运行失败或得到全空/全满蒙版；保留输出，禁止继续安装' }
```

- `--refine-iterations` 可选 0–5，默认仍为 2；输入默认采用第 3 节的保比例补边。
- `--compare-raw` 另外输出 `raw-cutout.png`、`raw-mask.png`、`raw-preview.png` 和 `comparison.png`；后者**上排为 0 次细化，下排为指定次数，左白底、右深底**。0 次已被选中时复用结果，不重复推理。
- 文字模式的 0 次细化直接用 detector 蒙版；框选模式的 0 次仍会做一次初始 SAM 解码，当前原生节点的 0 和 1 都不追加细化。`raw` 是诊断基线，不是真值或质量保证。
- 若原始版完整而细化版变坏，可另存 `--refine-iterations 0` 候选并目视验收；若原始版已经破碎，关闭细化不能算修复，也不能仅凭这一结果归因量化。
- 比较时保持原图、提示/框、权重和计算精度不变。`result.json` 记录两版前景比例、变化像素比例和 IoU；这些只描述差异，不自动判优。某图分数很高但蒙版破碎时仍为不合格。

### 4.2 显式选择文字模式作为对照

需要按概念找目标或比较文字与框选时，另用新 `$TextOutput`，显式传入短英文描述，不传 `--box`：

```powershell
& $ComfyPython -s $Runner --comfy $ComfyRoot --checkpoint $Checkpoint `
  --image $SourceImage --output $TextOutput --prompt person --compare-raw
if ($LASTEXITCODE -ne 0) { throw '文字对照失败；保留错误和框选结果' }
```

人物可用 `person`，物体可用 `guitar` 等简短名词；不使用角色姓名或长篇生成提示词。`person` 不保证保留手持物。
文字模式输出的检测框不等于输入了 Bbox；报告应为 `selection_mode=text`、`input_box=null`。
两版都要看图，不预设 Bbox 对所有图片必然更好。纯白背景仍可转用边缘连通蒙版或既有 Photoshop 路线，保留失败证据，不强行使用坏结果。

### 4.3 同图编码复用：默认进程内，可选跨命令

同一次命令的细化与 `--compare-raw` 默认复用视觉骨干的 trunk 编码，继续用原生 FPN 和解码器，不缓存提示或最终 mask。一次加载模型；文本细化若裁成不同局部，其图像编码单独计算，不能保证整条文字路线只编码一次。内存最多保留两组编码，退出释放；不修改 ComfyUI 核心，不启动服务器。

同图之后还要改框或提示时，给各次命令传同一个任务缓存目录，输出仍各用新目录：

```powershell
$EncodingCache = Join-Path $RepoRoot 'scratch/<任务>/sam-encoding-cache'
& $ComfyPython -s $Runner --comfy $ComfyRoot --checkpoint $Checkpoint `
  --image $SourceImage --output $Output --box $X1 $Y1 $X2 $Y2 `
  --compare-raw --cache-dir $EncodingCache
```

`<任务>` 换成当前任务目录，不照抄占位符。缓存键包含实际预处理图像字节、shape/dtype、权重绝对路径/大小/修改时间、相关 Comfy 源码摘要、Torch/设备/计算精度；不按图片文件名判同图。改变框或提示可复用编码，换像素、裁切、缩放、补边、权重身份或相关代码则失效。若人为保留路径/大小/修改时间替换了权重，应换缓存目录；这条身份策略避免每次重新哈希整个大权重。

跨命令缓存保存 safetensors，原子写入，同键并发写不会发布半个文件；各进程仍独立加载模型与提示，不能共用可变模型 state。损坏缓存作为 miss 重算并计数，不反序列化 pickle。恢复时保留原生 tensor 内存布局：将 channels-last 改成 NCHW 连续布局曾改变 FP16 卷积舍入，造成少量边界像素差异，不能只校验张量数值而忽略布局。磁盘缓存按实际图像增长，不自动清理用户目录；仅需要本轮细化时省略 `--cache-dir`。

`result.json.encoding_cache` 记录 `trunk_encodes`、`memory_hits`、`disk_hits`、`invalid_disk_entries` 和 `model_loads`；这是实际执行计数，不是视觉通过证据。`--no-encoding-cache` 用于原生基线对照，不与 `--cache-dir` 同用。缓存依赖本机 backbone 的 `cached_trunk` 接口；不支持时明确报错，不能伪造命中。本地编码缓存不控制 harness 图片重传或 API 计费。

### 4.4 按需 matting：先验收轮廓，再提供 trimap

默认 `--matting off`，不导入 PyMatting、不额外修边。确认人物、翅膀/角及必留物完整后，仍需精细 alpha 才启用 `--matting pymatting`。该路线用现有 `estimate_alpha_cf` 做 Closed-Form Alpha Matting，无新权重；缺包会在 SAM 和创建输出目录前报告，不安装、不下载、不回退为模糊。[PyMatting 官方接口](https://pymatting.github.io/alpha.html#pymatting.alpha.estimate_alpha_cf)

必须提供与工作副本尺寸/方向一致的单通道 L PNG `--trimap`：0=确定背景、255=确定不透明前景、128=待估计区域。三值不是预测透明度。先从首次拼图和必留清单确认区域；不自动将 SAM 结果腐蚀后当真值、不全局填孔。细羽、角尖、杯把孔和细链要保护；透明杯壁/翼膜内部可为128，已有可靠 alpha 直接保留。全未知或缺少前景/背景锚点的 trimap 拒绝执行。

已有已验收 mask 时，直接修边，**不重跑 SAM、不需要 `--comfy/--checkpoint`、不加载 GPU**：

```powershell
# 只登记已确认的一组文件；不推理、不读图上传。每个任务单独保存这份 JSON。
& $ComfyPython -s $Runner --image $SourceImage --mask $ExistingMask `
  --trimap $ReviewedTrimap --bind-inputs $InputManifest
if ($LASTEXITCODE -ne 0) { throw '输入登记失败；检查文件来源，不绕过校验' }

& $ComfyPython -s $Runner --image $SourceImage --mask $ExistingMask `
  --matting pymatting --trimap $ReviewedTrimap --input-manifest $InputManifest `
  --output $MattingOutput
```

`$ExistingMask` 为同尺寸 L PNG；`$ReviewedTrimap` 为本次确认的 trimap，`$InputManifest` 为任务目录内尚不存在的 `inputs.json`，`$MattingOutput` 为新目录。已经登记且文件未变时复用该 JSON，不反复登记或读图。旧 matting 命令现在必须补上 `--input-manifest`；只需登记已有文件，无须重做素材。

若需进一步限域，加 `--matting-roi X1 Y1 X2 Y2`（整数原图像素，右下边界不含）。SAM 后直接 matting 时，先用 `--image ... --trimap ... --bind-inputs ...` 登记，不传 `--mask`；再在普通 SAM 命令上加 `--matting pymatting --trimap ... --input-manifest ...`。缺项先修分割，不借 matting 补人体或器官。

仅写回 trimap=128 且在 ROI 内的像素；其它 alpha 保持原候选。已知前景/背景作为估计约束，不拿 trimap 自动覆盖整张旧蒙版。求解使用未知区外32像素上下文；若没有前景/背景锚点则读取整幅作为上下文，写回范围仍不扩大。没有未知像素时记录 `skipped_no_unknown`；求解失败明确失败，保留修前版本，不静默交付假结果。

额外输出 `segmentation-cutout/mask/preview.png`、`trimap.png` 和 `matting-comparison.png`（上修前、下修后，左浅底、右深底）；最终 `cutout.png` 始终取工作副本 RGB，只换 alpha。原生 alpha 作为上限，透明部分不会被填实。`result.json.matting` 记录后端、处理区、变化数、trimap hash 和耗时；检查受影响区域，原来通过的区域不反复读图。若同时 `--compare-raw`，`comparison.png` 始终比较 matting 前的两份 SAM 结果，不能混淆分割与修边效果。

### 4.5 多代理隔离：绑定输入、独占输出、GPU 自动排队

**输入登记是文件身份校验，不是视觉验收，也不是编码缓存。** `--bind-inputs` 只读取本地文件，检查尺寸/方向与 trimap 三值，保存各角色的 SHA-256、画布和 binding ID。首次配对仍须依据已看的拼图/来源记录；它无法识别首次就选错但没有来源记录的 trimap，不能自动宣称语义正确。运行时要求角色集合、画布和每个文件 hash 一致，同尺寸串图也会拒绝。文件允许移动或改名，内容不能偷偷替换。新蒙版/trimap 经确认后另存版本并登记新 JSON；不编辑 hash、不重新登记错误组合来消除报错。

复用本 runner 产物时保留同目录 `result.json`：读取已知 mask/trimap 会校验来源图；新回执还检查对应产物 hash。原图/蒙版/trimap 在入队前各读取一次，解码和报告均使用这批字节；排队中路径内容变化不会把另一张图读进本轮。源文件始终只读，结果以报告中的输入 hash 为准。

- **输出目录各任务独立，且每轮用新目录。** `mkdir(exist_ok=False)` 原子占用，争用同一路径只允许一个进程写入；不会自动覆盖或猜另一个皮肤目录。`job.json` 记录 job ID、输入身份、`claimed/waiting/running/processing/completed/rejected/failed`；失败目录保留诊断，重试选新目录，不删别人的目录。
- **SAM 在导入 Torch、加载模型前 FIFO 排队。** 工作区和全局技能副本共用 `%USERPROFILE%/.linn-modder/sam3-queue/session-<Windows会话号>/queue.json`；放在 AppData 外，避免 MSIX 客户端虚拟化后与 OpenCode 分成不同队列。按登记顺序一次只放行一个 GPU 推理。推理完成并清理显存后释放，再做 CPU matting/保存。无需复制多个模型或 ComfyUI 环境。`result.json.gpu_queue` 记录序号与等待秒数，等待只由本地脚本完成，不反复调用 Agent 重试。
- **等待默认900秒。** 可用 `--gpu-wait-seconds <秒>` 调整；只限制排队，不中断已获准的推理。超时/正常取消移除自己的票据，崩溃由后续任务根据 PID＋进程创建时间清理；不会因运行时间长就踢掉活进程，不杀其他任务。队列损坏时停止并保留证据，不清空来强行抢跑。
- **`--mask` 路线完全绕过 GPU 队列。** 不加载 SAM/显卡，可并行修不同图片；输入、trimap、输出各任务独立。仍共享 CPU/RAM，机器资源不足时减少并发，不能承诺无限开不会变慢。

排队范围是同一 Windows 用户/会话中使用此新版 runner 的进程；旧脚本、ComfyUI GUI、其他 GPU 程序及其他登录会话不受它调度。此版本 GPU 排队只支持 Windows，CPU mask 修边不受这一限制。共享锁不能替代输入配对与输出目录隔离。

实现参考本项目衣柜提交的原子票据模式；Windows mutex 本身不保证 FIFO，顺序由票据控制；持有者崩溃会产生 abandoned mutex，仍需核对记录一致性。[Microsoft mutex 说明](https://learn.microsoft.com/en-us/windows/win32/sync/mutex-objects)、[等待返回值](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject)。

本机还验证了两个 Windows 边界：MSIX 可将 AppData 文件访问重定向到应用私有目录，因此不能只把环境变量换成 AppData 绝对路径；读状态文件时未允许 delete sharing 会短暂阻止原子重命名，写入端仅对这类 Windows 错误有界重试2秒，始终保留旧完整 JSON，不原地截断。依据：[MSIX 文件虚拟化](https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes)、[CreateFile 共享模式](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)。

## 5. 必须打开结果，不能只看退出码

| 文件 | 含义 | 必须检查 |
|---|---|---|
| `cutout.png` | 同尺寸透明 RGBA 图 | alpha 是否真的存在；主体是否完整 |
| `mask.png` | 白色保留、黑色去除的蒙版 | 不应整黑、整白或误选背景 |
| `preview.png` | 同一结果叠在白底与深灰底，已缩小 | 只作目视预览，不当作原尺寸成品 |
| `result.json` | 选区、耗时、显存和格式检查 | `visual_review` 默认 pending，必须另外目视复核 |
| `job.json` | 当前任务、输入绑定与排队/运行状态 | 只查自己的输出目录；进程被强制终止时状态可能停在最后一次写入，队列按进程存活判断 |
| `raw-*`、`comparison.png` | 仅 `--compare-raw` 时输出的诊断基线与对照图 | 同一选区的原始/细化差异，不是真值对比 |
| `segmentation-*`、`trimap.png`、`matting-comparison.png` | 仅启用 matting 时的修前候选和修边对照 | 未知区之外 alpha 不变，RGB 不变；不把柔边当成必然正确 |

按顺序观察：整个人物 → 兔耳/发饰 → 脸和手指 → 细发丝 → 衣服镂空 → 背景残留。
`result.json.preprocessing` 记录 `mode=pad_to_square`、补边后尺寸、`padding_ltrb`（左/上/右/下）、白色填充值与内部框坐标；`size`、`boxes`、蒙版覆盖率和交付 PNG 均对应原图画布。
预览不清楚时回到原尺寸 `cutout.png` 与原图，检查具体局部，不反复全图扫描。
不因人物服装、体型、遮眼或原画截边而擅自换图、补画或裁掉。

脚本自动验证：尺寸一致、RGBA/蒙版数据有限、alpha 方向正确、可见图像的 RGB 与经 EXIF 方向处理的原图一致。
全空/全满蒙版会先保存诊断产物和 `result.json`，再以退出码 2 结束，禁止继续安装；输出目录已存在等参数错误也会非零退出，应区分错误文本。
前景低于 5% 或高于 95% 只产生复核提示，不当作硬性错误，因为小物体和铺满画布的人物可能合法。
没有提示也不表示质量合格：例如内部破碎但仍占画面 20% 的结果可以通过这些结构检查，仍必须看图。
这些条件不证明头发、饰品或语义选择正确；检测分数也不是抠图质量分数。

SAM 输出是分割蒙版，不是真实半透明抠图。细发丝、薄纱、烟雾或透明饰品可按4.4节按需 matting 或人工修边；这不承诺从混有旧背景色的 RGB 完美恢复真实透明材质。
若做修边，另存一版并记录处理参数；只改蒙版时继续验证 RGB 未变。
不要为了去绿边全局删除绿色：衣服、眼睛、饰品本身也可能是绿色。

## 6. 已复现的问题与固定处理

| 现象 | 已确认原因或下一步 |
|---|---|
| `getCudnnDataTypeFromScalarType() not supported for Float8_e4m3fn` | 本机 SAM 节点把 FP8 输入传给卷积。配套脚本已通过 `--fp16-unet` 指定 FP16 计算；保留 FP8 文件，不修改核心代码 |
| GUI 能加载权重，运行仍报上述错 | 换工作流文件不足以改变启动参数；确认实际 ComfyUI 进程带 `--fp16-unet`，已有进程须在用户同意后重启 |
| 显示 `compute_dtype torch.float16` | 对这条兼容路线是预期行为；不能宣称全程原生 FP8 推理 |
| `No module named torch`、`comfy` 或 `comfy_extras` | 核对解释器与源码路径，不在当前随机 Python 中自动 `pip install` |
| `--output already exists` | 换一个新的输出目录，保留旧结果，不删除目录来绕过保护 |
| 蒙版反了 | 官方链路为 SAM 蒙版 → InvertMask → JoinImageWithAlpha；后者会再次反转输入。直接把白色主体蒙版接入后者会反向 |
| 显存不足 | 记录实际错误、图像尺寸与占用。经授权关闭占显存的任务后再试；不能自动杀进程、减图或换权重 |
| 发丝缺失、绿色残边、物品遗漏 | 对照原图，按第 4 节区分选区和细化问题，再考虑框选或局部修边；仍不理想则明确为初稿，不用置信度掩盖目视问题 |
| 进程成功但脸部/衣饰大片透明 | 先确认调用正式脚本且报告含 `preprocessing.mode=pad_to_square`，避免旧脚本直接拉伸竖图；再按 4.1 对照细化。保留坏蒙版，不凭此认定权重坏了 |
| `full_canvas_box` | 位置提示不足的复核提示，不代表命令语法错；不得为避开提示截掉发饰或触边头发 |

### 复制其他角色的 Photoshop/转换脚本时

运行前展开核对 `srcPath`、`psdPath`、`pngPath` 及所有后续输入/输出路径，确认输出父目录也属于当前角色。
只替换文件名不够：`verification/旧角色/新角色文件.png` 仍写进旧目录。逐项检查实际写入路径不存在，并位于当前授权任务目录。
脚本返回 `OK` 后仍须验证声明的实际路径、尺寸和内容；不能只检查外层 PowerShell 变量，也不能在未读完脚本的情况下直接重跑。
若已误写到另一角色目录，先核实是否覆盖旧文件及实际产物位置，按授权范围恢复/移动；不要删除整个旧目录或覆盖其他角色产物。

同一故障三次修改验证仍失败，停止盲改并重新收集证据；不得靠不断换模型、装节点、升级环境回避。

## 7. GUI 与项目后续处理

用户要求 GUI 时，使用配套的 [Bbox 默认工作流](../workflows/sam3-bbox.json)，选择原图和本地已有 checkpoint。
本机已安装位置为 `K:/ComfyUI/ComfyUI/user/default/workflows/LinnModder-SAM3.1-FP8.json`。
`Bounding Box` 节点使用原图像素 **x、y、width、height**，与 CLI 的 X1/Y1/X2/Y2 不同；运行前按目标修改，包含全部所需配件，不把示例框套到新图片。
工作流直接连接原生 `PrimitiveBoundingBox` → `SAM3_Detect.bboxes`，`conditioning` 留空，不连接文字编码器；仅把文字框清空但保留编码连接不等于纯 Bbox。
模型通常放在 `models/checkpoints/`；保留蒙版反转和透明合成链，`SaveImage` 保存 RGBA。模型放置、启动/重启和界面操作按已有用户授权执行。

如需延续本机 FP8 兼容参数，在专用启动入口加入 `--fp16-unet`，不要无条件更改其他工作流的通用启动器。
无界面脚本成功只说明原生节点链执行成功，不能写成浏览器工作流已验收。
本次保比例处理在配套脚本中实现；原有 GUI 模板未自动获得这项改动。GUI 直接处理非方图前也须补边并在输出时还原，未完成该链路验证时使用配套脚本。

验收后的 PNG 继续交给 `image_prepare` / `sprite fit`，再按[目标格式](target-format.md)转换。
立绘抠图、小头像取景、DDS 转换、游戏安装与实机验收分别处理；不要顺手替换已安装画像。

## 8. 交付格式

交付必须包含：透明 PNG 的可点击路径、白/深底预览、采用文字还是框选、原图是否保持、是否修边，以及具体仍未解决的位置。
将 `result.json` 与原始蒙版保留在同一输出目录；不要把自动字段 pending 改成 passed 来代替看图。
耗时与显存只代表本次图片/版本/参数，不能推广为全项目效率或量化精度保证。

2026-10-21 本地验证：RTX 5070 Ti，ComfyUI `88ab4a0656`，Python 3.13.6，PyTorch 2.9.1+cu130；FP8/FP16 混合 safetensors 权重以 FP16 计算。
官方吉他样例和用户提供的二次元人物图已分别执行文字/框选；框选改善了该人物的轮廓，原始输出仍有少量边缘残色。浏览器界面及游戏内未验证。
托尔白底竖图曾在旧流程直接拉伸时严重碎裂：FP8 默认细化前景仅 20.06%，0 次仅 13.70%；改用 FP32 计算或关闭细化未解决。官方 FP16 权重直接拉伸同样失败（前景 18.00%）。
同图先补白保比例后，FP8/官方 FP16 均恢复基本完整主体，按原画布计算覆盖率约 55.73%/55.75%，两版蒙版 IoU 99.66%。因此本例优先修正输入几何处理，不能把它归因于小权重质量；这些数值不是通用精度保证。正式脚本已默认接入该处理，细发丝仍需目视验收。
版本变化时重新检查实际节点，不把这一快照当作所有系统的兼容承诺。

参考：[ComfyUI 官方教程](https://docs.comfy.org/tutorials/utility/video-segment-sam3)、[原生节点](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_sam3.py)、[Comfy-Org 权重说明](https://huggingface.co/Comfy-Org/sam3.1)。官方 FP16 对照权重经用户单独授权下载；日常仍可使用已有 FP8。本脚本不下载权重，不安装新依赖。
