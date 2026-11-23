---
kind: technique
title: "按制作问题查找上游的 11 个游戏示例工程"
date: 2026-11-23
agents: [Codex]
tags: [examples, 示例工程, 案例, 参考游戏, 跨游戏, 上游]
links: [https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples]
---

# 上游游戏示例工程

当项目只有制作目标、还没选技术路线时，先按问题选一行。下列链接固定在同一上游版本。运行平台与验证结果以各作者的 README 为准。

## 势力、美术与数据 Mod

| 制作问题 | 示例及适用范围 |
|---|---|
| 如何给新势力配特殊单位、图像、科技和建筑？ | [帝国时代 II：决定版 / Age of Empires II DE](../games/age-of-empires-ii-de/san-franciscans-civ.md)。San Franciscans 复用一个文明席位，涵盖从 3D 到游戏精灵的流程。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/aoe2-de-civ) |
| 如何把一套美术接入敌人、物品和首领？ | [泰拉瑞亚 / Terraria](../games/terraria/fal-arsenal-tmodloader.md)。通过 tModLoader 注册内容，按游戏动画布局切精灵帧。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/terraria-tmodloader) |
| 如何比较两个游戏参数对同一场景的影响？ | Mindustry 160.7 使用固定场景、脚本目标和事件计数，比较两组游戏内参数；上游测试平台是 macOS。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/mindustry-homing) |
| 如何把模拟数据展示成独立 UI？ | [城市：天际线 / Cities: Skylines](../games/cities-skylines/read-only-city-dashboard.md)。一代的只读城市面板用真实城市与模拟数据分别核对数据采样和显示。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/cities-skylines-city-dashboard) |

## 跨游戏素材、场景与状态

| 制作问题 | 示例及适用范围 |
|---|---|
| 画面合成后，怎样检查交互是否也生效？ | [Minecraft × GTA V](../games/gta-v/minecraft-passthrough.md)。在故事模式中分别验证相机、遮挡和放置方块后的碰撞。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/minecraft-gta5-passthrough) |
| 两个游戏对同一画面的视角不一致，先查哪里？ | Minecraft × 星际拓荒（Outer Wilds）把相机交给宿主，用有色地标和多组视角核对坐标变换。上游记录的是 Linux / Proton 的初步实现。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/minecraft-outerwilds-passthrough) |
| 如何转换供体素材，同时保留宿主的移动与循环行为？ | [Portal 2 × Outer Wilds](../games/outer-wilds/portal-assets-and-loop.md)。材质、音效与模型从用户本机读取，再分别验证移动参考系和循环重置。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/outer-wilds-portal-gun) |
| 在叙事游戏里切换沙盒，怎样回到原剧情？ | The Wolf Among Us × Garry’s Mod：记录暂停时的剧情位置和角色，检测退出后的场景恢复。作者按子系统标记验证进度。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/twau-gmod-sandbox) |

## 旧作兼容与持久化

| 制作问题 | 示例及适用范围 |
|---|---|
| 菜单能打开，关卡切换或读取检查点时仍会崩溃？ | Collapse（2008）的 collapsefix 区分冷启动、读档和长战役，适合参考其兼容性验收场景。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/collapse-collapsefix) |
| 怎样描述只影响某个发行版的显示问题？ | 地铁 2033 / Metro 2033（2010 原版）区分启动、全屏、刷新率与前台焦点，并记录对应游戏版本。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/metro2033-m2033fix) |
| 本地角色库怎样验收一名角色的完整生命周期？ | 中土世界：战争之影 / Middle-earth: Shadow of War 的本地驻军示例涵盖存入、列出、查看详情和重新部署。[示例工程](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/examples/shadow-of-war-offline-mode) |

其他游戏可按名称查同一版本的[上游游戏笔记目录](https://github.com/rehan-remade/universal-modder/tree/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games)。
