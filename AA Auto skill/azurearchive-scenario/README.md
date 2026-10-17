# azurearchive-scenario v4.0

生成或修改 AzureArchive AAP2 工程，并自动编译、校验和发布可浏览的 AAS 成品。主要指令见 [SKILL.md](SKILL.md)。

整个目录可作为技能安装；`.skill` 是同目录的打包副本。环境配置、原生编译依赖、命令参数与精简剧情输入见 [自动编译说明](references/automation.md)。仓库根目录附带拖放编译和编译后浏览的 Windows 入口。

## 内容

- SKILL.md：精简工作流、格式约束和参考路由。
- references：工程格式、演出、环境排障、自定义包及原有资源清单。
- scripts：生成/校验/编译发布助手、桥接构建与行为测试。
- assets/compiler：原生编译桥接 DLL 和可重建源码。
- examples：带分支的完整 AAP2 示例。
- CHANGELOG.md：版本历史。

编译成功、请求播放和人工播放验收分别报告。失败保留源文件、原成品和诊断日志。

鼓励用合时宜的语气气泡点亮演出，按情境与节奏取舍，不设固定数量或间隔；情境、清空与复核指引见 SKILL.md 和演出参数。自动编译版编号为 2.0，气泡指引版为 2.1，本版为 4.0。

默认按出场学生读取[剧情证据档案](references/characters/INDEX.md)，首批72名；复杂问题再[按需查原文](references/character-writing.md)，避免每次加载全量资料。原文缓存独立于技能，现成卡离线可用。

每个对话选项节点指定一个 Auto 选项，保留用户选定的自动路线。录制交付使用 `validate/compile --require-auto` 检查遗漏，字段与示例见[选项与自动录制](references/project-format.md#选项与自动录制)。

剧情必须填写预览与入口标题，交付前使用 --require-title 检查。已有标题予以保留，未指定时根据剧情拟题。

4.0 新增[AI 配音](references/ai-dubbing.md)：IndexTTS-2.5 中日配音、角色情绪参考、三候选质检、LineId 绑定与工程语音包接入；模型和原声库留在本机。带配音编译额外使用 `--require-voices`。
