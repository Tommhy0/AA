# AA
Utilities for Azure Archive, a tool for BA players to create their own BA fan-created storylines.
AA/AA Auto skill: see README_*your language*_AA_KIT.md

Current skill: **azurearchive-scenario 4.0**. The original 1.6 copies have been replaced.

- [Installation and features](<AA Auto skill/skill_README.md>)
- [Complete skill folder](<AA Auto skill/azurearchive-scenario/>)
- [Download the .skill package](<AA Auto skill/azurearchive-scenario.skill>)
- [English](<AA Auto skill/README_en_AA_KIT.md>) · [日本語](<AA Auto skill/README_ja_AA_KIT.md>) · [한국어](<AA Auto skill/README_ko_AA_KIT.md>)

Version 3.2 adds scenario titles and pre-compilation title checks.

Version 4.0 adds local IndexTTS-2.5 AI dubbing in Chinese/Japanese: one character reference, three candidates per line, audio QC, LineId binding and project-local VoiceOverrides. Use `dub_tool.py prepare/render/apply`, then compile with `--require-voices`. Models and original voice libraries stay outside this repository. Human listening review remains necessary. See [AI dubbing](<AA Auto skill/azurearchive-scenario/references/ai-dubbing.md>).
