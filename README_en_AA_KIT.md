# AA_KIT · AzureArchive Scenario-Authoring Kit

![license](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-lightgrey)
![author](https://img.shields.io/badge/by-Tommhy0-informational)
![platform](https://img.shields.io/badge/platform-Windows-0078D6)
![base](https://img.shields.io/badge/AzureArchive-1.0--beta-orange)
![langs](https://img.shields.io/badge/docs-中文%20%7C%20EN%20%7C%20日本語%20%7C%20한국어-blue)

A self-contained kit **for anyone who wants to write *Blue Archive* scenario** — either **by hand** or **with an AI assistant**.
The whole idea is one sentence: **AzureArchive's project file `.aap2` is plain JSON, and writing it directly is far more
reliable than clicking around its Unity node editor.**

> Languages: [中文](README.md) ｜ [**English**](README.en.md) ｜ [日本語](README.ja.md) ｜ [한국어](README.ko.md)

> AzureArchive ("**AA**") is an **unofficial** scenario editor for *Blue Archive*, developed and maintained by
> **Foxxlight (狐光体)** and released only at <https://aadoc.foxxlight.top/>. This repository is **third-party**
> material, unaffiliated with the AA team, and **contains no game assets whatsoever**.

---

## Table of contents

- [What this is](#what-this-is)
- [Repository layout](#repository-layout)
- [Quick start](#quick-start)
- [Supported features](#supported-features)
- [Reference lists (six tables)](#reference-lists-six-tables)
- [`.aap2` cheat sheet](#aap2-cheat-sheet)
- [Four key tables](#four-key-tables)
- [Extra directives & rich text](#extra-directives--rich-text)
- [Extra custom resource packs (overrides)](#extra-custom-resource-packs-overrides)
- [Environment & troubleshooting](#environment--troubleshooting)
- [Pitfalls (must-follow)](#pitfalls-must-follow)
- [Sample project](#sample-project)
- [Version history](#version-history)
- [License & credits](#license--credits)

---

## What this is

**AA's project file `.aap2` is plain JSON.** Instead of clicking buttons in the Unity editor (which often refuses to
respond), just **write that JSON** — it's more reliable, version-controllable, and scriptable. This kit gathers
**every field, lookup table, and pitfall** you need to author AA stories:

```
write .aap2  →  click "Edit" in AA (auto-saves + compiles)  →  switch to "Appreciation mode" to play
```

The repository provides:

1. **Six reference tables** + `xxhash32.py` (to compute resource-name hashes);
2. **A sample project** `Schale_Demo.aap2` (rename and use, or study it);
3. **A troubleshooting script** `修复资源缓存_双击运行.cmd` (fixes "cannot load resources");
4. **A bundled AI skill** `azurearchive-scenario` (for Claude / Claude Code) — once installed, an AI can produce
   `.aap2` files following the same spec. **AI is optional**: write by hand from the tables, or let the AI draft — both
   follow the same spec.

---

## Repository layout

```
AA_KIT/
├─ README.md / README.en.md / README.ja.md / README.ko.md   docs in four languages
├─ LICENSE                          CC BY-NC-SA 4.0
├─ azurearchive-scenario.skill      packaged AI skill (import directly in Claude desktop)
├─ claude-code-skill/
│   └─ azurearchive-scenario/       skill folder (Claude Code; core is SKILL.md)
│       ├─ SKILL.md                 skill body (v1.6)
│       ├─ README.md                skill readme
│       ├─ CHANGELOG.md             changelog (0.1 → 1.6)
│       ├─ references/              six tables + xxhash32.py
│       └─ examples/Schale_Demo.aap2  sample project
├─ 参考资料/                        loose copies of the above references/
├─ 示例工程_Schale_Demo.aap2         sample project (loose copy)
└─ 修复资源缓存_双击运行.cmd          one-click "cannot load resources" fix
```

> Note: this repository contains **only text material and scripts — no game assets**. You must supply the
> **AA application** and the **official resource pack** yourself.

---

## Quick start

### Path A — write by hand

1. Read this README and [`参考资料/`](#reference-lists-six-tables), and study the [sample project](#sample-project);
2. Generate `.aap2` with any editor (or a small script);
3. Drop it into `…\data\projects\`, then in AA go **Project mode → select → Edit**, and switch to **Appreciation mode** to play.

### Path B — let an AI assistant draft it (bundled skill)

1. **Install the skill**:
   - Claude desktop: use the app's "Skills → Add" and pick `azurearchive-scenario.skill`;
   - Claude Code: copy `claude-code-skill/azurearchive-scenario/` into your skills directory, e.g.
     `~/.claude/skills/azurearchive-scenario/` (Windows: `C:\Users\<you>\.claude\skills\azurearchive-scenario\`).
2. Tell the AI: "Write a Blue Archive scenario using the azurearchive-scenario skill …";
3. The AI writes `.aap2` into `…\data\projects\`; then, as above, you click "Edit" and play to verify.

> A successful compile ≠ you've seen the result — **always play it through yourself**.

---

## Supported features

| Capability | Notes |
|---|---|
| Script / nodes | Four node kinds: entry / dialogue / choice / exit; narration, multi-ending links |
| Character art | Characters are referenced by their **Korean** names; 5 slots (left / mid-left / center / mid-right / right), up to 5 on stage |
| Expressions | Per-character `faceId` (`"00"`..`"17"`; the available ids differ per character) |
| Emoticons | `emoticon`, 20 kinds (♪ music, ❤ heart, ✦ twinkle, sweat, ⁉, 💡 …) |
| Actions | 7 kinds: crouch / fall / tremble / jump, etc. |
| Appear / exit | Slide in/out from left/right, or appear/vanishing in place (**default: same-side entry**, see tables) |
| Background / transitions | Scene changes + 9 transitions (slide, black/white fade, square, circle …) |
| Music / SFX / popups | BGM (242 tracks), sound effects (697 string names), popup images (character CG / generic) |
| Extra directives | `#wait` / `#bgshake` / `#zmc` / `#st` on-screen text, etc. (things the UI can't do) |
| Rich text | `[size=]` scale, `[RRGGBBAA]` color, `[ruby=]` ruby |
| Extra resource packs | Install/inspect overrides for custom characters, backgrounds, BGM, SFX, popups |

---

## Reference lists (six tables)

`references/` (and `参考资料/`) holds the authoritative lookup tables (all as searchable Markdown):

| File | Contents |
|---|---|
| `人物表情对照表.md` | `faceId → expression` for **401 characters** (133 NPCs/masks have no data); **available ids differ per character** (Shiroko 7, Hoshino 17) |
| `角色名清单.md` | **1467** character/NPC **Korean names** (put these in `characters[].name`; with suffixes like `부상`/`테러`) |
| `BGM用途注释清单.md` | `bgmId → title/artist/suggested use` for 242 BGM tracks (uses inferred from titles — **verify by ear**) |
| `弹窗图注释清单.md` | Visual descriptions of 203 unnamed popup images (`popup02..popup221`) |
| `音效名清单.md` | 697 sound-effect names (for the `sound` field, e.g. `SE_DoorOpen_01`) |
| `额外资源包清单.md` | Contents of one extra pack (`Win20241023前-20260818`): characters/backgrounds/BGM/SFX/popups |
| `bgm_table.tsv` | Raw BGM table (number/title/artist) |
| `xxhash32.py` | Reference xxHash32(seed=0) implementation for `bgName` |

---

## `.aap2` cheat sheet

**The first line must be `AAP2` + a single LF (0x0A)** (CRLF triggers `Unsupported AAP file marker`); JSON follows
(UTF-8 **without BOM**).

```json
{ "LegacySourceVersion":"absent", "FormatVersion":2,
  "ProjectId":"<guid>", "ProjectName":"...",
  "PreviewBgName":<uint bg hash>, "PreviewHeader":"...", "PreviewTitle":"...",
  "nodes":[ ... ] }
```

Node `Kind`:

- `entry`: `{Title,Header,Guid:"00000000-0000-0000-0000-000000000000",ConnectionsTo:[<guid>],X,Y,Kind:"entry"}`
- `dialogue`: `{Scripts:[ScriptData],NodeName:null,Guid,ConnectionsTo:[...],X,Y,Kind:"dialogue"}`
- `choice`: `{Options:[{OptionId,Text,TargetNodeId}],DefaultOptionId:null,UnusedSelectionTexts:[],Guid,X,Y,Kind:"choice"}`
  (**no ConnectionsTo**; two options pointing at the same `TargetNodeId` = "different choice, same plot")
- `exit`: `{IsEnding,EndText,NeHeader,NeTitle,NeScriptDirty:<ScriptData>,Guid,ConnectionsTo:[],X,Y,Kind:"exit"}`

`ScriptData`: `LineId`(guid), `text`, `popup`(str), `bgEffect`(uint), `bgName`(uint bg hash), `bgFriendlyName`(str),
`sound`(str), `voice`(str), `transition`(uint), `bgmId`(**int**), `selectionGroup`(uint), `additionalPrompt`(str),
`characters`(**exactly 6**), `speakerSlotNum`(int), `highlightedSlotNums`(int[]), `isDialogScript`(bool), `placeText`(str)

`characters[slot]`: `{name,faceId:"00",startingPos,endingPos,displayOrder:1,emoticon:-1,action:0,effect:0,appear:0,shapeOverride:0}`

- Empty slot: `name:""`, start/end `0`. Occupied slot: **array index = current slot = `startingPos`**;
  `speakerSlotNum` = the speaker's slot.
- Slots 1..5 hold characters (**two on stage → use 3 + 5**, spaced apart to avoid overlap); slot 0 is the narrator/teacher slot.
- Narration: `isDialogScript:false` with speaker pointing at an empty slot.

**Resource name → hash**: `bgName` = **`xxHash32(name, seed=0)`** (over the UTF-8 bytes).
E.g. `BG_MainOffice`=1046815759, `BG_Black`=1047754314. `popup`/`sound`/`voice` are **string names**, not hashes.

---

## Four key tables

### Transition `transition` (durations are baked into presets; not per-line editable)

| id | Effect |
|---|---|
| `1408872282` | Cross-fade 500ms (**only for same-scene day↔night** light changes) |
| `3854440696` | Black fade 250ms |
| `3868567233` | White fade 250ms |
| `3957412172` | Slide left |
| `1127535352` | Slide right |
| `4152299906` | Slide up |
| `3029168926` | Slide down |
| `3344317924` | Black squares |
| `1914875660` | Black circle |

### Appear / exit `appear` (= the `AppearType` enum)

| Value | Name | Look |
|---|---|---|
| `0` | None | none (stay in place; default) |
| `1` | **AL** | slides **left** ⇒ looks like **entering from the right** |
| `2` | **AR** | slides **right** ⇒ looks like **entering from the left** |
| `3` | A | appear in place |
| `4` | **DL** | slides **left** (exits to the left) |
| `5` | **DR** | slides **right** (exits to the right) |
| `6` | D | vanish in place |

> **The letter is the slide direction** (`L`=slides left, `R`=slides right), **not** "which side it comes from".
> **Default rule: a character enters from the side of the screen it stands on** — on the **right** use `1`, on the
> **left** use `2`, center use `3`; exits: right `5` / left `4` / center `6`. Reverse only when the story calls for it.

### Character action `action`

`1`=crouch briefly (common for picking things up) ｜ `2`=fall left ｜ `3`=fall right ｜ `4`=tremble slightly ｜
`5`=shake violently ｜ `6`=jump once ｜ `7`=jump twice. (After falling, the character stands back up unless removed
on the next line.)

### Override `shapeOverride`

`1`=on a call (electronic form on the other end) ｜ `2`=in shadow (fully black) ｜ `4`=closer (portrait enlarged).

### Others

- **Emoticon**: `-1`=none ｜ `0`=Angry ｜ `1`=Chat ｜ `2`=Dot⋯ ｜ `3`=Exclaim！ ｜ `4`=Heart❤ ｜ `5`=Music♪ ｜
  `6`=Question? ｜ `7`=Respond ｜ `8`=Shy ｜ `9`=Surprise ｜ `10`=Sweat ｜ `11`=Twinkle✦ ｜ `12`=Upset ｜ `13`=Think ｜
  `14`=Bulb💡 ｜ `15`=Sad ｜ `16`=Sigh ｜ `17`=Steam ｜ `18`=Tear ｜ `19`=Zzz.
- **Slot = screen position**: `#1`=left, `#2`=mid-left, `#3`=center, `#4`=mid-right, `#5`=right; `#0`=speaker/narration.
- `bgmId` = track number (the NN of `theme_NN`); `999` = mute.

---

## Extra directives & rich text

**Extra directives** go into the `text` field (multiple lines allowed, prefix `#`) and cover what the UI can't:

| Directive | Effect |
|---|---|
| `#wait;ms` | pause before advancing (for a line with no dialogue) |
| `#bgshake` | shake the background once |
| `#fx;AronaTouch` | special effect (currently only the prologue fingerprint) |
| `#zmc;mode;X,Y;scale;ms` | pan/zoom the background (mode `instant` / `smooth`) |
| `#st;[X,Y];mode;fontSize;` ｜ `#stm;…` | on-screen text (left-aligned / centered; mode `instant`/`smooth`/`serial`; **the trailing semicolon is required**) |
| `#clearST` | clear the on-screen text (it does not disappear on its own) |
| `#<slot>;fx;shot` | hit effect on the character in that slot, e.g. `#3;fx;shot` |
| `#hidemenu` ｜ `#showmenu` | hide / restore the top-right menu |

Screen coordinates are centered at the **middle of the screen**; width is fixed at 2960 units.

**Dialogue rich text**: `[size=px]text[/size]`, `[RRGGBBAA]text[-]` (color, e.g. `[FF0000]red[-]`),
`[ruby=reading]text[/ruby]`; nestable (e.g. `[size=200][FF0000]x[/size][-]`).

---

## Extra custom resource packs (overrides)

An **extra custom resource pack** is an AA add-on pack (with its own `manifest.json` + `characters/ bgs/ bgms/ sounds/ popups/`)
that adds **custom characters / backgrounds / BGM / SFX / popups** to AA.

- **Install**: extract the contents into AA's **`…\AzureArchive\data\overrides\`** (global — applies to every project);
  putting it in `projects\<project-name>\` makes it apply to that project only. **Back up `overrides` first**, then
  **restart AA**.
- Packs from the official group are often **fully AES-encrypted** (zip `compress_type=99`): plain tools
  (.NET `ZipFile`, `tar`) **extract only 0 bytes** — use **7-Zip** or Python `pyzipper` (`AESZipFile` + `setpassword`).
  **The password is on the official docs' installation page.**
- `manifest.json` keys: `CharacterOverrides / VoiceOverrides / PopupOverrides / SoundOverrides / BgOverrides /
  BgEffectOverrides / BgSpineOverrides / BgmOverrides` (missing keys are treated as empty).
- **`生成清单.ps1`** is the tool for making **your own** pack: drop it into a folder containing
  `characters/bgms/bgs/sounds/popups` and it scans them into a `manifest.json`. Character folders are named
  `Name_Club` (underscore-separated; omit the club), each holding `<name>.skel` / `.atlas` / `.png` / `-avatar.png`.
  **A finished pack does not need it.**

---

## Environment & troubleshooting

| Item | Location |
|---|---|
| App | `<somewhere>\AzureArchive.exe` |
| Data dir | `C:\Users\<you>\AppData\LocalLow\foxxlight\AzureArchive\data` |
| Projects | `…\data\projects\<name>.aap2` (UTF-8, no BOM) |
| Compiled output | `…\data\saves\<name>.aas` (+ `.build.json`) |
| Custom resources | `…\data\overrides\` |
| Resource cache | `C:\Users\<you>\AppData\LocalLow\Unity\foxxlight_AzureArchive` (~6 GB, **hash-named, no `.bundle` suffix**) |

### Fixing "cannot load resources"

Symptom: the UI reports "cannot detect resources" and `Player.log` is spammed with
`…ScenarioResourceManager.AddrLoadUrl/{texts,flatdata,databases}_assets_all.bundle` **404**s.

**Key insight: `completeResStructVer: 0` in `user_settings.json` is a *result*, not the cause** — the app writes 0
only when it can't read the cache. **Don't just set it back to `11`** (that only suppresses the symptom until the next launch).

What actually matters: **whether these two things are present in the `LocalLow` root the app sees at launch**:

- Addressables catalog dir: `foxxlight\AzureArchive\com.unity.addressables\`
- Resource cache: `Unity\foxxlight_AzureArchive\` (~6 GB)

> ⚠ **There can be two `LocalLow` roots on one machine** (MSIX redirection): processes started from a
> **Store/packaged** app see `AppData\LocalLow` redirected to `…\AppData\Local\Packages\<app>\LocalCache\LocalLow\`;
> processes started from **Explorer** see the real `C:\Users\<you>\AppData\LocalLow\`. **First figure out which side the
> cache is on**, then get it onto the side the app actually uses (copy, or a directory junction).
> A ready-made script: **`修复资源缓存_双击运行.cmd`** (just double-click; it reports whether each root exists).

Success criteria: log **404 = 0**, and `completeResStructVer` **is no longer written back to 0**.

---

## Pitfalls (must-follow)

1. The first line `AAP2` must be followed by a **single LF** (not CRLF).
2. **`bgName:0` / `bgmId:0` mean "clear", not "keep"** → **rewrite the current `bgName` (hash) + `bgFriendlyName` +
   `bgmId` on *every* line**, otherwise the background/music vanish (go black) from the 2nd line on. Write
   `transition` **only on the line that actually changes the scene**; `0` elsewhere.
3. **Moving a character between lines (changing `endingPos` to another slot) fails project validation** (only a generic
   `failed validation` is shown) → keep each character in a fixed slot every line (`startingPos = endingPos = slot`).
4. GUIDs must be valid hexadecimal GUIDs; `characters` must be **exactly 6**.
5. After writing `.aap2`, **delete the same-named `.aap` (v1) and old `saves\<name>.*`**, then restart AA (otherwise it
   may read an old version).
6. Chinese text must be **UTF-8 without BOM**; **PowerShell treats `.ps1` as ANSI and processes backtick escapes** —
   keep Chinese (and backtick-containing) text in a separate UTF-8 file and read it in; don't inline it into a command string.
7. In this beta, `AzureArchive.exe --cli …` **prints no result**, and the editor's MCP service often fails to start
   (port in use) → **don't take detours; just "write the file + click Edit/Play manually"**.

---

## Sample project

`examples/Schale_Demo.aap2`: a day at Schale — 3 characters, 4 backgrounds, a popup, sound effects, emoticons, actions,
a two-option branch, and narration, 15 lines total. **Copy it into `…\data\projects\`, rename it, and use it**
(remember the first line `AAP2` + LF).

---

## Version history

The bundled skill is versioned; the full log is in
[`claude-code-skill/azurearchive-scenario/CHANGELOG.md`](claude-code-skill/azurearchive-scenario/CHANGELOG.md).
Currently **v1.6**; lineage: `0.1 → … → 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6`.
`0.x` was the growth phase and `1.0` onward is stable; **1.3 fixed a critical bug**: the appear/exit direction
(`appear`) — the old table had left/right swapped.

---

## License & credits

- This repository's **text material and scripts**, by **Tommhy0**, are licensed under **CC BY-NC-SA 4.0**
  (Attribution · NonCommercial · ShareAlike) — see [`LICENSE`](LICENSE).
- **AA itself and all game assets** (character art, backgrounds, music, SFX, text, etc.) are the property of their
  respective owners; this repository contains none of them.
- **AzureArchive** is developed and maintained by **Foxxlight (狐光体)**, released only at
  <https://aadoc.foxxlight.top/>, as an **unofficial, non-profit** project. This repository is third-party material,
  unaffiliated with the AA team or with Yostar / Nexon / Nexon Games.

If you find this useful, Issues / PRs adding more tables and transition ids are welcome.
