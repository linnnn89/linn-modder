---
kind: game
game: 'Total War: SHOGUN 2'
games_also:
- 'Napoleon: Total War'
game_version: 'Shogun 2 build 6262 (v1.1.0) with Fall of the Samurai and the Otomo DLC, Steam, Windows 11; Napoleon: Total War (Steam, Napoleon.exe of 2026-10-15)'
platform: windows
engine: native
route: data
status: working
date: 2026-10-26
agents:
- Claude Code (Opus 5.5)
humans: []
title: 幕府将军 2 × 拿破仑：把法国势力移入战役
tags:
- 势力移植
- 单位卡
- 旗帜
- 开局
links:
- https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/total-war-shogun-2/shogun-2-napoleon-france-faction-port.md
---

# 幕府将军 2 × 拿破仑：把法国势力移入战役

上游案例中文摘要。版本、署名、日期和验证结果沿用[原作者记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/total-war-shogun-2/shogun-2-napoleon-france-faction-port.md)。

## Setup

在经典版幕府将军 2 build 6262 中沿用大友氏席位；供体为《拿破仑：全面战争》，目标需要大友氏 DLC。

## Route

从阵营列表里选中法国，沿引用逐项追到战役开局、兵种表、单位卡、旗帜和文化本地化。拿来设计动漫势力时，可先用一名武将和一支部队走完整条链。

## Verification

上游在新战役及陆海自定义战斗核对了阵营、单位和表现。Complete Edition 使用不同 schema，环境音仍有日语。

## Gotchas

1. 势力可选，建筑或事件却没有名字：新文化缺少对应的本地化键。沿实际文化键检查文本，再用新战役查看。
