---
name: orca_co-op
description: >-
  Coordinate multiple LIVE AI agent panes running side-by-side inside the orca
  desktop app (onOrca.dev; you can tell because TERM_PROGRAM=Orca). Use this
  whenever you (the AI agent in this pane, whichever it is) are running inside an
  orca terminal and the user
  wants to: discover which agent panes are open and what each one is, send or
  dispatch work to a neighboring pane, ask another agent a question and read its
  answer back, or run a multi-agent relay/ring where the panes hand work around
  to each other. The other panes are SEPARATE agents living in the orca app — a
  second Claude, `agy`/Antigravity/Gemini, `codex` — reached by typing into their
  terminal. Trigger phrases include "orca co-op", "옆/다른 pane", "옆 창", "다른
  에이전트한테 시켜/보내", "pane 간", "옆에 뜬 codex/agy/claude한테", "멀티 에이전트
  릴레이", "토큰링", "fan out to the panes", "orca 오케스트레이션", "검수/리뷰
  파이프라인", "pane들로 순서대로 (생산→검수→수정) 돌려" — and trigger even
  when the user names no command, since pane IDs change every session and the
  skill's whole job is to discover the live environment first, then drive it.
  Do NOT trigger for things that merely sound similar: spawning Claude's OWN
  sub-agents via the Agent tool (those are not orca panes), tmux/vscode/docker
  terminal splits, installing or logging into an agent CLI, editing or comparing
  DOCS about orca/wmux, or generic docker-compose / celery / message-queue
  "orchestration" that has nothing to do with orca panes.
---

# orca_co-op — multi-agent orchestration inside orca

You are one AI agent pane among several inside the orca desktop app. **This
SKILL.md is just the copy your agent loaded — the pattern is identical for any
agent that can run the `orca` CLI (Claude, agy, codex, opencode, …), so read
every "you" below as "whatever agent is running this," not "Claude."** orca
exposes a CLI (`orca ...`) that lets any pane **type into another pane's input
and read its output**. That is the whole mechanism: `orca terminal
send` injects real keystrokes + Enter into a target pane's stdin, so an idle
agent (including an idle Claude) wakes exactly as if the user had typed — and
`orca terminal read` pulls that pane's output back. Everything below is built on
those two primitives.

Nothing here is hardcoded, and it can't be: **handles, worktree IDs, and which
pane runs which agent all change every session** (handles are runtime-scoped and
rotate even mid-session; a pane that ran `agy` a minute ago may be back at a bare
shell). So always start by discovering the live environment.

## Entry point — "시작" / "start"

Premise: the user has already opened the panes and logged the agents in before
they call you — this skill does not launch or sign in agents. So don't spend a
turn verifying readiness; discover, then act on whatever the user actually gave.
**Ask only for what's missing** — never for what the message already contains.

**If the message already carries the work** (e.g. "orca_co-op — test4에 코딩하고
agy 검수시켜"): run Step 0 → Step 1 (roster), then **declare the role map in one
line and dispatch in the same turn** ("agy를 검수자로 배정, 바로 시작합니다") —
zero questions. Don't stop to confirm what the user already told you.

**If it's a bare "시작"** with no task (e.g. "orca_co-op 시작", "co-op 시작해줘"):
run Step 0 → Step 1, present the roster, and ask only the missing info — what to
orchestrate, plus (only if roles are ambiguous, see Step 2) which pane does what.
That roster + one question is the deliverable; don't invent a task.

## Step 0 — Confirm you're inside orca

You must be running in an orca pane. Check `TERM_PROGRAM=Orca` and that
`$ORCA_TERMINAL_HANDLE` is set. If not, stop and tell the user — this skill only
works from a pane inside the orca app.

Your own identity comes from env vars (no lookup needed):

- `$ORCA_TERMINAL_HANDLE` — your pane's handle (never send to this; that's you)
- `$ORCA_WORKTREE_ID` — your worktree; siblings usually share it
- `$ORCA_TAB_ID` — your tab

## Step 1 — Build the roster (do this first, every session)

Run the bundled discovery script (`<skill-dir>` = the directory this SKILL.md
lives in). It lists the OTHER panes in your worktree and tags each with a role
from orca's own `agentIdentity` (usually right, but NOT infallible — it has
mis-tagged an `agy` pane as `claude`, so cross-check with `preview`),
falling back to a title/preview heuristic only for panes orca hasn't tagged:

```bash
python <skill-dir>/scripts/roster.py          # panes in my worktree
python <skill-dir>/scripts/roster.py --all    # every pane orca knows
```

It prints `self_handle`, `worktree`, and a `roster` array of
`{handle, role, identity, title, preview, connected, writable}` (`identity` is
orca's raw `agentIdentity` tag, `""` when the pane is a bare shell orca can't tag).

**The roles are heuristic — confirm before you rely on them.** Trust `preview`
and `role`, not `title`: when an agent is launched from a shell (e.g. `agy` from
PowerShell), the pane's `title` stays the host shell's name (`pwsh.exe`) while
`preview` shows the real agent banner. `role: "unknown"` usually means that pane
has no agent running right now (it fell back to a plain shell).

**`connected: true` IS the "pane recognized" check — and it's free.** Do NOT
`terminal read` a pane at startup to see whether it's "ready" or logged in:
scrollback lags (a signed-in agy still shows an old "not signed in" banner), so a
readiness read burns tokens and can mislead. You don't need it — **readiness is
proven by the first real dispatch's callback**: if the worker pings back it was
ready; if a hop hangs, *that's* when you do the one bounded liveness read (see the
safety rules under 파일 버스). The only startup read worth doing is a targeted one
to break a real ambiguity (two same-type panes) — otherwise just ask "옆 pane 중
agy가 어느 거예요?".

```bash
orca terminal read --terminal <handle> --json   # ambiguity-break only, not routine
```

Present the roster to the user (role → handle) when roles need confirming (see
Step 2). Handles are long; keep them in variables for the rest of the turn.

Note: the roster's `role` is the **agent TYPE** (claude/codex/agy), not yet a job.
Assigning jobs is Step 2.

## Step 2 — Assign roles (who does what)

Discovery tells you *what* each pane is; now decide *what each one does* in this
session. **Pane count is arbitrary (2, 3, 4, …N)** and roles are free-form, not
tied to agent type — one dev + two reviewers, a researcher + an implementer, a
pure coordinator + three workers, whatever the task needs.

**Don't force a role-assignment turn — read what the user already gave:**

- **Role implied by the task** ("agy한테 검수 시켜", "codex한테 짜게 해") → don't
  ask; **declare it in one line and proceed** ("agy를 검수자로 배정, 바로
  시작합니다"). Confirmation is a statement, not a question.
- **User wants to assign** (nicknames, a custom map: "b=개발, c·d=검수") → do it
  their way and address panes by their nickname from then on. Nicknames are an
  option for whoever wants them, never a required step.
- **Genuinely ambiguous** (bare "시작", or the mapping is unclear) → propose a
  default map and confirm once.

**Ask only in these exception cases** (otherwise: silence + proceed):

- **Two panes of the same type** (agy ×2, claude ×2) → you can't auto-pick; ask
  "어느 게 검수예요?" once (this is the one routine startup read/question worth it).
- **A bare shell / `unknown` pane** → exclude it from auto-assignment; ringing a
  doorbell into a non-agent shell just throws a syntax error and goes silent.

The **coordinator is a role, not an identity.** It's whoever activated co-op and
holds the orca CLI this session — that happens to be the pane running this skill,
but the pattern is agent-agnostic: another agent (agy, codex, …) driving its own
co-op fills the exact same role, so never assume "the coordinator = Claude." The
coordinator can be **coordination-only** (a pure router: dispatch, route, collect —
never touches the work itself) **or** coordinator-plus-worker (also owns a slice,
like the dev or a review) — the *user* decides which. If the user wants a
*different* pane to command, reassign and step back to relaying for it.

**Default proposal (only a starting point — lean on each agent's strengths):**

- **Coordinator (this pane) → orchestrator.** Holds the handles and drives:
  dispatch work, **end your turn while workers run, and collect their report-back
  pings** (not by polling — see Patterns). The user talks to it; it fans out to the
  others. Whether it *also* does work is the user's call (see above).
- **`codex` / `opencode` → implementer.** Codegen, running tests, mechanical
  edits. `opencode` (runs whatever model its config points at, e.g. GLM) is a
  first-class worker here — drive it exactly like codex.
- **`agy` (Gemini) → researcher / second opinion.** Quick lookups, alternative
  takes, review. Remember agy is focus-sensitive and its idle-signal is
  unreliable — collect via `terminal read`, not `wait`.
  - **agy needs `--dangerously-skip-permissions` — but detect it, don't
    interrogate at 시작.** Unlike codex (YOLO mode) and Claude (its own auto
    modes), **agy has no auto/permission-skip mode of its own**, so it must be
    started as `agy --dangerously-skip-permissions` or it stalls on a permission
    prompt and every hop into it hangs. Per the premise the user launched it
    themselves, so don't add a startup question — instead **treat a hung first hop
    as the tell**: if agy never pings back, do the one bounded liveness read, and
    if you see a permission-approval screen, escalate ("agy를
    `--dangerously-skip-permissions`로 다시 띄워주세요"). Detect, don't pre-ask.
- **a second `claude` → reviewer / parallel worker**, as the task needs.

Keep the confirmed map as `role → handle` variables and, from here on, **refer to
panes by job** ("send to the implementer") so the intent survives even though the
underlying handle is just an opaque string. Re-run `roster.py` and re-confirm if a
pane later rotates, closes, or a new agent joins — the job map is only as live as
the roster it was built from.

This map is the input to everything below (dispatch, ask, relay): a "fan out"
means the orchestrator hands each worker its slice; a relay ROUTE is just the job
order expressed as handles.

## The two communication modes (this trips people up)

Because messaging is just typing into another pane, whether you can see a reply
**in the same turn** depends on the direction:

1. **You read the other pane** (`orca terminal read`) → **synchronous.** You send
   into pane B, wait/poll, and read B's scrollback back — all within your current
   turn. Use this when B is `agy`/`codex`/a tool and you're driving it.

2. **The other pane injects back into YOUR pane** (`orca terminal send --terminal
   $ORCA_TERMINAL_HANDLE ...`) → **asynchronous.** That text lands in your own
   input as a *new* user turn. You cannot see it in the current turn — you must
   **end your turn** and let it arrive as the next prompt. This is exactly how a
   relay ring wakes you back up.

Don't try to poll your own pane for an injection — end the turn and let it come.

### Cost model — waiting is free, reading is not (read this)

This is *the* thing to get right. `sleep`/waiting costs **zero tokens** — the
shell blocks, the model isn't running. What costs tokens is **`terminal read`
pulling scrollback into your context**: every poll dumps the target's screen
(banners, broken emoji, half-finished output) into the conversation, and because
the model re-reads the whole conversation each turn, chatty polling loops get
*quadratically* expensive. So the async report-back (mode 2) is not just tidy —
it's the **cheap** path: you spend nothing while the worker runs and pay for
exactly one short "완료" ping. Synchronous polling (mode 1) is the expensive
exception, justified only when you genuinely need the answer *this turn* to keep
going. **Default to dispatch + report-back; reach for polling only when blocked.**

## Messaging primitives

```bash
# Inject text (+Enter) into a pane. Check accepted:true in the JSON.
orca terminal send --terminal <handle> --text "your message" --enter --json

# Read a pane's output back.
orca terminal read --terminal <handle> --json
orca terminal read --terminal <handle> --cursor <cursor> --limit 1000 --json

# Block until a pane's TUI goes idle (see caveat).
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
```

**Measured caveats — save yourself the debugging:**

- **`--text` must be a single line.** A newline inside the message can submit the
  target's prompt early and split your message. Use ` | ` or `. ` as separators,
  keep it one line.
- **Force UTF-8 in any helper script.** On Korean/Windows, subprocess text
  decoding defaults to cp949 and crashes on orca's emoji/Korean output. The
  bundled script already sets `encoding="utf-8"`; do the same in any new one.
- **`wait --for tui-idle` is unreliable on the `agy` (Antigravity) TUI** — it
  times out even when the agent is done. For agy, don't trust idle-wait; poll
  `terminal read` on the cursor instead. Claude/codex TUIs are more likely to
  report idle, but verify per agent rather than assuming.
- **Reacquire handles if a send is rejected** — rerun `roster.py`; a stale handle
  means the pane rotated.

## Patterns

### Dispatch + report-back (THE DEFAULT — use this unless you have a reason not to)
Throw a task at a worker, tell it to **ping you back when done**, then **end your
turn**. You burn no tokens while it works; you wake up on its one-line completion
report. This is the default for basically every "옆 애한테 이거 시켜줘" — file
edits, doc writing, test runs, research.

**Point, don't spell out — this is the whole game.** The goal of delegating is
that *you* spend the fewest tokens directing while the worker does the reading,
the format-figuring, and the writing. So DON'T pre-digest the task into a full
spec in your prompt (that just moves all the work back onto your bill, the exact
mistake to avoid). Instead hand the worker **pointers**: which file(s) to read,
what to produce, and "report back." Let it open the sources and infer the rules
itself — the repo already carries the format/conventions (often the target file
literally documents its own "how to add an entry" procedure).

- ❌ spec (expensive, wrong): "페이스 6:30~7:00, frontmatter는 type/status/…, 표는
  이 컬럼들로, 목표 25~30분…" — you just wrote the whole thing.
- ✅ pointer (cheap, right): "`러닝 트레이닝 로그.md`의 '다음 세션 계획' 섹션 읽고,
  같은 폴더 기존 세션 파일 형식대로 일요일 세션 계획 파일 만들어. 끝나면 보고."

The trick for report-back: bake **your own handle** into the task.
`$ORCA_TERMINAL_HANDLE` expands to *your* handle in your shell before the text is
sent, so the worker receives the literal string and reports to you (its own
`$ORCA_TERMINAL_HANDLE` is different — its pane, not yours):

```bash
orca terminal send --terminal $AGY \
  --text "<짧은 포인터 지시>. 다 끝나면 반드시 이 명령으로 나한테 완료보고: orca terminal send --terminal $ORCA_TERMINAL_HANDLE --text '✅완료: <한줄요약>' --enter --json" \
  --enter --json
# check accepted:true, then STOP. End your turn. Do NOT poll.
# The worker's "✅완료" lands as your next user turn (async mode) — that's your cue
# to verify the result (read the file it changed, not its scrollback) and report up.
```

Verify the *artifact* (the file, the git log), not the worker's screen — reading
what changed on disk is cheaper and more trustworthy than scraping its TUI. If the
short pointer produced a wrong result, correct it with another short pointer — a
cheap re-dispatch still beats writing the full spec up front.

### 파일 버스 + 초인종 — 순서형·이종 파이프라인 (검수/승인 체인의 권장형)
여러 pane이 정해진 순서로 **각자 다른 일**을 하는 파이프라인(예: 생산→검수→2차검수→수정→재검수→문서화)에서는 **터미널을 데이터 채널로 쓰지 마라.** 긴 지시나 누적 결과를 `terminal send`에 실으면 한 줄 제약·따옴표 중첩·payload 비대·한글 mojibake에 전부 걸린다(전부 실측된 실패다). 대신 역할을 갈라라:

- **터미널 = 초인종만.** 워커에게 보내는 건 매번 딱 한 줄: `"<작업폴더>\.relay\TASK.md 읽고 그 안의 지시를 그대로 수행해."` 완료 신호도 워커가 보내는 한 줄(`완료:B-1차검수`)뿐.
- **파일시스템 = 데이터 버스.** 작업 폴더에 `.relay/`를 만들고, 이번 hop의 상세 지시는 `TASK.md`(코디네이터가 자기 파일쓰기 수단으로 갱신 — Claude면 Write 툴, 다른 에이전트면 그에 준하는 파일 쓰기), 누적 결과는 `RESULTS.md`(워커가 append), 산출물은 실제 파일로. 따옴표·mojibake·payload 문제가 **구조적으로** 사라진다.
- **너(코디네이터)가 라우터, 폴링은 없음.** 다음 담당은 네 턴에서 정한다. 워커는 끝나면 너에게 `완료:X`를 inject하고, 그게 새 입력(user turn)으로 도착해 너를 깨운다. **진행상황을 `terminal read`로 폴링하지 마라** — 결과는 `RESULTS.md` 파일을 직접 읽는다(스크롤백 아님, 위 비용 모델 그대로).

한 hop의 루프:

1. **매 hop마다 역할 템플릿을 셸로 복사해 `.relay/TASK.md`를 덮어쓴 뒤(예: `cp scripts/TASK.review.template.md .relay/TASK.md`) 빈칸(`<...>`)만 채운다.** 항상 템플릿에서 fresh하게 시작하는 게 핵심 — **지난 `TASK.md`를 그대로 고쳐 쓰면(edit-in-place) 이전 역할의 필드가 찌꺼기로 남아 오염된다.** 복사를 셸(`cp`)이 하니 조율자 토큰이 거의 안 들고, 조율자는 파일 전체를 다시 쓰지 말고 **빈칸만** 채운다(템플릿은 내용 고정이라 세션 처음에 한 번 읽어두면 빈칸 위치를 안다). 지시·결과기록 위치·완료보고 명령을 **파일이 전부 담아** 따옴표·길이 문제를 흡수한다. 옛 `TASK.md`는 보관 불필요(감사 이력은 `RESULTS.md`가 들고 있으니 삭제 말고 그냥 덮어쓴다).
2. 담당 pane에 초인종 한 줄 send → **턴을 끝낸다.**
3. 신호로 깨어난다: `완료:X`면 `RESULTS.md`를 읽고 다음 담당의 `TASK.md`로 갈아끼워 2로 / `실패:X: <사유>`면 재배정하거나 사용자에게 에스컬레이션 / `완주`면 종료. 연속 같은 담당(예: 2차재검수→문서화가 둘 다 C)은 한 `TASK.md`에 묶어 초인종을 한 번만 울린다.

#### `.relay/` 파일 규격 (정형 — 이대로 고정한다)

즉흥 작성하지 말고 **`<skill-dir>/scripts/TASK.template.md`를 복사**해 값만 채워 `<작업폴더>/.relay/TASK.md`로 저장한 뒤 초인종을 울린다. 규격은 아래로 **고정**한다:

**`TASK.md`** = 계약 헤더(YAML frontmatter) + 본문 6섹션.
- **헤더(키 고정, 조율자가 값만 채움)**: `task_id · assignee · step · target · inputs · constraints · report_to · on_done · on_fail · final`. 완료/실패 신호와 추적 키가 여기서 확정된다.
- **본문**: `## 목표`(검증 가능한 한 줄) · `## 입력 — 먼저 읽을 것`(inputs 파일) · `## 할 일`(포인터 위주) · `## 완료 기준(DoD)`(체크박스 — 전부 참이어야 done) · `## 결과 기록`(RESULTS.md append) · `## 완료/실패 보고`(정확한 send 명령).

**`RESULTS.md`** — 첫 줄 `# 릴레이 결과 누적 로그`로 초기화. 각 워커가 `## <닉네임> <단계>` 블록(`- 결과:` + 검수 단계면 `- 판정: 통과|보류`)을 **append만** 한다(덮어쓰기 금지). 조율자는 여기를 읽어 다음 hop을 정한다.

**신호 문법(고정, 세 가지)** — 성공 중간 `완료:<닉네임>-<단계>`, 파이프라인 종료 `완주`, 실패·중단 `실패:<닉네임>-<단계>: <사유>`. 워커는 승인 프롬프트·에러로 막혀도 **조용히 멈추지 말고 실패 신호를 반드시 보낸다(무보고 = 체인 사망).** 조율자는 이 셋 중 하나로 깨어나 — 완료면 다음 `TASK.md` 교체, 실패면 재배정/사용자 에스컬레이션.

스켈레톤 전체는 `scripts/TASK.template.md` 참고. **매번 새로 쓰지 말고 사전 제작 템플릿을 복사해 값만 채운다**(토큰 절약·일관성): 범용 `TASK.template.md`, 역할별 `TASK.dev.template.md`(구현/수정) · `TASK.review.template.md`(정적 검수, 5렌즈+판정) · `TASK.doc.template.md`(문서화). 셋 다 base 구조에 역할별 `할 일`·`DoD`만 미리 채워져 있다.

이 방식과 **Relay ring의 차이**: ring은 route를 메시지에 실어 워커끼리 직접 넘긴다(payload가 지저분하고 각 워커가 라우팅을 재작성). 파일 버스는 route를 코디네이터가 쥐고 데이터는 파일로 빼서, 순서가 한 곳에서 통제되고 pane 사이 메시지는 초인종 한 줄로 남는다. **이종 작업 파이프라인이면 파일 버스를 기본으로 써라.**

**무인 전제:** 워커의 `RESULTS.md` 쓰기와 완료보고 send가 **승인 프롬프트에서 멈추면 체인이 죽고 너는 안 깨어난다.** 무인으로 돌리려면 워커를 auto-approve로 띄운다(agy는 `--dangerously-skip-permissions`, opencode 등도 자동승인/도구실행허용 모드). 그게 안 되면 파일쓰기·send마다 사람이 Enter로 승인해야 하고, 멈춘 지점은 사용자가 알려줘야 한다.

**안전·재귀 규칙 (실측·리뷰로 도출 — 코드 0):**

- **초인종 전 대상 준비 확인**: `send`는 상대 상태를 안 보고 주입하므로, 직전 작업 직후엔 초인종 전 `orca terminal wait --for tui-idle`(또는 짧은 read)로 대상이 프롬프트 대기인지 확인한다. 안 그러면 신호가 실행 중 화면에 섞여 씹힌다.
- **워커 재사용 시 컨텍스트 리셋**: 같은 워커 pane에 **새 무관 hop**을 줄 땐, 초인종 전에 세션 리셋(예: `/clear`)을 1회 send한다. 워커는 장기 TUI 세션이라 스텝이 쌓이면 컨텍스트 누적으로 토큰 폭증·지시 drift·침묵 크래시가 온다(실전 **최빈** 실패). 비용 0. (파일 버스가 지시를 파일로 빼두므로 리셋해도 hop은 TASK.md로 이어진다.)
- **크래시성 무보고 대비(생사 확인)**: 워커가 *stall*이면 `실패:`를 보내지만 *크래시/OOM/rate-limit*이면 그것조차 못 보낸다. 무보고가 `expect_sec`를 크게 넘으면 **`orca terminal read --terminal <id> --limit 30 --json` 딱 1회**(반드시 `--limit`으로 tail 제한 — 무제한 read는 조율자 컨텍스트를 터뜨린다)로 생사만 확인하고, 죽었으면 재배정. 상시 폴링은 여전히 금지.
- **AGENT_PROFILES 강제 갱신(재귀 학습 엔진)**: 파이프라인 중 `실패:` 신호가 1회라도 나면, 조율자는 그 원인(새로 안 에이전트 한계/주의)을 **`scripts/AGENT_PROFILES.md`에 1줄 추가하기 전에는 `완주`를 선언하지 않는다.** 자동 패치 엔진 없이 이 규약 하나로 파일이 안 썩고 스킬이 경험에서 학습한다. 역할 배정 전엔 이 파일을 참조한다.
- **완주 시 회고 취합**: `완주` 때 조율자는 RESULTS의 `개선점` 줄들을 훑어 반복되는 통증이 있으면 템플릿(`TASK.*.template.md`) tweak을 **수동 제안**한다(자동화는 진짜 반복될 때).
- **병렬 확장 주의**: 순차 파이프라인은 단일 `TASK.md`로 안전(경합 없음). 병렬 fan-out으로 갈 땐 워커별 파일 네임스페이싱(`TASK_<run>_<step>.md`)이 필요하다 — 락은 그때만.

### Ask / round-trip (synchronous — the expensive exception)
Only when you truly need the answer **this turn** to continue (e.g. its reply
decides your very next step and you can't end the turn). Send, poll, read — all in
one turn. **Poll cheaply: one bounded `sleep` then a single read of the last few
lines, not a per-iteration scrollback dump.** (Some harnesses — Claude Code among
them — block a standalone `sleep`; there, wait with a bounded `until … read` loop
or run the wait in the background instead.) If the answer isn't blocking your next
move, don't do this — dispatch + report-back instead.
```bash
orca terminal send --terminal $AGY --text "이 함수 시간복잡도 한 줄로만 답해줘" --enter --json
sleep 20   # waiting is free; give it room so you read once, not five times
orca terminal read --terminal $AGY --json   # one read, check for the answer
```

### Relay ring / token ring (the pattern from this skill's origin)
Pass a message around a ring of panes — e.g. claude→agy→codex→claude→… Make the
routing **unambiguous by carrying an explicit ordered list of remaining
recipients** and the rule "send to the FIRST handle, then remove it." Do NOT use
an index-plus-counter scheme — an off-by-one in "increment then look up" vs
"look up then increment" silently drops a hop (learned the hard way).

Seed message you inject into the first pane:

> 🔗릴레이. 규칙: 이 메시지 끝의 ROUTE 목록에서 **맨 앞 핸들 = 네가 보낼 대상**이다.
> 대상을 스스로 계산하지 말고 오직 맨 앞만 써라. (A) ROUTE에 2개 이상 남았으면:
> 맨 앞 하나만 지운 새 ROUTE로 이 메시지를 갱신해서 그 대상에게
> `orca terminal send --terminal <그대상> --text "<갱신된 메시지 전체>" --enter --json`
> 실행. (B) 정확히 1개 남았으면: 그 대상에게 `--text "🏁완주"`만 보내고 종료.
> ROUTE=[ handleA , handleB , handleC , ... ]

Build the ROUTE as the ordered targets *after* your seed send. When the ring
routes back through your own pane, the message arrives as a new turn (async
mode): recognize it, pop the head, forward to the new head, and end your turn
again. You appear in the ring wherever your handle sits in ROUTE.

## Safety: always terminate the loop

Cross-pane messaging can run away — an unbounded ping-pong burns tokens on every
agent forever. Every relay/loop MUST carry a stop condition the agents can see: a
draining ROUTE list, a hop counter with a ceiling, or an explicit "🏁완주 → stop."
Never seed a loop without one. If you're unsure a chain will terminate, prefer a
fixed ROUTE (finite by construction) over a "keep going until X" rule.

## Why this beats a passive multiplexer

Older Windows AI multiplexers (e.g. wmux) either refused raw injection into
managed agent panes or couldn't wake an idle receiver, so full automatic
back-and-forth needed a human or a self-loop. orca's `terminal send` writes to
the target's stdin directly, so idle panes wake and true agent↔agent tiki-taka
runs unattended. That difference is the reason this skill exists.
