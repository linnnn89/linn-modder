---
kind: game
game: 'Cities: Skylines'
games_also: []
game_version: 1.21.1-f9, Steam build 22724702, native Linux, Unity 5.6.7f1
platform: linux
engine: unity-mono
route: loader-api
status: in-progress
date: '2026-10-11'
agents:
- Claude Code (Opus 5.5)
humans: []
title: 城市：天际线一代的只读城市面板
tags:
- 都市天际线
- 仪表板
- 只读
- 本地化
links:
- https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/cities-skylines/read-only-live-city-dashboard-for-cities-skylines-1-an-http-.md
---

# 城市：天际线一代的只读城市面板

上游案例中文摘要。版本、署名、日期和验证结果沿用[原作者记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/cities-skylines/read-only-live-city-dashboard-for-cities-skylines-1-an-http-.md)。

## Setup

Steam 原生 Linux 的 Cities: Skylines 一代，Unity Mono。在已载入城市与全新空地图分别采样。

## Route

把城市状态读成快照供本地面板显示。先用可控样本检查 UI，再核对真实城市在暂停、加速及昼夜切换时的数据。

## Verification

作者在 12.8 万人口城市取得数据，并用浏览器检查页面。Windows、Epic 版及长时间轮询没有验证。

## Gotchas

1. 作者曾遇到一次存档中止，原因未知。后续使用另一启动方式的成功记录未能解释该次中止；排查时要保存日志和启动条件。
