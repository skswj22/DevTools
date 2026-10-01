# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.utils.hooks import collect_all


# 로고 없으면 기본 아이콘으로 빌드.
ICON = os.path.join(SPECPATH, "logo", "logo.png")
ICON = ICON if os.path.exists(ICON) else None


playwright_datas, playwright_binaries, playwright_hiddenimports = collect_all("playwright")


a = Analysis(
    ["lecture_progress_helper.py"],
    pathex=[],
    binaries=playwright_binaries,
    datas=playwright_datas,
    hiddenimports=playwright_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="lecture_progress_helper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON,
    version="version_info.txt",
)
