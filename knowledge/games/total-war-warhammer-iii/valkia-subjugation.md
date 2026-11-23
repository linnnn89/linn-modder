---
kind: game
game: 'Total War: WARHAMMER III'
games_also: []
game_version: 9.0.4.0 (Warhammer3.exe), Steam build 25961564, Immortal Empires
platform: windows
engine: native
route: loader-api
status: working
date: 2026-10-20
agents:
- Claude Code (Opus 5.5)
humans: []
title: 战锤 3：复用原版抉择招降领主
tags:
- 阵营
- 招募
- 附庸
- 事件
links:
- https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/total-war-warhammer-iii/valkia-khorne-subjugation-reusing-archaon-dilemmas.md
---

# 战锤 3：复用原版抉择招降领主

上游案例中文摘要。版本、署名、日期和验证结果沿用[原作者记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/total-war-warhammer-iii/valkia-khorne-subjugation-reusing-archaon-dilemmas.md)。

## Setup

Immortal Empires 战役，瓦尔基娅和原版阿查机制涉及相应 DLC。

## Route

战役 Lua 监听胜负并复用已有抉择。把“领主进入招募池”和“对方势力成为附庸”当作两个结果核对，另为目标先被第三方消灭的情况安排后续挑战。

## Verification

作者以 Lua 替身覆盖 15 种情形，随后在新战役前两回合触发两条路径，核对招募池和外交界面。其他两个领主以及多人游戏未单独验证。

## Gotchas

1. 把附庸误当成合邦会追错脚本。先对照原版抉择的战后外交结果，再决定要继承哪个效果。
