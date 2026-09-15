---
# 구현/개발 단계용 TASK (base: TASK.template.md). 조율자가 값 설정.
task_id:      <RUN>-<STEP>
assignee:     <NICK>
step:         <구현 | 수정반영>
target:       <구현/수정할 파일·경로>
inputs:       []                    # 예: [대상 파일, 관련 컨벤션 문서, .relay/RESULTS.md(직전 보류 항목)]
constraints:  []                    # 구현 단계는 통상 편집 허용 → []
report_to:    <COORD_HANDLE>
on_done:      "완료:<NICK>-<STEP>"
on_fail:      "실패:<NICK>-<STEP>"
final:        false
---

# TASK — 구현/개발

## 목표 (한 줄)
<구현 완료 동작 기준 1문장>

## 입력 — 선행 확인 대상
- <대상 파일 및 관련 컨벤션. 검수 피드백 반영 시 .relay/RESULTS.md 내 직전 `보류` 항목 필수 확인>

## 할 일
1. <구현/수정 대상 명시 — 포인터 위주>
2. **기존 코드 스타일·구조·컨벤션 준수** (주변 파일 선행 참조 필수).
3. 최소 자체 스모크 테스트 수행을 통한 동작 검증 (가능 시).

## 완료 기준 (DoD) — 전 항목 충족 필수
- [ ] 목표 동작 충족
- [ ] 기존 컨벤션 준수 (신규 외부 의존성 추가 및 과잉 추상화 지양)
- [ ] 자체 스모크 테스트 통과 (또는 미실시 사유 명시)
- [ ] RESULTS.md 내 결과 블록 추가(append) 완료

## 결과 기록 (필수)
`<작업폴더>/.relay/RESULTS.md` 끝에 추가(append). 형식:

    ## <NICK> <STEP>
    - 결과: <수정 내역 1~3줄 요약 + 변경 파일 목록>

## 완료/실패 보고 (필수 — 해당 명령 즉시 실행)
- 성공: `orca terminal send --terminal <report_to> --text "<on_done>" --enter --json`  (final: true 시 "완주" 전송)
- 실패: `orca terminal send --terminal <report_to> --text "<on_fail>: <한 줄 사유>" --enter --json`  (정체 발생 시 임의 대기 금지)
