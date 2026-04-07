# # # packaging/basira_paths.py
# # import os
# # import sys
# # from pathlib import Path


# # APP_NAME = "Basira"


# # def get_install_dir() -> Path:
# #     if getattr(sys, "frozen", False):
# #         return Path(sys.executable).resolve().parent
# #     return Path(__file__).resolve().parent


# # def get_local_appdata_dir() -> Path:
# #     base = os.environ.get("LOCALAPPDATA")
# #     if not base:
# #         base = str(Path.home() / "AppData" / "Local")
# #     path = Path(base) / APP_NAME
# #     path.mkdir(parents=True, exist_ok=True)
# #     return path


# # def get_default_user_data_dir() -> Path:
# #     return Path.home() / "Documents" / "BasiraData"


# # def get_config_path() -> Path:
# #     return get_local_appdata_dir() / "config.json"


# # def get_session_path() -> Path:
# #     return get_local_appdata_dir() / "session.json"


# # def get_state_path() -> Path:
# #     return get_local_appdata_dir() / "state.json"


# # def ensure_user_data_tree(data_dir: Path):
# #     required_dirs = [
# #         data_dir / "input_files",
# #         data_dir / "output_files",
# #         data_dir / "audit",
# #         data_dir / "reports",
# #         data_dir / "temp",
# #         data_dir / "exports",
# #     ]
# #     for folder in required_dirs:
# #         folder.mkdir(parents=True, exist_ok=True)

# # packaging/basira_paths.py
# import os
# import sys
# from pathlib import Path


# APP_NAME = "Basira"


# def get_install_dir() -> Path:
#     if getattr(sys, "frozen", False):
#         return Path(sys.executable).resolve().parent
#     return Path(__file__).resolve().parent


# def get_local_appdata_dir() -> Path:
#     base = os.environ.get("LOCALAPPDATA")
#     if not base:
#         base = str(Path.home() / "AppData" / "Local")
#     path = Path(base) / APP_NAME
#     path.mkdir(parents=True, exist_ok=True)
#     return path


# def get_default_user_data_dir() -> Path:
#     return Path.home() / "Documents" / "BasiraData"


# def get_config_path() -> Path:
#     return get_local_appdata_dir() / "config.json"


# def get_session_path() -> Path:
#     return get_local_appdata_dir() / "session.json"


# def get_state_path() -> Path:
#     return get_local_appdata_dir() / "state.json"


# def ensure_user_data_tree(data_dir: Path):
#     required_dirs = [
#         data_dir / "input_files",
#         data_dir / "output_files",
#         data_dir / "audit",
#         data_dir / "reports",
#         data_dir / "temp",
#         data_dir / "exports",
#     ]
#     for folder in required_dirs:
#         folder.mkdir(parents=True, exist_ok=True)

# packaging/basira_paths.py
"""
All path resolution for Basira.
RULE: Nothing here ever creates folders inside the source/repo tree.
"""
import os
import sys
from pathlib import Path

APP_NAME = "Basira"


def get_install_dir() -> Path:
    """Folder where launcher.py (and all .py files) live — the repo clone."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_appdata_dir() -> Path:
    """
    OS-standard location for config/session/logs. Never inside the repo.
      Windows : %LOCALAPPDATA%\\Basira
      macOS   : ~/Library/Application Support/Basira
      Linux   : ~/.basira
    """
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


def get_default_user_data_dir() -> Path:
    """Default suggestion shown to first-time user."""
    return Path.home() / "Documents" / "BasiraData"


def get_templates_dir() -> Path:
    """
    packaging/templates/ — ships with the repo.
    basira_app.html lives here and is served by Flask.
    """
    return get_install_dir() / "templates"


def ensure_user_data_tree(data_dir: Path):
    """Create all sub-folders in the user's chosen data directory."""
    for name in ["input_files", "output_files", "models",
                 "assets", "audit", "reports", "temp", "exports"]:
        (data_dir / name).mkdir(parents=True, exist_ok=True)
