# AzureArchive 시나리오 스킬 4.0

기존 1.6 스킬을 완전한 4.0 패키지로 교체했습니다. `_skill`, `_skill2`의 이전 경로도 새 버전의 호환 사본입니다.

- [azurearchive-scenario](azurearchive-scenario/) 폴더 전체를 Codex의 `~/.agents/skills/azurearchive-scenario/` 또는 Claude Code의 `~/.claude/skills/azurearchive-scenario/`에 복사하세요. scripts, references, assets, examples를 함께 설치해야 합니다.
- 아카이브를 지원하는 클라이언트: [azurearchive-scenario.skill](azurearchive-scenario.skill).
- 각 선택지 노드에 Auto 항목 하나를 지정합니다. `validate/compile --require-auto --require-title`가 누락을 검사합니다. Auto는 DefaultOptionId로 저장하며 선택지 문구에 붙이지 않습니다.
- 기본 컴파일러로 `.aas`를 생성하고 해시 및 누락 리소스를 검사합니다. 컴파일 성공이 재생이나 녹화 완료를 뜻하지는 않습니다.
- 등장 학생의 자료만 읽습니다. 학생 72명의 초기 증거 자료와 필요할 때 사용하는 원문 검색을 제공합니다. 전체 원문은 포함하지 않습니다.
- 감정 기호는 장면과 성격에 맞게 사용하고 반복 장식을 피합니다.

안내: [SKILL.md](azurearchive-scenario/SKILL.md), [컴파일](azurearchive-scenario/references/automation.md), [학생 목록](azurearchive-scenario/references/characters/INDEX.md), [변경 기록](azurearchive-scenario/CHANGELOG.md). 상세 자료는 현재 중국어이며, 호환되는 AzureArchive/BepInEx가 이미 설치되어 있어야 합니다.

[LICENSE](LICENSE)를 참고하세요. 비공식 자료이며 앱이나 게임 소재를 포함하지 않습니다.

완료 전에 PreviewTitle과 시작 노드의 Title을 입력합니다. 기존 제목을 유지하고 없으면 이야기에 맞는 제목을 정합니다. `--require-title`은 컴파일 전에 누락된 제목을 검사합니다.

4.0: 로컬 IndexTTS-2.5 중국어/일본어 AI 더빙을 추가했습니다. 단일 참조 음성, 대사별 후보 3개와 품질 검사, LineId 연결, 프로젝트 전용 VoiceOverrides를 사용합니다. 더빙 후 컴파일에는 `--require-voices`를 추가하세요. 모델과 원본 음성 라이브러리는 포함하지 않으며 청취 검수가 필요합니다. [사용법](azurearchive-scenario/references/ai-dubbing.md).
