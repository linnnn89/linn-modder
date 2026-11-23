---
kind: game
game: Hearts of Iron IV
game_version: 1.19.3
platform: windows
engine: clausewitz
route: data
status: in-progress
date: 2026-10-08
agents:
- Codex (gpt-6)
title: 钢铁雄心 IV：阿尔巴尼亚的最小国策树
tags:
- HOI4
- 国策树
- 国家选择
- 本地化
links:
- https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/hearts-of-iron-iv/creating-a-national-focus-for-albania.md
---

# 钢铁雄心 IV：阿尔巴尼亚的最小国策树

上游案例中文摘要。版本、署名、日期和验证结果沿用[原作者记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/hearts-of-iron-iv/creating-a-national-focus-for-albania.md)。

## Setup

上游目标为 HOI4 1.19.3。范围是新国策树和一条国策，沿用原版图标。

## Route

在 common/national_focus 定义国家评分和带唯一 ID 的国策。把“阿尔巴尼亚能选中该树”和“国策完成后获得政治点数”分别列入验收。

## Verification

上游只运行了发布检查，三个文件通过。国策选择、完成奖励及游戏错误日志仍待新战役验证。

## Gotchas

1. 若界面显示国策 ID，先查与该 ID 对应的名称和描述键。上游将此列为据 Wiki 整理的排查线索。
