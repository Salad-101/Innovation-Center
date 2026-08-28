import os
import sys
import time
import threading
import webbrowser


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

# Tell Django where the packaged application lives.
os.environ["IC_BASE_DIR"] = BASE_DIR

# Allow Python to import Django's project packages.
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def start_server():
    from waitress import serve
    from config.wsgi import application

    os.chdir(BACKEND_DIR)

    serve(
        application,
        host="127.0.0.1",
        port=8000,
    )


def main():
    server_thread = threading.Thread(
        target=start_server,
        daemon=True,
    )

    server_thread.start()

    time.sleep(2)

    webbrowser.open("http://127.0.0.1:8000/")

    try:
        while server_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()