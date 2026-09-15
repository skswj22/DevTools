---
# 문서화 단계용 TASK (base: TASK.template.md). 조율자가 값 설정.
task_id:      <RUN>-<STEP>
assignee:     <NICK>
step:         <문서화 | README작성>
target:       <문서로 설명할 대상 파일·모듈>
inputs:       []                    # 예: [대상 파일, .relay/RESULTS.md(반영된 방어로직)]
constraints:  []                    # 문서 파일 생성 필요 → 편집 허용
report_to:    <COORD_HANDLE>
on_done:      "완료:<NICK>-<STEP>"
on_fail:      "실패:<NICK>-<STEP>"
final:        true                  # 통상 파이프라인 최종 단계 → 성공 시 "완주" 전송
---

# TASK — 문서화

## 목표 (한 줄)
<대상 활용이 즉시 가능하도록 명확한 문서 작성>

## 입력 — 선행 확인 대상
- <대상 파일. .relay/RESULTS.md 내 리뷰 반영 사항(방어 로직/설계 결정) 확인 후 문서 반영>

## 할 일
1. 대상 코드 분석 및 지정된 `<산출 문서 경로>`(예: README.md) 문서 작성.
2. 필수 포함 항목: **목적 · 사용 예시 · 인자 · 발생 가능한 예외 · 주의/제약사항** (간결한 한국어 개조식 작성 권장).
3. 실제 동작 검증된 코드 예시 포함.

## 완료 기준 (DoD) — 전 항목 충족 필수
- [ ] 필수 항목 섹션 전체 포함
- [ ] 사용 예시의 실제 동작 일치 여부 확인
- [ ] 문서 파일 지정 경로 저장 완료
- [ ] RESULTS.md 내 결과 블록 추가(append) 완료

## 결과 기록 (필수)
`<작업폴더>/.relay/RESULTS.md` 끝에 추가(append). 형식:

    ## <NICK> <STEP>
    - 결과: <작성 문서 경로 + 주요 섹션 요약 1~2줄>

## 완료/실패 보고 (필수 — 해당 명령 즉시 실행)
- 성공(최종 단계): `orca terminal send --terminal <report_to> --text "완주" --enter --json`
- 실패: `orca terminal send --terminal <report_to> --text "<on_fail>: <한 줄 사유>" --enter --json`  (정체 발생 시 임의 대기 금지)
