# AA_KIT · AzureArchive シナリオ制作キット

![license](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-lightgrey)
![author](https://img.shields.io/badge/by-Tommhy0-informational)
![platform](https://img.shields.io/badge/platform-Windows-0078D6)
![base](https://img.shields.io/badge/AzureArchive-1.0--beta-orange)
![langs](https://img.shields.io/badge/docs-中文%20%7C%20EN%20%7C%20日本語%20%7C%20한국어-blue)

**『ブルーアーカイブ』のシナリオを作りたい人**のための自己完結型キット —— **手書き**でも、**AI アシスタントに
書かせても**使えます。肝はたった一言：**AzureArchive のプロジェクトファイル `.aap2` はただの JSON で、手書きの方が
Unity のノードエディタをクリックするよりずっと確実**、ということです。

> 言語：[中文](README.md) ｜ [English](README.en.md) ｜ [**日本語**](README.ja.md) ｜ [한국어](README.ko.md)

> AzureArchive（以下 **AA**）は『ブルーアーカイブ』の**非公式**シナリオエディタで、**狐光体（Foxxlight）** が開発・
> 保守し、公式サイト <https://aadoc.foxxlight.top/> のみで配布されています。本リポジトリは**第三者の**資料であり、
> AA 公式とは無関係で、**ゲーム素材は一切含みません**。

---

## 目次

- [これは何か](#これは何か)
- [リポジトリ構成](#リポジトリ構成)
- [クイックスタート](#クイックスタート)
- [対応機能](#対応機能)
- [参考資料（6 つの表）](#参考資料6-つの表)
- [`.aap2` 早見表](#aap2-早見表)
- [4 つの対応表](#4-つの対応表)
- [追加命令とリッチテキスト](#追加命令とリッチテキスト)
- [追加カスタムリソースパック（overrides）](#追加カスタムリソースパックoverrides)
- [環境とトラブルシューティング](#環境とトラブルシューティング)
- [ハマりどころ（必守）](#ハマりどころ必守)
- [サンプルプロジェクト](#サンプルプロジェクト)
- [バージョン履歴](#バージョン履歴)
- [ライセンスとクレジット](#ライセンスとクレジット)

---

## これは何か

**AA のプロジェクトファイル `.aap2` はただの JSON です。** Unity エディタのボタンをクリックする（しばしば反応しない）
代わりに、**この JSON を直接書く** —— その方が確実で、バージョン管理もでき、スクリプトで一括生成もできます。
本キットは AA シナリオ制作に必要な**全フィールド・対応表・落とし穴**を 1 か所にまとめたものです：

```
.aap2 を書く  →  AA で「編集」をクリック（開くと自動保存＋コンパイル）  →  「鑑賞モード」で再生して確認
```

本リポジトリが提供するもの：

1. **6 つの参考表** ＋ `xxhash32.py`（リソース名のハッシュ計算用）；
2. **サンプルプロジェクト** `Schale_Demo.aap2`（名前を変えてそのまま使える／参考用）；
3. **トラブル対処スクリプト** `修复资源缓存_双击运行.cmd`（「リソースを読み込めない」の修復）；
4. **同梱の AI スキル** `azurearchive-scenario`（Claude / Claude Code 用）—— 入れておけば、AI が同じ仕様に沿って
   `.aap2` を生成できます。**AI は任意**：手書きでも AI に書かせても、同じ仕様に従います。

---

## リポジトリ構成

```
AA_KIT/
├─ README.md / README.en.md / README.ja.md / README.ko.md   4 言語の説明
├─ LICENSE                          CC BY-NC-SA 4.0
├─ azurearchive-scenario.skill      同梱 AI スキルのパッケージ（Claude デスクトップで読み込み可）
├─ claude-code-skill/
│   └─ azurearchive-scenario/       スキルフォルダ（Claude Code 用；中核は SKILL.md）
│       ├─ SKILL.md                 スキル本体（v1.6）
│       ├─ README.md                スキルの説明
│       ├─ CHANGELOG.md             更新履歴（0.1 → 1.6）
│       ├─ references/              6 つの表 ＋ xxhash32.py
│       └─ examples/Schale_Demo.aap2  サンプルプロジェクト
├─ 参考资料/                        上記 references/ のバラ置きコピー
├─ 示例工程_Schale_Demo.aap2         サンプルプロジェクト（バラ置き）
└─ 修复资源缓存_双击运行.cmd           「リソースを読み込めない」ワンクリック修復
```

> 注：本リポジトリは**テキスト資料とスクリプトのみで、ゲーム素材は含みません**。**AA 本体**と**公式リソースパック**は
> 各自で用意してください。

---

## クイックスタート

### ルート A：手書き

1. 本 README と [`参考资料/`](#参考資料6-つの表) を読み、[サンプルプロジェクト](#サンプルプロジェクト) を真似する；
2. 任意のエディタ（または小さなスクリプト）で `.aap2` を生成；
3. `…\data\projects\` に入れ、AA で**プロジェクトモード → 選択 → 編集**、続いて**鑑賞モード**で再生。

### ルート B：AI アシスタントに書かせる（同梱スキル）

1. **スキルを入れる**：
   - Claude デスクトップ：アプリの「スキル → 追加」で `azurearchive-scenario.skill` を選ぶ；
   - Claude Code：`claude-code-skill/azurearchive-scenario/` を skills ディレクトリへコピー（例
     `~/.claude/skills/azurearchive-scenario/`、Windows なら `C:\Users\<あなた>\.claude\skills\azurearchive-scenario\`）。
2. AI に「azurearchive-scenario スキルで BA のシナリオを書いて…」と頼む；
3. AI が `…\data\projects\` に `.aap2` を書き出す；あとは上と同様、「編集」をクリックして再生し確認。

> コンパイル成功 ≠ 確認済み —— **必ず自分で一度通して再生してください**。

---

## 対応機能

| 機能 | 説明 |
|---|---|
| 脚本／ノード | 入口／脚本（会話）／選択（分岐）／出口 の 4 種；ナレーション、複数エンドの接続 |
| 立ち絵 | **韓国語の原名**で指定；5 スロット（左／中左／中央／中右／右）、同時に最大 5 人 |
| 表情 | キャラごとの `faceId`（`"00"`..`"17"`、使える番号はキャラごとに異なる） |
| 感情マーク | `emoticon` 全 20 種（♪ 鼻歌、❤ ハート、✦ キラキラ、汗、⁉、💡 …） |
| モーション | しゃがむ／倒れる／震える／跳ぶ など 7 種 |
| 登場／退場 | 左右からのスライド入退場、その場で出現／消失（**既定は「同じ側から入る」**、表を参照） |
| 背景／トランジション | 場面転換 ＋ 9 種のトランジション（スライド、黒/白フェード、四角、円 …） |
| 音楽／SE／ポップアップ | BGM（242 曲）、SE（697 個の文字列名）、ポップアップ画像（キャラ CG／汎用） |
| 追加命令 | `#wait` / `#bgshake` / `#zmc` / `#st` 画面テキスト など（UI ではできないこと） |
| リッチテキスト | `[size=]` 拡大、`[RRGGBBAA]` 色、`[ruby=]` ルビ |
| 追加リソースパック | overrides によるカスタムキャラ／背景／BGM／SE／ポップアップの導入・確認 |

---

## 参考資料（6 つの表）

`references/`（および `参考资料/`）に、照会用の権威ある一覧（検索しやすい Markdown）があります：

| ファイル | 内容 |
|---|---|
| `人物表情对照表.md` | **401 キャラ**の `faceId → 表情`（133 の NPC／仮面はデータ無し）；**使える番号はキャラごとに違う**（シロコ 7、ホシノ 17） |
| `角色名清单.md` | **1467** キャラ/NPC の**韓国語原名**（`characters[].name` に入れる；`부상`/`테러` などの接尾辞つき） |
| `BGM用途注释清单.md` | 242 曲の `bgmId → 曲名/作者/想定用途`（用途は曲名からの推測 —— **試聴で確認**） |
| `弹窗图注释清单.md` | 203 枚の無名ポップアップ画像（`popup02..popup221`）の内容メモ |
| `音效名清单.md` | 697 個の SE 名（`sound` フィールド用、例 `SE_DoorOpen_01`） |
| `额外资源包清单.md` | ある追加パック（`Win20241023前-20260818`）のキャラ／背景／BGM／SE／ポップアップ一覧 |
| `bgm_table.tsv` | BGM 原表（番号/曲名/作者） |
| `xxhash32.py` | `bgName` 計算用 xxHash32(seed=0) の参考実装 |

---

## `.aap2` 早見表

**先頭行は必ず `AAP2` ＋ 単一 LF(0x0A)**（CRLF だと `Unsupported AAP file marker`）；以降が JSON（UTF-8・**BOM なし**）。

```json
{ "LegacySourceVersion":"absent", "FormatVersion":2,
  "ProjectId":"<guid>", "ProjectName":"...",
  "PreviewBgName":<uint 背景ハッシュ>, "PreviewHeader":"...", "PreviewTitle":"...",
  "nodes":[ ... ] }
```

ノード `Kind`：

- `entry`：`{Title,Header,Guid:"00000000-0000-0000-0000-000000000000",ConnectionsTo:[<guid>],X,Y,Kind:"entry"}`
- `dialogue`：`{Scripts:[ScriptData],NodeName:null,Guid,ConnectionsTo:[...],X,Y,Kind:"dialogue"}`
- `choice`：`{Options:[{OptionId,Text,TargetNodeId}],DefaultOptionId:null,UnusedSelectionTexts:[],Guid,X,Y,Kind:"choice"}`
  （**ConnectionsTo なし**；2 つの選択肢が同じ `TargetNodeId` を指す＝「選択は違うが展開は同じ」）
- `exit`：`{IsEnding,EndText,NeHeader,NeTitle,NeScriptDirty:<ScriptData>,Guid,ConnectionsTo:[],X,Y,Kind:"exit"}`

`ScriptData`：`LineId`(guid)、`text`、`popup`(str)、`bgEffect`(uint)、`bgName`(uint 背景ハッシュ)、`bgFriendlyName`(str)、
`sound`(str)、`voice`(str)、`transition`(uint)、`bgmId`(**int**)、`selectionGroup`(uint)、`additionalPrompt`(str)、
`characters`(**ちょうど 6 個**)、`speakerSlotNum`(int)、`highlightedSlotNums`(int[])、`isDialogScript`(bool)、`placeText`(str)

`characters[スロット]`：`{name,faceId:"00",startingPos,endingPos,displayOrder:1,emoticon:-1,action:0,effect:0,appear:0,shapeOverride:0}`

- 空スロット：`name:""`、start/end `0`；有人スロット：**配列添字 = 現在スロット = `startingPos`**、`speakerSlotNum` = 発言者のスロット。
- スロット 1..5 にキャラ（**2 人同時は 3 + 5**、間隔を空けて重なり回避）；スロット 0 はナレーション／先生枠。
- ナレーション：`isDialogScript:false` かつ speaker を空スロットに向ける。

**リソース名 → ハッシュ**：`bgName` = **`xxHash32(名前, seed=0)`**（UTF-8 バイト）。
例：`BG_MainOffice`=1046815759、`BG_Black`=1047754314。`popup`/`sound`/`voice` は**文字列名**でハッシュではない。

---

## 4 つの対応表

### トランジション `transition`（長さはプリセットに内蔵、行ごとの変更不可）

| id | 効果 |
|---|---|
| `1408872282` | クロスフェード 500ms（**同一場面の昼夜変化にのみ**） |
| `3854440696` | 黒フェード 250ms |
| `3868567233` | 白フェード 250ms |
| `3957412172` | 左スライド |
| `1127535352` | 右スライド |
| `4152299906` | 上スライド |
| `3029168926` | 下スライド |
| `3344317924` | 黒い四角 |
| `1914875660` | 黒い円 |

### 登場／退場 `appear`（= `AppearType` 列挙）

| 値 | 名前 | 見え方 |
|---|---|---|
| `0` | None | なし（その場、既定） |
| `1` | **AL** | **左**へスライド ⇒ **右から登場**して見える |
| `2` | **AR** | **右**へスライド ⇒ **左から登場**して見える |
| `3` | A | その場で出現 |
| `4` | **DL** | **左**へスライド（左へ退場） |
| `5` | **DR** | **右**へスライド（右へ退場） |
| `6` | D | その場で消失 |

> **英字はスライドの向き**（`L`=左へ、`R`=右へ）で、**「どちらから来るか」ではありません**。
> **既定ルール：キャラは自分が立っている画面側から入る** —— 画面**右**は `1`、**左**は `2`、中央は `3`；
> 退場は右 `5`／左 `4`／中央 `6`。演出上必要なときだけ逆にします。

### モーション `action`

`1`=少ししゃがむ（物を取る時など）｜`2`=左に倒れる｜`3`=右に倒れる｜`4`=少し震える｜`5`=激しく震える｜
`6`=一度跳ぶ｜`7`=二度跳ぶ。（倒れた後、次の行でそのキャラを外さなければ自分で立ち上がります。）

### 見た目 `shapeOverride`

`1`=通話中（電話越しの電子姿）｜`2`=影（全身黒）｜`4`=接近（立ち絵拡大）。

### その他

- **感情マーク `emoticon`**：`-1`=無し ｜ `0`=Angry ｜ `1`=Chat ｜ `2`=Dot⋯ ｜ `3`=Exclaim！ ｜ `4`=Heart❤ ｜ `5`=Music♪ ｜
  `6`=Question? ｜ `7`=Respond ｜ `8`=Shy ｜ `9`=Surprise ｜ `10`=Sweat ｜ `11`=Twinkle✦ ｜ `12`=Upset ｜ `13`=Think ｜
  `14`=Bulb💡 ｜ `15`=Sad ｜ `16`=Sigh ｜ `17`=Steam ｜ `18`=Tear ｜ `19`=Zzz。
- **スロット = 画面位置**：`#1`=左、`#2`=中左、`#3`=中央、`#4`=中右、`#5`=右；`#0`=発言者／ナレーション。
- `bgmId` = 曲番号（`theme_NN` の NN）；`999` = ミュート。

---

## 追加命令とリッチテキスト

**追加命令**は `text` フィールドに書きます（複数行可、先頭に `#`）。UI でできないことを補います：

| 命令 | 効果 |
|---|---|
| `#wait;ミリ秒` | 会話の無い行を一定時間待ってから進める |
| `#bgshake` | 背景を一度揺らす |
| `#fx;AronaTouch` | 特殊効果（現在は序章の指紋認証のみ） |
| `#zmc;モード;X,Y;倍率;ms` | 背景の平行移動／拡大縮小（`instant` / `smooth`） |
| `#st;[X,Y];モード;フォントサイズ;` ｜ `#stm;…` | 画面テキスト（左寄せ／中央寄せ；`instant`/`smooth`/`serial`；**末尾のセミコロン必須**） |
| `#clearST` | 画面テキストを消す（自然には消えない） |
| `#<スロット>;fx;shot` | そのスロットのキャラに被弾エフェクト、例 `#3;fx;shot` |
| `#hidemenu` ｜ `#showmenu` | 右上メニューを隠す／戻す |

画面座標の原点は**画面中央**、幅は 2960 単位で固定。

**セリフのリッチテキスト**：`[size=px]テキスト[/size]`、`[RRGGBBAA]テキスト[-]`（色、例 `[FF0000]赤[-]`）、
`[ruby=ルビ]テキスト[/ruby]`；ネスト可（例 `[size=200][FF0000]x[/size][-]`）。

---

## 追加カスタムリソースパック（overrides）

**追加カスタムリソースパック**とは、AA に追加できるパック（`manifest.json` ＋ `characters/ bgs/ bgms/ sounds/ popups/`）で、
**カスタムキャラ／背景／BGM／SE／ポップアップ**を AA に足せます。

- **導入**：中身を AA の **`…\AzureArchive\data\overrides\`**（グローバル、全プロジェクトに適用）に展開。
  `projects\<プロジェクト名>\` に入れるとそのプロジェクト限定。**導入前に `overrides` をバックアップ**し、**AA を再起動**。
- 公式グループ配布のパックは**全体が AES 暗号化**（zip `compress_type=99`）のことが多く、通常のツール
  （.NET `ZipFile`、`tar`）では**0 バイトしか取り出せません** —— **7-Zip** か Python `pyzipper`（`AESZipFile` +
  `setpassword`）を使ってください。**解凍パスワードは公式ドキュメントの installation ページにあります。**
- `manifest.json` のキー：`CharacterOverrides / VoiceOverrides / PopupOverrides / SoundOverrides / BgOverrides /
  BgEffectOverrides / BgSpineOverrides / BgmOverrides`（無いキーは空扱い）。
- **`生成清单.ps1`** は**自作**パック用ツール：`characters/bgms/bgs/sounds/popups` を含むフォルダに置いて実行すると
  `manifest.json` を生成します。キャラフォルダ名は `名前_所属`（アンダースコア区切り、所属が無ければ省略）、中に
  `<名前>.skel` / `.atlas` / `.png` / `-avatar.png`。**完成済みのパックには不要です。**

---

## 環境とトラブルシューティング

| 項目 | 場所 |
|---|---|
| アプリ | `<どこか>\AzureArchive.exe` |
| データディレクトリ | `C:\Users\<あなた>\AppData\LocalLow\foxxlight\AzureArchive\data` |
| プロジェクト | `…\data\projects\<名前>.aap2`（UTF-8・BOM なし） |
| コンパイル成果物 | `…\data\saves\<名前>.aas`（＋ `.build.json`） |
| カスタムリソース | `…\data\overrides\` |
| リソースキャッシュ | `C:\Users\<あなた>\AppData\LocalLow\Unity\foxxlight_AzureArchive`（約 6 GB、**ハッシュ名で `.bundle` 拡張子なし**） |

### 「リソースを読み込めない」の直し方

症状：UI が「リソースを検出できない」と表示し、`Player.log` に
`…ScenarioResourceManager.AddrLoadUrl/{texts,flatdata,databases}_assets_all.bundle` の **404** が並ぶ。

**重要な認識：`user_settings.json` の `completeResStructVer: 0` は「結果」であって原因ではない** —— キャッシュを
読めないからアプリが 0 を書くのです。**`11` に戻すだけではダメ**（次回起動まで症状を抑えるだけ）。

本当に見るべきは：**アプリが起動時に見ている `LocalLow` ルートに、次の 2 つが揃っているか**：

- Addressables カタログ：`foxxlight\AzureArchive\com.unity.addressables\`
- リソースキャッシュ：`Unity\foxxlight_AzureArchive\`（約 6 GB）

> ⚠ **同じ PC に 2 つの `LocalLow` ルートがあり得ます**（MSIX リダイレクト）：**ストア版／パッケージ版**アプリから
> 起動したプロセスの `AppData\LocalLow` は `…\AppData\Local\Packages\<アプリ>\LocalCache\LocalLow\` に
> リダイレクトされ、**エクスプローラ**から起動したプロセスは本当の `C:\Users\<あなた>\AppData\LocalLow\` を見ます。
> **まずキャッシュがどちら側かを確認**し、アプリが実際に使う側へ持って行きます（コピー、またはディレクトリ ジャンクション）。
> 既製スクリプト：**`修复资源缓存_双击运行.cmd`**（ダブルクリックで OK、両ルートの有無を先に報告します）。

直った判定：ログの **404 = 0**、かつ `completeResStructVer` が**もう 0 に書き戻されない**。

---

## ハマりどころ（必守）

1. 先頭行 `AAP2` の直後は**単一 LF**（CRLF 不可）。
2. **`bgName:0` / `bgmId:0` は「クリア」であって「継続」ではない** → **毎行で現在の `bgName`(ハッシュ) +
   `bgFriendlyName` + `bgmId` を書き直す**。さもないと 2 行目以降で背景／音楽が消えて真っ黒に。`transition` は
   **実際に場面が変わる行だけ**に書き、他は `0`。
3. **行をまたぐキャラの「移動」（`endingPos` を別スロットに変える）は検証エラーになる**（汎用の `failed validation`
   しか出ない）→ 毎行スロット固定（`startingPos = endingPos = スロット`）。
4. GUID は正しい 16 進 GUID であること；`characters` は**ちょうど 6 個**。
5. `.aap2` を書いたら**同名の `.aap`(v1) と古い `saves\<名前>.*` を消して**から AA を再起動（古い版を読む恐れ）。
6. 中国語は **UTF-8・BOM なし**；**PowerShell は `.ps1` を ANSI として読み、バッククォートをエスケープ** ——
   中国語やバッククォートを含む文字列は別の UTF-8 ファイルに置いて読み込み、コマンド文字列に直接埋めない。
7. このベータ版の `AzureArchive.exe --cli …` は**結果を出さず**、エディタ右下の MCP サービスも（ポート占有で）
   起動しないことが多い → **回り道せず「ファイルを書く ＋ 手動で『編集/再生』をクリック」**。

---

## サンプルプロジェクト

`examples/Schale_Demo.aap2`：シャーレのある日 —— 3 キャラ、4 背景、ポップアップ、SE、感情マーク、モーション、
二者択一の分岐、ナレーション、全 15 行。**`…\data\projects\` にコピーして名前を変えて使えます**
（先頭行 `AAP2` + LF を忘れずに）。

---

## バージョン履歴

同梱スキルはバージョン管理されており、全履歴は
[`claude-code-skill/azurearchive-scenario/CHANGELOG.md`](claude-code-skill/azurearchive-scenario/CHANGELOG.md) にあります。
現在 **v1.6**；系譜：`0.1 → … → 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6`。
`0.x` は成長期、`1.0` 以降が安定版；**`1.3` で重大なバグを修正**：登場／退場の向き（`appear`）—— 旧表は左右が逆でした。

---

## ライセンスとクレジット

- 本リポジトリの**テキスト資料とスクリプト**は **Tommhy0** によるもので、**CC BY-NC-SA 4.0**（表示・非営利・継承）で公開されています ——
  [`LICENSE`](LICENSE) を参照。
- **AA 本体およびすべてのゲーム素材**（立ち絵、背景、音楽、SE、テキスト等）の著作権は**各作者**に帰属します。
  本リポジトリはそれらを含みません。
- **AzureArchive** は **狐光体（Foxxlight）** が開発・保守し、公式サイト <https://aadoc.foxxlight.top/> のみで
  配布される**非公式・非営利**プロジェクトです。本リポジトリは第三者の資料であり、AA 公式や Yostar / Nexon /
  Nexon Games とは無関係です。

役に立ったら、対応表やトランジション id の追加 PR / Issue を歓迎します。
