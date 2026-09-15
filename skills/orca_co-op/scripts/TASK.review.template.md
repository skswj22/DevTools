---
# 검수 단계용 TASK (base: TASK.template.md). 코디네이터가 값만 채운다.
task_id:      <RUN>-<STEP>
assignee:     <NICK>
step:         <1차검수 | 2차검수 | 재검수>
target:       <검수할 파일·경로>
inputs:       []                    # 예: [대상 파일, .relay/RESULTS.md(앞선 리뷰)]
constraints:  [no-file-edit, no-exec]   # 검수는 정적으로만 — 파일 수정·코드 실행 금지
report_to:    <COORD_HANDLE>
on_done:      "완료:<NICK>-<STEP>"
on_fail:      "실패:<NICK>-<STEP>"
final:        false
---

# TASK — 검수(정적)

## 목표 (한 줄)
<대상의 결함·리스크를 정적으로 찾아 통과/보류를 판정한다>

## 입력 — 먼저 읽을 것
- <대상 파일. 2차/재검수면 .relay/RESULTS.md의 앞선 리뷰를 읽고 중복 지적을 피한다>

## 할 일
1. 대상을 **정적으로만** 리뷰한다(파일 수정·코드 실행 금지).
2. 표준 렌즈로 본다: **정확성 · 엣지케이스 · 에러 처리 · 보안 · 테스트 커버리지**.
3. 이미 지적된 것은 반복하지 말고, 놓친 점·우선순위를 보탠다.

## 완료 기준 (DoD) — 전부 참이어야 done
- [ ] 위 5개 렌즈를 각각 확인
- [ ] 발견사항을 RESULTS.md에 append
- [ ] `판정`을 남김(보류면 **어떤 DoD/요구가 미충족인지** 명시 → 개발자가 그것만 고치게)

## 결과 기록 (필수)
`<작업폴더>/.relay/RESULTS.md` 끝에 append. 형식:

    ## <NICK> <STEP>
    - 결과: <발견사항 1~3줄>
    - 판정: <통과 | 보류>            # 보류면 미충족 항목을 결과에 명시

## 완료/실패 보고 (필수 — 그대로 실행)
- 성공: `orca terminal send --terminal <report_to> --text "<on_done>" --enter --json`  (final:true면 "완주")
- 실패: `orca terminal send --terminal <report_to> --text "<on_fail>: <한 줄 사유>" --enter --json`  (막히면 조용히 멈추지 말 것)
