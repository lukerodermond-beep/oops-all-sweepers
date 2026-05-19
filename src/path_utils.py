import sys
from pathlib import Path


def get_bundle_base_path():
    """
    Returns the base path where bundled app resources are stored.

    In development:
        project folder

    In PyInstaller build:
        internal bundled folder, usually _internal
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent.parent


def get_writable_base_path():
    """
    Returns the folder where user-updated data can be stored.

    In development this is the project folder.
    In the built app this is the folder containing the .exe.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


def get_data_path(filename):
    """
    Prefer updated local data next to the app if it exists.
    Otherwise fall back to bundled data.
    """
    writable_data_path = get_writable_base_path() / "data" / filename

    if writable_data_path.exists():
        return writable_data_path

    bundled_data_path = get_bundle_base_path() / "data" / filename

    return bundled_data_path


def get_writable_data_path(filename):
    data_dir = get_writable_base_path() / "data"
    data_dir.mkdir(exist_ok=True)

    return data_dir / filename