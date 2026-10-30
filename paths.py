import os
import sys

APP_FOLDER_NAME = "RestaurantRecommender"


def is_packaged() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def resource_path(relative_path: str) -> str:
    if is_packaged():
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base, relative_path)


def writable_dir() -> str:
    if not is_packaged():
        target = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data"
        )
    elif sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        target = os.path.join(base, APP_FOLDER_NAME)
    elif sys.platform == "darwin":
        target = os.path.join(
            os.path.expanduser("~"),
            "Library", "Application Support", APP_FOLDER_NAME
        )
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(
            os.path.expanduser("~"), ".local", "share")
        target = os.path.join(base, APP_FOLDER_NAME)

    os.makedirs(target, exist_ok=True)
    return target


def database_path() -> str:
    """Absolute path to the SQLite database file."""
    return os.path.join(writable_dir(), "restaurants.db")
