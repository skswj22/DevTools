# LiteToast (라이트 토스트)

**LiteToast**는 외부 의존성이 전혀 없는(Zero Dependency), 초경량 순수 자바스크립트 토스트 알림 라이브러리.
스크립트 로드 후 JS 한 줄 호출만으로 즉시 사용 가능.

## ✨ 주요 기능 (Key Features)

- **초경량 (Ultra-Lightweight)**: 외부 라이브러리 및 별도 CSS 파일 불필요. 단일 JS 파일 내 스타일 포함.
- **자동 스타일 주입 (Auto Injection)**: 첫 호출 시 필요한 CSS 및 컨테이너가 DOM에 자동 삽입.
- **4가지 테마 지원**: 성공(Success), 오류(Error), 경고(Warning), 정보(Info) 전용 스타일 제공.
- **애니메이션 처리**: 유동적인 입출력 애니메이션 적용.

## 🚀 시작하기 (Quick Start)

### 1. 설치 (Installation)
프로젝트에 `lite_toast.js` 파일 포함.

```html
<script src="js/lite_toast.js"></script>
```

### 2. 기본 사용법 (Usage)

자바스크립트 어디서든 즉시 호출.

```javascript
// 기본 사용 (성공)
LiteToast.success('작업이 완료되었습니다.');

// 오류 알림
LiteToast.error('알 수 없는 오류 발생');

// 알림 지속 시간 설정 (단위: ms)
LiteToast.info('5초 동안 표시됩니다.', 5000);
```

## 📚 API 레퍼런스

### `LiteToast.success(message, [duration])`
성공 알림 표시. (초록색)

### `LiteToast.error(message, [duration])`
오류 알림 표시. (빨간색)

### `LiteToast.warning(message, [duration])`
경고 알림 표시. (주황색)

### `LiteToast.info(message, [duration])`
정보 알림 표시. (파란색)

- **message** (String): 표시할 메시지 텍스트.
- **duration** (Number, Optional): 표시 시간 (기본값: 3000ms).

## 📜 라이선스 (License)
본 소프트웨어는 **Apache License 2.0**을 준수함.<br/>
유연한 사용과 수정이 보장되며, 상업적 활용을 포함한 모든 권리가 전적으로 허용됨.

## 👤 만든이 (Author)
Created by **김동완**.
