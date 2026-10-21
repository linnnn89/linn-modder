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
保留同目录的 `sam3_geometry.py`；不要只复制主脚本而漏掉配套坐标处理文件。

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
本脚本只实现 CUDA 路线，不承诺 CPU、其他显卡或所有 ComfyUI 版本可用。

## 3. 第一次：文字选中主体

正式脚本默认先将非方图居中补白为正方形，保留人物长宽比，再交给原生节点缩放。
**不要自行先把竖图/横图拉伸成方图。** 不需要新增命令参数，也不需要手工制作补边图。
分割后自动去掉补边，只把还原到原尺寸的蒙版应用到原图；RGB、原画布大小和取景保持不变。
方图不增加补边。此默认行为同时适用于文字、框选和 `--compare-raw`。

```powershell
& $ComfyPython -s $Runner --comfy $ComfyRoot --checkpoint $Checkpoint `
  --image $SourceImage --output $Output --prompt person
if ($LASTEXITCODE -ne 0) { throw '分割失败：检查原始错误；不要把已有文件当作成功结果' }
```

- 人物从 `person` 开始；物体用 `guitar` 等简短英文名词，不用角色姓名或长篇生成提示词。
- `person` 不保证保留手持物；需要的配件必须检查。多个描述可用逗号分隔，但每项可能增加误选。
- 当前脚本将结果合成一张蒙版；不提供逐个人物选择界面。多人图优先改用下一节框选，不能把所有人物一起交付为指定角色。
- 模型只识别可见像素，不会恢复缺失的兔耳尖、被挡住的手臂或画面之外的身体。

## 4. 质量不好：先诊断，再决定是否框选

### 4.1 原始蒙版和细化蒙版对照

出现脸部、头发或衣服大面积透明孔洞时，不要立刻认定是解释器错误、颜色相近或 FP8 精度不足。
先在新目录对同一原图、同一提示做对照，一次加载模型即可：

```powershell
$DiagnosticOutput = Join-Path (Split-Path $Output -Parent) ('sam3-diagnostic-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
& $ComfyPython -s $Runner --comfy $ComfyRoot --checkpoint $Checkpoint `
  --image $SourceImage --output $DiagnosticOutput --prompt person `
  --refine-iterations 2 --compare-raw
if ($LASTEXITCODE -ne 0) { throw '诊断运行失败或得到全空/全满蒙版；保留输出，禁止继续安装' }
```

- `--refine-iterations` 可选 0–5，默认仍为 2；输入默认采用第 3 节的保比例补边。
- `--compare-raw` 另外输出 `raw-cutout.png`、`raw-mask.png`、`raw-preview.png` 和 `comparison.png`；后者**上排为 0 次细化，下排为指定次数，左白底、右深底**。0 次已被选中时复用结果，不重复推理。
- 文字模式的 0 次细化直接用 detector 蒙版；框选模式的 0 次仍会做一次初始 SAM 解码，当前原生节点的 0 和 1 都不追加细化。`raw` 是诊断基线，不是真值或质量保证。
- 若原始版完整而细化版变坏，可另存 `--refine-iterations 0` 候选并目视验收；若原始版已经破碎，关闭细化不能算修复，也不能仅凭这一结果归因量化。
- 比较时保持原图、提示/框、权重和计算精度不变。`result.json` 记录两版前景比例、变化像素比例和 IoU；这些只描述差异，不自动判优。某图分数很高但蒙版破碎时仍为不合格。

### 4.2 框选候选

先看原图尺寸，在原图上确定包含完整目标的矩形。坐标为 **左上角 X1、Y1，右下角 X2、Y2**，单位是原图像素；左上为 `(0,0)`，右下可取 `(宽,高)`。不得使用缩略图坐标，也不能把宽高当 X2/Y2。
脚本自动将输入框平移到补边坐标；**调用者不得自行加补边偏移**。输出 `boxes` 自动转回原图坐标并裁到原画布范围；完全落在补边区的检测框会被丢弃。

换一个新 `$BoxOutput`，然后执行：

```powershell
& $ComfyPython -s $Runner --comfy $ComfyRoot --checkpoint $Checkpoint `
  --image $SourceImage --output $BoxOutput --box $X1 $Y1 $X2 $Y2
if ($LASTEXITCODE -ne 0) { throw '框选分割失败；保留错误和第一版结果' }
```

`--box` 会选择 SAM 解码器框选路线，忽略 `--prompt`，不是对文字结果再加裁切。
框必须包含要保留的兔耳、头发、双手和配件。框选模式的 `result.json` 中 `boxes` 可以是空列表，不代表分割失败。
文字版与框选版都要看图比较；框选并非对所有图必然更好。
**不要机械地用整张画布当“更精确的框选”。** `(0,0,宽,高)` 是合法框，但没有增加更具体的主体位置提示；脚本会提示并记录 `full_canvas_box`，不擅自拒绝或缩框。
人物头发/配件触及画布边缘时，不为消除提示而截掉这些部分。如果无法提供有意义的位置提示，记录限制；不要把一次全画布框的失败推广成所有框选均失败。
框选也可加 `--compare-raw` 对照，仍使用新目录。纯白背景素材可以转用边缘连通蒙版或既有 Photoshop 路线，保留 SAM 失败证据；不必为了强行使用 SAM 破坏已合格的素材。

## 5. 必须打开结果，不能只看退出码

| 文件 | 含义 | 必须检查 |
|---|---|---|
| `cutout.png` | 同尺寸透明 RGBA 图 | alpha 是否真的存在；主体是否完整 |
| `mask.png` | 白色保留、黑色去除的蒙版 | 不应整黑、整白或误选背景 |
| `preview.png` | 同一结果叠在白底与深灰底，已缩小 | 只作目视预览，不当作原尺寸成品 |
| `result.json` | 选区、耗时、显存和格式检查 | `visual_review` 默认 pending，必须另外目视复核 |
| `raw-*`、`comparison.png` | 仅 `--compare-raw` 时输出的诊断基线与对照图 | 同一选区的原始/细化差异，不是真值对比 |

按顺序观察：整个人物 → 兔耳/发饰 → 脸和手指 → 细发丝 → 衣服镂空 → 背景残留。
`result.json.preprocessing` 记录 `mode=pad_to_square`、补边后尺寸、`padding_ltrb`（左/上/右/下）、白色填充值与内部框坐标；`size`、`boxes`、蒙版覆盖率和交付 PNG 均对应原图画布。
预览不清楚时回到原尺寸 `cutout.png` 与原图，检查具体局部，不反复全图扫描。
不因人物服装、体型、遮眼或原画截边而擅自换图、补画或裁掉。

脚本自动验证：尺寸一致、RGBA/蒙版数据有限、alpha 方向正确、可见图像的 RGB 与经 EXIF 方向处理的原图一致。
全空/全满蒙版会先保存诊断产物和 `result.json`，再以退出码 2 结束，禁止继续安装；输出目录已存在等参数错误也会非零退出，应区分错误文本。
前景低于 5% 或高于 95% 只产生复核提示，不当作硬性错误，因为小物体和铺满画布的人物可能合法。
没有提示也不表示质量合格：例如内部破碎但仍占画面 20% 的结果可以通过这些结构检查，仍必须看图。
这些条件不证明头发、饰品或语义选择正确；检测分数也不是抠图质量分数。

SAM 输出是分割蒙版，不是真实半透明抠图。细发丝、薄纱、烟雾或透明饰品仍可能需要单独的 matting 或人工修边。
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

用户要求 GUI 时，使用[官方图片分割模板](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_image_segment_sam3.json)，将 checkpoint 选择改为本地权重文件名。
模型通常放在 `models/checkpoints/`；保留官方子图，检查其外层暴露的模型选择与内层 loader 是否一致。
模板的预览节点不等于保存成品，须接入 `SaveImage` 保存 RGBA。模型放置、启动/重启和界面操作按已有用户授权执行。

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
