# import os
# import sys
# from pathlib import Path

# APP_NAME = "Basira"


# def get_install_dir() -> Path:
#     if getattr(sys, "frozen", False):
#         return Path(sys.executable).resolve().parent
#     return Path(__file__).resolve().parent


# def get_appdata_dir() -> Path:
#     if sys.platform == "win32":
#         base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
#         p = Path(base) / APP_NAME
#     elif sys.platform == "darwin":
#         p = Path.home() / "Library" / "Application Support" / APP_NAME
#     else:
#         p = Path.home() / f".{APP_NAME.lower()}"
#     p.mkdir(parents=True, exist_ok=True)
#     return p


# def get_config_path() -> Path:
#     return get_appdata_dir() / "config.json"


# def get_session_path() -> Path:
#     return get_appdata_dir() / "session.json"


# def get_log_path() -> Path:
#     return get_appdata_dir() / "launcher.log"


# def get_install_path_file() -> Path:
#     return get_appdata_dir() / "install_path.txt"


# def get_templates_dir() -> Path:
#     return get_install_dir() / "templates"


# def get_default_user_data_dir() -> Path:
#     return get_install_dir() / "data"


# def ensure_user_data_tree(data_dir: Path):
#     for name in [
#         "input_files",
#         "output_files",
#         "models",
#         "assets",
#         "audit",
#         "reports",
#         "temp",
#         "exports",
#     ]:
#         (data_dir / name).mkdir(parents=True, exist_ok=True)
import os
import sys
from pathlib import Path

APP_NAME = "Basira"


def get_install_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_appdata_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        p = Path(base) / APP_NAME
    elif sys.platform == "darwin":
        p = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        p = Path.home() / f".{APP_NAME.lower()}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_config_path() -> Path:
    return get_appdata_dir() / "config.json"


def get_session_path() -> Path:
    return get_appdata_dir() / "session.json"


def get_log_path() -> Path:
    return get_appdata_dir() / "launcher.log"


def get_install_path_file() -> Path:
    return get_appdata_dir() / "install_path.txt"


def get_templates_dir() -> Path:
    return get_install_dir() / "templates"


def get_default_user_data_dir() -> Path:
    return get_install_dir() / "data"


def ensure_user_data_tree(data_dir: Path):
    for name in [
        "input_files",
        "output_files",
        "models",
        "assets",
        "audit",
        "reports",
        "temp",
        "exports",
    ]:
        (data_dir / name).mkdir(parents=True, exist_ok=True)
