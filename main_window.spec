# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.building.api import PYZ, EXE
from PyInstaller.building.build_main import Analysis

a = Analysis(
    ['main_window.py'],
    pathex=[],
    binaries=[],
    datas=[('utils/formulas/res/formulas_lab1.png', 'utils/formulas/res'),
        ('utils/formulas/res/formulas_lab2.png', 'utils/formulas/res'),
        ('utils/formulas/res/formulas_lab4.png', 'utils/formulas/res'),
        ('utils/formulas/res/formulas_lab8.png', 'utils/formulas/res'),
        ('utils/formulas/res/formulas_lab9.png', 'utils/formulas/res'),],
    hiddenimports=[],
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
    name='main_window',
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
)
