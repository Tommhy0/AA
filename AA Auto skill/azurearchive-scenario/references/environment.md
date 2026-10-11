# 环境发现和资源排障

不要从聊天客户端名称推断 MSIX 重定向。先发现实际程序、数据根、缓存和 Addressables catalog，再执行写入或启动。

- Windows 常见程序位置是用户选定的 AzureArchive 目录；原记录位置为 `E:\BaiduNetdiskDownload\AzureArchive_Win_1.0_beta\AzureArchive.exe`，这是本机候选，不是通用路径。
- 常见 LocalLow 根为 `<用户目录>\AppData\LocalLow`。打包应用可能有 `<LocalAppData>\Packages\<包名>\LocalCache\LocalLow`。只检查确实存在的候选；可从 `user_settings.json` 的 workspacePath/cachePath 查找用户自定义位置。
- 数据一般在 `foxxlight\AzureArchive\data`，工程在 projects，成品在 saves；Addressables catalog 一般位于数据根同级 `com.unity.addressables`。
- 缓存一般在 `Unity\foxxlight_AzureArchive`。文件是哈希名，可能无 `.bundle` 后缀，不能用扫描 `*.bundle` 判断安装情况。目录存在也不能证明完整。
- 原 Claude 桌面版记录使用 `Claude_pzs8sxrjxfjjc` 的包目录；这不是 Codex 实测。Codex、Claude Code、VSCode、外部终端分别探测，不机械替换产品名。

`scripts/aa_tool.py discover` 列出候选路径与非空 catalog/cache 状态，`--data-root` 或 `--exe` 可明确覆盖。候选有歧义时检查用户设置和最近运行日志，不能静默选择有资源的旧根作为当前程序数据根。

官方基础资源包可解压到 data/manual_install，程序启动后安装并清空该目录。原记录包为 `WIN_202412150051.zip`；大小、文件数、catalog 文件名和版本号都只是该包快照。

遇到 AddrLoadUrl 404，检查同一运行环境可见的 catalog 和缓存。`completeResStructVer:0` 在原实测中是读缓存失败后的结果；修改版本号不能修复缓存。若缓存只存在另一根，确认来源、目标与磁盘空间后复制，或使用明确记录目标的目录联接；不要递归删除链接指向的数据。

如必须验证重定向，使用随机唯一文件名和内容，在两根比较实际文件内容/链接属性，结束后只清理本次探针。不能用残留的固定 `__probe.txt` 判断。

成功证据：本次运行日志没有相关资源 404，资源版本初始化成功，设置没有被回写成失败状态。避免把整个历史日志中的 404 算作本次故障。旧双击修复脚本只适用于它注明的 Claude 缓存布局，不能替代环境探测。

编码：AAP2 使用 UTF-8 无 BOM，文件头使用 LF。不同 PowerShell 版本的脚本编码默认值不同；显式读写 UTF-8，必要时用 Python，不能把所有乱码都当成正常现象。
