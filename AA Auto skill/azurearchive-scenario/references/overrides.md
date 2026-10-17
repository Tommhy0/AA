# 自定义资源包

成品「额外自定义资源包」= 一个 zip，内含 `manifest.json` + `characters/ bgs/ bgms/ sounds/ popups/` 五个文件夹。

- **安装**：解压后把内容放进 `%LocalLow%\foxxlight\AzureArchive\data\overrides\`（**全局**，对所有工程生效）；放进 `projects\<工程同名文件夹>\` 则只对该工程生效。**装前先备份 overrides**（文档原话）。装好后**重启 AA** 生效。
- 官群下发的包常**整包 WinZip-AES 加密**（zip `compress_type=99`、flag 带加密位）：**`.NET` 的 `ZipFile`、Windows `tar` 都只能抽出 0 字节**，需用 **7-Zip** 或 **Python `pyzipper`**（`AESZipFile` + `setpassword`）。**该包历史解压码为 `0721`；其他版本以随包说明或官方文档为准**。
- manifest 键：`CharacterOverrides / VoiceOverrides / PopupOverrides / SoundOverrides / BgOverrides / BgEffectOverrides / BgSpineOverrides / BgmOverrides`。
- **`生成清单.ps1`** 是**自制**包用的工具（《电脑端使用说明.txt》讲的就是它）：把脚本丢进一个含 `characters/bgms/bgs/sounds/popups` 的文件夹里（右键"在终端中打开"→拖入脚本→回车），它扫出 `manifest.json`。角色要按 `人物名_社团名` 命名文件夹（下划线分隔，无社团名则不写），每个文件夹放 `<名>.skel`/`.atlas`/`.png`/`-avatar.png`。**别人做好的成品包不需要跑它。**
- 原记录机器在 2026-10-08 已装 `Win20241023前-20260818`（158 角色 / 665 背景 / 178 BGM / 261 音效 / 136 弹窗）；全部清单见 `额外资源包清单.md`。**实测**：该包背景 665 张里 655 张是 **jpg**——官方文档只写“PNG”，但 **AA 实际 jpg 背景也能正常显示**；包内 2 处小瑕疵：1 个角色缺 `-avatar.png`、1 个音效被引用但缺文件。旧 overrides 备份在 `E:\BaiduNetdiskDownload\AzureArchive_Win_1.0_beta\_AAwork\overrides_backup_20261008`。

## 引用与冲突

资源清单是包快照，不证明当前机器已安装。创作前确认所需包和实际 manifest；角色使用 `Identifier`，不把显示名 `Name` 或 `Nickname` 当成引用键。基础包和自定义包的标识规则分别处理。

同名资源可能在基础、全局 overrides 和工程资源中同时存在。不要仅凭目录位置推断最终优先级：优先用当前程序资源目录/查询接口的解析结果；接口不可用时列出冲突并使用唯一标识。必要时读取对应 Spine 的实际表情能力；基础包表情清单不覆盖所有自定义角色。

安装先在临时目录解压，检查 manifest 引用的文件是否存在，再备份目标目录并安装。失败保留原包，不把不完整的解压结果作为有效资源。


## 剧情 AI 语音

4.0 支持工程专属 `VoiceOverrides`，已实测 `voices/<唯一文件名>.wav` 与台词 `voice:<唯一文件名>`（不含扩展名）可由本机原生编译器收录。配音无需改全局 overrides；新副本保留已有本地资源并合并 manifest。见[AI 配音](ai-dubbing.md)，其他版本先单句验证。
