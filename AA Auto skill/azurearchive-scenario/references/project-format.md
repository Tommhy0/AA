# AAP2 工程格式

文件是 `AAP2\n` 文件头加 JSON，不能对整个文件直接调用 JSON 解析器。以下字段基于本包 v1.6 样本。

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
- `choice`  `{Options:[{OptionId,Text,TargetNodeId}],DefaultOptionId:"<选定选项的OptionId>",UnusedSelectionTexts:[],Guid,X,Y,Kind:"choice"}`（**无 ConnectionsTo**，出口=各选项的 TargetNodeId；两选项指向同一节点＝“选项不同但剧情相同”）
- `exit`  `{IsEnding,EndText,NeHeader,NeTitle,NeScriptDirty:<ScriptData>,Guid,ConnectionsTo:[],X,Y,Kind:"exit"}`（`IsEnding:true`=结局，false=未完待续）

`ScriptData` 字段：
`LineId`(guid)、`text`、`popup`(str)、`bgEffect`(uint)、`bgName`(uint 背景哈希)、`bgFriendlyName`(str)、`sound`(str)、`voice`(str)、`transition`(uint)、`bgmId`(int)、`selectionGroup`(uint)、`additionalPrompt`(str)、`characters`(**恰好 6 项**)、`speakerSlotNum`(int)、`highlightedSlotNums`(int[])、`isDialogScript`(bool)、`placeText`(str)

`CharacterRecordData`（每栏位）：
`{name,faceId:"00",startingPos,endingPos,displayOrder:1,emoticon:-1,action:0,effect:0,appear:0,shapeOverride:0}`
- 空栏位：`name:""`、start/end=0。
- 有人栏位：**数组下标 = 当前栏号 = `startingPos`**；不动就 `endingPos` 相同；`speakerSlotNum`=发言者栏号。
- 旁白：`isDialogScript:false` 且 speaker 指向空栏（0）。

**硬规则**：`characters` 必须**恰好 6 项**（栏 0..5）；栏 0 是旁白/老师位，角色一般放 1..5；两人同台可默认用 3、5 号位；这是构图建议，可按剧情调整。

## 选项与自动录制

每个 `choice` 节点选定一个 Auto 选项，使自动播放/录制在遇到选项时沿该路线继续。AAP2 中以 `DefaultOptionId` 指向当前节点某个选项的 `OptionId`；一个节点只有一个默认选择，不将 `auto`、`[auto]` 或其他标签拼到 `Text` 中。编辑器操作对应点选选项本身（非文字编辑框），显示 Auto 标记。

例如节点中有两项：

```json
{
  "Options": [
    {"OptionId":"b1000001-0000-0000-0000-000000000001", "Text":"（点点头）辛苦了。", "TargetNodeId":"a1000004-0000-0000-0000-000000000004"},
    {"OptionId":"b1000002-0000-0000-0000-000000000002", "Text":"（微笑）有劳你们了。", "TargetNodeId":"a1000004-0000-0000-0000-000000000004"}
  ],
  "DefaultOptionId":"b1000001-0000-0000-0000-000000000001"
}
```

这里第一项为 Auto，其余选项仍可手动选择。上例仅展示选项字段，完整节点仍须保留 Guid、Kind、位置等字段。两个选项即使汇入同一节点，也要设置 Auto；共同后续须能承接选中选项的台词或动作。

保留用户已有的有效 Auto 与录制路线。新增或缺失时按剧情目标、语气及后续承接选一项，不一律改为第一项；若选项决定重要结局且无法推断用户意图，应先澄清路线。保留所有 OptionId、TargetNodeId 和其他选项，不靠删除选项来绕过录制停顿。

`DefaultOptionId:null` 表示未选 Auto，旧工程可用于手动选择，但不满足默认录制交付要求。普通 `validate` 会提示缺失的节点；`validate --require-auto` 与 `compile --require-auto` 把缺失列为错误。不存在或属于别的节点的 OptionId 始终报错。没有选项的工程无需 Auto。检查通过仅说明选项可自动继续，不代表实际录制已完成。

依据：本机程序 CHANGELOG 0.8.9 的 Auto 功能说明；当前 AAP2 模型的 DefaultOptionId、SelectionNodeInspector.ApplyDefaultOption 与 InspectorSelectionItem.defaultAutoSprite，及原生 API 的 `option.set_default`。

## 资源哈希

资源引用 `bgName` = **`xxHash32(名字, seed=0)`**（对 UTF-8 字节）。
已知：`BG_MainOffice`=1046815759、`BG_MainOffice_Night`=3289055107、`BG_Black`=1047754314（默认预览）、`BG_ClassRoom`=1738686580、`BG_Library`=3976053942、`BG_BeachFrontSide_Sunset`=3332100768。
`popup`/`sound`/`voice` 是**字符串名**（不是哈希）。
（Python 参考实现见 `references/xxhash32.py`。）

## 状态与校验

每句明确写入当前背景和 BGM；`0` 表示清空，不是沿用。静音使用 `bgmId:999`。过渡一般只写在换景句，其余为 0。人物字段是该句的舞台状态，不能只写发言者。无气泡时 `emoticon:-1`；有意表现角色反应时填写相应编号，反应结束后清空。复制角色状态时检查旧气泡，避免无意连续重播，使用时参考 [气泡规则](演出参数.md#语气气泡使用规则)。

`startingPos`、`endingPos` 与逻辑栏位不是同一概念。旧版样本曾因跨句走位校验失败，默认保持固定栏位；若需要移动，以当前运行时的 compile 校验和播放结果为准，不把该经验推广为所有版本禁止移动。

调用 `scripts/aa_tool.py validate` 检查文件头、字段类型、六栏位、GUID 唯一性、发言/高亮栏、分支目标、可达性与环。字段错误须报告节点/行与 JSON 路径。静态通过不等于运行时编译或资源校验通过。

修改已有工程保留 ProjectId、节点 Guid、LineId 和 OptionId；只为新增对象生成 ID。老师台词若与旁白区别不明，先查看现有工程表示方式，不能自动把老师替换成学生。


## 剧情标题

交付前填写顶层 `PreviewTitle`（预览标题）及 `entry` 节点的 `Title`（入口标题），默认一致。`ProjectName` 和文件名仅用于工程命名，不能代替显示标题。保留已有有效标题；未指定且缺失时根据故事拟题。用户有意区分预览和开场标题时允许不同，不强制覆盖。`PreviewHeader` / `Header` 为可选副标题；不为补标题而改变节点 ID 或正文。

`validate/compile --require-title` 要求两个标题均为非空字符串；普通校验对旧工程的空标题给出警告。
