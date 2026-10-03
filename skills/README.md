# Skill router

Read this index only when the next skill is unclear. A known task can go directly to its
`SKILL.md`. Load one entry and only the reference needed for the current step; do not
read every skill, engine playbook or historical example.

## Choose by the task

| User needs | Skill | Expected result |
|---|---|---|
| A whole mod or an unclear multi-stage route | [mod-any-game](mod-any-game/SKILL.md) | Route, staged changes and evidence |
| Install/engine/loader identification or feasibility | [game-recon](game-recon/SKILL.md) | `MODDING_PLAN.md` |
| 联网学习、版本兼容、英中日教程与工具查证 | [mod-research](mod-research/SKILL.md) | 可追溯来源与适用边界 |
| UI MOD、HUD、菜单皮肤、字体与界面汉化 | [ui-mod](ui-mod/SKILL.md) | 可恢复的界面修改与交互证据 |
| 修改配置/数据/脚本/纹理/容器，保持编码与 ID | [file-mod](file-mod/SKILL.md) | staged 文件、差异与格式验证 |
| Anime cast/portraits/flags/localization for strategy games | [anime-strategy-mod](anime-strategy-mod/SKILL.md) | Versioned staging project and asset requirements |
| Inspect internals or an undocumented file format | [reverse-engineering](reverse-engineering/SKILL.md) | Findings or a proven reader/writer |
| Generate new assets specifically with fal | [fal-assets](fal-assets/SKILL.md) | Downloaded assets and provenance |
| Find official references, use GPT Image, prepare PSD/art or render frames | [asset-pipeline](asset-pipeline/SKILL.md) | Traceable references, prepared files or an editable master |
| 二次元头像、立绘、表情、Live2D/3D 资源合同 | [二次元素材抽屉](asset-pipeline/references/anime-assets.md) | 一个角色的完整资源链；配合 asset-pipeline |
| Capture/control a game or diagnose runtime behavior | [game-automation](game-automation/SKILL.md) | Runtime observations and repeatable steps |
| Combine two games' mechanics or simulations | [mashup-mods](mashup-mods/SKILL.md) | Integration design and a minimal slice |
| Make a demo/trailer/montage | [showcase-video](showcase-video/SKILL.md) | Video, edit recipe and credits |
| Package/release a mod | [publish-mod](publish-mod/SKILL.md) | Reviewable package and release draft |
| Search/write/contribute reusable modding findings | [share-field-notes](share-field-notes/SKILL.md) | Relevant notes or a validated contribution |

For toolkit development, use the checkout's `docs/development.md` instead of a game
workflow. For a small known task, a specialist is enough; load `mod-any-game` only
when coordinating multiple stages.

## Loading with different interfaces

- File-capable harness: read the linked file relative to this document.
- MCP: this index is `um://guide`. Read a skill with `manual_read` and
  `{"collection":"skills","path":"anime-strategy-mod/SKILL.md"}`. For a linked reference,
  resolve the link relative to the current document, then pass its collection-relative path.
- JSON CLI: use `um tool call manual_read --args-file read.json` with the same arguments.
- A harness needing local skill directories: `manuals_export` creates real copies;
  discover/export once, then read selected files instead of repeatedly exporting everything.

Example: from `anime-strategy-mod/SKILL.md`, `references/targets.md` resolves to
`anime-strategy-mod/references/targets.md` in the `skills` collection.
The [tool reference](references/tools.md) describes available operations and boundaries.

## 抽屉式使用

发现描述 → 一个 `SKILL.md` → 当前问题的一份 reference → 必要的网页原文。
已知任务直接进入对应抽屉，不预读全部资料。先查本地版本；首次路线/工具选择、
未知格式、版本变更和陌生错误需要联网核实。例行本地修改无需重复搜索。
来源清单分别按[引擎/文件](mod-research/references/engine-and-file-sources.md)和
[美术/UI](mod-research/references/art-and-ui-sources.md)组织，均包含多语言入口。
实际项目发现仍归 knowledge；教程原则不伪装成已运行的游戏经验。

## Scope and evidence

Respect the requested validation level. Code-only work can use fixtures; do not install
or launch a game just to follow a workflow. Record unknown versions/formats as unknown.
CK3/Victoria II currently provide scaffolds; Koei series profiles are planning only.
Prepared PNGs are not verified archive imports. Video and publication are separate tasks.
