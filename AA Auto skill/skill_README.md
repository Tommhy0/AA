# azurearchive-scenario

《蔚蓝档案》剧情创作技能（AzureArchive / `.aap2`）—— 让 AI 直接**手写 `.aap2` 工程 JSON** 来创作剧情，
比驱动 AA 那套 Unity 节点编辑器可靠得多。**版本 v1.6。**

> 本技能是 [AA_KIT](../../README.md) 的一部分 —— 那份资料包里还有**四语 README**、六张参考资料、示例工程与排障脚本。

## 安装

- **Claude 桌面版**：用 App 的“技能 → 添加”，选择上两级目录里的 `azurearchive-scenario.skill`。
- **Claude Code**：把本目录整个拷到你的 skills 目录，例如
  `~/.claude/skills/azurearchive-scenario/`（Windows：`C:\Users\<你>\.claude\skills\azurearchive-scenario\`）。

## 目录内容

| 文件 | 说明 |
|---|---|
| **`SKILL.md`** | 技能正文 —— 数据目录、`.aap2` 结构、全部字段、对照表、坑。**核心。** |
| `CHANGELOG.md` | 更新日志（`0.1 → 1.6`）。 |
| `references/` | 六张参考资料清单 + `xxhash32.py`（算资源名哈希）。 |
| `examples/Schale_Demo.aap2` | 示例工程（3 角色 / 4 背景 / 弹窗 / 音效 / 气泡 / 动作 / 分支 / 旁白）。 |

## 快速用法

1. 对 AI 说：“**用 `azurearchive-scenario` 技能写一段 AA 剧情……**”（可指定学校、角色、基调、长度）。
2. AI 把 `.aap2` 写进 AA 的 `…\data\projects\`。
3. 你在 AA 里进 **项目模式 → 选中 → 编辑**（打开即自动保存 + 编译），再切 **鉴赏模式** 播放验收。

> 编译成功 ≠ 已看过效果 —— **务必亲自播一遍**。

## 许可

文本与脚本采用 **CC BY-NC-SA 4.0**（署名 · 非商业性使用 · 相同方式共享），© 2026 **Tommhy0** —— 详见 [LICENSE](../../LICENSE)。
AA 本体与全部游戏素材版权归各自作者，本技能不含任何游戏素材。
