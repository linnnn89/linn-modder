---
kind: game
game: Outer Wilds
games_also:
- Portal 2
game_version: 1.1.16.1372 (Steam 753640, buildid 20230391), Unity 2019.4.39f1 Mono, Echoes of the Eye installed
platform: windows
engine: unity-mono
route: loader-api
status: working
date: '2026-10-10'
agents:
- Claude Code (Opus 5.5)
humans:
- charlystereo
title: 星际拓荒 × 传送门 2：跨游戏素材、移动与循环重置
tags:
- Outer Wilds
- Portal 2
- 星际拓荒
- 素材转换
- 循环
links:
- https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/outer-wilds/portal-2-portal-gun-in-outer-wilds-1-1-16-owml-see-through-p.md
---

# 星际拓荒 × 传送门 2：跨游戏素材、移动与循环重置

上游案例中文摘要。版本、署名、日期和验证结果沿用[原作者记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/outer-wilds/portal-2-portal-gun-in-outer-wilds-1-1-16-owml-see-through-p.md)。

## Setup

Outer Wilds 1.1.16.1372，Windows Steam、OWML 2.16.3，供体为用户安装的 Portal 2。

## Route

从本机供体转换模型、材质和音频，在宿主内建立可以随天体移动的传送门。分别核对视觉效果、玩家或飞船穿越时的速度，以及循环重置后的对象清理。

## Verification

上游有实机截图及速度轨迹，并检查了飞船和侦察器。Epic 版、手柄按钮及其他屏幕尺寸均未验证。

## Gotchas

1. 从标题画面直接跳进场景会缺少档案初始化。验证循环时从正常档案流程进入，再观察穿越及重置。
