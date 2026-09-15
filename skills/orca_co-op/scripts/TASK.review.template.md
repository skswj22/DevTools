---
# 검수 단계용 TASK (base: TASK.template.md). 조율자가 값 설정.
task_id:      <RUN>-<STEP>
assignee:     <NICK>
step:         <1차검수 | 2차검수 | 재검수>
target:       <검수할 파일·경로>
inputs:       []                    # 예: [대상 파일, .relay/RESULTS.md(선행 리뷰)]
constraints:  [no-file-edit, no-exec]   # 검수는 정적 분석만 — 파일 수정·코드 실행 금지
report_to:    <COORD_HANDLE>
on_done:      "완료:<NICK>-<STEP>"
on_fail:      "실패:<NICK>-<STEP>"
final:        false
---

# TASK — 검수 (정적 분석)

## 목표 (한 줄)
<대상 결함 및 잠재 리스크 정적 분석을 통한 통과/보류 판정>

## 입력 — 선행 확인 대상
- <대상 파일. 2차/재검수 시 .relay/RESULTS.md 내 선행 리뷰 내용 확인 및 중복 지적 방지>

## 할 일
1. 대상 코드 **정적 분석 위주 리뷰** (임의 파일 수정 및 코드 실행 금지).
2. 표준 검수 기준 적용: **정확성 · 엣지 케이스 · 예외 처리 · 보안 · 테스트 커버리지**.
3. 기 지적 사항 반복 지양, 누락 사항 및 우선순위 중심 피드백 제시.

## 완료 기준 (DoD) — 전 항목 충족 필수
- [ ] 표준 5대 검수 기준 전원 확인
- [ ] 검수 발견 사항 RESULTS.md 기록 완료
- [ ] `판정` 명시 (보류 판정 시 **미충족 완료 기준(DoD) 및 요구 사항** 명시)

## 결과 기록 (필수)
`<작업폴더>/.relay/RESULTS.md` 끝에 추가(append). 형식:

    ## <NICK> <STEP>
    - 결과: <발견 사항 1~3줄 요약>
    - 판정: <통과 | 보류>            # 보류 판정 시 미충족 항목 결과 명시

## 완료/실패 보고 (필수 — 해당 명령 즉시 실행)
- 성공: `orca terminal send --terminal <report_to> --text "<on_done>" --enter --json`  (final: true 시 "완주" 전송)
- 실패: `orca terminal send --terminal <report_to> --text "<on_fail>: <한 줄 사유>" --enter --json`  (정체 발생 시 임의 대기 금지)
