# -*- mode: python ; coding: utf-8 -*-
r"""
PyInstaller spec for Innovation Center.

BEFORE BUILDING:
  1. cd frontend && npm install && npm run build      (creates frontend/dist)
  2. Delete backend/db.sqlite3, backend/staticfiles/, and any __pycache__
     folders so a dev database doesn't get baked into the installer.
  3. Make sure this venv has: pyinstaller, django, djangorestframework,
     django-cors-headers, whitenoise, waitress, pillow  (uv sync covers
     everything except pyinstaller itself: `uv pip install pyinstaller`)

BUILD (from the project root):
    pyinstaller packaging/main.spec --noconfirm --clean

Output: dist/InnovationCenter/  (an ONEDIR build - more reliable to freeze
than --onefile for a Django app, and starts noticeably faster). This whole
folder is what Inno Setup will install.

WHY 'config' and 'ideas' ARE EXCLUDED, ON PURPOSE:
Django loads INSTALLED_APPS and discovers migrations dynamically at
runtime (by name, and by listing a directory) rather than through normal
`import` statements. PyInstaller's static analysis can't see those and
frequently mis-packages this into the frozen archive in a way that breaks
migrations. So instead of asking PyInstaller to freeze our own project
code, we explicitly exclude it and copy backend/ and frontend/dist as
plain files (see `datas` below) - main.py already puts backend/ on
sys.path at startup, so Django imports it exactly like it would from
source. Only third-party libraries get frozen into the archive.
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_all

# Spec files are exec()'d by PyInstaller, not run as a normal module, so
# there is no __file__ here - PyInstaller injects SPECPATH instead (the
# directory containing this .spec file).
PROJECT_ROOT = Path(SPECPATH).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

datas = [
    (str(BACKEND_DIR), "backend"),
    (str(FRONTEND_DIST), "frontend/dist"),
]
binaries = []
hiddenimports = []

# These ARE frozen normally, since they're real third-party packages Django
# loads dynamically (admin, DRF, cors headers) or that we import directly
# (whitenoise, waitress, Pillow).
for pkg in ("django", "rest_framework", "corsheaders", "whitenoise", "waitress", "PIL"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["config", "ideas"],  # see note above - shipped as plain files instead
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="InnovationCenter",
    console=True,  # keep the console window - if startup fails, the error is visible
    icon=None,     # point this at a .ico file if you have one, e.g. "icon.ico"
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="InnovationCenter",
)
