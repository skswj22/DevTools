from __future__ import annotations

import argparse
import asyncio
import os
import re
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


try:
    from playwright.async_api import (
        Browser,
        BrowserContext,
        Error as PlaywrightError,
        Locator,
        Page,
        Playwright,
        TimeoutError as PlaywrightTimeoutError,
        async_playwright,
    )
except ImportError:  # pragma: no cover - operator-facing dependency message.
    print(
        "playwright package is required.\n"
        "Install: python -m pip install playwright\n"
        "This app uses your installed Chrome channel.",
        file=sys.stderr,
    )
    raise

try:
    from winotify import Notification, audio
except ImportError:  # pragma: no cover - desktop notification is optional at runtime.
    Notification = None
    audio = None


DEFAULT_PROFILE_DIR = Path(r"C:\tmp\lecture-progress-helper-profile")
DEFAULT_START_URL = "https://esangedu.kr/esang/main/"
MY_CLASSROOM_TEXT = "나의 강의실"
CLASSROOM_TITLE = "내강의실"
END_BUTTON_TEXT = "학습종료"
END_BUTTON_TEXT_2 = "목차"
COURSE_START_TEXT = "수강하기"
NEXT_BUTTON_SELECTOR = (
    'a[href*="jumpVideo"][href*="next"], '
    'a[onclick*="jumpVideo"][onclick*="next"], '
    'button[onclick*="jumpVideo"][onclick*="next"]'
)

VIDEO_STATE_SCRIPT = """
video => ({
  currentTime: video.currentTime || 0,
  duration: Number.isFinite(video.duration) ? video.duration : 0,
  ended: video.ended,
  paused: video.paused,
  readyState: video.readyState,
  src: video.currentSrc || video.src || ""
})
"""

HIGHLIGHT_SCRIPT = """
el => {
  el.style.outline = "4px solid #ff2d55";
  el.style.outlineOffset = "3px";
  el.style.background = "#fff36d";
  el.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
}
"""


@dataclass(frozen=True)
class Decision:
    action: str
    key: str
    message: str


_STATUS_LINE_ACTIVE = False
_ANSI_READY = False


def enable_ansi_console() -> None:
    global _ANSI_READY
    if _ANSI_READY:
        return

    if os.name == "nt":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            stdout_handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(stdout_handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(stdout_handle, mode.value | 0x0004)
        except Exception:
            pass

    _ANSI_READY = True


def clear_status_line() -> None:
    global _STATUS_LINE_ACTIVE
    if _STATUS_LINE_ACTIVE:
        enable_ansi_console()
        sys.stdout.write("\r\x1b[2K\n")
        sys.stdout.flush()
        _STATUS_LINE_ACTIVE = False


def write_status_line(message: str) -> None:
    global _STATUS_LINE_ACTIVE

    enable_ansi_console()
    width = max(shutil.get_terminal_size((100, 20)).columns - 4, 40)
    if len(message) > width:
        message = message[: max(width - 3, 1)] + "..."

    sys.stdout.write("\r\x1b[2K" + message)
    sys.stdout.flush()
    _STATUS_LINE_ACTIVE = True


def format_seconds(seconds: float | int | None) -> str:
    if seconds is None:
        return "--:--"
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_mmss(seconds: float | int | None) -> str:
    if seconds is None:
        return "--:--"
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    return f"{minutes}:{secs:02d}"


def progress_bar(percent: float | int | None, width: int = 30) -> str:
    if percent is None:
        return "[" + ("-" * width) + "]"

    bounded = max(0.0, min(100.0, float(percent)))
    filled = round((bounded / 100.0) * width)
    return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"


def find_page_progress(text: str) -> dict[str, int | str] | None:
    # Avoid matching video time such as 17:31/63:59.
    pattern = re.compile(r"(?<!:)\b(\d{1,3})\s*/\s*(\d{1,3})\b(?!:)")
    candidates: list[dict[str, int | str]] = []
    for match in pattern.finditer(text):
        current = int(match.group(1))
        total = int(match.group(2))
        if total > 0 and 0 < current <= total:
            candidates.append({"current": current, "total": total, "text": match.group(0)})
    return candidates[-1] if candidates else None


def count_course_list_rows(text: str) -> int:
    return sum(1 for line in text.splitlines() if re.search(r"\d{1,2}강", line) and "수강하기" in line)


def send_windows_notification(message: str) -> bool:
    if os.name != "nt" or Notification is None:
        return False

    try:
        toast = Notification(
            app_id="Lecture Progress Helper",
            title="강의 진행 알림",
            msg=message,
            duration="long",
        )
        if audio is not None:
            toast.set_audio(audio.Default, loop=False)
        toast.show()
        return True
    except Exception:
        return False


async def locator_count(locator: Locator) -> int:
    try:
        return await locator.count()
    except PlaywrightError:
        return 0


async def locator_exists(locator: Locator) -> bool:
    return await locator_count(locator) > 0


async def get_body_text(page: Page) -> str:
    try:
        return await page.locator("body").inner_text(timeout=3000)
    except PlaywrightError:
        return ""


async def get_video_state(page: Page) -> dict[str, Any] | None:
    videos = page.locator("video")
    if not await locator_exists(videos):
        return None

    try:
        state = await videos.first.evaluate(VIDEO_STATE_SCRIPT, timeout=3000)
    except PlaywrightError:
        return None

    duration = float(state.get("duration") or 0)
    current_time = float(state.get("currentTime") or 0)
    state["percent"] = (current_time / duration * 100) if duration > 0 else None
    return state


def end_button_locator(page: Page) -> Locator:
    return page.locator("a, button").filter(has_text=END_BUTTON_TEXT).filter(has_text=END_BUTTON_TEXT_2)


async def has_end_button(page: Page) -> bool:
    return await locator_exists(end_button_locator(page))


def action_target_locator(page: Page, action: str) -> Locator | None:
    if action == "next":
        return page.locator(NEXT_BUTTON_SELECTOR)
    if action == "end":
        return end_button_locator(page)
    return None


async def collect_page_state(page: Page) -> dict[str, Any]:
    title = await safe_title(page)
    url = await safe_url(page)
    body_text = await get_body_text(page)
    video = await get_video_state(page)
    page_progress = find_page_progress(body_text)
    course_list_count = count_course_list_rows(body_text)

    has_next_button = await locator_exists(page.locator(NEXT_BUTTON_SELECTOR))
    has_video_js = await locator_exists(page.locator(".video-js, .vjs-tech, .vjs-control-bar"))
    has_progress_bar = await locator_exists(
        page.locator('[role="slider"][aria-label*="Progress"], .vjs-progress-holder, .vjs-play-progress')
    )
    end_button_exists = await has_end_button(page)

    lecture_signals = [
        video is not None,
        bool(video and (video.get("duration") or 0) > 0),
        has_video_js,
        has_progress_bar,
        has_next_button or end_button_exists,
        "/player/" in url,
        "학습" in title,
    ]
    lecture_score = sum(1 for signal in lecture_signals if signal)

    return {
        "title": title,
        "url": url,
        "isLectureScreen": lecture_score >= 3 and course_list_count < 3,
        "isCourseListScreen": course_list_count > 0 and lecture_score < 3,
        "lectureScore": lecture_score,
        "courseListCount": course_list_count,
        "video": video,
        "pageProgress": page_progress,
        "hasNextButton": has_next_button,
        "hasEndButton": end_button_exists,
    }


def decide(state: dict[str, Any], threshold: float) -> Decision | None:
    if not state.get("isLectureScreen"):
        return None

    video = state.get("video")
    if not video:
        return None

    percent = video.get("percent")
    if percent is None or percent < threshold:
        return None

    current_time = format_seconds(video.get("currentTime"))
    duration = format_seconds(video.get("duration"))
    page = state.get("pageProgress")
    lecture_key = video.get("src") or state.get("url") or "unknown-lecture"

    if not page:
        return Decision(
            action="unknown",
            key=f"unknown:{lecture_key}:{int(percent)}",
            message=(
                f"영상 진행률이 {percent:.1f}%입니다. 현재 시간 {current_time} / {duration}.\n"
                "페이지 진행률 n/n을 찾지 못했습니다. 화면을 직접 확인해주세요."
            ),
        )

    current = int(page["current"])
    total = int(page["total"])
    page_label = f"{current}/{total}"

    if current < total:
        return Decision(
            action="next",
            key=f"next:{lecture_key}:{page_label}",
            message=(
                f"영상 진행률이 {percent:.1f}%입니다. 현재 페이지는 {page_label}입니다.\n"
                "다음 버튼을 자동으로 누릅니다."
            ),
        )

    return Decision(
        action="end",
        key=f"end:{lecture_key}:{page_label}",
        message=(
            f"영상 진행률이 {percent:.1f}%입니다. 현재 페이지는 {page_label}입니다.\n"
            "'학습종료 및 목차이동' 버튼을 자동으로 누릅니다."
        ),
    )


def log_state(state: dict[str, Any]) -> None:
    if not state.get("isLectureScreen"):
        message = (
            "[monitor] 강의 화면 대기 중 | "
            f"score {state.get('lectureScore', 0)} | "
            f"course rows {state.get('courseListCount', 0)} | "
            f"{state.get('title', '')}"
        )
        write_status_line(message)
        return

    video = state.get("video") or {}
    percent = video.get("percent")
    page = state.get("pageProgress")
    percent_text = "--" if percent is None else f"{percent:5.1f}%"
    bar_text = progress_bar(percent)
    page_text = "--" if not page else f"{page['current']}/{page['total']}"
    remaining_pages = "--" if not page else str(max(int(page["total"]) - int(page["current"]), 0))
    current = format_mmss(video.get("currentTime"))
    duration = format_mmss(video.get("duration"))
    status = "paused" if video.get("paused") else "playing"
    message = (
        f"[monitor] {bar_text} {percent_text} | {current}/{duration} | "
        f"p {page_text} | left {remaining_pages} | {status}"
    )
    write_status_line(message)


async def wait_for_enter(message: str) -> None:
    await asyncio.to_thread(input, message)


async def safe_title(page: Page) -> str:
    try:
        return await page.title()
    except PlaywrightError:
        return ""


async def safe_url(page: Page) -> str:
    try:
        return page.url
    except PlaywrightError:
        return ""


async def setup_zoom(context: BrowserContext, zoom: float) -> None:
    if zoom == 1.0:
        return

    await context.add_init_script(
        f"""
(() => {{
  const zoom = {zoom!r};
  const applyZoom = () => {{
    if (document.documentElement) {{
      document.documentElement.style.zoom = String(zoom);
    }}
  }};
  applyZoom();
  document.addEventListener("DOMContentLoaded", applyZoom, {{ once: true }});
}})();
"""
    )


async def apply_zoom(page: Page, zoom: float) -> None:
    if zoom == 1.0:
        return

    try:
        await page.evaluate("zoom => { document.documentElement.style.zoom = String(zoom); }", zoom)
    except PlaywrightError:
        pass


async def newest_page_matching(
    context: BrowserContext,
    predicate: Callable[[str, str], bool],
) -> Page | None:
    for page in reversed(context.pages):
        url = await safe_url(page)
        title = await safe_title(page)
        if predicate(url, title):
            return page
    return None


async def choose_initial_page(context: BrowserContext, start_url: str) -> Page:
    if context.pages:
        page = context.pages[-1]
    else:
        page = await context.new_page()

    if start_url:
        await page.goto(start_url, wait_until="domcontentloaded")

    return page


async def click_my_classroom(context: BrowserContext, fallback_page: Page) -> Page:
    print("[step] '나의 강의실' 링크를 찾는 중입니다.", flush=True)
    # 로그인 시 공지 팝업 탭이 뜨므로 최신 탭만 보지 않고 링크가 있는 탭을 찾음.
    for page in [*reversed(context.pages), fallback_page]:
        if page.is_closed():
            continue
        link = page.locator("a", has_text=MY_CLASSROOM_TEXT)
        if await locator_count(link) > 0:
            break
    else:
        raise RuntimeError("'나의 강의실' 링크를 찾지 못했습니다. 로그인 상태와 현재 페이지를 확인해주세요.")
    await page.bring_to_front()

    try:
        async with context.expect_page(timeout=5000) as popup_info:
            await link.first.click(timeout=10000)
        opened_page = await popup_info.value
        await opened_page.wait_for_load_state("domcontentloaded", timeout=10000)
    except PlaywrightTimeoutError:
        opened_page = page
        try:
            await opened_page.wait_for_load_state("domcontentloaded", timeout=10000)
        except PlaywrightTimeoutError:
            pass

    await asyncio.sleep(1)
    classroom = await newest_page_matching(
        context,
        lambda url, title: "/myClass/study" in url or CLASSROOM_TITLE in title,
    )
    classroom = classroom or opened_page
    await classroom.bring_to_front()
    print(f"[step] 내 강의실 후보: {classroom.url} / {await safe_title(classroom)}", flush=True)
    return classroom


async def find_lecture_player_page(context: BrowserContext, fallback_page: Page) -> Page:
    player = await newest_page_matching(
        context,
        lambda url, title: "cont.nayanet.co.kr/player" in url
        or "mp4PlayerSSO.php" in url
        or "나야넷 안전보건교육센터 학습" in title,
    )
    if player:
        await player.bring_to_front()
        return player

    for page in reversed(context.pages):
        try:
            state = await collect_page_state(page)
        except PlaywrightError:
            continue
        if state.get("isLectureScreen"):
            await page.bring_to_front()
            return page

    await fallback_page.bring_to_front()
    return fallback_page


def action_label(action: str) -> str:
    if action == "next":
        return "다음"
    if action == "end":
        return "학습종료 및 목차이동"
    return action


async def perform_action_target(page: Page, action: str) -> None:
    """대상 버튼을 잠깐 하이라이트한 뒤 실제로 클릭합니다.

    대상이 없으면 조용히 종료하고, 클릭 실패는 모니터 루프를 죽이지 않도록
    여기서 흡수하면서 사용자에게 성공/실패 메시지를 출력합니다.
    """
    target = action_target_locator(page, action)
    if target is None:
        return

    if await locator_count(target) == 0:
        return

    button = target.first
    label = action_label(action)

    # 어떤 버튼을 누르는지 보이도록 클릭 직전 하이라이트(실패해도 클릭은 진행).
    try:
        await button.evaluate(HIGHLIGHT_SCRIPT, timeout=3000)
    except PlaywrightError:
        pass

    try:
        await button.click(timeout=5000)
    except (PlaywrightError, PlaywrightTimeoutError):
        # 영상 위 오버레이 등으로 일반 클릭이 가로막힐 수 있어 force로 1회 재시도.
        try:
            await button.click(timeout=5000, force=True)
        except (PlaywrightError, PlaywrightTimeoutError) as exc:
            print(f"[warn] '{label}' 버튼 자동 클릭에 실패했습니다: {exc}", flush=True)
            return

    print(f"[alert] '{label}' 버튼을 자동으로 눌렀습니다.", flush=True)


async def find_next_course_button(page: Page) -> tuple[Locator, str] | None:
    """강의 목록에서 아직 끝나지 않은 첫 `수강하기` 버튼을 찾습니다."""
    for row_selector in ("tr", "li"):
        rows = page.locator(row_selector).filter(has_text=COURSE_START_TEXT)
        row_count = await locator_count(rows)
        for index in range(row_count):
            row = rows.nth(index)
            try:
                text = await row.inner_text(timeout=1000)
            except PlaywrightError:
                continue

            if not re.search(r"\d{1,2}강", text):
                continue

            progress_matches = [int(value) for value in re.findall(r"(\d{1,3})\s*%", text)]
            if progress_matches and max(progress_matches) >= 100:
                continue

            button = row.locator("a, button").filter(has_text=COURSE_START_TEXT)
            if await locator_count(button) > 0:
                return button.first, " ".join(text.split())

    fallback = page.locator("a, button").filter(has_text=COURSE_START_TEXT)
    fallback_count = await locator_count(fallback)
    if fallback_count > 0:
        # 남은 '수강하기' 개수를 key에 포함해 강의가 하나 끝날 때마다 새 key가 되도록 함
        # (고정 key면 두 번째 강의부터 중복으로 걸러져 자동 진행이 멈춤).
        return fallback.first, f"fallback-course-start:{fallback_count}"
    return None


async def click_next_course(page: Page, button: Locator, label: str, windows_notify: bool) -> bool:
    """강의 목록에서 찾은 다음 '수강하기' 버튼을 하이라이트한 뒤 클릭합니다.

    클릭 실패는 모니터 루프를 죽이지 않도록 여기서 흡수합니다. 클릭에 성공하면
    True, 실패하면 False를 반환해 호출부가 성공한 강의만 중복 처리하도록 합니다.
    """
    # 어떤 강의를 누르는지 보이도록 클릭 직전 하이라이트(실패해도 클릭은 진행).
    try:
        await button.evaluate(HIGHLIGHT_SCRIPT, timeout=3000)
    except PlaywrightError:
        pass

    message = "강의 목록으로 돌아왔습니다. 다음 남은 강의의 '수강하기' 버튼을 자동으로 누릅니다."
    clear_status_line()
    print("\a", end="", flush=True)
    print(f"[alert] {message}", flush=True)
    if windows_notify:
        send_windows_notification(message)

    try:
        await button.click(timeout=5000)
    except (PlaywrightError, PlaywrightTimeoutError):
        # 목록 행이 오버레이/애니메이션에 가려질 수 있어 force로 1회 재시도.
        try:
            await button.click(timeout=5000, force=True)
        except (PlaywrightError, PlaywrightTimeoutError) as exc:
            print(f"[warn] '수강하기' 버튼 자동 클릭에 실패했습니다: {exc}", flush=True)
            return False

    print(f"[alert] '수강하기' 버튼을 자동으로 눌렀습니다. ({label})", flush=True)
    return True


async def find_active_lecture_page(context: BrowserContext) -> Page | None:
    """살아있는 탭 중 강의 플레이어/강의목록 화면을 찾아 반환합니다.

    학습종료로 플레이어 탭이 닫히고 강의목록이 다른 탭에 있는 경우처럼,
    감시 대상이던 탭이 닫혔을 때 감시 대상을 다시 찾기 위해 사용합니다.
    """
    for page in reversed(context.pages):
        if page.is_closed():
            continue
        try:
            state = await collect_page_state(page)
        except PlaywrightError:
            continue
        if state.get("isLectureScreen") or state.get("isCourseListScreen"):
            return page
    return None


async def monitor_page(
    get_page: Callable[[], Page],
    context: BrowserContext,
    threshold: float,
    interval: float,
    windows_notify: bool,
) -> None:
    alerted: set[str] = set()
    course_list_alerted: set[str] = set()
    print("강의 진행 알림 도우미가 켜졌습니다. Ctrl+C로 종료합니다.", flush=True)

    while True:
        try:
            page = get_page()
            # 감시하던 탭이 닫혔으면(예: 학습종료로 플레이어 탭이 닫힘) 살아있는
            # 강의/목록 탭으로 감시 대상을 다시 찾는다.
            if page.is_closed():
                resolved = await find_active_lecture_page(context)
                if resolved is not None:
                    page = resolved
            state = await collect_page_state(page)
            log_state(state)
            if state.get("isCourseListScreen"):
                result = await find_next_course_button(page)
                if result is not None:
                    button, key = result
                    if key not in course_list_alerted:
                        # 클릭에 성공한 강의만 기록해, 실패한 강의가 영영 건너뛰어지지 않게 함.
                        if await click_next_course(page, button, key, windows_notify):
                            course_list_alerted.add(key)
                await asyncio.sleep(interval)
                continue

            decision = decide(state, threshold)
            if decision and decision.key not in alerted:
                alerted.add(decision.key)
                clear_status_line()
                print("\a", end="", flush=True)
                print(f"[alert] {decision.message}", flush=True)
                if windows_notify and send_windows_notification(decision.message):
                    print("[alert] Windows 알림을 보냈습니다.", flush=True)
                await perform_action_target(page, decision.action)
        except Exception as exc:
            clear_status_line()
            print(f"[warn] 페이지 상태를 읽지 못했습니다: {exc}", flush=True)

        await asyncio.sleep(interval)


async def launch_context(playwright: Playwright, args: argparse.Namespace) -> tuple[BrowserContext, Browser | None]:
    if args.cdp:
        browser = await playwright.chromium.connect_over_cdp(args.cdp)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        return context, browser

    profile_dir = Path(args.profile_dir).expanduser()
    profile_dir.mkdir(parents=True, exist_ok=True)
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        channel=args.channel,
        headless=False,
        viewport=None,
        args=[
            "--start-maximized",
            f"--window-size={args.width},{args.height}",
            "--disable-blink-features=AutomationControlled",
        ],
    )
    return context, None


async def main_async(args: argparse.Namespace) -> None:
    async with async_playwright() as playwright:
        context, browser = await launch_context(playwright, args)
        await setup_zoom(context, args.zoom)
        active_page = await choose_initial_page(context, args.url)
        await apply_zoom(active_page, args.zoom)

        def on_page(new_page: Page) -> None:
            nonlocal active_page
            active_page = new_page
            asyncio.create_task(apply_zoom(new_page, args.zoom))
            print(f"[info] 새 페이지 감지: {new_page.url}", flush=True)

        context.on("page", on_page)

        print(f"[step] 이상에듀 홈페이지를 열었습니다: {args.url}", flush=True)
        print("[step] 브라우저에서 직접 로그인해주세요.", flush=True)
        await wait_for_enter("[cmd] 로그인 완료 후 Enter를 누르면 '나의 강의실'을 눌러 이동합니다...")

        active_page = await click_my_classroom(context, active_page)

        print("[step] 내 강의실이 열렸습니다.", flush=True)
        print("[step] 브라우저에서 직접 원하는 강의를 열고 재생을 시작해주세요.", flush=True)
        await wait_for_enter("[cmd] 강의 플레이어 페이지가 열린 뒤 Enter를 누르면 감지를 시작합니다...")

        active_page = await find_lecture_player_page(context, active_page)
        print(f"[step] 감지 대상 페이지: {active_page.url} / {await safe_title(active_page)}", flush=True)

        try:
            await monitor_page(
                lambda: active_page,
                context,
                args.threshold,
                args.interval,
                not args.no_windows_notify,
            )
        finally:
            if browser:
                await browser.close()
            else:
                await context.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "이상에듀 로그인 이후 내 강의실 이동을 돕고, 강의 플레이어에서 영상 진행률과 "
            "페이지 n/n 진행률을 감지해 다음/학습종료 버튼을 자동으로 클릭합니다."
        )
    )
    parser.add_argument("--url", default=DEFAULT_START_URL, help="처음 열 URL입니다. 기본값은 이상에듀 메인입니다.")
    parser.add_argument("--threshold", type=float, default=90.0, help="알림을 띄울 영상 진행률입니다. 기본값 90.")
    parser.add_argument("--interval", type=float, default=1.0, help="감지 주기(초)입니다. 기본값 1.")
    parser.add_argument("--profile-dir", default=str(DEFAULT_PROFILE_DIR), help="Chrome 로그인 세션을 저장할 별도 프로필 폴더입니다.")
    parser.add_argument("--channel", default="chrome", help="Playwright 브라우저 채널입니다. 기본값 chrome.")
    parser.add_argument("--cdp", default="", help="기존 원격 디버깅 Chrome에 붙을 CDP 주소입니다. 예: http://127.0.0.1:9222")
    parser.add_argument("--width", type=int, default=1600, help="브라우저 창 너비 힌트입니다. 기본값 1600.")
    parser.add_argument("--height", type=int, default=900, help="브라우저 창 높이 힌트입니다. 기본값 900.")
    parser.add_argument("--zoom", type=float, default=1.0, help="페이지 내용 확대 비율입니다. 예: 1.25")
    parser.add_argument("--no-windows-notify", action="store_true", help="Windows 토스트 알림을 끕니다.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        clear_status_line()
        print("\n종료했습니다.", flush=True)


if __name__ == "__main__":
    main()
