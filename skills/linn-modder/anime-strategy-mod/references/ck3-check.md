# CK3 文件检查与 Tiger 报告

用于一次改动收尾时排查描述文件和本地化格式，或定位已有 Tiger 诊断。操作只读，不修改或安装 MOD。

## 一个入口

```json
{"source":"project/mod/my_mod"}
```

传给 `ck3_check`；`source` 是包含 `descriptor.mod` 的 **MOD 内容目录**，不是游戏根或整个脚手架工程。通过 MCP、`um tool call ck3_check --args-file check.json` 或 `Service.invoke` 使用同一操作。

检查内容：

- `descriptor.mod` 存在、UTF-8 可读且不是空文件/只有注释。
- `localization/` 下 `.yml`/误写的 `.yaml`：UTF-8 BOM、`<name>_l_<language>.yml` 文件名、首个非注释行的语言头与文件名一致。
- 保留 `localization/replace/` 等布局，不强制语言目录名；没有本地化文件的 MOD 可以通过这些检查。

`ok:true` 表示检查操作完成；**看 `data.passed` 判断是否发现 error/fatal**。`diagnostics` 给出 `source`、`severity`、`code`、`message` 和 `locations`，行号从 1 开始；文件缺失等没有行号的位置为 `null`。`counts` 和 `total` 统计全部发现，默认只返回前 50 项，用 `next_offset` 续读，`limit` 为 1..100。只有 warning/tips/untidy 时 `passed` 可以为 true，仍按变更范围审阅。

每个文本/报告最多 16 MiB，本地文本合计 128 MiB，localization 树最多 10,000 个条目；超限或无法读取时报结构化错误，不把未完成检查视为通过。只遍历本地化目录，不扫描整套纹理资源。

## 先定位严重错误

报告较多时，在同一操作中增加 `min_severity`：

```json
{"source":"project/mod/my_mod","tiger_report":"verification/tiger.json","min_severity":"error"}
```

级别从低到高为 `tips < untidy < warning < error < fatal`；`error` 同时返回 error 和
fatal，空字符串或省略表示不过滤。筛选同时适用于本地检查和导入的 Tiger 诊断，保留原始顺序、
内容和全部位置，不聚合或改写原报告。重新生成报告时，也可按 Tiger 版本使用其
`--consolidate` 合并部分重复错误，或 `--suppress` 保留已有基线。

**`counts`、`total` 和 `passed` 始终基于全部诊断。** 过滤后另有 `min_severity` 和
`matched_total`；`offset/next_offset` 是筛选结果内的位置，后续页沿用相同过滤条件。
零条匹配不代表全部通过，例如仅看 fatal 时仍可能有 error。修改源文件或报告后从第一页重读。
这只减少返回给 agent 的信息，不减少检查范围，也不证明验证器或游戏已重新运行。

## 使用已有 Tiger

Tiger 的 scope、引用、脚本语法等诊断由原工具生成，Linn Modder 不重新实现解析器。确认同版原版、依赖与内容根后，可用已安装的 Tiger 生成 UTF-8 JSON。用 Python 保存原始 stdout，避免 Windows PowerShell 5.1 的 `>` 把报告转成 UTF-16：

```python
from pathlib import Path
import subprocess

with Path("verification/tiger.json").open("wb") as output:
    run = subprocess.run(["ck3-tiger", "--json", "project/mod/my_mod/descriptor.mod"], stdout=output)
print("Tiger exit code:", run.returncode)  # 检查 stderr/退出状态；失败不能当作空报告通过
```

先创建 `verification/`；仅在用户任务需要静态脚本检查且 Tiger 已可用时执行。要保留已有依赖/基线设置，按该 Tiger 版本配置。随后读取报告：

```json
{"source":"project/mod/my_mod","tiger_report":"verification/tiger.json","limit":50}
```

支持作者当前的 JSON **数组**格式，保留原分类、级别、置信度及多个位置。报告路径中的原版/依赖标识仅用于展示，不据此读取其他文件。报告必须位于允许读取的工作区或游戏根内；来源字段 `tiger.path/sha256` 方便核对原始报告。

**导入不代表重新运行 Tiger。** JSON 本身没有足够的游戏版本、完整输入哈希和执行状态；结果保留 `freshness:not-verified`。旧报告、过滤或 `--suppress` 后的空数组不能证明当前脚本没有问题。重新生成报告的时机是本轮相关源文件、原版或依赖发生变化。

## 验证范围

`not_checked` 明确保留完整 descriptor 语法/注册路径、脚本语义及运行行为。本地检查和导入报告都不会将结果升级为实机验证，始终保留 `not-tested-in-game`。本工具不判断所有语言是否为该 build 支持，也不解析本地化正文中的键、占位符或引号；这些问题交给对应版本的 Tiger 与实际日志。

格式依据在 **2026-10-13** 核对：[Tiger JSON writer](https://github.com/amtep/tiger/blob/9e3d3b25c7524cdcc86d5f4190f3f8cffbc4d630/src/report/writer_json.rs)、[报告级别](https://github.com/amtep/tiger/blob/9e3d3b25c7524cdcc86d5f4190f3f8cffbc4d630/src/report/report_struct.rs)、[README](https://github.com/amtep/tiger/blob/9e3d3b25c7524cdcc86d5f4190f3f8cffbc4d630/README.md)。本地规范沿用本项目 [CK3 验证资料](verification.md#ck3-author-sources)，本次未运行 Tiger 或游戏。
