"""
Single entry point for the Innovation Center app.

- In development you can still run the backend and frontend separately
  (`manage.py runserver` + `npm run dev`) exactly as before.
- This script instead runs the *built* frontend and the Django backend
  together, on one port, so the whole project starts from one command:

      python main.py

- This is also the script PyInstaller freezes into InnovationCenter.exe
  (see the packaging guide) so double-clicking the exe does the same thing.

Before running this for the first time, build the frontend once:
    cd frontend && npm install && npm run build
"""

import os
import sys
import socket
import threading
import webbrowser
from pathlib import Path

HOST = "127.0.0.1"
PREFERRED_PORT = 8000


def project_root() -> Path:
    """Root folder containing backend/ and frontend/, whether running from
    source or from a PyInstaller-frozen exe."""
    if getattr(sys, "frozen", False):
        # PyInstaller onedir/onefile: bundled data files live next to the
        # executable under _MEIPASS (onefile) or the exe's own folder (onedir).
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent


def user_data_dir() -> Path:
    """Per-user, writable folder for db.sqlite3 and collected static files.
    Used only when frozen, since the install folder itself (e.g. under
    Program Files) usually isn't writable by a normal user."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    data_dir = base / "InnovationCenter"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def find_open_port(host: str, preferred: int) -> int:
    """Use `preferred` if free, otherwise let the OS pick an open port."""
    for port in (preferred, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return sock.getsockname()[1]
    raise RuntimeError("Could not find an open port")


def main() -> None:
    root = project_root()
    backend_dir = root / "backend"
    sys.path.insert(0, str(backend_dir))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    if getattr(sys, "frozen", False):
        os.environ["ICENTER_DATA_DIR"] = str(user_data_dir())
        os.environ.setdefault("ICENTER_DEBUG", "0")

    import django
    django.setup()

    from django.core.management import call_command

    print("Applying database migrations...")
    call_command("migrate", interactive=False, verbosity=0)

    print("Collecting static files...")
    call_command("collectstatic", interactive=False, verbosity=0)

    from config.wsgi import application
    from waitress import serve

    port = find_open_port(HOST, PREFERRED_PORT)
    url = f"http://{HOST}:{port}/"

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    print(f"Innovation Center is running at {url}")
    print("Close this window (or press Ctrl+C) to stop the server.")
    serve(application, host=HOST, port=port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as exc:  # noqa: BLE001
        # If this is a frozen .exe launched by double-click, the console
        # window would otherwise vanish before the user can read the error.
        print(f"\nInnovation Center failed to start: {exc}")
        if getattr(sys, "frozen", False):
            input("Press Enter to exit...")
        raise
