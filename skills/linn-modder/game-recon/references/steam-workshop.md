# Steam 模组位置抽屉

只读定位已安装/下载的 mod；不启动 Steam 更新、完整性校验或重新订阅来“找文件”，这些操作可能覆盖手动改动。

1. 从用户指定游戏目录往上找到该库的 `steamapps`，在 `appmanifest_*.acf` 中匹配 `installdir`，读取 App ID 和 build ID。只读必要字段，不收集账户信息。
2. 查看同一库的 `steamapps/workshop/content/<AppID>/<PublishedFileID>/`。用目录内元数据/发布 ID、`appworkshop_<AppID>.acf` 和作者页面交叉核对，不能靠数字目录名字猜是哪款 mod。
3. 若未找到，再按 Steam 的 `libraryfolders.vdf` 列出的其他库检查对应 App ID；限制检索范围，避免扫描所有磁盘或所有游戏资产。
4. 同时区分游戏的 `Mods/MODs`、加载器插件目录、用户文档中的模组目录和编辑器工程。路径因游戏而异；本机证据优先于网页示例。
5. 确认工坊包是否还附有手动安装的补充压缩包/本体覆盖说明。文件存在只证明下载，不证明游戏启用、补丁安装或当前 build 兼容。未知时明确记录。

路径中的 `<AppID>`、`<PublishedFileID>` 必须来自当前目标的证据；`steamapps` 的上级目录由当前库位置决定。不要硬编码某款游戏的数字 ID、安装名或维护者的盘符。对外输出发现方法和相对于 Steam 库的结构；当前机器的绝对路径仅用于本次操作记录。

作者工坊页面访问可能限流。联网按[检索方法](../../mod-research/references/search-and-evidence.md)处理，不绕过限制，不从搜索摘要推断安装状态。
