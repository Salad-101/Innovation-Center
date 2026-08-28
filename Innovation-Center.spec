from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


ROOT = Path(SPEC).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND_DIST = ROOT / "frontend" / "dist"


hiddenimports = [
    # Django project
    "config",
    "config.settings",
    "config.urls",
    "config.wsgi",
    "config.asgi",

    # Django application
    "ideas",
    "ideas.admin",
    "ideas.apps",
    "ideas.models",
    "ideas.serializers",
    "ideas.urls",
    "ideas.views",

    # Django dependencies loaded dynamically
    "corsheaders",
    "corsheaders.middleware",
    "corsheaders.apps",

    "rest_framework",
    "rest_framework.apps",
    "rest_framework.views",
    "rest_framework.serializers",

    "whitenoise",
    "whitenoise.middleware",

    "waitress",
]

hiddenimports += collect_submodules("config")
hiddenimports += collect_submodules("ideas")


a = Analysis(
    [str(ROOT / "main.py")],

    # This is the important part:
    # backend becomes a Python import location.
    pathex=[str(BACKEND)],

    binaries=[],

    datas=[
        (str(FRONTEND_DIST), "frontend/dist"),
        (str(BACKEND / "db.sqlite3"), "backend"),
    ],

    hiddenimports=hiddenimports,

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(a.pure)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Innovation-Center",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)