# 🧰 도구 (Tools)

복잡한 설정 없이 즉시 사용 가능한 경량 유틸리티 (순수 자바스크립트 / 파이썬).

## 구조

```
tools/
└─ <tool-name>/
    ├─ index.html   # 데모 / 사용 예시 (JS 도구)
    ├─ js/          # 라이브러리 소스 (JS 도구)
    ├─ *.py         # 실행 스크립트 (파이썬 도구)
    └─ README.md    # 도구 설명
```

## 도구 목록

### 1. [LiteGantt](./lite-gantt)
초경량 순수 자바스크립트 간트 차트 라이브러리.
- **특징**: 의존성 없음, 자동 무지개 색상, 반응형 디자인.
- **용도**: 경력 기술서, 프로젝트 일정, 로드맵 시각화.
- [자세히 보기](./lite-gantt/README.md)

### 2. [LiteToast](./lite-toast)
의존성 없는 초경량 토스트 알림 라이브러리.
- **특징**: CSS 자동 주입, 4가지 테마(Success, Error, Warning, Info) 지원.
- **용도**: 웹 애플리케이션 알림, 사용자 피드백 제공.
- [자세히 보기](./lite-toast/README.md)

### 3. [Lecture Progress Helper](./lecture-progress-helper)
이상에듀 온라인 강의 페이지 넘김 자동화 도구 (Python + Playwright).
- **특징**: 영상 진행률 감지, 다음/학습종료/수강하기 자동 클릭, 단일 exe 빌드 지원.
- **용도**: 장시간 온라인 의무교육 수강 보조.
- [자세히 보기](./lecture-progress-helper/README.md)
