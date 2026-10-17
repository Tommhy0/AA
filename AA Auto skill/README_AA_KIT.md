# azurearchive-scenario 4.0

AzureArchive 剧情创作、人物证据查询、自动编译与录制准备技能。仓库原 1.6 技能已由完整 4.0 版本替换；`_skill` 和 `_skill2` 的旧文件路径保留为新版兼容副本。

## 安装

- Codex：将完整 [azurearchive-scenario](azurearchive-scenario/) 目录复制到 `~/.agents/skills/azurearchive-scenario/`。
- Claude Code：将同一完整目录复制到 `~/.claude/skills/azurearchive-scenario/`。
- 支持 `.skill` 导入的客户端：下载 [azurearchive-scenario.skill](azurearchive-scenario.skill)。

必须连同 scripts、references、assets、examples 一起安装，不能仅复制 SKILL.md。

## 4.0 的主要功能

- 每个对话选项节点设置一个 Auto，保留既定录制路线，避免自动播放在选项处等待。
- `validate/compile --require-auto --require-title` 检查每个选项的 DefaultOptionId，遗漏时定位到具体节点；不把 auto 拼到选项文字中。
- 自动编译为可浏览的 `.aas`，检查成品、源文件哈希和缺失资源。
- 72 名学生的初版证据档案默认按出场人物读取，复杂关系和剧情阶段按需查询原文。
- 气泡按人物、情境与演出节奏使用，鼓励点睛，避免滥用。

使用说明：[SKILL.md](azurearchive-scenario/SKILL.md)、[自动编译](azurearchive-scenario/references/automation.md)、[Auto 选项](azurearchive-scenario/references/project-format.md#选项与自动录制)、[学生索引](azurearchive-scenario/references/characters/INDEX.md)、[更新日志](azurearchive-scenario/CHANGELOG.md)。

```powershell
# 在完整技能目录中执行
python -B -X utf8 scripts/aa_tool.py validate "examples/Schale_Demo.aap2" --require-auto --require-title
python -B -X utf8 scripts/aa_tool.py compile "剧情.aap2" --require-auto --require-title --exe "程序目录/AzureArchive.exe" --data-root "实际数据目录/data"
```

原生编译需要已有 AzureArchive 与支持的 BepInEx/Authoring API，详见编译说明。编译通过不代表已经实际播放或录制完成。原文缓存位于技能之外，未随仓库打包；基础性格卡可以离线读取。

文本与脚本许可见 [LICENSE](LICENSE)。本仓库为第三方工具与资料，不包含 AA 本体或游戏素材。

3.2 新增剧情标题要求：填写预览 `PreviewTitle` 和入口 `Title`，保留已有标题，缺失时按剧情拟题。交付前使用 `--require-title` 检查，防止空标题进入编译。

4.0 新增[AI 剧情配音](azurearchive-scenario/references/ai-dubbing.md)：本地 IndexTTS-2.5 中日配音、同角色状态参考音、每句三候选取最短有效结果、异常筛查、LineId 绑定和工程专属 VoiceOverrides。调用 `dub_tool.py prepare/render/apply`，带配音编译使用 `--require-voices`。模型与原声库不打包，音色与语气仍需人耳验收。
