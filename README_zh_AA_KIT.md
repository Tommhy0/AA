# AA_KIT · AzureArchive 剧情创作资料包

![license](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-lightgrey)
![author](https://img.shields.io/badge/by-Tommhy0-informational)
![platform](https://img.shields.io/badge/platform-Windows-0078D6)
![base](https://img.shields.io/badge/AzureArchive-1.0--beta-orange)
![langs](https://img.shields.io/badge/docs-中文%20%7C%20EN%20%7C%20日本語%20%7C%20한국어-blue)

**给任何想创作《蔚蓝档案》剧情的人**用的自包含资料包 —— 你既可以**照着手写**，也可以**让 AI 助手帮你写**。
核心思路只有一句：**AzureArchive 的工程文件 `.aap2` 就是纯 JSON，手写远比去点那套 Unity 节点编辑器可靠。**

> 语言：[**中文**](README.md) ｜ [English](README.en.md) ｜ [日本語](README.ja.md) ｜ [한국어](README.ko.md)

> AzureArchive（下称 **AA**）是《蔚蓝档案》的**非官方**剧情编辑器，由 **狐光体（Foxxlight）** 开发维护，
> 仅在官网 <https://aadoc.foxxlight.top/> 发布。本仓库是**第三方**资料，与 AA 官方无关，也**不含任何游戏素材**。

---

## 目录

- [这是什么](#这是什么)
- [仓库结构](#仓库结构)
- [快速开始](#快速开始)
- [支持的功能](#支持的功能)
- [参考资料（六张清单）](#参考资料六张清单)
- [`.aap2` 结构速查](#aap2-结构速查)
- [四类对照表](#四类对照表)
- [额外指令与对话富文本](#额外指令与对话富文本)
- [额外自定义资源包（overrides）](#额外自定义资源包overrides)
- [环境与排障](#环境与排障)
- [坑（务必遵守）](#坑务必遵守)
- [示例工程](#示例工程)
- [版本历史](#版本历史)
- [许可与致谢](#许可与致谢)

---

## 这是什么

**AA 的工程文件 `.aap2` 是纯 JSON。** 与其去点 Unity 编辑器里那些按钮（经常点不动），不如**直接写这个 JSON** ——
更可靠、可版本管理、可脚本批量生成。本资料包把创作 AA 剧情所需要的**全部字段、对照表与坑**整理在一起：

```
写 .aap2  →  在 AA 里点“编辑”（打开即自动保存 + 编译）  →  切“鉴赏模式”播放验收
```

本仓库提供：

1. **六张参考资料清单** + `xxhash32.py`（算资源名哈希）；
2. **示例工程** `Schale_Demo.aap2`（可直接改名使用/参考）；
3. **排障脚本** `修复资源缓存_双击运行.cmd`（修“无法加载资源”）；
4. **一个随附的 AI 技能** `azurearchive-scenario`（给 Claude / Claude Code 用）—— 装上后，AI 就能照着同一套参考
   直接产出 `.aap2`。**用不用 AI 都行**：手动照清单写、或让 AI 代笔，两条路都走同一份规范。

---

## 仓库结构

```
AA_KIT/
├─ README.md / README.en.md / README.ja.md / README.ko.md   四种语言的说明
├─ LICENSE                          CC BY-NC-SA 4.0
├─ azurearchive-scenario.skill      随附 AI 技能的打包件（Claude 桌面版可直接导入）
├─ claude-code-skill/
│   └─ azurearchive-scenario/       技能目录（Claude Code 版；核心是 SKILL.md）
│       ├─ SKILL.md                 技能正文（v1.6）
│       ├─ README.md                技能说明（单拷技能时随附）
│       ├─ CHANGELOG.md             更新日志（0.1 → 1.6）
│       ├─ references/              六张清单 + xxhash32.py
│       └─ examples/Schale_Demo.aap2  示例工程
├─ 参考资料/                        上面 references/ 的散装副本
├─ 示例工程_Schale_Demo.aap2         示例工程（散装副本）
└─ 修复资源缓存_双击运行.cmd           “无法加载资源”一键修复
```

> 说明：本仓库**只含文本资料与脚本，不含任何游戏素材**。使用前请自备 **AA 本体**与**官方资源包**。

---

## 快速开始

### 路线 A：手动创作

1. 读本 README 与 [`参考资料/`](#参考资料六张清单)，对着 [`示例工程`](#示例工程) 照猫画虎；
2. 用任意编辑器（或写个小脚本）生成 `.aap2`；
3. 放进 `…\data\projects\`，在 AA 里**项目模式 → 选中 → 编辑**，再切**鉴赏模式**播放。

### 路线 B：让 AI 助手代笔（随附技能）

1. **装技能**：
   - Claude 桌面版：用 App 的“技能 → 添加”，选择 `azurearchive-scenario.skill`；
   - Claude Code：把 `claude-code-skill/azurearchive-scenario/` 拷到你的 skills 目录，例如
     `~/.claude/skills/azurearchive-scenario/`（Windows：`C:\Users\<你>\.claude\skills\azurearchive-scenario\`）。
2. 对 AI 说：“用 azurearchive-scenario 技能写一段 AA 剧情……”；
3. AI 把 `.aap2` 写进 `…\data\projects\`；然后同上，你点“编辑”并播放验收。

> 编译成功 ≠ 已看过效果 —— **务必亲自播一遍**。

---

## 支持的功能

| 能力 | 说明 |
|---|---|
| 剧本 / 节点 | 入口 / 脚本（对话）/ 选择（分支）/ 出口 四类节点；旁白、多结局衔接 |
| 立绘 | 按韩文原名上人；5 个栏位（左 / 中偏左 / 中 / 中偏右 / 右），最多 5 人同台 |
| 表情 | 每个角色的 `faceId`（`"00"`..`"17"`，各角色可用编号不同） |
| 语气气泡 | `emoticon` 共 20 种（♪ 哼歌、❤ 爱心、✦ 闪亮、汗、⁉、💡……） |
| 动作 | 蹲下 / 倒下 / 抖动 / 跳 等 7 种 |
| 出场 / 退场 | 从左/右滑入滑出、原地出现消失（**默认同侧入场**，见对照表） |
| 背景 / 过渡 | 换景 + 9 种过渡（滑动、黑/白淡入淡出、方格、圆形……） |
| 音乐 / 音效 / 弹窗 | BGM（242 首）、音效（697 个字符串名）、弹窗图（角色 CG / 通用图） |
| 额外指令 | `#wait` / `#bgshake` / `#zmc` / `#st` 屏幕文字 等（界面做不到的） |
| 对话富文本 | `[size=]` 放大、`[RRGGBBAA]` 颜色、`[ruby=]` 注音 |
| 额外资源包 | 装/查 overrides 自定义角色、背景、BGM、音效、弹窗 |

---

## 参考资料（六张清单）

`references/`（与 `参考资料/`）里是查表用的权威清单（都已整理成可检索的 Markdown）：

| 文件 | 内容 |
|---|---|
| `人物表情对照表.md` | **401 个角色**的 `faceId → 表情`（133 个 NPC/面具无数据）；**每角色可用编号不同**（白子 7 个、星野 17 个） |
| `角色名清单.md` | **1467 个**角色/NPC 的**韩文原名**（`characters[].name` 填它，带 `부상`/`테러` 等变体后缀） |
| `BGM用途注释清单.md` | 242 首 BGM 的 `bgmId → 曲名/作者/建议用途`（用途为按曲名推断，**建议试听核实**） |
| `弹窗图注释清单.md` | 203 张无名弹窗图（`popup02..popup221`）的画面注释 |
| `音效名清单.md` | 697 个音效名（`sound` 字段用，如 `SE_DoorOpen_01`） |
| `额外资源包清单.md` | 某扩展包（`Win20241023前-20260818`）的角色/背景/BGM/音效/弹窗清单 |
| `bgm_table.tsv` | BGM 原始表（曲号/曲名/作者） |
| `xxhash32.py` | 算 `bgName` 用的 xxHash32(seed=0) 参考实现 |

---

## `.aap2` 结构速查

**首行必须是 `AAP2` + 单个 LF(0x0A)**（写成 CRLF 会报 `Unsupported AAP file marker`）；其后是 JSON（UTF-8 **无 BOM**）。

```json
{ "LegacySourceVersion":"absent", "FormatVersion":2,
  "ProjectId":"<guid>", "ProjectName":"...",
  "PreviewBgName":<uint 背景哈希>, "PreviewHeader":"...", "PreviewTitle":"...",
  "nodes":[ ... ] }
```

节点 `Kind`：

- `entry`：`{Title,Header,Guid:"00000000-0000-0000-0000-000000000000",ConnectionsTo:[<guid>],X,Y,Kind:"entry"}`
- `dialogue`：`{Scripts:[ScriptData],NodeName:null,Guid,ConnectionsTo:[...],X,Y,Kind:"dialogue"}`
- `choice`：`{Options:[{OptionId,Text,TargetNodeId}],DefaultOptionId:null,UnusedSelectionTexts:[],Guid,X,Y,Kind:"choice"}`
  （**无 ConnectionsTo**；两个选项指向同一 `TargetNodeId`＝“选项不同但剧情相同”）
- `exit`：`{IsEnding,EndText,NeHeader,NeTitle,NeScriptDirty:<ScriptData>,Guid,ConnectionsTo:[],X,Y,Kind:"exit"}`

`ScriptData`：`LineId`(guid)、`text`、`popup`(str)、`bgEffect`(uint)、`bgName`(uint 背景哈希)、`bgFriendlyName`(str)、
`sound`(str)、`voice`(str)、`transition`(uint)、`bgmId`(**int**)、`selectionGroup`(uint)、`additionalPrompt`(str)、
`characters`(**恰好 6 项**)、`speakerSlotNum`(int)、`highlightedSlotNums`(int[])、`isDialogScript`(bool)、`placeText`(str)

`characters[槽]`：`{name,faceId:"00",startingPos,endingPos,displayOrder:1,emoticon:-1,action:0,effect:0,appear:0,shapeOverride:0}`

- 空槽：`name:""`、start/end `0`；有人槽：**数组下标 = 当前栏号 = `startingPos`**，`speakerSlotNum` = 发言者栏号。
- 栏 1..5 站人（**两人同台用 3 + 5**，隔开防重叠）；栏 0 是旁白/老师位。
- 旁白：`isDialogScript:false`，且 speaker 指向空栏。

**资源名 → 哈希**：`bgName` = **`xxHash32(名字, seed=0)`**（对 UTF-8 字节）。
例：`BG_MainOffice`=1046815759、`BG_Black`=1047754314。`popup`/`sound`/`voice` 是**字符串名**，不是哈希。

---

## 四类对照表

### 过渡 `transition`（时长打包在预设里，不可逐句改）

| id | 效果 |
|---|---|
| `1408872282` | 交叉渐变 500ms（**只用于白天↔黑夜**这类同场景明暗变化） |
| `3854440696` | 黑色淡入淡出 250ms |
| `3868567233` | 白色淡入淡出 250ms |
| `3957412172` | 向左滑动 |
| `1127535352` | 向右滑动 |
| `4152299906` | 向上滑动 |
| `3029168926` | 向下滑动 |
| `3344317924` | 黑色方格 |
| `1914875660` | 黑色圆形 |

### 出场 / 退场 `appear`（= `AppearType` 枚举）

| 值 | 名称 | 观感 |
|---|---|---|
| `0` | None | 无（原地不动，默认） |
| `1` | **AL** | 向**左**滑入 ⇒ 观感**从右侧出现** |
| `2` | **AR** | 向**右**滑入 ⇒ 观感**从左侧出现** |
| `3` | A | 原地出现 |
| `4` | **DL** | 向**左**滑出（退场到左边） |
| `5` | **DR** | 向**右**滑出（退场到右边） |
| `6` | D | 原地消失 |

> **字母指滑动方向**（`L`=向左滑、`R`=向右滑），**不是**“从哪边来”。
> **默认规则：人物从与自己所在屏幕同一侧的那一边滑入** —— 站画面**右**侧用 `1`，**左**侧用 `2`，中间用 `3`；
> 退场右 `5` / 左 `4` / 中 `6`。仅剧情需要时才反向。

### 人物动作 `action`

`1`=微微蹲一下（拿东西常用）｜ `2`=向左倒下 ｜ `3`=向右倒下 ｜ `4`=微微抖动 ｜ `5`=剧烈抖动 ｜ `6`=跳一下 ｜ `7`=跳两下。
（倒下后若下一句不把该角色移除，会自行站起。）

### 外形 `shapeOverride`

`1`=通话中（电话对面的电子形象）｜ `2`=阴影中（整个人黑色）｜ `4`=靠近（立绘放大）。

### 其它

- **语气气泡 `emoticon`**：`-1`=无 ｜ `0`=Angry ｜ `1`=Chat ｜ `2`=Dot⋯ ｜ `3`=Exclaim！ ｜ `4`=Heart❤ ｜ `5`=Music♪ ｜
  `6`=Question? ｜ `7`=Respond ｜ `8`=Shy ｜ `9`=Surprise ｜ `10`=Sweat ｜ `11`=Twinkle✦ ｜ `12`=Upset ｜ `13`=Think ｜
  `14`=Bulb💡 ｜ `15`=Sad ｜ `16`=Sigh ｜ `17`=Steam ｜ `18`=Tear ｜ `19`=Zzz。
- **栏位 = 屏幕位置**：`#1`=左、`#2`=中偏左、`#3`=中、`#4`=中偏右、`#5`=右；`#0`=发言者/旁白位。
- `bgmId` = 曲号（`theme_NN` 的 NN）；`999` = 静音。

---

## 额外指令与对话富文本

**额外指令**写进 `text` 字段（可多行，前缀 `#`），用于补足界面做不到的事：

| 指令 | 作用 |
|---|---|
| `#wait;毫秒` | 无对话的脚本等待一段时间再推进 |
| `#bgshake` | 背景抖动一次 |
| `#fx;AronaTouch` | 特殊效果（目前仅序章指纹识别） |
| `#zmc;模式;X,Y;缩放;持续ms` | 背景平移/缩放（模式 `instant` / `smooth`） |
| `#st;[X,Y];模式;字号;` ｜ `#stm;…` | 屏幕文字（分别左对齐 / 居中；模式 `instant`/`smooth`/`serial`；**末尾分号不可省**） |
| `#clearST` | 清除屏幕文字（它不会自动消失） |
| `#<栏位号>;fx;shot` | 指定栏位角色中弹特效，如 `#3;fx;shot` |
| `#hidemenu` ｜ `#showmenu` | 隐藏 / 恢复右上角菜单 |

屏幕坐标原点在**画面中心**，宽固定 2960 单位。

**对话文字富文本**：`[size=字号]文本[/size]`、`[RRGGBBAA]文本[-]`（颜色，如 `[FF0000]红[-]`）、
`[ruby=注音]文本[/ruby]`；可嵌套（如 `[size=200][FF0000]x[/size][-]`）。

---

## 额外自定义资源包（overrides）

**额外自定义资源包** = 一个专给 AA 用的资源包（自带 `manifest.json` + `characters/ bgs/ bgms/ sounds/ popups/`），
用来给 AA 增加**自定义角色 / 背景 / BGM / 音效 / 弹窗**。

- **安装**：解压后把内容放进 AA 的 **`…\AzureArchive\data\overrides\`**（全局，对所有工程生效）；
  放进 `projects\<工程同名文件夹>\` 则只对该工程生效。**装前先备份 `overrides`**，装好后**重启 AA**。
- 官群下发的包常**整包 AES 加密**（zip `compress_type=99`）：普通方式（.NET `ZipFile`、`tar`）**只能抽出 0 字节**，
  需用 **7-Zip** 或 Python `pyzipper`（`AESZipFile` + `setpassword`）。**解压码见官方文档 installation 页**。
- `manifest.json` 的键：`CharacterOverrides / VoiceOverrides / PopupOverrides / SoundOverrides / BgOverrides /
  BgEffectOverrides / BgSpineOverrides / BgmOverrides`（缺的键按空处理）。
- **`生成清单.ps1`** 是**自制**包的工具：把它丢进一个含 `characters/bgms/bgs/sounds/popups` 的文件夹里运行，
  会扫出 `manifest.json`。角色文件夹命名 `人物名_社团名`（下划线分隔，无社团名则不写），每个文件夹放
  `<名>.skel` / `.atlas` / `.png` / `-avatar.png`。**别人做好的成品包不需要跑它。**

---

## 环境与排障

| 项 | 位置 |
|---|---|
| 程序 | `<某处>\AzureArchive.exe` |
| 数据目录 | `C:\Users\<你>\AppData\LocalLow\foxxlight\AzureArchive\data` |
| 工程 | `…\data\projects\<名>.aap2`（UTF-8 无 BOM） |
| 编译产物 | `…\data\saves\<名>.aas`（+ `.build.json`） |
| 自定义资源 | `…\data\overrides\` |
| 资源缓存 | `C:\Users\<你>\AppData\LocalLow\Unity\foxxlight_AzureArchive`（约 6 GB，**哈希名、无 `.bundle` 后缀**） |

### “无法加载资源” 怎么修

症状：界面报“无法检测到资源”，`Player.log` 刷 `…ScenarioResourceManager.AddrLoadUrl/{texts,flatdata,databases}_assets_all.bundle` **404**。

**关键认知：`user_settings.json` 里的 `completeResStructVer: 0` 是结果，不是原因** —— 程序读不到缓存才会写 0。
**别只把它改回 `11`**（那只能按住症状到下次启动）。

真正要查的是：**程序启动时看到的那个 `LocalLow` 根里，有没有这两样**：

- Addressables 目录 `foxxlight\AzureArchive\com.unity.addressables\`
- 资源缓存 `Unity\foxxlight_AzureArchive\`（约 6 GB）

> ⚠ **同一台机器可能有两个 `LocalLow` 根**（MSIX 重定向）：从**商店版/打包版**应用启动的进程，`AppData\LocalLow`
> 会被重定向到 `…\AppData\Local\Packages\<应用>\LocalCache\LocalLow\`；从**资源管理器**启动则看真正的
> `C:\Users\<你>\AppData\LocalLow\`。**先确认缓存在哪一侧**，把缓存弄到程序实际使用的那一侧（复制或做目录联接）。
> 现成脚本：**`修复资源缓存_双击运行.cmd`**（双击即可，会先报告两个根各自在不在）。

修好的判据：日志 **404 = 0**，且 `completeResStructVer` **不再被写回 0**。

---

## 坑（务必遵守）

1. 首行 `AAP2` 后必须是**单个 LF**（不能 CRLF）。
2. **`bgName:0` / `bgmId:0` 是“清空”不是“沿用”** → **每一句都要重写当前 `bgName`(哈希) + `bgFriendlyName` + `bgmId`**，
   否则从第 2 句起背景/音乐消失变黑。`transition` **只在真正换景那句**写，其它写 `0`。
3. **人物跨句“走位”（改 `endingPos` 换栏）会让工程校验失败**（只报通用 `failed validation`）→ 每句保持固定栏位
   （`startingPos = endingPos = 栏号`）。
4. GUID 必须是合法十六进制 GUID；`characters` 必须**恰好 6 项**。
5. 写完 `.aap2` 后**删掉同名 `.aap`(v1) 与旧 `saves\<名>.*`**，再重启 AA（否则可能读旧版）。
6. 中文一律 **UTF-8 无 BOM**；**PowerShell 会把 `.ps1` 当 ANSI / 把反引号转义** —— 中文与含反引号的文本要放单独
   UTF-8 文件再读入，别直接塞进命令行字符串。
7. 本 beta 版 `AzureArchive.exe --cli …` **不输出结果**；编辑器右下角 MCP 服务常因端口占用起不来
   → **别绕道，走“写文件 + 人工点‘编辑/播放’”**。

---

## 示例工程

`examples/Schale_Demo.aap2`：夏莱的值日日常——3 角色、4 背景、弹窗、音效、语气气泡、动作、双向选择分支、旁白，
共 15 句。**可直接复制到 `…\data\projects\` 改名使用**（记得首行 `AAP2` + LF）。

---

## 版本历史

资料包随附的技能采用版本号管理，完整记录见
[`claude-code-skill/azurearchive-scenario/CHANGELOG.md`](claude-code-skill/azurearchive-scenario/CHANGELOG.md)。
当前 **v1.6**，沿革：`0.1 → … → 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6`。
其中 `0.x` 为成长期、`1.0` 起为稳定版；`1.3` 起修正了一个**关键错误**：出场/退场方向（`appear`）——旧表把左右记反了。

---

## 许可与致谢

- 本仓库的**文本资料与脚本**由 **Tommhy0** 整理，采用 **CC BY-NC-SA 4.0**（署名 · 非商业性使用 · 相同方式共享）—— 详见 [`LICENSE`](LICENSE)。
- **AA 本体与全部游戏素材**（立绘、背景、音乐、音效、文本等）版权归**各自作者**所有；本仓库不含这些素材。
- **AzureArchive** 由 **狐光体（Foxxlight）** 开发维护，仅在官网 <https://aadoc.foxxlight.top/> 发布，为**非官方、非盈利**项目。
  本仓库为第三方资料，与 AA 官方及 Yostar / Nexon / Nexon Games 无任何关联。

如果你觉得有用，欢迎提 Issue / PR 补充更多对照表与转场 id。
