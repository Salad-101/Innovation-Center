# Packaging Innovation Center as a Windows installer

This has to be done **on a Windows machine** — PyInstaller builds a native
exe for whatever OS it runs on, and Inno Setup itself is Windows-only.

## 1. One-time setup

```powershell
cd Innovation-Center
uv sync                          # installs everything in pyproject.toml, incl. pyinstaller
cd frontend
npm install
```

Install Inno Setup separately: https://jrsoftware.org/isinfo.php

## 2. Every time you build a new release

```powershell
# From the project root:

# a) Build the frontend
cd frontend
npm run build
cd ..

# b) Make sure no dev database/cache gets baked into the installer
Remove-Item backend\db.sqlite3 -ErrorAction SilentlyContinue
Remove-Item backend\staticfiles -Recurse -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force

# c) Freeze the app with PyInstaller
uv run pyinstaller packaging\main.spec --noconfirm --clean
# -> creates dist\InnovationCenter\InnovationCenter.exe

# d) Sanity-check the frozen app before packaging it further
.\dist\InnovationCenter\InnovationCenter.exe
# It should print a URL and open your browser. Ctrl+C to stop.

# e) Build the installer
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\installer.iss
# -> creates packaging\Output\InnovationCenter-Setup.exe
```

`InnovationCenter-Setup.exe` is the file you hand out. It installs to the
user's local AppData by default (no admin rights needed), adds Start Menu
/ desktop shortcuts, and the app stores its database under
`%LOCALAPPDATA%\InnovationCenter\db.sqlite3` — separate from the install
folder, so re-installing or upgrading never wipes user data.

## If PyInstaller build fails with `ModuleNotFoundError`

This is the most common snag when freezing Django apps: some package Django
loads dynamically (via `INSTALLED_APPS` or a plugin system) wasn't picked up
by static analysis. Add it to the `collect_all(...)` loop near the top of
`main.spec`, alongside `"django", "rest_framework", "corsheaders"`, then
rebuild. Do **not** add `ideas` or `config` to that loop — they're
intentionally excluded and shipped as plain files instead (see the comment
at the top of `main.spec` for why).

## If the frozen app starts but the browser tab is blank / shows a 404

Almost always means `frontend/dist` wasn't built (or was empty) before you
ran PyInstaller — step (a) above must happen before step (c).
