# launcher.py  —  inside Basira_app/
"""
Basira Launcher
===============
Started by:
  - Install_Basira.bat  (first install)
  - Windows startup registry  (every login, --background mode)
  - Desktop shortcut  (manual launch)

On every launch:
  1. Reads Basira_app install path from AppData\Basira\install_path.txt
  2. Starts basira_local_bootstrap.py  ->  http://127.0.0.1:5001
  3. Starts Basira_app_structure.py    ->  http://127.0.0.1:5000
  4. Opens browser:
       - First time  -> cloud setup page (local-setup.html)
       - Returning   -> local app directly (127.0.0.1:5000)
"""

import os
import sys
import time
import json
import socket
import webbrowser
import subprocess
import urllib.request
from pathlib import Path

# ── Find Basira_app install directory ────────────────────────────────────────
# The .bat saved the install path to AppData\Local\Basira\install_path.txt
def get_install_dir() -> Path:
    """
    Returns the Basira_app folder path.
    First checks AppData for the saved path (set by installer).
    Falls back to the directory containing this script.
    """
    appdata = Path(os.environ.get("LOCALAPPDATA", "")) / "Basira"
    path_file = appdata / "install_path.txt"
    if path_file.exists():
        saved = path_file.read_text(encoding="utf-8").strip()
        if saved and Path(saved).exists():
            return Path(saved)
    # Fallback: this file is inside Basira_app/
    return Path(__file__).resolve().parent


INSTALL_DIR     = get_install_dir()
BOOTSTRAP_FILE  = INSTALL_DIR / "basira_local_bootstrap.py"
MAIN_APP_FILE   = INSTALL_DIR / "Basira_app_structure.py"
APPDATA_DIR     = Path(os.environ.get("LOCALAPPDATA", "")) / "Basira"
LOG_FILE        = APPDATA_DIR / "launcher.log"

BOOTSTRAP_PORT      = 5001
MAIN_APP_PORT       = 5000
PREPROCESSOR_PORT   = 5050
# SCRAPER_PORT is dynamic — determined at runtime by launch_webscraping.py
ANALYSIS_PORT       = 5055

# Files may live directly in INSTALL_DIR or in a templates/ subfolder.
# _find_file() checks both so the launcher works either way.
TEMPLATES_DIR = INSTALL_DIR / "templates"

def _find_file(*names) -> Path:
    for name in names:
        for d in [INSTALL_DIR, TEMPLATES_DIR]:
            p = d / name
            if p.exists():
                return p
    return INSTALL_DIR / names[0]  # fallback (will log "not found")

PREPROCESSOR_FILE     = _find_file("basira_app.py")
PREPROCESSOR_LAUNCHER = _find_file("launcher_preprocessor.py", "launch_preprocessor.py")
SCRAPER_LAUNCHER      = _find_file("launch_webscraping.py")
ANALYSIS_LAUNCHER     = _find_file("launch_analysis.py")
CLOUD_SETUP_URL = "https://basira.basira-toolmodel.workers.dev/local-setup.html"
LOCAL_APP_URL   = f"http://127.0.0.1:{MAIN_APP_PORT}"


# ── Logging ───────────────────────────────────────────────────────────────────
def log(msg: str):
    line = f"[launcher] {msg}"
    print(line, flush=True)
    try:
        APPDATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ── Windows startup registration ──────────────────────────────────────────────
def register_startup():
    if os.name != "nt":
        return
    try:
        import winreg
        python_dir = Path(sys.executable).parent
        pythonw    = python_dir / "pythonw.exe"
        exe        = str(pythonw) if pythonw.exists() else sys.executable
        cmd        = f'"{exe}" "{Path(__file__).resolve()}" --background'
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Basira", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        log("Registered in Windows startup")
    except Exception as e:
        log(f"Startup registration (non-fatal): {e}")


def is_startup_registered() -> bool:
    if os.name != "nt":
        return True
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "Basira")
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


# ── Port helpers ──────────────────────────────────────────────────────────────
def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port(port: int, timeout: int = 30) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_port_open(port):
            return True
        time.sleep(0.5)
    return False


def get_python_exe() -> str:
    """
    Returns the full path to python.exe or pythonw.exe.
    Using sys.executable guarantees we use the same Python that
    launched launcher.py — NOT VS Code or any other association.
    """
    exe = Path(sys.executable)
    # Prefer pythonw.exe (no console window) if it exists next to python.exe
    pythonw = exe.parent / "pythonw.exe"
    if pythonw.exists():
        return str(pythonw)
    return str(exe)


def service_log_file(name: str):
    log_dir = INSTALL_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return open(log_dir / f"{name}.log", "a", encoding="utf-8")


def silent_popen(cmd: list, log_name: str = "main_app") -> subprocess.Popen:
    """Launch a Python script with no console window."""
    # Always use the same Python that launched this launcher
    if cmd[0] == sys.executable or cmd[0] == "python":
        cmd[0] = get_python_exe()
    kwargs: dict = {"cwd": str(INSTALL_DIR)}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"]   = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    log_handle = service_log_file(log_name)
    kwargs["stdout"] = log_handle
    kwargs["stderr"] = log_handle
    return subprocess.Popen(cmd, **kwargs)


# ── Service starters ──────────────────────────────────────────────────────────
def start_bootstrap():
    if is_port_open(BOOTSTRAP_PORT):
        log(f"Bootstrap already running on :{BOOTSTRAP_PORT}")
        return
    if not BOOTSTRAP_FILE.exists():
        raise FileNotFoundError(f"Missing: {BOOTSTRAP_FILE}")
    log(f"Starting bootstrap  ->  :{BOOTSTRAP_PORT}")
    silent_popen([sys.executable, str(BOOTSTRAP_FILE)], "bootstrap")


def get_file_hash(path: Path) -> str:
    """Return MD5 hash of a file to detect changes."""
    import hashlib
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except Exception:
        return ""


def get_running_hash() -> str:
    """Read the hash we saved when we last started the server."""
    hash_file = APPDATA_DIR / "main_app.hash"
    try:
        return hash_file.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def save_running_hash(h: str):
    APPDATA_DIR.mkdir(parents=True, exist_ok=True)
    (APPDATA_DIR / "main_app.hash").write_text(h, encoding="utf-8")


def kill_port(port: int):
    """Kill whatever process is using this port (Windows only)."""
    if os.name != "nt":
        return
    try:
        result = subprocess.run(
            f"netstat -ano | findstr :{port}",
            shell=True, capture_output=True, text=True
        )
        for line in result.stdout.strip().splitlines():
            parts = line.strip().split()
            if parts and parts[-1].isdigit():
                pid = int(parts[-1])
                subprocess.run(f"taskkill /PID {pid} /F",
                               shell=True, capture_output=True)
                log(f"Killed old server PID {pid} on :{port}")
    except Exception as e:
        log(f"kill_port non-fatal: {e}")


def start_main_app():
    # Always start — even if another server is running on a different port
    if is_port_open(MAIN_APP_PORT):
        log(f"Main app already running on :{MAIN_APP_PORT}")
        return

    if not MAIN_APP_FILE.exists():
        raise FileNotFoundError(f"Missing: {MAIN_APP_FILE}")

    log(f"Starting main app   ->  :{MAIN_APP_PORT}")
    silent_popen([sys.executable, str(MAIN_APP_FILE)], "main_app")


def start_preprocessor():
    if is_port_open(PREPROCESSOR_PORT):
        log(f"Preprocessor already running on :{PREPROCESSOR_PORT}")
        return
    target = PREPROCESSOR_LAUNCHER if PREPROCESSOR_LAUNCHER.exists() else PREPROCESSOR_FILE
    if not target.exists():
        log(f"Preprocessor not found (skipping): {target}")
        return
    log(f"Starting preprocessor via: {target.name}  (cwd={target.parent})")
    exe = Path(sys.executable)
    pythonw = exe.parent / "pythonw.exe"
    python_exe = pythonw if pythonw.exists() else exe
    log_handle = service_log_file("preprocessor")
    kwargs = {"cwd": str(target.parent), "stdout": log_handle, "stderr": log_handle}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"]   = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    subprocess.Popen([str(python_exe), str(target), "--silent"], **kwargs)


def start_scraper():
    """
    يشغّل السكرابر عبر launch_webscraping.py.
    البورت ديناميكي — launch_webscraping.py يختاره ويكتبه في scraper.port.
    """
    if not SCRAPER_LAUNCHER.exists():
        log(f"Scraper launcher not found (skipping): {SCRAPER_LAUNCHER}")
        return
    log(f"Starting Web Scraper (dynamic port)  via {SCRAPER_LAUNCHER.name}")
    exe = Path(sys.executable)
    pythonw = exe.parent / "pythonw.exe"
    python_exe = pythonw if pythonw.exists() else exe
    log_handle = service_log_file("webscraper_launcher")
    kwargs = {"cwd": str(SCRAPER_LAUNCHER.parent), "stdout": log_handle, "stderr": log_handle}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"]   = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    subprocess.Popen([str(python_exe), str(SCRAPER_LAUNCHER), "--silent"], **kwargs)


def start_analysis():
    if is_port_open(ANALYSIS_PORT):
        log(f"Analysis Engine already running on :{ANALYSIS_PORT}")
        return
    if not ANALYSIS_LAUNCHER.exists():
        log(f"Analysis launcher not found (skipping): {ANALYSIS_LAUNCHER}")
        return
    log(f"Starting Analysis Engine  ->  :{ANALYSIS_PORT}")
    exe = Path(sys.executable)
    pythonw = exe.parent / "pythonw.exe"
    python_exe = pythonw if pythonw.exists() else exe
    log_handle = service_log_file("analysis_launcher")
    kwargs = {"cwd": str(ANALYSIS_LAUNCHER.parent), "stdout": log_handle, "stderr": log_handle}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"]   = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    subprocess.Popen([str(python_exe), str(ANALYSIS_LAUNCHER), "--silent"], **kwargs)


def init_bootstrap():
    """Call /api/setup/init — creates config.json in AppData if missing."""
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{BOOTSTRAP_PORT}/api/setup/init",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST")
        with urllib.request.urlopen(req, timeout=5) as r:
            result = json.loads(r.read())
            log(f"Bootstrap init: {result.get('message', 'ok')}")
    except Exception as e:
        log(f"Bootstrap init (non-fatal): {e}")


def get_startup_state() -> str:
    """Ask bootstrap what state the setup is in."""
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{BOOTSTRAP_PORT}/api/startup-status",
            timeout=5) as r:
            return json.loads(r.read()).get("state", "unknown")
    except Exception:
        return "unknown"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    background = "--background" in sys.argv

    log("=" * 52)
    log(f"Basira_app dir : {INSTALL_DIR}")
    log(f"Background mode: {background}")
    log("Starting...")
    log("=" * 52)

    # Register in Windows startup (once)
    if not is_startup_registered():
        register_startup()

    # Start bootstrap API (:5001)
    start_bootstrap()
    if not wait_for_port(BOOTSTRAP_PORT, timeout=25):
        raise RuntimeError(f"Bootstrap did not start on :{BOOTSTRAP_PORT}")
    log(f"Bootstrap ready  ->  http://127.0.0.1:{BOOTSTRAP_PORT}")

    # Init config
    init_bootstrap()

    # Start main Flask app (:5000)
    start_main_app()
    if not wait_for_port(MAIN_APP_PORT, timeout=30):
        raise RuntimeError(f"Main app did not start on :{MAIN_APP_PORT}")
    log(f"Main app ready   ->  http://127.0.0.1:{MAIN_APP_PORT}")

    # Start preprocessor (:5050)
    start_preprocessor()
    if wait_for_port(PREPROCESSOR_PORT, timeout=20):
        log(f"Preprocessor ready ->  http://127.0.0.1:{PREPROCESSOR_PORT}")
    else:
        log(f"WARNING: Preprocessor did not start on :{PREPROCESSOR_PORT} — check preprocessor.log")

    # Start web scraper (dynamic port, see scraper.port)
    start_scraper()
    log("Scraper starting (port assigned dynamically — see scraper.port file)")

    # Start analysis engine (:5055)
    start_analysis()
    log(f"Analysis starting  ->  http://127.0.0.1:{ANALYSIS_PORT}")

    # Open browser (skip if background startup)
    if not background:
        url = LOCAL_APP_URL
        webbrowser.open(url)
        log(f"Browser opened  ->  {url}")

    log("Basira is running.")
    log(f"  Bootstrap : http://127.0.0.1:{BOOTSTRAP_PORT}")
    log(f"  Main App      : http://127.0.0.1:{MAIN_APP_PORT}")
    log(f"  Preprocessor  : http://127.0.0.1:{PREPROCESSOR_PORT}")


if __name__ == "__main__":
    main()
