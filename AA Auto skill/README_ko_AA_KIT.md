# AA_KIT · AzureArchive 시나리오 제작 키트

![license](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-lightgrey)
![author](https://img.shields.io/badge/by-Tommhy0-informational)
![platform](https://img.shields.io/badge/platform-Windows-0078D6)
![base](https://img.shields.io/badge/AzureArchive-1.0--beta-orange)
![langs](https://img.shields.io/badge/docs-中文%20%7C%20EN%20%7C%20日本語%20%7C%20한국어-blue)

**『블루 아카이브』 시나리오를 만들고 싶은 모든 분**을 위한 자립형 키트 —— **직접 써도** 되고, **AI 어시스턴트에게
맡겨도** 됩니다. 핵심은 한 문장입니다: **AzureArchive의 프로젝트 파일 `.aap2`는 그냥 JSON이고, Unity 노드
에디터를 클릭하는 것보다 직접 쓰는 게 훨씬 안정적이다.**

> 언어: [中文](README.md) ｜ [English](README.en.md) ｜ [日本語](README.ja.md) ｜ [**한국어**](README.ko.md)

> AzureArchive(이하 **AA**)는 『블루 아카이브』의 **비공식** 시나리오 에디터로, **狐光体(Foxxlight)** 가 개발·유지하며
> 공식 사이트 <https://aadoc.foxxlight.top/> 에서만 배포됩니다. 이 저장소는 **제3자** 자료이며 AA 공식과 무관하고,
> **게임 에셋은 일절 포함하지 않습니다**.

---

## 목차

- [이것은 무엇인가](#이것은-무엇인가)
- [저장소 구조](#저장소-구조)
- [빠른 시작](#빠른-시작)
- [지원 기능](#지원-기능)
- [참고 자료(6개 표)](#참고-자료6개-표)
- [`.aap2` 요약](#aap2-요약)
- [4개 대조표](#4개-대조표)
- [추가 명령과 리치 텍스트](#추가-명령과-리치-텍스트)
- [추가 커스텀 리소스 팩(overrides)](#추가-커스텀-리소스-팩overrides)
- [환경과 문제 해결](#환경과-문제-해결)
- [함정(반드시 준수)](#함정반드시-준수)
- [예제 프로젝트](#예제-프로젝트)
- [버전 기록](#버전-기록)
- [라이선스와 크레딧](#라이선스와-크레딧)

---

## 이것은 무엇인가

**AA의 프로젝트 파일 `.aap2`는 그냥 JSON입니다.** Unity 에디터의 버튼을 클릭하는(자주 반응하지 않는) 대신,
**이 JSON을 직접 작성**하세요 —— 더 안정적이고, 버전 관리도 되고, 스크립트로 일괄 생성도 됩니다. 이 키트는
AA 시나리오 제작에 필요한 **모든 필드·대조표·함정**을 한곳에 모았습니다:

```
.aap2 작성  →  AA에서 "편집" 클릭(열면 자동 저장 + 컴파일)  →  "감상 모드"로 재생해 확인
```

이 저장소가 제공하는 것:

1. **6개의 참고 표** + `xxhash32.py`(리소스 이름 해시 계산용);
2. **예제 프로젝트** `Schale_Demo.aap2`(이름만 바꿔 바로 사용/참고);
3. **문제 해결 스크립트** `修复资源缓存_双击运行.cmd`("리소스를 불러올 수 없음" 수정);
4. **동봉 AI 스킬** `azurearchive-scenario`(Claude / Claude Code용) —— 설치하면 AI가 같은 규격대로 `.aap2`를
   생성합니다. **AI는 선택 사항**입니다: 직접 쓰든 AI에게 맡기든 같은 규격을 따릅니다.

---

## 저장소 구조

```
AA_KIT/
├─ README.md / README.en.md / README.ja.md / README.ko.md   4개 언어 설명
├─ LICENSE                          CC BY-NC-SA 4.0
├─ azurearchive-scenario.skill      동봉 AI 스킬 패키지(Claude 데스크톱에서 가져오기 가능)
├─ claude-code-skill/
│   └─ azurearchive-scenario/       스킬 폴더(Claude Code용; 핵심은 SKILL.md)
│       ├─ SKILL.md                 스킬 본문(v1.6)
│       ├─ README.md                스킬 설명
│       ├─ CHANGELOG.md             변경 기록(0.1 → 1.6)
│       ├─ references/              6개 표 + xxhash32.py
│       └─ examples/Schale_Demo.aap2  예제 프로젝트
├─ 参考资料/                        위 references/의 낱개 사본
├─ 示例工程_Schale_Demo.aap2         예제 프로젝트(낱개 사본)
└─ 修复资源缓存_双击运行.cmd          "리소스 불러오기 실패" 원클릭 수정
```

> 참고: 이 저장소는 **텍스트 자료와 스크립트만 포함하며 게임 에셋은 없습니다**. **AA 본체**와 **공식 리소스 팩**은
> 직접 준비하세요.

---

## 빠른 시작

### 경로 A: 직접 작성

1. 이 README와 [`参考资料/`](#참고-자료6개-표)를 읽고 [예제 프로젝트](#예제-프로젝트)를 참고;
2. 아무 편집기(또는 간단한 스크립트)로 `.aap2` 생성;
3. `…\data\projects\`에 넣고, AA에서 **프로젝트 모드 → 선택 → 편집**, 이어서 **감상 모드**로 재생.

### 경로 B: AI 어시스턴트에게 맡기기(동봉 스킬)

1. **스킬 설치**:
   - Claude 데스크톱: 앱의 "스킬 → 추가"에서 `azurearchive-scenario.skill` 선택;
   - Claude Code: `claude-code-skill/azurearchive-scenario/`를 skills 디렉터리로 복사(예
     `~/.claude/skills/azurearchive-scenario/`, Windows는 `C:\Users\<사용자>\.claude\skills\azurearchive-scenario\`).
2. AI에게 "azurearchive-scenario 스킬로 BA 시나리오를 써줘…"라고 요청;
3. AI가 `…\data\projects\`에 `.aap2`를 작성; 그다음 위와 같이 "편집"을 누르고 재생해 확인.

> 컴파일 성공 ≠ 확인 완료 —— **반드시 직접 한 번 재생해 보세요**.

---

## 지원 기능

| 기능 | 설명 |
|---|---|
| 시나리오/노드 | 입구/스크립트(대사)/선택(분기)/출구 4종; 나레이션, 다중 엔딩 연결 |
| 일러스트 | **한국어 원명**으로 지정; 5개 슬롯(왼쪽/중간왼쪽/가운데/중간오른쪽/오른쪽), 최대 5명 동시 |
| 표정 | 캐릭터별 `faceId`(`"00"`..`"17"`, 사용 가능 번호는 캐릭터마다 다름) |
| 감정 마크 | `emoticon` 총 20종(♪ 콧노래, ❤ 하트, ✦ 반짝, 땀, ⁉, 💡 …) |
| 모션 | 웅크리기/쓰러지기/떨기/뛰기 등 7종 |
| 등장/퇴장 | 좌우 슬라이드 입퇴장, 제자리 등장/소멸(**기본은 "같은 쪽에서 입장"**, 대조표 참조) |
| 배경/트랜지션 | 장면 전환 + 9종 트랜지션(슬라이드, 흑/백 페이드, 사각형, 원 …) |
| 음악/효과음/팝업 | BGM(242곡), 효과음(697개 문자열 이름), 팝업 이미지(캐릭터 CG/범용) |
| 추가 명령 | `#wait` / `#bgshake` / `#zmc` / `#st` 화면 텍스트 등(UI로는 못 하는 것) |
| 리치 텍스트 | `[size=]` 확대, `[RRGGBBAA]` 색, `[ruby=]` 루비 |
| 추가 리소스 팩 | overrides로 커스텀 캐릭터/배경/BGM/효과음/팝업 설치·확인 |

---

## 참고 자료(6개 표)

`references/`(및 `参考资料/`)에 조회용 권위 목록(검색하기 쉬운 Markdown)이 있습니다:

| 파일 | 내용 |
|---|---|
| `人物表情对照表.md` | **401개 캐릭터**의 `faceId → 표정`(133개 NPC/가면은 데이터 없음); **사용 가능 번호는 캐릭터마다 다름**(시로코 7, 호시노 17) |
| `角色名清单.md` | **1467개** 캐릭터/NPC의 **한국어 원명**(`characters[].name`에 기입, `부상`/`테러` 등 접미사 포함) |
| `BGM用途注释清单.md` | 242곡의 `bgmId → 곡명/작곡가/권장 용도`(용도는 곡명 기반 추정 —— **청음으로 확인**) |
| `弹窗图注释清单.md` | 203장의 무명 팝업 이미지(`popup02..popup221`) 설명 |
| `音效名清单.md` | 697개 효과음 이름(`sound` 필드용, 예 `SE_DoorOpen_01`) |
| `额外资源包清单.md` | 한 추가 팩(`Win20241023前-20260818`)의 캐릭터/배경/BGM/효과음/팝업 목록 |
| `bgm_table.tsv` | BGM 원본 표(번호/곡명/작곡가) |
| `xxhash32.py` | `bgName` 계산용 xxHash32(seed=0) 참조 구현 |

---

## `.aap2` 요약

**첫 줄은 반드시 `AAP2` + 단일 LF(0x0A)**(CRLF면 `Unsupported AAP file marker`); 이후가 JSON(UTF-8, **BOM 없음**).

```json
{ "LegacySourceVersion":"absent", "FormatVersion":2,
  "ProjectId":"<guid>", "ProjectName":"...",
  "PreviewBgName":<uint 배경 해시>, "PreviewHeader":"...", "PreviewTitle":"...",
  "nodes":[ ... ] }
```

노드 `Kind`:

- `entry`: `{Title,Header,Guid:"00000000-0000-0000-0000-000000000000",ConnectionsTo:[<guid>],X,Y,Kind:"entry"}`
- `dialogue`: `{Scripts:[ScriptData],NodeName:null,Guid,ConnectionsTo:[...],X,Y,Kind:"dialogue"}`
- `choice`: `{Options:[{OptionId,Text,TargetNodeId}],DefaultOptionId:null,UnusedSelectionTexts:[],Guid,X,Y,Kind:"choice"}`
  (**ConnectionsTo 없음**; 두 선택지가 같은 `TargetNodeId`를 가리키면 "선택은 다르지만 전개는 같음")
- `exit`: `{IsEnding,EndText,NeHeader,NeTitle,NeScriptDirty:<ScriptData>,Guid,ConnectionsTo:[],X,Y,Kind:"exit"}`

`ScriptData`: `LineId`(guid), `text`, `popup`(str), `bgEffect`(uint), `bgName`(uint 배경 해시), `bgFriendlyName`(str),
`sound`(str), `voice`(str), `transition`(uint), `bgmId`(**int**), `selectionGroup`(uint), `additionalPrompt`(str),
`characters`(**정확히 6개**), `speakerSlotNum`(int), `highlightedSlotNums`(int[]), `isDialogScript`(bool), `placeText`(str)

`characters[슬롯]`: `{name,faceId:"00",startingPos,endingPos,displayOrder:1,emoticon:-1,action:0,effect:0,appear:0,shapeOverride:0}`

- 빈 슬롯: `name:""`, start/end `0`; 캐릭터 슬롯: **배열 인덱스 = 현재 슬롯 = `startingPos`**, `speakerSlotNum` = 발화자 슬롯.
- 슬롯 1..5에 캐릭터(**2명 동시는 3 + 5**, 간격을 두어 겹침 방지); 슬롯 0은 나레이션/선생님 자리.
- 나레이션: `isDialogScript:false`, speaker를 빈 슬롯으로.

**리소스 이름 → 해시**: `bgName` = **`xxHash32(이름, seed=0)`**(UTF-8 바이트 기준).
예: `BG_MainOffice`=1046815759, `BG_Black`=1047754314. `popup`/`sound`/`voice`는 **문자열 이름**이며 해시가 아닙니다.

---

## 4개 대조표

### 트랜지션 `transition`(길이는 프리셋에 내장, 줄 단위 변경 불가)

| id | 효과 |
|---|---|
| `1408872282` | 크로스페이드 500ms(**같은 장면의 낮↔밤 변화에만**) |
| `3854440696` | 검은 페이드 250ms |
| `3868567233` | 흰 페이드 250ms |
| `3957412172` | 왼쪽 슬라이드 |
| `1127535352` | 오른쪽 슬라이드 |
| `4152299906` | 위로 슬라이드 |
| `3029168926` | 아래로 슬라이드 |
| `3344317924` | 검은 사각형 |
| `1914875660` | 검은 원 |

### 등장/퇴장 `appear`(= `AppearType` 열거형)

| 값 | 이름 | 보이는 방식 |
|---|---|---|
| `0` | None | 없음(제자리, 기본) |
| `1` | **AL** | **왼쪽**으로 슬라이드 ⇒ **오른쪽에서 등장**하는 것처럼 보임 |
| `2` | **AR** | **오른쪽**으로 슬라이드 ⇒ **왼쪽에서 등장**하는 것처럼 보임 |
| `3` | A | 제자리 등장 |
| `4` | **DL** | **왼쪽**으로 슬라이드(왼쪽으로 퇴장) |
| `5` | **DR** | **오른쪽**으로 슬라이드(오른쪽으로 퇴장) |
| `6` | D | 제자리 소멸 |

> **알파벳은 슬라이드 방향**(`L`=왼쪽으로, `R`=오른쪽으로)이며, **"어느 쪽에서 오는가"가 아닙니다**.
> **기본 규칙: 캐릭터는 자신이 서 있는 화면 쪽에서 입장** —— 화면 **오른쪽**은 `1`, **왼쪽**은 `2`, 가운데는 `3`;
> 퇴장은 오른쪽 `5`/왼쪽 `4`/가운데 `6`. 연출상 필요할 때만 반대로.

### 모션 `action`

`1`=잠깐 웅크리기(물건 집을 때 흔히 사용)｜`2`=왼쪽으로 쓰러짐｜`3`=오른쪽으로 쓰러짐｜`4`=살짝 떨림｜
`5`=격하게 떨림｜`6`=한 번 점프｜`7`=두 번 점프. (쓰러진 뒤 다음 줄에서 그 캐릭터를 빼지 않으면 스스로 일어납니다.)

### 외형 `shapeOverride`

`1`=통화 중(전화 반대편 전자 형상)｜`2`=그림자(전신 검정)｜`4`=접근(일러스트 확대).

### 기타

- **감정 마크 `emoticon`**: `-1`=없음 ｜ `0`=Angry ｜ `1`=Chat ｜ `2`=Dot⋯ ｜ `3`=Exclaim！ ｜ `4`=Heart❤ ｜ `5`=Music♪ ｜
  `6`=Question? ｜ `7`=Respond ｜ `8`=Shy ｜ `9`=Surprise ｜ `10`=Sweat ｜ `11`=Twinkle✦ ｜ `12`=Upset ｜ `13`=Think ｜
  `14`=Bulb💡 ｜ `15`=Sad ｜ `16`=Sigh ｜ `17`=Steam ｜ `18`=Tear ｜ `19`=Zzz.
- **슬롯 = 화면 위치**: `#1`=왼쪽, `#2`=중간왼쪽, `#3`=가운데, `#4`=중간오른쪽, `#5`=오른쪽; `#0`=발화자/나레이션.
- `bgmId` = 곡 번호(`theme_NN`의 NN); `999` = 음소거.

---

## 추가 명령과 리치 텍스트

**추가 명령**은 `text` 필드에 작성합니다(여러 줄 가능, 접두사 `#`). UI로 못 하는 것을 보완합니다:

| 명령 | 효과 |
|---|---|
| `#wait;밀리초` | 대사 없는 줄을 일정 시간 기다린 뒤 진행 |
| `#bgshake` | 배경을 한 번 흔듦 |
| `#fx;AronaTouch` | 특수 효과(현재는 프롤로그 지문 인식만) |
| `#zmc;모드;X,Y;배율;ms` | 배경 이동/확대·축소(`instant` / `smooth`) |
| `#st;[X,Y];모드;글자크기;` ｜ `#stm;…` | 화면 텍스트(각각 왼쪽 정렬/가운데; `instant`/`smooth`/`serial`; **끝 세미콜론 필수**) |
| `#clearST` | 화면 텍스트 지우기(저절로 사라지지 않음) |
| `#<슬롯번호>;fx;shot` | 해당 슬롯 캐릭터 피격 효과, 예 `#3;fx;shot` |
| `#hidemenu` ｜ `#showmenu` | 우측 상단 메뉴 숨기기/되돌리기 |

화면 좌표 원점은 **화면 중앙**이며, 너비는 2960 단위로 고정입니다.

**대사 리치 텍스트**: `[size=px]텍스트[/size]`, `[RRGGBBAA]텍스트[-]`(색, 예 `[FF0000]빨강[-]`),
`[ruby=독음]텍스트[/ruby]`; 중첩 가능(예 `[size=200][FF0000]x[/size][-]`).

---

## 추가 커스텀 리소스 팩(overrides)

**추가 커스텀 리소스 팩**은 AA에 추가하는 팩(`manifest.json` + `characters/ bgs/ bgms/ sounds/ popups/`)으로,
**커스텀 캐릭터/배경/BGM/효과음/팝업**을 AA에 더합니다.

- **설치**: 내용물을 AA의 **`…\AzureArchive\data\overrides\`**(전역, 모든 프로젝트에 적용)에 압축 해제.
  `projects\<프로젝트명>\`에 넣으면 해당 프로젝트에만 적용. **설치 전 `overrides`를 백업**하고 **AA를 재시작**하세요.
- 공식 그룹 배포 팩은 대개 **전체가 AES 암호화**되어 있습니다(zip `compress_type=99`): 일반 도구
  (.NET `ZipFile`, `tar`)로는 **0바이트만 나옵니다** —— **7-Zip** 또는 Python `pyzipper`(`AESZipFile` +
  `setpassword`)를 쓰세요. **해제 비밀번호는 공식 문서 installation 페이지에 있습니다.**
- `manifest.json` 키: `CharacterOverrides / VoiceOverrides / PopupOverrides / SoundOverrides / BgOverrides /
  BgEffectOverrides / BgSpineOverrides / BgmOverrides`(없는 키는 빈 값 처리).
- **`生成清单.ps1`** 은 **직접 만든** 팩용 도구입니다: `characters/bgms/bgs/sounds/popups`가 있는 폴더에 넣고 실행하면
  `manifest.json`을 생성합니다. 캐릭터 폴더명은 `이름_소속`(밑줄 구분, 소속 없으면 생략), 안에
  `<이름>.skel` / `.atlas` / `.png` / `-avatar.png`. **완성된 팩에는 필요 없습니다.**

---

## 환경과 문제 해결

| 항목 | 위치 |
|---|---|
| 프로그램 | `<어딘가>\AzureArchive.exe` |
| 데이터 폴더 | `C:\Users\<사용자>\AppData\LocalLow\foxxlight\AzureArchive\data` |
| 프로젝트 | `…\data\projects\<이름>.aap2`(UTF-8, BOM 없음) |
| 컴파일 결과물 | `…\data\saves\<이름>.aas`(+ `.build.json`) |
| 커스텀 리소스 | `…\data\overrides\` |
| 리소스 캐시 | `C:\Users\<사용자>\AppData\LocalLow\Unity\foxxlight_AzureArchive`(약 6 GB, **해시 이름이며 `.bundle` 확장자 없음**) |

### "리소스를 불러올 수 없음" 해결

증상: UI가 "리소스를 감지할 수 없음"을 표시하고, `Player.log`에
`…ScenarioResourceManager.AddrLoadUrl/{texts,flatdata,databases}_assets_all.bundle` **404**가 쏟아집니다.

**핵심 인식: `user_settings.json`의 `completeResStructVer: 0`은 "결과"이지 원인이 아닙니다** —— 캐시를 못 읽어서
앱이 0을 쓰는 것입니다. **`11`로 되돌리는 것만으로는 안 됩니다**(다음 실행까지만 증상을 억제).

정말 봐야 할 것은: **앱이 시작할 때 보는 `LocalLow` 루트에 다음 두 가지가 있는가**입니다:

- Addressables 카탈로그: `foxxlight\AzureArchive\com.unity.addressables\`
- 리소스 캐시: `Unity\foxxlight_AzureArchive\`(약 6 GB)

> ⚠ **한 PC에 두 개의 `LocalLow` 루트가 있을 수 있습니다**(MSIX 리디렉션): **스토어판/패키지판** 앱에서 시작한
> 프로세스의 `AppData\LocalLow`는 `…\AppData\Local\Packages\<앱>\LocalCache\LocalLow\`로 리디렉션되고,
> **탐색기**에서 시작한 프로세스는 실제 `C:\Users\<사용자>\AppData\LocalLow\`를 봅니다. **먼저 캐시가 어느 쪽인지
> 확인**하고, 앱이 실제로 쓰는 쪽으로 옮기세요(복사 또는 디렉터리 정션). 기성 스크립트:
> **`修复资源缓存_双击运行.cmd`**(더블클릭만 하면 되고, 두 루트의 존재 여부를 먼저 보고합니다).

해결 판정: 로그 **404 = 0**, 그리고 `completeResStructVer`가 **더 이상 0으로 기록되지 않음**.

---

## 함정(반드시 준수)

1. 첫 줄 `AAP2` 뒤에는 **단일 LF**(CRLF 불가).
2. **`bgName:0` / `bgmId:0`은 "초기화"이지 "유지"가 아닙니다** → **매 줄마다 현재 `bgName`(해시) + `bgFriendlyName` +
   `bgmId`를 다시 써야** 합니다. 그러지 않으면 2번째 줄부터 배경/음악이 사라져 새까맣게 됩니다. `transition`은
   **실제로 장면이 바뀌는 줄에만** 쓰고 나머지는 `0`.
3. **줄을 넘어 캐릭터를 "이동"(`endingPos`를 다른 슬롯으로)하면 프로젝트 검증에 실패**합니다(일반적인
   `failed validation`만 표시) → 매 줄 슬롯 고정(`startingPos = endingPos = 슬롯`).
4. GUID는 유효한 16진수 GUID여야 합니다; `characters`는 **정확히 6개**.
5. `.aap2`를 쓴 뒤 **같은 이름의 `.aap`(v1)과 예전 `saves\<이름>.*`를 지우고** AA를 재시작(구버전을 읽을 수 있음).
6. 중국어는 **UTF-8, BOM 없음**; **PowerShell은 `.ps1`을 ANSI로 읽고 백틱을 이스케이프**합니다 —— 중국어나 백틱이
   포함된 문자열은 별도 UTF-8 파일에 두고 읽어들이세요(명령 문자열에 직접 넣지 말 것).
7. 이 베타의 `AzureArchive.exe --cli …`는 **결과를 출력하지 않으며**, 에디터 우측 하단 MCP 서비스도 (포트 점유로)
   자주 뜨지 않습니다 → **우회하지 말고 "파일 작성 + 수동으로 '편집/재생' 클릭"**.

---

## 예제 프로젝트

`examples/Schale_Demo.aap2`: 샬레의 당직 일상 —— 3캐릭터, 4배경, 팝업, 효과음, 감정 마크, 모션, 양자택일 분기,
나레이션, 총 15줄. **`…\data\projects\`로 복사해 이름을 바꿔 바로 사용**할 수 있습니다(첫 줄 `AAP2` + LF 잊지 마세요).

---

## 버전 기록

동봉 스킬은 버전 관리되며, 전체 기록은
[`claude-code-skill/azurearchive-scenario/CHANGELOG.md`](claude-code-skill/azurearchive-scenario/CHANGELOG.md) 에 있습니다.
현재 **v1.6**; 계보: `0.1 → … → 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6`.
`0.x`는 성장기, `1.0`부터 안정판; **`1.3`에서 중대한 버그를 수정**: 등장/퇴장 방향(`appear`) —— 옛 표는 좌우가 반대였습니다.

---

## 라이선스와 크레딧

- 이 저장소의 **텍스트 자료와 스크립트**는 **Tommhy0** 이 정리했으며, **CC BY-NC-SA 4.0**(저작자표시 · 비영리 · 동일조건변경허락)으로
  배포됩니다 —— [`LICENSE`](LICENSE) 참조.
- **AA 본체 및 모든 게임 에셋**(일러스트, 배경, 음악, 효과음, 텍스트 등)의 저작권은 **각 저작자**에게 있습니다.
  이 저장소는 이를 포함하지 않습니다.
- **AzureArchive**는 **狐光体(Foxxlight)** 가 개발·유지하며 공식 사이트 <https://aadoc.foxxlight.top/> 에서만 배포하는
  **비공식·비영리** 프로젝트입니다. 이 저장소는 제3자 자료이며 AA 공식 및 Yostar / Nexon / Nexon Games와 무관합니다.

도움이 되셨다면, 대조표와 트랜지션 id 추가 PR / Issue를 환영합니다.
