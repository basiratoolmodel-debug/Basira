# Basira_local/basira_paths.py
"""
Path resolution for Basira.

Install structure (chosen by user during Install_Basira.bat):
  <user_chosen>\Basira_local\          ← INSTALL_DIR (this file lives here)
      launcher.py
      basira_local_bootstrap.py
      Basira_app_structure.py
      basira_paths.py
      basira_session.py
      requirements.txt
      templates\
          basira_app.html

Runtime config (AppData — never inside Basira_local):
  %LOCALAPPDATA%\Basira\
      config.json        ← setup config, chosen data_dir, session tokens
      session.json
      install_path.txt   ← path to Basira_local (set by Install_Basira.bat)
      launcher.log
"""
import os
import sys
from pathlib import Path

APP_NAME = "Basira"


def get_install_dir() -> Path:
    """
    The Basira_local folder — where all .py files and templates live.
    This is chosen by the user during installation.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_appdata_dir() -> Path:
    """
    %LOCALAPPDATA%\\Basira — for config, session, logs.
    Never inside Basira_local.
    Created automatically.
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


def get_templates_dir() -> Path:
    """Basira_local/templates/ — basira_app.html lives here."""
    return get_install_dir() / "templates"


def get_default_user_data_dir() -> Path:
    """
    Default suggestion for user's data/output files.
    This is INSIDE Basira_local so everything is in one place.
    """
    return get_install_dir() / "data"


def ensure_user_data_tree(data_dir: Path):
    """Create all sub-folders for user data inside Basira_local/data/"""
    for name in ["input_files", "output_files", "models",
                 "assets", "audit", "reports", "temp", "exports"]:
        (data_dir / name).mkdir(parents=True, exist_ok=True)
