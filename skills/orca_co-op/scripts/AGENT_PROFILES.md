# AGENT_PROFILES — 에이전트별 특성·지뢰밭 (역할 배정 시 참조)

> **갱신 트리거(규약, 코드 0)**: 파이프라인 중 `실패:` 신호가 **1회라도** 발생하면,
> 조율자는 그 원인(새로 알게 된 에이전트 한계/주의점)을 이 파일에 **1줄 추가하기 전에는
> `완주`를 선언하지 않는다.** 이 규칙 하나가 "매번 갱신 습관"의 방치(bit rot)를 막고
> 스킬이 실행 경험에서 학습하게 만든다. 아래는 살아있는 문서다.

## 요약 표

| 에이전트 | 관리형 훅 | 감독형 orchestration | auto-approve | idle 감지 | 비고 |
|---|---|---|---|---|---|
| **claude** | O | 워커로 안정 | 자체 auto 모드 | 비교적 신뢰 | 조율자로도 씀 |
| **codex** | O | 워커로 안정 | YOLO 모드 | 비교적 신뢰 | GPT-5 계열 |
| **opencode** | X | **false stall** | **필요**(툴실행 승인서 멈춤) | **불안정** | 모델은 config 따름(GLM 등) |
| **agy** (antigravity) | X | **false stall** | **`--dangerously-skip-permissions` 필수** | **불안정** | Gemini 계열, fresh 런칭 시 재로그인 필요할 수 있음 |

## 상세 (실측)

- **claude / codex**: orca 관리형 훅이 있어 "턴 시작" 신호가 떠서 orca **자체** 오케스트레이션(`worker-start`) 워커로 신뢰성 있게 돌아간다. 감독형 루프가 필요하면 이 둘.
- **opencode / agy**: 훅이 없어 orca 자체 오케스트레이션에선 `agent_prompt_stalled`(false stall)로 dispatch가 실패 처리되고 worker_done이 거부된다 → 이 둘에겐 **co-op(터미널 릴레이)** 를 쓴다.
- **agy**: 자체 권한스킵 모드가 없어 **`--dangerously-skip-permissions`로 띄우지 않으면** 매 파일쓰기·send 승인에서 멈춘다. `tui-idle` 감지가 부정확(다 됐는데 미도달) → 완료는 결과 파일로 확인. fresh 런칭 시 로그인이 이어지지 않을 수 있음.
- **opencode**: 자기 테스트 실행·파일쓰기에서 **승인 프롬프트에 멈춤**(auto-approve 아니면). `tui-idle`도 작업 종료 후 미도달인 경우 있음 → 결과 파일로 확인. **GLM/OpenRouter 생성이 다소 복잡한 분석 태스크에서 십수 분 hung될 수 있음**(2회 재현, 토큰·진행 고정, `실패:` 신호도 못 보냄) → 조율자 liveness read로 감지되나 복구는 **사용자가 pane에서 `Esc`**로만. 무인 신뢰성이 낮으니 중요 파이프라인엔 claude/codex 우선.

## 배정 힌트
- 감독형(worker_done 추적)·중요 파이프라인 → claude/codex.
- opencode/agy는 co-op에서 워커로 쓰되 **반드시 auto-approve 상태**로. 무인이면 그게 전제.
