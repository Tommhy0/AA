# AzureArchive Scenario Skill 3.2

The original 1.6 skill has been replaced with the complete 3.2 package. The old `_skill` and `_skill2` paths contain updated compatibility copies.

- Copy the complete [azurearchive-scenario](azurearchive-scenario/) folder to `~/.agents/skills/azurearchive-scenario/` for Codex or `~/.claude/skills/azurearchive-scenario/` for Claude Code. Install the scripts, references, assets and examples together.
- For clients supporting skill archives, download [azurearchive-scenario.skill](azurearchive-scenario.skill).
- Set one Auto option in every choice node. `validate/compile --require-auto --require-title` detects missing defaults; Auto is stored as DefaultOptionId, not added to the option text.
- Native compilation produces a browsable `.aas` and checks source/output hashes and missing resources. Compilation does not confirm playback or recording.
- Read evidence cards for the students in the scene. 72 initial cards are included; original-text lookup is available when needed. Full source stories are not bundled.
- Use reaction bubbles when they fit the scene and character; avoid repetitive decoration.

Instructions: [SKILL.md](azurearchive-scenario/SKILL.md), [compilation](azurearchive-scenario/references/automation.md), [character index](azurearchive-scenario/references/characters/INDEX.md), [changelog](azurearchive-scenario/CHANGELOG.md). Detailed references are currently in Chinese. Native compilation requires an existing supported AzureArchive/BepInEx installation.

See [LICENSE](LICENSE). This is a third-party skill; it does not include the application or game assets.

Fill both PreviewTitle and entry.Title before delivery. Preserve existing titles; choose a fitting story title when absent. `--require-title` rejects missing titles before compilation.
