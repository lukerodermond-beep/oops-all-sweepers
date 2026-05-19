import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


def get_base_path():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).parent


def find_free_port(start_port=8501, max_attempts=50):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("localhost", port))

            if result != 0:
                return port

    raise RuntimeError("No free port found for the app.")


def open_browser(port):
    time.sleep(4)
    webbrowser.open(f"http://localhost:{port}")


def main():
    base_path = get_base_path()
    app_path = base_path / "app.py"

    port = find_free_port()

    os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"

    threading.Thread(
        target=open_browser,
        args=(port,),
        daemon=True
    ).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--global.developmentMode=false",
        "--server.headless=true",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]

    stcli.main()


if __name__ == "__main__":
    main()