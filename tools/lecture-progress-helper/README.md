# Lecture Progress Helper (강의 진행 도우미)

**Lecture Progress Helper**는 이상에듀(esangedu.kr) 온라인 강의 수강 시 페이지 넘김을 자동화하는 Playwright 기반 파이썬 도구.<br/>
영상이 기준 진행률에 도달하면 `다음` / `학습종료 및 목차이동` / 다음 강의 `수강하기` 버튼 자동 클릭.

## ✨ 주요 기능 (Key Features)

- **진행률 감지**: 영상 진행률과 페이지 진행률(n/n) 실시간 표시.
- **자동 넘김**: 기준 진행률(기본 90%) 도달 시 다음 페이지 또는 학습종료 버튼 자동 클릭.
- **연속 수강**: 강의 목록 복귀 시 미완료 강의의 `수강하기` 버튼 자동 클릭.
- **알림**: Windows 토스트 알림, CMD 벨, 클릭 대상 버튼 강조 표시.
- **세션 유지**: 별도 Chrome 프로필에 로그인 세션 저장.

## 🚀 시작하기 (Quick Start)

### 1. 설치 (Installation)
Google Chrome 설치 필요.

```cmd
python -m pip install -r requirements.txt
```

### 2. 실행 (Usage)

```cmd
python lecture_progress_helper.py
```

1. Chrome 실행 및 이상에듀 홈페이지 이동.
2. 브라우저에서 직접 로그인 후 CMD에서 Enter.
3. 프로그램이 `나의 강의실` 클릭.
4. 브라우저에서 과정을 눌러 강의 목록(수강하기) 화면을 연 뒤 CMD에서 Enter.
5. 남은 첫 강의 `수강하기`(이어보기) 자동 클릭 및 감지 시작. 이후 페이지/강의 넘김 자동 진행.
   - 강의를 직접 재생한 상태에서 Enter를 눌러도 동작.

감지 중 CMD 표시 예시:

```text
[monitor] [########----------------------]  27.4% | 17:31/63:59 | p 1/1 | left 0 | playing
```

- `27.4%`: 영상 진행률
- `17:31/63:59`: 재생 시간 / 전체 시간
- `p 1/1`, `left 0`: 현재 페이지 / 전체 페이지, 남은 페이지 수

종료: CMD에서 `Ctrl+C`.

## ⚙️ 옵션 (Options)

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--threshold` | `90` | 자동 클릭 기준 영상 진행률(%) |
| `--interval` | `1` | 감지 주기(초) |
| `--profile-dir` | `C:\tmp\lecture-progress-helper-profile` | 로그인 세션 저장 Chrome 프로필 폴더 |
| `--zoom` | `1.0` | 페이지 확대 비율 (예: `1.25`) |
| `--cdp` | - | 기존 원격 디버깅 Chrome 연결 주소 (예: `http://127.0.0.1:9222`) |
| `--no-windows-notify` | - | Windows 토스트 알림 끄기 |

## 📦 단일 EXE 빌드 (Build)

Python 미설치 PC 배포용. 실행 PC에는 Chrome만 필요.

```cmd
python build_release.py
```

결과물: `release\lecture_progress_helper.exe` (exe에도 동일 옵션 사용 가능)

## 🧪 자가 점검 (Self-check)

```cmd
python test_lecture_progress_helper.py
```

## ⚠️ 주의 (Notes)

- 이상에듀 / 나야넷 플레이어 화면 구조 기준 동작. 사이트 개편 시 셀렉터 수정 필요.
- 영상은 실제 재생 필요(건너뛰기 아님). 기준 진행률 도달 후 버튼 클릭만 대행.
