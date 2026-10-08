# -*- coding: utf-8 -*-
"""生成 AzureArchive 工程：三一综合学园 补习部日常二创演示。
手写 JSON 拼装 -> 自检 -> 输出 .aap2（UTF-8 无 BOM，首行 AAP2+LF）。

出场/退场动画 appear（= AppearType 枚举；字母指"滑动方向" L=向左滑 / R=向右滑）：
  0=None
  1=AL → 从左向右滑入 ⇒ 观感"从【右】侧出现"（站画面右侧的人默认用这个）
  2=AR → 从右向左滑入 ⇒ 观感"从【左】侧出现"（站画面左侧的人默认用这个）
  3=A  → 原地出现
  4=DL → 向左滑出 ⇒ 向【左】侧消失（站画面左侧的人退场用）
  5=DR → 向右滑出 ⇒ 向【右】侧消失（站画面右侧的人退场用）
  6=D  → 原地消失
默认规则（用户 2026-10-08 确认）：**人物从与自己所在屏幕同一侧的那一边滑入**；
  左侧(slot1) 进场 2(AR)、退场 4(DL)；右侧(slot5) 进场 1(AL)、退场 5(DR)；中间(slot3) 3(A)/6(D)。
  仅在剧情需要时才反向（如绕到反侧、横穿）。
"""
import json, uuid, os

# ---------- 背景常量 (名字, xxHash32) ----------
CR  = ("BG_TrinityClassRoom",        2374730366)  # 三一教室
LIB = ("BG_TrinityOldLibrary",       3386676547)  # 旧图书馆
SUN = ("BG_TrinityClassRoom_Sunset", 3339826718)  # 黄昏教室

BGM_COMEDY = 7    # Unwelcome School 校园搞笑
BGM_AFTER  = 128  # After School Dessert 放学甜点
BGM_WARM   = 34   # Aoharu 青春（收尾）

T_BLACK = 3854440696   # 黑淡
T_WHITE = 3868567233   # 白淡
T_LEFT  = 3957412172   # 向左滑动

HIHUMI = "히후미"   # 日富美
HANAKO = "하나코"   # 花子
KOHARU = "코하루"   # 小春
AZUSA  = "아즈사"   # 梓

S_KOHARU, S_HIHUMI, S_RIGHT = 1, 3, 5   # 1=画面左  3=中  5=画面右

# appear 取值（AppearType）
NONE, AL, AR, A, DL, DR, D = 0, 1, 2, 3, 4, 5, 6
APPEAR_RIGHT = AL   # 站画面右侧的人：从右滑入
APPEAR_LEFT  = AR   # 站画面左侧的人：从左滑入
APPEAR_MID   = A    # 中间：原地出现
LEAVE_LEFT   = DL   # 站画面左侧的人：向左滑出
LEAVE_RIGHT  = DR   # 站画面右侧的人：向右滑出
LEAVE_MID    = D    # 中间：原地消失


def empty():
    return dict(name="", faceId="00", startingPos=0, endingPos=0, displayOrder=1,
                emoticon=-1, action=0, effect=0, appear=0, shapeOverride=0)


def slot(i, name, faceId="00", emoticon=-1, action=0, appear=0, shapeOverride=0):
    return dict(name=name, faceId=faceId, startingPos=i, endingPos=i, displayOrder=1,
                emoticon=emoticon, action=action, effect=0, appear=appear,
                shapeOverride=shapeOverride)


def chars(d):
    return [d.get(i, empty()) for i in range(6)]


_n = [0]
def lid():
    _n[0] += 1
    return "d1000000-0000-0000-0000-%012d" % _n[0]


def line(text, bg, bgm, slots=None, speaker=0, narr=True,
         trans=0, sound="", popup=""):
    slots = slots or {}
    return {
        "LineId": lid(),
        "text": text, "popup": popup, "bgEffect": 0,
        "bgName": bg[1], "bgFriendlyName": bg[0],
        "sound": sound, "voice": "", "transition": trans, "bgmId": bgm,
        "selectionGroup": 0, "additionalPrompt": "",
        "characters": chars(slots),
        "speakerSlotNum": speaker,
        "highlightedSlotNums": [],
        "isDialogScript": (not narr),
        "placeText": ""
    }


# ================= 节点 1：放学后的教室 =================
n1_lines = [
    line("放学后的三一综合学园。夕阳把教室的窗框，镀上了一层暖金色。",
         CR, BGM_COMEDY, trans=T_BLACK),
    line("补习部的活动时间——名义上如此。可今天的教室，似乎格外热闹。",
         CR, BGM_COMEDY),
    line("大家——今天我们把上次的模拟考卷，一题一题讲完，好吗？",
         CR, BGM_COMEDY, narr=False, speaker=S_HIHUMI, sound="SE_SitChair_01a",
         slots={S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03", appear=APPEAR_MID)}),
    line("哎呀，日富美。你今天又把发卡戴反了哦？♪",
         CR, BGM_COMEDY, narr=False, speaker=S_RIGHT,
         slots={S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03", emoticon=5, appear=APPEAR_RIGHT)}),
    line("诶——？！骗、骗人的吧！",
         CR, BGM_COMEDY, narr=False, speaker=S_HIHUMI,
         slots={S_HIHUMI: slot(S_HIHUMI, HIHUMI, "04", emoticon=8, action=4),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
    line("骗你的～你果然会当真呢。真可爱。",
         CR, BGM_COMEDY, narr=False, speaker=S_RIGHT,
         slots={S_HIHUMI: slot(S_HIHUMI, HIHUMI, "04", emoticon=8),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03", emoticon=11)}),
    line("花子……请你认真一点。我们下周，是真的要考试了。",
         CR, BGM_COMEDY, narr=False, speaker=S_HIHUMI,
         slots={S_HIHUMI: slot(S_HIHUMI, HIHUMI, "05", emoticon=10),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
    line("就在这时，走廊尽头传来一阵急促的脚步声。",
         CR, BGM_COMEDY, sound="SE_Run_02",
         slots={S_HIHUMI: slot(S_HIHUMI, HIHUMI, "05"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
    line("呜哇——！谁、谁把一摞试卷，堆在教室门口了？！",
         CR, BGM_COMEDY, narr=False, speaker=S_KOHARU,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "02", emoticon=9, appear=APPEAR_LEFT),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "05"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
    line("……可我明明，把试卷都收进柜子里了呀？",
         CR, BGM_COMEDY, narr=False, speaker=S_HIHUMI,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "02"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "05", emoticon=6),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
    line("会不会是……风，把它搬到门口的呢？",
         CR, BGM_COMEDY, narr=False, speaker=S_RIGHT,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "02"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "05"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03", emoticon=13)}),
    line("风才不会把试卷摞成一摞呢！",
         CR, BGM_COMEDY, narr=False, speaker=S_HIHUMI,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "02"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "06", emoticon=12, action=6),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
]

# ================= 节点 2：旧图书馆 =================
n2_lines = [
    line("于是，一行人循着线索，来到了旧图书馆。",
         LIB, BGM_AFTER, trans=T_LEFT, sound="SE_DoorSlowOpen_01",
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "01"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
    line("啊，我好像想起来了——我把一摞“讲义”，忘在图书馆的桌子上了。那我先走一步啦～",
         LIB, BGM_AFTER, narr=False, speaker=S_RIGHT,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "01"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03", emoticon=3, appear=LEAVE_RIGHT)}),
    line("花子一溜烟地不见了踪影。",
         LIB, BGM_AFTER, sound="SE_Run_03",
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "01")}),
    line("……花子前辈昨天，把这摞讲义忘在了这里。",
         LIB, BGM_AFTER, narr=False, speaker=S_RIGHT,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "01"),
                S_RIGHT: slot(S_RIGHT, AZUSA, "01", emoticon=2, appear=APPEAR_RIGHT)}),
    line("桌面上，整整齐齐地码着一摞字迹工整的讲义。",
         LIB, BGM_AFTER, popup="popup193",
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "01"),
                S_RIGHT: slot(S_RIGHT, AZUSA, "01")}),
    line("所以那个“自己长脚的试卷”……根本就是花子前辈搞的鬼？！！",
         LIB, BGM_AFTER, narr=False, speaker=S_KOHARU,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "06", emoticon=17, action=5),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "01"),
                S_RIGHT: slot(S_RIGHT, AZUSA, "01")}),
    line("……我只是，一直在旁边看着。",
         LIB, BGM_AFTER, narr=False, speaker=S_RIGHT,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "06"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "01"),
                S_RIGHT: slot(S_RIGHT, AZUSA, "01", emoticon=16)}),
    line("不管怎样，能找到讲义就好。梓，谢谢你。",
         LIB, BGM_AFTER, narr=False, speaker=S_HIHUMI,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "06"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03", emoticon=11),
                S_RIGHT: slot(S_RIGHT, AZUSA, "01")}),
    line("对了！既然都到图书馆了——不如就在这儿复习吧，这里最安静了！",
         LIB, BGM_AFTER, narr=False, speaker=S_KOHARU,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "03", emoticon=14, action=6),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03"),
                S_RIGHT: slot(S_RIGHT, AZUSA, "01")}),
    line("于是，旧图书馆就这么成了补习部的临时据点。",
         LIB, BGM_AFTER,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "03"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03"),
                S_RIGHT: slot(S_RIGHT, AZUSA, "01")}),
]

# ================= 节点 3：黄昏教室 =================
n3_lines = [
    line("等回过神来，窗外已经染上了暮色。",
         SUN, BGM_WARM, trans=T_WHITE,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03"),
                S_RIGHT: slot(S_RIGHT, AZUSA, "01")}),
    line("……我该回宿舍了。补习，就到这里吧。",
         SUN, BGM_WARM, narr=False, speaker=S_RIGHT,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03"),
                S_RIGHT: slot(S_RIGHT, AZUSA, "00", emoticon=16, appear=LEAVE_RIGHT)}),
    line("哎呀，你们居然真的复习了一整个下午？真是刻苦呢～",
         SUN, BGM_WARM, narr=False, speaker=S_RIGHT,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03", emoticon=5, appear=APPEAR_RIGHT)}),
    line("花子！！你才是一页都没翻吧！",
         SUN, BGM_WARM, narr=False, speaker=S_HIHUMI,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "06", emoticon=0, action=7),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
    line("怎么会呢？我可是很认真地……看着你们认真哦。",
         SUN, BGM_WARM, narr=False, speaker=S_RIGHT,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "01"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "06"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03", emoticon=11)}),
    line("呜……总感觉，今天的补习，完全没有效果……",
         SUN, BGM_WARM, narr=False, speaker=S_KOHARU,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "06", emoticon=18, action=4),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "06"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
    line("没关系啦。只要大家在一起——明天，也一定能顺利的。",
         SUN, BGM_WARM, narr=False, speaker=S_HIHUMI,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "06"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03", emoticon=4),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
    line("三一综合学园补习部的黄昏——就这样，在吵闹与笑声里，轻轻拉上了帷幕。",
         SUN, BGM_WARM,
         slots={S_KOHARU: slot(S_KOHARU, KOHARU, "00"),
                S_HIHUMI: slot(S_HIHUMI, HIHUMI, "03"),
                S_RIGHT: slot(S_RIGHT, HANAKO, "03")}),
]

G_ENTRY = "00000000-0000-0000-0000-000000000000"
G_N1 = "a1000001-0000-0000-0000-000000000001"
G_C1 = "a1000002-0000-0000-0000-000000000002"
G_N2 = "a1000003-0000-0000-0000-000000000003"
G_N3 = "a1000004-0000-0000-0000-000000000004"
G_EX = "a1000005-0000-0000-0000-000000000005"

def dlg(guid, lines, conn, y):
    return {"Scripts": lines, "NodeName": None, "Guid": guid,
            "ConnectionsTo": [conn], "X": 0.0, "Y": y, "Kind": "dialogue"}

nodes = [
    {"Title": "", "Header": "", "Guid": G_ENTRY, "ConnectionsTo": [G_N1],
     "X": 0.0, "Y": 0.0, "Kind": "entry"},
    dlg(G_N1, n1_lines, G_C1, -240.0),
    {"Options": [
        {"OptionId": "b1000001-0000-0000-0000-000000000001",
         "Text": "（走过去看看那摞“试卷”）", "TargetNodeId": G_N2},
        {"OptionId": "b1000002-0000-0000-0000-000000000002",
         "Text": "（无奈地扶额）……又来了。", "TargetNodeId": G_N2},
      ],
     "DefaultOptionId": None, "UnusedSelectionTexts": [],
     "Guid": G_C1, "X": 0.0, "Y": -480.0, "Kind": "choice"},
    dlg(G_N2, n2_lines, G_N3, -720.0),
    dlg(G_N3, n3_lines, G_EX, -960.0),
    {"IsEnding": True, "EndText": "", "NeHeader": "", "NeTitle": "",
     "NeScriptDirty": line("", ("", 0), 0, narr=True),
     "Guid": G_EX, "ConnectionsTo": [], "X": 0.0, "Y": -1200.0, "Kind": "exit"},
]

project = {
    "LegacySourceVersion": "absent",
    "FormatVersion": 2,
    "ProjectId": str(uuid.uuid4()),
    "ProjectName": "三一补习部的放学后",
    "PreviewBgName": CR[1],
    "PreviewHeader": "",
    "PreviewTitle": "",
    "nodes": nodes,
}

# ---------- 自检 ----------
assert len(nodes) == 6
for nd in nodes:
    if nd["Kind"] == "dialogue":
        assert len({x["LineId"] for x in nd["Scripts"]}) == len(nd["Scripts"])
        for s in nd["Scripts"]:
            assert len(s["characters"]) == 6, "characters 必须是 6 项"
            if s["isDialogScript"]:
                assert s["characters"][s["speakerSlotNum"]]["name"], "发言栏必须有人"

text = "AAP2\n" + json.dumps(project, ensure_ascii=False, indent=2)
raw = text.encode("utf-8")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "三一补习部的放学后.aap2")
with open(out, "wb") as f:
    f.write(raw)

with open(out, "rb") as f:
    b = f.read()
assert b[:5] == b"AAP2\n", "首行标记必须是 AAP2 + 单个 LF"
json.loads(b[5:].decode("utf-8"))
print("OK ->", out)
print("bytes:", len(b), " lines:", sum(len(n['Scripts']) for n in nodes if n['Kind'] == 'dialogue'))
print("appear 用到的值:", sorted({c['appear'] for n in nodes if n['Kind'] == 'dialogue' for s in n['Scripts'] for c in s['characters'] if c['appear']}))
