---
# 릴레이 계약 (기계가 읽는 헤더 — 코디네이터가 값만 채운다. 키는 고정)
task_id:      <RUN>-<STEP>          # 예: r1-1차검수 · RESULTS 추적 키(유일)
assignee:     <NICK>                # 담당 닉네임(=역할)
step:         <STEP>                # 1차검수 / 2차검수 / 수정반영 / 재검수 / README작성 ...
target:       <파일/경로/범위>       # 이번 단계가 실제로 다루는 대상
inputs:       []                    # 먼저 읽을 컨텍스트 파일/경로 목록. 없으면 []
constraints:  []                    # 예: [no-file-edit, no-exec]. 없으면 []
report_to:    <COORD_HANDLE>        # 완료/실패 보고 대상(조율자 핸들)
on_done:      "완료:<NICK>-<STEP>"   # 성공 시 보낼 정확한 신호 문자열
on_fail:      "실패:<NICK>-<STEP>"   # 실패/중단 시 보낼 신호(뒤에 ": 사유" 붙임)
final:        false                 # true면 성공 시 on_done 대신 "완주" 전송
expect_sec:   <예상 소요 초>          # 선택. 조율자가 liveness 판단에 쓰는 힌트(예: 300)
---

# TASK — 이 파일을 읽은 네가 이 단계의 담당자다

## 목표 (한 줄)
<이 단계가 끝나면 무엇이 참이어야 하는가 — 검증 가능한 한 문장>

## 입력 — 먼저 읽을 것
- <위 inputs의 각 파일을 파일로 읽는다(스크롤백 말고). 없으면 "없음">

## 할 일
1. <포인터 위주 지시. 스펙 전체를 나열하지 말고 읽을 것/만들 것만 가리킨다>
2. <필요시 추가>

## 완료 기준 (Definition of Done) — 전부 참이어야 done
- [ ] <검증 가능한 항목 1 (예: 대상 파일이 X를 만족)>
- [ ] <검증 가능한 항목 2 (예: 지적사항 N건이 모두 반영)>
- [ ] RESULTS.md에 내 블록이 append 됨

## 결과 기록 (필수)
`<작업폴더>/.relay/RESULTS.md` 파일 **끝에 append**(덮어쓰기 금지). 형식 정확히:

    ## <NICK> <STEP>
    - 결과: <핵심 1~3줄>
    - 판정: <통과 | 보류 | 해당없음>      # 검수/승인 단계만, 그 외 생략
    - 개선점: <선택. 지시가 모호했거나 낭비된 부분 1줄 — 조율자가 완주 때 취합>

## 완료/실패 보고 (필수 — 반드시 아래 중 하나를 그대로 실행)
- **성공**: `orca terminal send --terminal <report_to> --text "<on_done>" --enter --json`
  (헤더 `final: true` 이면 `--text` 를 `"완주"` 로 바꾼다.)
- **실패·중단**: `orca terminal send --terminal <report_to> --text "<on_fail>: <한 줄 사유>" --enter --json`

> 규칙: DoD를 못 채우거나 승인 프롬프트·에러로 막히면 **조용히 멈추지 말고 반드시 실패 신호를 보낸다.** 그래야 조율자가 깨어나 재배정한다(무보고 = 체인 사망).
