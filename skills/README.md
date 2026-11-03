# AI 스킬 (AI Skills) 🤖

자주 사용하는 AI 스킬 모음. 폴더 단위 관리 및 하위 `SKILL.md`를 통한 스킬 정의.

## 구조

```
skills/
└─ <skill-name>/
    ├─ SKILL.md    # 스킬 정의 (frontmatter: name, description)
    ├─ scripts/   # 실행 스크립트 (선택)
    ├─ references/ # 참고 문서 (선택)
    └─ assets/    # 템플릿, 아이콘, 폰트 등 (선택)
```

## 스킬 목록

### [orca_co-op](./orca_co-op)
orca 데스크톱 앱(onOrca.dev) 환경 내 다중 AI 에이전트 pane 간 협업 조율 스킬.
- **용도**: 인접 pane 작업 전달, 타 에이전트 대상 질의·응답 수신, 멀티 에이전트 릴레이(토큰링).

### [git-commit](./git-commit)
Conventional Commits 기반 git 커밋 메시지 작성 규칙 (type 영문 표기, 본문 한국어 적용).
- **용도**: 일관된 커밋 이력 관리, type 식별을 통한 변경 성격 즉시 판단.

### [stack-diagram](./stack-diagram)
브랜드 로고를 활용한 기술 스택·시스템 아키텍처 다이어그램 생성 스킬.
- **용도**: 기술 스택, 인프라 구성, 서비스 연결 관계 시각화.
- **출력**: HTML, PNG, React/TSX.
- **출처**: [caru-ini/stack-diagram](https://github.com/caru-ini/stack-diagram)
