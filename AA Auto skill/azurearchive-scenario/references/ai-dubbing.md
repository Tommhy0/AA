# AI 配音（4.0）

依据用户提供的 `E:/IndexTTS/README.md` 部署与试听报告（2026-10-16），采用 **IndexTTS-2.5 零样本克隆 + 单条参考音**，中文、日文均使用此路线。该路径是本机部署位置，其他机器通过参数指定。模型、虚拟环境、原声库和生成音频不打包进技能或上传 GitHub。

## 环境与角色选材

- 本机部署：`E:/IndexTTS/repo/.venv/Scripts/python.exe`、`repo/checkpoints/config.yaml`；常规参考音在 `E:/IndexTTS/refs/refs.json`（275 项），状态参考在 `E:/IndexTTS/refs_modes/refs.json`。先确认实际文件，不把快照当作当前安装证明。
- `refs.json` 的 `path_name` 是配音映射键，与 AA 的韩文资源名、中文显示名不是同一个标识。用 cast 显式对应；不要靠字符串相似度猜学生或衣装。同角色不同状态可选 `hoshino_daily`、`hoshino_serious`、`mika_excited`、`mika_tender`；只有相应参考音库存在时可用。
- 优先单条、干净、完整、无 BGM 的角色原声，约 6–15 秒，优选 8–14 秒；模型会截断过长参考。平静独白优先，不机械使用喊叫、战斗、标题和 UI 短音；台词情绪明显变化时换同角色相应状态参考，而不是所有句子都用平静档。
- 现有主管线为 `E:/IndexTTS/_scripts/aa_dub.py`，可继续单独生成场景。技能的 `scripts/dub_tool.py` 专门处理 AAP2 的 LineId、分支、资源包和源文件版本，避免场景脚本跳过缺失角色或重排索引后错配台词。
- 缺参考时先明确缺少的角色，不擅自换音色。已有 `make_refs.py --char <path_name>` 可按需构建，保留来源。报告快照：原声元数据 278 角色/18,830 条，18,607 个独立 MP3；阿洛娜、普拉娜等 NPC 不在该库。SchaleDB 中日文转写共用日语原声，中文转写不是中文原配。

## 生成与质检决策

默认让**参考音本身承载情绪**，不传一热 `emo_vector`。报告确认求和为 1 的向量会抹掉参考音推导的情感条件，早期报告里一热向量“有效”的结论已撤回。普通流程用同角色的状态参考；音色锚与情绪参考分离是实验选项，不是默认升级。

每句默认生成 **3 个候选，取可解码、非空且非静音候选中最短的一个**。这是报告对拖音、重复和长尾退化的实测对策，不保证最短者一定完整或语气最好；听到截字、漏读、错音仍须重做。保留候选时长、失败原因、参考音来源、哈希与结果 WAV。不要把中位数当默认，报告已测到多数候选退化的情况。

脚本标记 >2 秒静音尾巴、足够长台词低于 2 字/秒的可疑输出。字符速率只适合粗筛，英文和不同情绪不可直接横比；有铺垫的慢速台词可标 `expect_slow:true`，它只豁免慢速提示，不豁免长静音。对异常先听并重做，不把“拖得长”解释成慵懒到位。不合格参考要更换；声纹 CAMPPlus 的高分不能证明像本人，报告已用无关角色对证伪该判断。

输出统一为单声道 22,050 Hz PCM16，留约 4 dB 余量；只衰减，不为提升响度重新归一到满幅。预览拼接先显式重采样、检查目标采样率，不能只改 WAV 文件头。报告中的混采样率错误曾让 40 kHz 音频按 22.05 kHz 播放、降低近一个八度；自动重采样的指标还可能掩盖这个错误。原始输入/输出排查要保留原采样率观察。

报告最终验收为“可用于剧情配音”，不等于所有角色与状态均完美。GPT-SoVITS 微调、TTS 后接社区 RVC 在该项目实测没有增益，中文 RVC 还变差；不自动安装这两套或再次训练。只有用户明确提出新的实验目标才重新评估。

## AAP2 工作流

先完成标题、人物、Auto 选项与文字复核，再配音；避免文稿未定就全量生成。首次使用的新角色或新状态先选少量典型句试音，通过后扩展。短片可直接完成全流程。旁白与老师默认不配音，有明确参考映射时才启用；已有 `voice` 保留。默认覆盖所有选中的对话节点，包括非 Auto 分支，不能把未覆盖分支说成已全配音。

1. 准备 cast：`characters` 键是每句发言栏位实际的 `characters[slot].name`，值为参考库 `path_name`。`lines` 以完整 `LineId` 覆盖某句角色状态、语言或配音文本；`skip:true` 明确跳过。一个 plan 对应一份源文件快照。

```json
{
  "lang": "ZH",
  "characters": {"시로코 부상": "shiroko"},
  "lines": {}
}
```

同一角色切状态时可在 `lines` 里给对应 LineId 写 `{"speaker":"hoshino_serious","expect_slow":true}`，同时通过 `--refs` 指定包含该键的库。要混用不同库，可在任务目录创建一份组合 `refs.json`，保持原始 `ref_wav` 与出处，不改现有参考库。JA 配音可用 `{"lang":"JA","text":"对应日文台词"}`；脚本不负责翻译，助手需按人物证据复核译文，屏幕原字幕保留。

2. 标准库 Python 生成计划；缺失角色映射会报出 LineId，不会静默漏配。可用 `--only "LineId1,LineId2"` 先做试音或增量。

完整示例工程可使用 [Schale_Demo.cast.json](../examples/Schale_Demo.cast.json)；它对应常规参考库，不包含状态专用音色。

```powershell
python -B -X utf8 scripts/dub_tool.py prepare "剧情.aap2" --cast "cast.json" --refs "E:/IndexTTS/refs" --plan "任务/plan.json"
```

3. 用现有 IndexTTS 虚拟环境生成，模型只加载一次；输出目录必须全新，避免上次音频混入结果。

```powershell
& "E:/IndexTTS/repo/.venv/Scripts/python.exe" -B -X utf8 scripts/dub_tool.py render "任务/plan.json" --repo "E:/IndexTTS/repo" --out "任务/render"
```

`report.json` 保存逐行/逐候选信息，`_scene_full.wav` 与 `timeline.json` 用于试听。**试听拼接按节点数组顺序，含替代分支，不等于选定 Auto 路线的连续演出**。按 LineId 定位试听；需要剧情顺序时在 AA 内播放。`listening_reviewed:false` 不可写成已验收。

4. 将语音附加到**新工程副本**；原工程与标识保留，已有同名工程资源目录也会复制并合并清单，未知资源不删除。目标工程或同名资源目录存在时拒绝覆盖，先选新名字。异常候选默认阻止附加，重新渲染或在试听确认后显式 `--allow-qc-warnings`。

```powershell
python -B -X utf8 scripts/dub_tool.py apply "任务/plan.json" --report "任务/render/report.json" --output "剧情_配音.aap2"
python -B -X utf8 scripts/aa_tool.py validate "剧情_配音.aap2" --require-auto --require-title
python -B -X utf8 scripts/aa_tool.py compile "剧情_配音.aap2" --require-auto --require-title --require-voices --exe "程序目录/AzureArchive.exe" --data-root "实际数据目录/data"
```

源文件或计划在生成后变化、音频哈希不同、逐行覆盖不一致均拒绝附加。修订文稿后重新准备计划；复用既有配音工程时，未改动句的 `voice` 自然保留，需要重配的句子在新工作副本中清空 `voice` 再按 LineId 生成，不修改稳定 ID。分支和现有 Auto 选择不改变。

## AA 资源接入与验收

2026-10-17 在本机 AzureArchive 1.0 beta 原生编译实测：

```text
剧情_配音.aap2
剧情_配音/
  manifest.json       VoiceOverrides: ["voices/aa_dub_<唯一键>.wav"]
  voices/
    aa_dub_<唯一键>.wav
```

对应台词 `voice` 写 `aa_dub_<唯一键>`，不带扩展名、目录或 xxHash。`voices/` 是这次验证成功的自定义目录布局，不代表运行时强制目录名。原生编译会重新封装为 `voice/res_<id>/文件.wav` 并写成品 manifest；发布时使用编译后的资源目录，不能只复制源 pack 或 `.aas`。无需修改全局 overrides。其他 AA 版本先做单句试编译；不要把报告原先“推测通路”扩写为所有版本都能播放。

检查 build 中 `missing_resources` **和** `omitted_missing_voices` 均为空，确认成品 manifest 与资源目录实际包含本次 WAV。`compile --require-voices` 在发现被省略语音时阻止发布；普通编译保留旧工程兼容性并报告警告。native 编译成功/资源收录、实际能播放、人耳语气与音色验收是三个不同结论。不能以文件存在或高相似分数代替后两项。

交付：源工程与同名资源包、可浏览 `.aas` 与编译资源、plan/report、逐句音频与试听轨、跳过/缺失/异常列表、语种和参考档、编译/发布/试听状态。只交付任务使用的音频；原声库、5GB 级模型和环境留在部署目录。

## 按需修复环境

优先复用已验收环境，详情回读用户原报告。不要因配音任务自动全量重新下载或训练。报告快照：Python 3.11 / NVIDIA / bf16；安装 `uv sync --extra webui`，不要 `--all-extras` 引入 Windows flash-attn 构建。辅助模型要按实际权重文件与 config 判断完整性，不能按目录存在或总大小判断，也不自动删除半成品或缓存。

报告确认的原声地址模板为 `https://r2.schaledb.com/voice/<AudioClip>`，旧 `static.schale.gg` 当时已不可用。只有需要补参考时才验证当前地址并按需下载，不为运行技能重抓 18,607 条。遵循模型和素材的实际许可；报告交付范围为个人学习与二次创作。
