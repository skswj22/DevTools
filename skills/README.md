# AI 스킬 (AI Skills) 🤖

자주 사용하는 AI 스킬 모음. 폴더 단위 관리 및 하위 `SKILL.md`를 통한 스킬 정의.

## 구조

```
skills/
└─ <skill-name>/
    └─ SKILL.md   # 스킬 정의 (frontmatter: name, description)
```

## 스킬 목록

### [orca_co-op](./orca_co-op)
orca 데스크톱 앱(onOrca.dev) 환경 내 다중 AI 에이전트 pane 간 협업 조율 스킬.
- **용도**: 인접 pane 작업 전달, 타 에이전트 대상 질의·응답 수신, 멀티 에이전트 릴레이(토큰링).

### [git-commit](./git-commit)
Conventional Commits 기반 git 커밋 메시지 작성 규칙 (type 영문 표기, 본문 한국어 적용).
- **용도**: 일관된 커밋 이력 관리, type 식별을 통한 변경 성격 즉시 판단.
