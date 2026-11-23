---
kind: game
game: Fantasy Maiden Wars Dream of the Stray Dreamer
games_also:
- Fantasy Maiden Wars DoSD
- 幻想少女大戦
game_version: Steam 3575980, build 25976175, fmw_dosd.exe 1.1.0.0 (x64), as of 2026-11-09
platform: windows
engine: gamemaker
route: managed-patch
status: in-progress
date: '2026-11-15'
agents:
- Claude Code (Opus 5.5)
humans:
- SophiaUrabe
title: 幻想少女大战：可复现的随机阵容
tags:
- SRPG
- 二次元
- 种子
- 随机开局
- 阵容
links:
- https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/fantasy-maiden-wars-dream-of-the-stray-dreamer/randomizer-mode-gml-via-undertalemodtool-cli-run-with-game-s.md
---

# 幻想少女大战：可复现的随机阵容

上游案例中文摘要。版本、署名、日期和验证结果沿用[原作者记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/fantasy-maiden-wars-dream-of-the-stray-dreamer/randomizer-mode-gml-via-undertalemodtool-cli-run-with-game-s.md)。

## Setup

Steam build 25976175，GameMaker 游戏。上游对 data.win 副本导入脚本，并用游戏的 -game 选项加载副本。

## Route

用存档保存的种子确定角色映射，同时按章节调整对手。排查卡关时记录种子、章节、实际人物、剧情要求人物和对话头像，便于在同一局复查。

## Verification

上游通过实际游玩、读档、日志和截图确认阵容重排、对话画像及第三章卡关修复。角色真正永久死亡和部分后期修复尚待验证。

## Gotchas

1. 同一种子的随机结果涉及剧情角色时，单看队伍列表不足以判断关卡可完成。回到出错的快速存档，核对剧情触发以及胜败判定各自读取的角色。
