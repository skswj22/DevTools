"""순수 판단 로직 자가 점검. 사용법: python test_lecture_progress_helper.py"""
from lecture_progress_helper import decide, find_page_progress


def lecture(percent: float, page: dict | None) -> dict:
    return {
        "isLectureScreen": True,
        "url": "u",
        "video": {"percent": percent, "currentTime": 60, "duration": 100, "src": "v"},
        "pageProgress": page,
    }


# 영상 시간(17:31/63:59)은 페이지 진행률로 오인하지 않음
assert find_page_progress("17:31/63:59") is None
assert find_page_progress("17:31/63:59  2 / 5")["current"] == 2
assert find_page_progress("0/5") is None

assert decide(lecture(50, {"current": 1, "total": 3}), 90) is None
assert decide(lecture(95, {"current": 1, "total": 3}), 90).action == "next"
assert decide(lecture(95, {"current": 3, "total": 3}), 90).action == "end"
assert decide(lecture(95, None), 90).action == "unknown"
assert decide({**lecture(95, None), "isLectureScreen": False}, 90) is None

print("ok")
