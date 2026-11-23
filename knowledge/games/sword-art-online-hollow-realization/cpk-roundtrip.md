---
kind: game
game: 'Sword Art Online: Hollow Realization Deluxe Edition'
games_also: []
game_version: Steam app 607890, sao_hr.exe PE timestamp 0x59DF33EF, SizeOfImage 0x10A2000, SHA-256 1923F0D8D2CAD559D6AD6E001AF54EA5EA5AA70171323F42D4E1FA3D63699E43;
  Windows 11 Pro 26100
platform: windows
engine: native
route: data
status: working
date: 2026-11-10
agents:
- Claude Code (Opus 5.5)
humans:
- BinaryNull
title: 刀剑神域：虚空幻界的大型 CPK 修改与回退
tags:
- SAO
- 封包
- 回封
- 经验值
- 卸载
links:
- https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/sword-art-online-hollow-realization/zero-exp-patcher-cri-cpk-append.md
---

# 刀剑神域：虚空幻界的大型 CPK 修改与回退

上游案例中文摘要。版本、署名、日期和验证结果沿用[原作者记录](https://github.com/rehan-remade/universal-modder/blob/a34eae75732d7fd5e7810abde188063e72829525/knowledge/games/sword-art-online-hollow-realization/zero-exp-patcher-cri-cpk-append.md)。

## Setup

Windows Steam Deluxe Edition（App 607890）。案例目标为原装约 37 GB 的 data.cpk。

## Route

针对用户自己安装的封包，只修改选项涉及的数据条目。选一个变更，回读目录项指向的内容，再测试卸载后的文件哈希。同一 CPK 配合两个补丁时，还要记录卸载顺序。

## Verification

上游分别实测击杀、任务、决斗与伙伴经验值；在副本上核对安装及卸载，包含与另一补丁交叉卸载的两种顺序。

## Gotchas

1. 输出文件已变但任务奖励仍然相同：案例中的任务表经过压缩。先回读实际目录项和解压后的记录，再决定怎样写回。
