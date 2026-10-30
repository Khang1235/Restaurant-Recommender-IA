import logging
import socket
import threading

import webview

from app import app

WINDOW_TITLE = "Northern Vietnam - Restaurant Recommender"
WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 820
MIN_WIDTH = 900
MIN_HEIGHT = 640


def find_free_port() -> int:
    """Ask the operating system for a port that is not in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_server(port: int) -> None:
    """Run Flask quietly on a daemon thread."""
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def main() -> None:
    port = find_free_port()

    thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    thread.start()

    webview.create_window(
        WINDOW_TITLE,
        f"http://127.0.0.1:{port}/",
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(MIN_WIDTH, MIN_HEIGHT),
    )
    webview.start()


if __name__ == "__main__":
    main()
