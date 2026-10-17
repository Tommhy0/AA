# AzureArchive シナリオ制作スキル 4.0

旧 1.6 スキルを完全な 4.0 パッケージに更新しました。`_skill` と `_skill2` の旧パスも新版の互換コピーです。

- [azurearchive-scenario](azurearchive-scenario/) フォルダー全体を、Codex では `~/.agents/skills/azurearchive-scenario/`、Claude Code では `~/.claude/skills/azurearchive-scenario/` にコピーします。scripts、references、assets、examples も必要です。
- アーカイブ対応クライアント向け：[azurearchive-scenario.skill](azurearchive-scenario.skill)。
- 各選択肢ノードで Auto を一つ指定します。`validate/compile --require-auto --require-title` で未設定を検出します。Auto は DefaultOptionId に保存し、選択肢の本文には追記しません。
- ネイティブコンパイルで `.aas` を生成し、ハッシュと不足リソースを検証します。コンパイル成功は再生・録画完了を意味しません。
- 登場する生徒の資料だけを読み込みます。初版の人物資料は 72 名分で、必要な場合に原文を検索できます。原文全体は同梱していません。
- 気泡は場面と個性に合わせて使い、単なる繰り返しを避けます。

参照：[SKILL.md](azurearchive-scenario/SKILL.md)、[コンパイル](azurearchive-scenario/references/automation.md)、[人物一覧](azurearchive-scenario/references/characters/INDEX.md)、[更新履歴](azurearchive-scenario/CHANGELOG.md)。詳細資料は現在中国語です。既存の対応する AzureArchive/BepInEx 環境が必要です。

[LICENSE](LICENSE) を参照してください。非公式の資料であり、アプリ本体やゲーム素材は含みません。

納品前に PreviewTitle と入口ノードの Title を設定します。既存の題名を保持し、未指定なら物語に合う題名を付けます。`--require-title` は題名の欠落をコンパイル前に検出します。

4.0：ローカル IndexTTS-2.5 による中国語・日本語 AI 吹き替えを追加。単一の参照音声、台詞ごとの3候補と品質検査、LineId 対応、プロジェクト専用 VoiceOverrides を使用します。配音後のコンパイルには `--require-voices` を付けます。モデルと原声音声庫は同梱せず、聴感は人による確認が必要です。[手順](azurearchive-scenario/references/ai-dubbing.md)。
