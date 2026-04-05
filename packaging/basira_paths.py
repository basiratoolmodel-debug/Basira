# packaging/basira_paths.py
import os
import sys
from pathlib import Path


APP_NAME = "Basira"


def get_install_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_local_appdata_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        base = str(Path.home() / "AppData" / "Local")
    path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_default_user_data_dir() -> Path:
    return Path.home() / "Documents" / "BasiraData"


def get_config_path() -> Path:
    return get_local_appdata_dir() / "config.json"


def get_session_path() -> Path:
    return get_local_appdata_dir() / "session.json"


def get_state_path() -> Path:
    return get_local_appdata_dir() / "state.json"


def ensure_user_data_tree(data_dir: Path):
    required_dirs = [
        data_dir / "input_files",
        data_dir / "output_files",
        data_dir / "audit",
        data_dir / "reports",
        data_dir / "temp",
        data_dir / "exports",
    ]
    for folder in required_dirs:
        folder.mkdir(parents=True, exist_ok=True)