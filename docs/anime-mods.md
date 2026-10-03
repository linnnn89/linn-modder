# 二次元 Mod 工作流

第一阶段目标是让不同 agent 可以重用项目结构、角色素材和游戏约束。
脚手架及图片处理可以用模拟数据验证；游戏导入效果仍需要后续单独验证。

| Profile ID | 当前实现 | 二次元化方向 | 关键约束 |
|---|---|---|---|
| `ck3` | 项目脚手架、descriptor、UTF-8 BOM 本地化占位文件 | 图标、事件插画、人物/家族数据、剧情文本、3D 人物资产 | 主要人物肖像是 3D 流程，PNG 不能直接替代模型 |
| `victoria2` | 旧式 `.mod` 与目录脚手架 | 国家旗帜、领导人、事件图、UI、国家设定 | 本地化为分号 CSV，编码须按版本和汉化补丁确定 |
| `romance-of-the-three-kingdoms` | 规划项目与素材工作区 | 武将头像、表情/裁切变体、列传、事件图 | 必须先确定作品、PK/本体、补丁及导入方式 |
| `nobunagas-ambition` | 规划项目与素材工作区 | 武将头像、立绘、事件图、人物资料 | 创造、大志、新生不能假设共享资源格式 |

## 可执行示例

先创建一个空工作目录，再在该目录运行（PowerShell 中可使用参数文件避免 JSON 引号问题）：

```powershell
um tool call game_profiles
um tool call project_create --args-file create-project.json
```

`create-project.json`：

```json
{
  "destination": "projects/anime_ck3",
  "profile": "ck3",
  "name": "anime_ck3",
  "game_version": "填写实际版本"
}
```

产物包含 `project.json`、`ART_DIRECTION.md`、`MODLOG.md`、`assets/source`、
`assets/prepared`、`assets/manifest.json`、`references/manifest.json`、`ASSET_WORKFLOW.md`、
`assets/layers`、`assets/editable` 和对应的 `mod/` 目录。光荣系列只创建
规划和素材目录，不生成假定可用的归档文件。脚手架不覆盖已有目录。

用 `image_prepare` 将原图裁切或缩放为透明 PNG 中间素材：

```json
{
  "source": "projects/anime_ck3/assets/source/character.png",
  "output": "projects/anime_ck3/assets/prepared/character_face.png",
  "width": 256,
  "height": 256,
  "mode": "cover",
  "anchor": "top"
}
```

这里的 256×256 只是工具示例，不是任何游戏的官方规格。运行方式：
`um tool call image_prepare --args-file prepare-image.json`。

## 素材与版本管理

1. 先确定具体游戏、版本、语言、基础 Mod 和现有导入工具。
2. 优先从游戏官网、角色官网、发行商媒体包或已验证官方账号取得图片参考，记录页面 URL、原图 URL、版本和 hash；优先复用匹配的本地副本。
3. 在 `ART_DIRECTION.md` 记录画风、角色 ID、配色、服装、光照、表情和构图规则。
4. 需要生成或修改图片时，Codex 可使用可用的 GPT Image 工具；其他 harness 使用其已配置的提供方。fal 不是必需依赖。
5. 素体 PSD 由参考图与 GPT Image 生成的底图/部件，交给真实 PSD 编辑器或写入器组装。保留命名图层、透明部件和预览，保存后重新打开检查可编辑性。
6. 按角色 ID 保留源图与不同用途的裁切版本，记录出处、授权和生成参数；从实际目标版本确认尺寸、透明通道、压缩、mipmap、文件名和资源 ID。
7. 在素材清单中记录 source/output hash 和角色映射；后续由该游戏的适配器做 DDS/TGA 等转换、资源映射及安装计划。
8. 将“参考图已取得”“图片已生成”“PSD 图层已验证”“游戏格式已验证”“已在游戏中验证”分别记录。

完整按需流程见[官方参考、GPT Image 与 PSD](../skills/linn-modder/asset-pipeline/references/sourcing-and-psd.md)。
新项目会复制该流程为 `ASSET_WORKFLOW.md`，初始参考清单为空，创建项目不会自动联网、生成图片或制造 PSD。
GPT Image 接入来自 harness 的图像工具；仓库当前没有原生 GPT Image API 客户端、图片下载器或 PSD 组装器。

CK3 的 3D 人物方向需要进一步记录骨骼、blendshape、材质插槽和动画兼容性。
Victoria 2 的旗帜应覆盖目标版本要求的政治体制变体。光荣系列优先采用作品自身
支持的头像导入/编辑器；专有归档回写须有相应版本的样本和 round-trip 测试。
