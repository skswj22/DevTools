# AGENT_PROFILES — 에이전트별 특성 및 제약사항 (역할 배정 시 참조)

> **갱신 규칙 (규약 코드 0)**: 파이프라인 진행 중 `실패:` 신호 1회 이상 발생 시,
> 조율자는 원인(신규 확인된 에이전트 제약/주의점)을 본 문서에 **1줄 추가 후 `완주` 선언 필수.**
> 규칙 준수를 통한 문서 방치(bit rot) 방지 및 실행 경험 기반의 지속적 개선 목적.

## 요약 표

| 에이전트 | 관리형 훅 | 감독형 orchestration | auto-approve | idle 감지 | 비고 |
|---|---|---|---|---|---|
| **claude** | O | 워커 안정 동작 | 자체 auto 모드 | 비교적 신뢰 | 조율자 겸용 가능 |
| **codex** | O | 워커 안정 동작 | YOLO 모드 | 비교적 신뢰 | GPT 계열 |
| **opencode** | X | **false stall 발생** | **필요** (도구 승인 대기 발생) | **불안정** | 모델 설정(GLM 등) 준용 |
| **agy** (antigravity) | X | **false stall 발생** | **`--dangerously-skip-permissions` 필수** | **불안정** | Gemini 계열, 신규 실행 시 재인증 필요 가능성 |

## 상세 실측 내용

- **claude / codex**: orca 관리형 훅 지원으로 "턴 시작" 신호 정상 수신 및 orca 자체 오케스트레이션(`worker-start`) 워커 안정 동작. 감독형 루프 구성 시 우선 권장.
- **opencode / agy**: 훅 미지원으로 orca 자체 오케스트레이션 사용 시 `agent_prompt_stalled`(false stall) 발생 및 dispatch 실패/`worker_done` 거부 발생 → **co-op(터미널 릴레이)** 방식 필수 적용.
- **agy**: 자체 권한 자동 승인 모드 부재로 **`--dangerously-skip-permissions` 옵션 실행 필수** (미적용 시 파일 쓰기·send 승인 대기 발생). `tui-idle` 감지 신뢰도 미흡(작업 완료 후 미도달) → 산출물 파일 기반 완료 확인 권장. 신규 실행 시 세션 유지 실패 가능성 존재.
- **opencode**: 도구 실행 및 파일 쓰기 시 **승인 대기 프롬프트 정체 발생** (auto-approve 필수). `tui-idle` 감지 미흡 → 결과 파일 직접 확인 권장. **복잡 분석 작업 시 GLM/OpenRouter 응답 정체(hang) 현상 발생 가능** (토큰 정체 및 `실패:` 신호 전송 불가). 조율자 liveness read 감지 가능하나 **사용자 수동 `Esc` 입력 복구 필수**. 신뢰도 고려 시 중요 파이프라인 대상 claude/codex 우선 배정.

## 역할 배정 가이드
- **감독형(worker_done 추적) 및 주요 파이프라인**: claude, codex 우선 배정.
- **opencode / agy**: co-op 워커로 활용하되 **반드시 auto-approve 활성화 상태 유지** (무인 자동화 실행 시 필수 전제).
