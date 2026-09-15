---
# 문서화 단계용 TASK (base: TASK.template.md). 코디네이터가 값만 채운다.
task_id:      <RUN>-<STEP>
assignee:     <NICK>
step:         <문서화 | README작성>
target:       <문서로 설명할 대상 파일·모듈>
inputs:       []                    # 예: [대상 파일, .relay/RESULTS.md(반영된 방어로직)]
constraints:  []                    # 문서 파일 생성 필요 → 편집 허용
report_to:    <COORD_HANDLE>
on_done:      "완료:<NICK>-<STEP>"
on_fail:      "실패:<NICK>-<STEP>"
final:        true                  # 보통 파이프라인 마지막 → 성공 시 "완주"
---

# TASK — 문서화

## 목표 (한 줄)
<사용자가 대상을 바로 쓸 수 있는 문서를 만든다>

## 입력 — 먼저 읽을 것
- <대상 파일. .relay/RESULTS.md에서 리뷰로 반영된 방어 로직/결정을 확인해 문서에 반영한다>

## 할 일
1. <대상>을 읽고 `<산출 문서 경로>`(예: README.md)를 작성한다.
2. 포함: **목적 · 사용 예시 · 인자 · 발생 가능한 예외 · 주의/제약**(한국어, 간결).
3. 예시는 실제로 동작하는 것으로.

## 완료 기준 (DoD) — 전부 참이어야 done
- [ ] 위 섹션 모두 포함
- [ ] 사용 예시가 실제 동작과 일치
- [ ] 문서 파일이 지정 경로에 저장됨
- [ ] RESULTS.md에 내 블록 append

## 결과 기록 (필수)
`<작업폴더>/.relay/RESULTS.md` 끝에 append. 형식:

    ## <NICK> <STEP>
    - 결과: <작성한 문서 경로 + 담은 섹션 요약 1~2줄>

## 완료/실패 보고 (필수 — 그대로 실행)
- 성공(마지막 단계): `orca terminal send --terminal <report_to> --text "완주" --enter --json`
- 실패: `orca terminal send --terminal <report_to> --text "<on_fail>: <한 줄 사유>" --enter --json`  (막히면 조용히 멈추지 말 것)
