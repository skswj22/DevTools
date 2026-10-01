"""단일 exe 빌드. 사용법: python build_release.py [--skip-install]"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RELEASE_ONEFILE = ROOT / "release" / "lecture_progress_helper.exe"


def run(command: list[str]) -> None:
    print(f"[run] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a standalone exe.")
    parser.add_argument("--skip-install", action="store_true", help="Skip pip install steps.")
    args = parser.parse_args()

    if not args.skip_install:
        run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-r", "requirements-build.txt"])

    run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", "lecture_progress_helper_onefile.spec"])
    source = ROOT / "dist" / "lecture_progress_helper.exe"
    if not source.exists():
        raise RuntimeError(f"PyInstaller output not found: {source}")

    RELEASE_ONEFILE.parent.mkdir(exist_ok=True)
    shutil.copy2(source, RELEASE_ONEFILE)
    for path in (ROOT / "build", ROOT / "dist"):
        shutil.rmtree(path, ignore_errors=True)

    print(f"\n단일 exe 생성 완료: {RELEASE_ONEFILE}")
    print("실행 PC에는 Google Chrome 설치 필요.")


if __name__ == "__main__":
    main()
