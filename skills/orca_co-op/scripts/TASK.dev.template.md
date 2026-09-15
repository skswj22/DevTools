---
# 구현/개발 단계용 TASK (base: TASK.template.md). 코디네이터가 값만 채운다.
task_id:      <RUN>-<STEP>
assignee:     <NICK>
step:         <구현 | 수정반영>
target:       <구현/수정할 파일·경로>
inputs:       []                    # 예: [대상 파일, 관련 컨벤션 문서, .relay/RESULTS.md(직전 보류 항목)]
constraints:  []                    # 구현 단계는 보통 편집 허용 → 대개 []
report_to:    <COORD_HANDLE>
on_done:      "완료:<NICK>-<STEP>"
on_fail:      "실패:<NICK>-<STEP>"
final:        false
---

# TASK — 구현/개발

## 목표 (한 줄)
<이 코드가 무엇을 하면 done인가 — 동작 기준 한 문장>

## 입력 — 먼저 읽을 것
- <대상 파일과 관련 컨벤션. 검수 피드백 반영이면 .relay/RESULTS.md의 직전 `보류` 항목을 읽어라>

## 할 일
1. <구현/수정할 것 — 포인터 위주>
2. **기존 코드 스타일·구조·컨벤션을 따른다**(주변 파일을 먼저 본다).
3. 최소 자체 스모크 체크로 동작을 확인한다(가능하면).

## 완료 기준 (DoD) — 전부 참이어야 done
- [ ] 목표 동작을 충족
- [ ] 기존 컨벤션 준수(새 의존성·과잉 추상화 금지)
- [ ] 자체 스모크 체크 통과(또는 불가 사유 명시)
- [ ] RESULTS.md에 내 블록 append

## 결과 기록 (필수)
`<작업폴더>/.relay/RESULTS.md` 끝에 append. 형식:

    ## <NICK> <STEP>
    - 결과: <무엇을 바꿨는지 1~3줄 + 바뀐 파일>

## 완료/실패 보고 (필수 — 그대로 실행)
- 성공: `orca terminal send --terminal <report_to> --text "<on_done>" --enter --json`  (final:true면 "완주")
- 실패: `orca terminal send --terminal <report_to> --text "<on_fail>: <한 줄 사유>" --enter --json`  (막히면 조용히 멈추지 말 것)
