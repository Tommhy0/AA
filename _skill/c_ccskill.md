---
name: azurearchive-scenario
version: "1.6"
description: 用 AzureArchive 创作/修改《蔚蓝档案》剧情——手写 .aap2 工程 JSON（立绘、表情、背景、BGM、弹窗、人物动作、场景过渡、分支、旁白），再编译播放验收。当用户提到 AzureArchive、.aap2/.aas、剧情编辑器/剧情工程，或要查动作/过渡/表情/BGM/弹窗/角色名对照、或安装额外自定义资源包(overrides)时使用。
---

# AzureArchive 剧情创作（手写 .aap2）

AzureArchive 是《蔚蓝档案》的非官方剧情编辑器（狐光体）。其工程文件 `.aap2` 是**纯 JSON**——**手写文件**远比驱动它那套 Unity 节点编辑器可靠（后者对合成鼠标事件挑食、按钮常点不动）。

## 0. 本机坐标（其他机器请按实际替换）

| 项 | 值 |
|---|---|
| 程序 | `E:\BaiduNetdiskDownload\AzureArchive_Win_1.0_beta\AzureArchive.exe` |
| 数据目录 | `C:\Users\<用户>\AppData\LocalLow\foxxlight\AzureArchive\data` |
| 工程 | `…\data\projects\<名>.aap2`（UTF-8 **无 BOM**） |
| 编译产物 | `…\data\saves\<名>.aas`（+ `.build.json`） |
| 资源缓存 | `C:\Users\<用户>\AppData\LocalLow\Unity\foxxlight_AzureArchive`（约 6.2 GB；缓存文件是**哈希名、无 `.bundle` 后缀**，如 `0509bdee…/7dc36556…`，别按 `*.bundle` 扫——否则会误判成"没装"） |
| ⚠ 两个 LocalLow 根 | 从 **Claude 桌面版**启动的进程，`LocalLow` 被 MSIX 重定向到 `…\AppData\Local\Packages\Claude_*\LocalCache\LocalLow\`；从资源管理器/Git Bash 启动则看真正的 `…\AppData\LocalLow\`。**同一台机器两个根**，缓存与游戏数据可能各在一侧——见 §1 |
| 本技能附带资料 | 与本 SKILL.md 同级的 `references/`、`examples/`（见 §8） |

**最快闭环**：读现有工程 → 写 `.aap2` → 请用户**项目模式 → 选中 → 编辑**（打开即自动保存+编译）→ 切**鉴赏模式**播放验收。

**注意**：打开工程前目录里**不能残留同名 `.aap`(v1) 或旧 `saves\<名>.*`**，否则软件可能读旧版。稳妥做法：写完 `.aap2` 后删掉同名 `.aap` 与 `saves\<名>.*`，再让用户重启软件。

## 1. 离线装资源 / 修"无法加载资源"

**装**：官方资源包 zip 解压到 `data\manual_install\`，启动即自动安装（文件夹随后清空）。`WIN_202412150051.zip`（6.08 GB）是 Windows 基础资源包。

**修**：症状是界面报"无法检测到资源"，`Player.log` 刷满
`file:///…/ScenarioResourceManager.AddrLoadUrl/{texts,flatdata,databases}_assets_all.bundle` 404。

**先搞清一点：`completeResStructVer: 0` 是结果，不是原因。** 程序读不到缓存时才把它写成 0；只改回 `11` 能按住症状到下一次启动，回来照样 404。**别把它当解法。**（2026-10-08 实测：同一次会话 18:44 失败 → 47 个 404 且写 0；修好缓存后 18:47 成功 → 0 个 404 且 11 保持不变。）

真正要查的是**程序需要两样东西，是否都在它启动时看得到的那个 LocalLow 根里**：

| 需要 | 位置（相对当前 LocalLow 根） |
|---|---|
| Addressables 目录 `catalog_2024.08.17.15.07.45.json`（24 MB） | `foxxlight\AzureArchive\com.unity.addressables\` |
| 资源缓存 6.2 GB / 13,309 个哈希名条目 | `Unity\foxxlight_AzureArchive\` |

诊断（**两个根都要量**，别用一个根的结论否定另一个）：
```powershell
# 容器根（Claude 桌面版启动时看到的）
Test-Path 'C:\Users\ASUS\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\LocalLow\Unity\foxxlight_AzureArchive'
# 普通根（资源管理器 / Git Bash 启动时看到的）
Test-Path 'C:\Users\ASUS\AppData\LocalLow\Unity\foxxlight_AzureArchive'
```
缓存若只在容器根里，普通根启动就必然 404。**把缓存弄到普通根**（二选一）：

```powershell
# A) 复制（持久，推荐；占 6.2 GB）——用 robocopy，13k 个小文件
robocopy '<容器根>\Unity\foxxlight_AzureArchive' 'C:\Users\ASUS\AppData\LocalLow\Unity\foxxlight_AzureArchive' /E /MT:16
# B) 目录联接（瞬时、0 额外磁盘；缺点：Windows 重置 Claude 包会变断链）
New-Item -ItemType Directory 'C:\Users\ASUS\AppData\LocalLow\Unity' -Force   # 父目录要先建
cmd /c mklink /J "C:\Users\ASUS\AppData\LocalLow\Unity\foxxlight_AzureArchive" "<容器根>\Unity\foxxlight_AzureArchive"
```
- **删联接只能用 `cmd /c rmdir` 或 `[System.IO.Directory]::Delete(p,$false)`**；PowerShell 的 `Remove-Item -Recurse` 会**跟进目标把容器里的真数据删掉**。
- **⚠ 「Claude 侧能不能修」取决于你有没有被 MSIX 重定向——先测，别照抄结论。** 判据（10 秒）：往 `C:\Users\ASUS\AppData\LocalLow\__probe.txt` 写个文件，再看 `…\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\LocalLow\__probe.txt` 有没有也冒出来——**容器里也出现＝你被重定向了**。
  - 2026-10-08 实测：**Claude Code（VSCode 扩展）的 Bash、windows-mcp 的 PowerShell 都没被重定向**，写普通根就真落在普通根，上面那行 robocopy 在 Claude 侧直接生效（副本 26,617 文件 / 6.21 GB，属性是真实 `Directory` 而非 `ReparsePoint`）。
  - **被重定向的是 Claude 桌面版的打包 agent 会话**（其 shell 写普通根会落进容器，同一标记文件在两个路径都可见）。只有那种环境才修不了 → 把 `AA_KIT\修复资源缓存_双击运行.cmd` 交给用户双击（内部就是上面那行 robocopy，会先报告两个根各自在不在）。
- 验证：启动后日志 404 = 0、`Resource structure version: 11`，且 `completeResStructVer` **保持 11 不被写回 0**。最后一条才是真的好了。
- `--cli` 启动**不输出任何结果**（详见 §6.7），别拿它验证。

## 2. `.aap2` 结构

首行必须是 `AAP2` + **单个 LF(0x0A)**（写 CRLF 会报 `Unsupported AAP file marker`）；其后是 JSON（行内换行用 CRLF 无妨）。

```json
{ "LegacySourceVersion":"absent", "FormatVersion":2,
  "ProjectId":"<guid>", "ProjectName":"...",
  "PreviewBgName":<uint 背景哈希>, "PreviewHeader":"...", "PreviewTitle":"...",
  "nodes":[ ... ] }
```

节点 `Kind`：
- `entry`  `{Title,Header,Guid:"00000000-0000-0000-0000-000000000000",ConnectionsTo:[<guid>],X,Y,Kind:"entry"}`
- `dialogue`  `{Scripts:[ScriptData],NodeName:null,Guid,ConnectionsTo:[...],X,Y,Kind:"dialogue"}`
- `choice`  `{Options:[{OptionId,Text,TargetNodeId}],DefaultOptionId:null,UnusedSelectionTexts:[],Guid,X,Y,Kind:"choice"}`（**无 ConnectionsTo**，出口=各选项的 TargetNodeId；两选项指向同一节点＝“选项不同但剧情相同”）
- `exit`  `{IsEnding,EndText,NeHeader,NeTitle,NeScriptDirty:<ScriptData>,Guid,ConnectionsTo:[],X,Y,Kind:"exit"}`（`IsEnding:true`=结局，false=未完待续）

`ScriptData` 字段：
`LineId`(guid)、`text`、`popup`(str)、`bgEffect`(uint)、`bgName`(uint 背景哈希)、`bgFriendlyName`(str)、`sound`(str)、`voice`(str)、`transition`(uint)、`bgmId`(int)、`selectionGroup`(uint)、`additionalPrompt`(str)、`characters`(**恰好 6 项**)、`speakerSlotNum`(int)、`highlightedSlotNums`(int[])、`isDialogScript`(bool)、`placeText`(str)

`CharacterRecordData`（每栏位）：
`{name,faceId:"00",startingPos,endingPos,displayOrder:1,emoticon:-1,action:0,effect:0,appear:0,shapeOverride:0}`
- 空栏位：`name:""`、start/end=0。
- 有人栏位：**数组下标 = 当前栏号 = `startingPos`**；不动就 `endingPos` 相同；`speakerSlotNum`=发言者栏号。
- 旁白：`isDialogScript:false` 且 speaker 指向空栏（0）。

**硬规则**：`characters` 必须**恰好 6 项**（栏 0..5）；栏 0 是旁白/老师位，角色一般放 1..5；**两人同台用 3 号位 + 5 号位**（不相邻不重叠）。

## 3. 资源名 → 哈希

资源引用 `bgName` = **`xxHash32(名字, seed=0)`**（对 UTF-8 字节）。
已知：`BG_MainOffice`=1046815759、`BG_MainOffice_Night`=3289055107、`BG_Black`=1047754314（默认预览）、`BG_ClassRoom`=1738686580、`BG_Library`=3976053942、`BG_BeachFrontSide_Sunset`=3332100768。
`popup`/`sound`/`voice` 是**字符串名**（不是哈希）。
（Python 参考实现见 `references/xxhash32.py`。）

## 4. 四张对照表

**过渡 `transition`**（时长不可逐句改，打包在预设里）：

| id | 效果 |
|---|---|
| 1408872282 | 交叉渐变 500ms（**只用于白天↔黑夜**这类同场景明暗变化） |
| 3854440696 | 黑色淡入淡出 250ms |
| 3868567233 | 白色淡入淡出 250ms |
| 3957412172 | 向左滑动 |
| 1127535352 | 向右滑动 |
| 4152299906 | 向上滑动 |
| 3029168926 | 向下滑动 |
| 3344317924 | 黑色方格 |
| 1914875660 | 黑色圆形 |

**角色名 `characters[].name`**：**韩文原名**（如 `시로코 부상`/`호시노`），完整 1467 个见 `references/角色名清单.md`。

**表情 `faceId`**：两位编号字符串（`"00"`..`"17"`）。**每个角色的可用编号不同**（白子/茜香 7 个；星野 17 个）。常见 `01`=平静、`02`=惊讶、`03`=微笑、`04`=害羞、`05`=严肃、`06`=大喊或低落（**因角色而异**）；`00` 默认。逐角色表见 `references/人物表情对照表.md`。

**人物动作 `action`**：`1`=微微蹲一下(拿东西常用)；`2`=向左倒下；`3`=向右倒下；`4`=微微抖动；`5`=剧烈抖动；`6`=跳一下；`7`=跳两下。（倒下后若下一句不移除该角色，会自行站起。）

**外形 `shapeOverride`**：`1`=通话中(电话对面的电子形象)；`2`=阴影中(整个人黑色)；`4`=靠近(立绘放大)。

**出场/退场动画 `appear`**（= `AppearType` 枚举；字母指**滑动方向**：`L`=向左滑、`R`=向右滑。已由 `BepInEx/interop/Assembly-CSharp.dll` 反查枚举名 + 实测确认）：`0`=None（无/原地不动）；`1`=**AL**（从**右**滑入 ⇒ 观感“从右侧出现”）；`2`=**AR**（从**左**滑入 ⇒ 观感“从左侧出现”）；`3`=**A**（原地出现）；`4`=**DL**（向**左**滑出）；`5`=**DR**（向**右**滑出）；`6`=**D**（原地消失）。**默认规则：角色从与自己所在屏幕同一侧的那一边滑入**（站画面右→`1`，站画面左→`2`；中间用 `3`），仅剧情需要时才反向；退场同理（右→`5`，左→`4`，中间 `6`）。⚠ 旧表把 `2` 写作“从左进入”、`4` 写作“从右进入”是**错的**——`AL/AR` 指的是**滑动方向**，且 `4/5/6` 是**消失**类（把 `4` 当入场用，角色会冲出去消失）。

**语气气泡 `emoticon`**（**已定稿**，20 个编号经用户逐格实测 + 5 个样本交叉验证）：`-1`=空/无 ｜ `0`=Angry(红爆炸·生气) ｜ `1`=Chat(蓝涂鸦·闲聊) ｜ `2`=Dot(⋯·省略) ｜ `3`=Exclaim(！·惊叹) ｜ `4`=Heart(❤·爱心) ｜ `5`=Music(♪·哼歌) ｜ `6`=Question(?·疑问) ｜ `7`=Respond(黄)·回应) ｜ `8`=Shy(红///·害羞) ｜ `9`=Surprise(橙⁉·吃惊) ｜ `10`=Sweat(蓝水滴·汗) ｜ `11`=Twinkle(✦·闪亮) ｜ `12`=Upset(灰乱线团·烦躁) ｜ `13`=Think(白气泡·思考) ｜ `14`=Bulb(黄圈点·灵光) ｜ `15`=Sad(紫雨线·难过) ｜ `16`=Sigh(白云·叹气) ｜ `17`=Steam(灰漩涡·冒烟) ｜ `18`=Tear(蓝水滴大·泪) ｜ `19`=Zzz(zzz·睡觉)。（气泡**无独立图片资源**，取不到图。）

**其它**：`bgmId` `999`=静音。

**BGM**：共 242 首，`bgmId` = 曲号（即 `theme_NN` 的 NN）。曲名/作者/建议用途见 `references/BGM用途注释清单.md`。**换曲要克制**：不要频繁切歌——只在**场景/情绪真正转折处**换（大体“一场景一曲”），同一首至少撑若干句；换得太快会让人工复核（试听）很吃力（用户 2026-10-08 交代）。
**弹窗图**：`Event01_<角色名>`（角色 CG）+ `popup02..popup221`（通用图）。注释见 `references/弹窗图注释清单.md`。
**音效**：`sound` 填**字符串名**（不带路径/后缀，如 `"SE_DoorOpen_01"`）。完整清单见 `references/音效名清单.md`（697 个，含 `SE_DoorOpen_01`/`SE_Knock_Soft_01` 等）。
**额外指令**（写进 `text` 字段，可多行，前缀 `#`；用于界面做不到的事）：`#wait;毫秒`（无对话的脚本等待后再推进）；`#bgshake`（背景抖动一次）；`#fx;AronaTouch`（特殊效果，目前仅序章的指纹识别）；`#zmc;模式;X,Y;缩放;持续ms`（背景平移/缩放；模式 `instant`=瞬时 / `smooth`=平滑）；`#st;[X,Y];模式;字号;` 与 `#stm;[X,Y];模式;字号;`（屏幕文字，分别左对齐/居中；模式 `instant`/`smooth`/`serial`；**末尾分号不可省**）；`#clearST`（清除屏幕文字——它不会自动消失）；`#<栏位号>;fx;shot`（指定栏位角色中弹特效，如 `#3;fx;shot`）；`#hidemenu` / `#showmenu`（隐藏 / 恢复右上角菜单）。屏幕中心为原点、宽固定 2960 单位。
**对话文字富文本**：`[size=字号]文本[/size]`、`[RRGGBBAA]文本[-]`（颜色，如 `[FF0000]红[-]`）、`[ruby=注音]文本[/ruby]`；可嵌套（如 `[size=200][FF0000]x[/size][-]`）。
**栏位 = 屏幕位置**：`#1`=左、`#2`=中偏左、`#3`=中、`#4`=中偏右、`#5`=右；`#0`=发言者/旁白位。位置属性可让已上场角色移动到别的栏位初始位置（但栏位不变）。

## 5. 校验规则（会被拦）

- `Speaker must reference an occupied stage slot.` —— 发言栏必须有人；旁白把 speaker 指到空栏。
- `Highlighted slots must be occupied slots.`
- `Each authoring line must have a unique LineId.`
- `Exit kind must be ending or continued.`
- 类型不符会报 `Error converting value ... to type '<类型>'. Path '...'`——`Path` 精确指出字段与期望类型，照它改。

## 6. 坑（务必遵守）

1. 首行 `AAP2` 后必须是**单个 LF**，不能 CRLF。
2. **`bgName:0` / `bgmId:0` 是“清空”不是“沿用”** → **每一句都要重写当前背景哈希与 bgmId**，否则从第 2 句起背景/音乐消失变黑。`transition` 只在真正换景那句写，其它写 0。
3. **人物跨句“走位”（用 `endingPos` 换栏）会让工程校验失败**（只报通用 `failed validation`）→ 稳妥做法是每句保持固定栏位。
4. GUID 必须是合法十六进制 GUID（含非 hex 字符会报 `Error converting value ... to type 'System.Guid'`）。
5. 打开前清掉同名 `.aap`(v1) 与旧 `saves\<名>.*`。
6. 中文一律 **UTF-8 无 BOM**；**PowerShell 会把 `.ps1` 当 ANSI 读**，中文文本要放单独的 UTF-8 文件再读入（`Get-Content -Encoding UTF8`）。控制台显示中文会乱码，属正常。
7. 本 beta 版 `AzureArchive.exe --cli ...` 不输出结果；编辑器右下角 MCP 服务常因端口占用起不来。→ **手写文件 + 人工点“编辑/播放”** 是可靠路径。脚本(SetCursorPos/mouse_event)驱动该 UI 不可靠，别依赖。**另：任何一次启动（含 `--cli`）只要当时看不到资源缓存，就会刷满 404 并把 `completeResStructVer` 写成 0——所以拿 `--cli` 去“验证”等于自己制造故障（2026-10-08 踩过）。**
8. 写 JSON 建议：先用脚本/程序拼装（避免手写 6 栏位数组出错），写完用 JSON 解析器自检，再校验首行是 `41 41 50 32 0a`。
9. **BGM 别频繁换**：只在场景/情绪真正转折处换曲，同一首至少持续若干句（大体“一场景一曲”）。频繁变来变去会让人工复核（试听）很吃力。

## 7. 交付

报告实际工程路径、编译产物 `saves\<名>.aas`、关键改动与未完成项；提醒用户**播放验收**（编译成功 ≠ 已看过效果）。

## 8. 参考文件（与本文件同级）

```
references/人物表情对照表.md      401 个角色的 faceId→表情（含 133 个无表情角色清单）
references/角色名清单.md            1467 个角色/NPC 的**韩文原名**（characters[].name 用；带 부상/테러 等变体后缀）
references/BGM用途注释清单.md     242 首 bgmId→曲名/作者/建议用途
references/弹窗图注释清单.md       203 张无名弹窗图（popup02..popup221）的画面注释
references/bgm_table.tsv          BGM 原始表（曲号/曲名/作者）
references/xxhash32.py            xxHash32(seed=0) 参考实现，用于算 bgName
references/音效名清单.md            697 个音效名（sound 字段用）
references/额外资源包清单.md       额外自定义资源包(Win20241023前)的角色/背景/BGM/音效/弹窗清单
examples/Schale_Demo.aap2         完整示例工程（3 角色/4 背景/弹窗/音效/气泡/动作/分支/旁白）
```


## 9. 额外自定义资源包（overrides）

成品「额外自定义资源包」= 一个 zip，内含 `manifest.json` + `characters/ bgs/ bgms/ sounds/ popups/` 五个文件夹。

- **安装**：解压后把内容放进 `%LocalLow%\foxxlight\AzureArchive\data\overrides\`（**全局**，对所有工程生效）；放进 `projects\<工程同名文件夹>\` 则只对该工程生效。**装前先备份 overrides**（文档原话）。装好后**重启 AA** 生效。
- 官群下发的包常**整包 WinZip-AES 加密**（zip `compress_type=99`、flag 带加密位）：**`.NET` 的 `ZipFile`、Windows `tar` 都只能抽出 0 字节**，需用 **7-Zip** 或 **Python `pyzipper`**（`AESZipFile` + `setpassword`）。**解压码见官方文档 installation 页，当前为 `0721`**。
- manifest 键：`CharacterOverrides / VoiceOverrides / PopupOverrides / SoundOverrides / BgOverrides / BgEffectOverrides / BgSpineOverrides / BgmOverrides`。
- **`生成清单.ps1`** 是**自制**包用的工具（《电脑端使用说明.txt》讲的就是它）：把脚本丢进一个含 `characters/bgms/bgs/sounds/popups` 的文件夹里（右键"在终端中打开"→拖入脚本→回车），它扫出 `manifest.json`。角色要按 `人物名_社团名` 命名文件夹（下划线分隔，无社团名则不写），每个文件夹放 `<名>.skel`/`.atlas`/`.png`/`-avatar.png`。**别人做好的成品包不需要跑它。**
- 本机已装 `Win20241023前-20260818`（158 角色 / 665 背景 / 178 BGM / 261 音效 / 136 弹窗）；全部清单见 `references/额外资源包清单.md`。旧 overrides 备份在 `E:\BaiduNetdiskDownload\AzureArchive_Win_1.0_beta\_AAwork\overrides_backup_20261008`。

## 10. 更新日志

本技能自本期起纳入版本管理；`version:` 在 `SKILL.md` 头部 frontmatter。**当前版本 1.6。** 时间为本地时区 UTC+8。

- **1.2** — 2026-10-08 19:46:51（本会话开启时）—— **基线**版本（事后追认的起始号）。当时 `appear` 对照表有误（误作“2=从左进入 / 4=从右进入”）、尚无 BGM 换曲规则、缺“额外指令”。
- **1.3** — 2026-10-08 20:05:07 —— **修正 `appear`（出场/退场）**：取值为 `0=None / 1=AL / 2=AR / 3=A / 4=DL / 5=DR / 6=D`，字母指**滑动方向**（`L`=向左滑、`R`=向右滑）；由此默认**同侧入场**——站画面**右**侧用 `1`、**左**侧用 `2`、中间用 `3`，退场右 `5`/左 `4`/中 `6`；仅剧情需要才反向。
- **1.4** — 2026-10-08 20:09:39 —— **BGM 换曲要克制**（§4 BGM 行 + §6 第 9 条）：只在场景/情绪真正转折处换曲，同一首至少撑若干句；换太快会让人工试听复核很吃力。
- **1.5** — 2026-10-08 20:12:53 —— **补齐“额外指令 / 对话富文本 / 栏位→屏幕位置”**（§4）：`#wait`/`#bgshake`/`#fx`/`#zmc`/`#st`/`#stm`/`#clearST`/`#<栏位号>;fx;shot`/`#hidemenu`/`#showmenu`；`[size=]`/`[RRGGBBAA]文本[-]`/`[ruby=]`（可嵌套）；`#1`~`#5` = 左/中偏左/中/中偏右/右。
- **1.6** — 2026-10-08 20:27:00 —— **新增 §9「额外自定义资源包（overrides）」**（安装位置、AES 加密包的解压与解压码、`生成清单.ps1` 用途、manifest 键）与 `references/额外资源包清单.md`（已装包 `Win20241023前-20260818` 的 158 角色 / 665 背景 / 178 BGM / 261 音效 / 136 弹窗）；技能纳入版本管理。**← 当前版本**
