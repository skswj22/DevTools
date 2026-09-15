# LiteGantt (라이트 간트)

**LiteGantt**는 외부 의존성이 전혀 없는(Zero Dependency), 초경량 순수 자바스크립트 간트 차트 라이브러리.<br/>
복잡한 설정 없이 스크립트 파일 하나만으로 즉시 아름다운 반응형 타임라인 차트 생성 가능.

## ✨ 주요 기능 (Key Features)

- **초경량 (Ultra-Lightweight)**: 외부 라이브러리(jQuery, D3 등) 의존성 0%. 단일 JS 파일.
- **범용성 (Generic)**: 경력(Career), 프로젝트 일정, 로드맵 등 어떤 기간 데이터든 표현 가능.
- **자동 반응형 (Responsive)**: PC에서는 고정된 사이드바, 모바일에서는 비율 자동 조정 (PC/Mobile Hybrid Layout).
- **자동 무지개 색상 (Auto Rainbow)**: 데이터 개수에 맞춰 자동으로 색상 스펙트럼(Red-Violet) 균등 분배.
- **컴팩트 디자인 (Compact Design)**: 여백을 최소화하여 한 화면에 많은 정보를 깔끔하게 표시.

## 🚀 시작하기 (Quick Start)

### 1. 설치 (Installation)
프로젝트에 `lite_gantt.js` 파일 포함.

```html
<script src="js/lite_gantt.js"></script>
```

### 2. 기본 사용법 (Usage)

HTML에 차트를 그릴 컨테이너를 생성하고, 자바스크립트로 데이터 추가.

```html
<!DOCTYPE html>
<html>
<body>

    <!-- 1. 차트가 들어갈 컨테이너 -->
    <div id="my-gantt"></div>

    <!-- 2. 라이브러리 로드 -->
    <script src="js/lite_gantt.js"></script>

    <script>
        // 3. 차트 인스턴스 생성 (컨테이너 ID 전달)
        var chart = new LiteGantt('my-gantt');

        // 4. 데이터 추가 (라벨, 시작일, 종료일)
        chart.add('프로젝트 A', '2023-01-01', '2023-06-30');
        chart.add('프로젝트 B', '2023-07-01', '2023-12-31');
        chart.add('진행 중인 작업', '2024-01-01'); // 종료일 생략 시 'Present' 처리

        // 5. 화면에 그리기
        chart.render();
    </script>

</body>
</html>
```

## 📚 API 레퍼런스

### `new LiteGantt(containerId, [data])`
- **containerId** (String): 차트를 렌더링할 HTML 요소의 ID.
- **data** (Array, Optional): 초기 데이터 배열 (선택 사항).

### `.add(label, startDate, [endDate])`
차트에 항목을 하나씩 추가.
- **label** (String): 항목 이름 (예: 회사명, 프로젝트명).
- **startDate** (String): 시작 날짜 (Format: 'YYYY-MM-DD').
- **endDate** (String, Optional): 종료 날짜. 생략 시 현재(Present)까지 진행 중인 것으로 간주하여 화살표 표시.

### `.render()`
추가된 데이터를 바탕으로 차트 렌더링.
- 데이터가 추가된 후 반드시 호출해야 화면에 나타남.

## 🎨 스타일 커스터마이징
`js/lite_gantt.js` 파일 상단의 `baseStyles` 변수에서 CSS를 직접 수정하여 디자인 변경 가능.<br/>
기본적으로 ID `lite-gantt-styles`로 스타일이 헤드에 주입됨.

## 📜 라이선스 (License)
본 소프트웨어는 **Apache License 2.0**을 준수함.<br/>
유연한 사용과 수정이 보장되며, 상업적 활용을 포함한 모든 권리가 전적으로 허용됨.

## 👤 만든이 (Author)
Created by **김동완**.
