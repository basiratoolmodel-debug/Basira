# Basira_local/launcher.py
"""
Basira Launcher — runs automatically on Windows startup.
Located inside: <user_chosen_folder>/Basira_local/launcher.py

Never run manually by the customer.
Started by: Install_Basira.bat (first time) and Windows startup (every login).
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

import basira_paths as paths

BOOTSTRAP_PORT  = 5001
MAIN_APP_PORT   = 5000

APP_ROOT        = paths.get_install_dir()    # Basira_local/
BOOTSTRAP_FILE  = APP_ROOT / "basira_local_bootstrap.py"
MAIN_APP_FILE   = APP_ROOT / "Basira_app_structure.py"
LOG_FILE        = paths.get_log_path()

CLOUD_SETUP_URL = "https://basira.basira-toolmodel.workers.dev/local-setup.html"
LOCAL_APP_URL   = f"http://127.0.0.1:{MAIN_APP_PORT}"


def log(msg):
    line = f"[launcher] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def register_startup():
    if os.name != "nt":
        return
    try:
        import winreg
        python_dir = Path(sys.executable).parent
        pythonw    = python_dir / "pythonw.exe"
        exe        = str(pythonw) if pythonw.exists() else sys.executable
        cmd        = f'"{exe}" "{Path(__file__).resolve()}" --background'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Basira", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        log("Registered in Windows startup")
    except Exception as e:
        log(f"Startup registration (non-fatal): {e}")


def is_startup_registered():
    if os.name != "nt":
        return True
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "Basira")
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port(port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_port_open(port):
            return True
        time.sleep(0.5)
    return False


def silent_popen(cmd):
    kwargs = {"cwd": str(APP_ROOT)}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"]   = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return subprocess.Popen(cmd, **kwargs)


def start_bootstrap():
    if is_port_open(BOOTSTRAP_PORT):
        log(f"Bootstrap already on :{BOOTSTRAP_PORT}")
        return
    if not BOOTSTRAP_FILE.exists():
        raise FileNotFoundError(f"Missing: {BOOTSTRAP_FILE}")
    log(f"Starting bootstrap → :{BOOTSTRAP_PORT}")
    silent_popen([sys.executable, str(BOOTSTRAP_FILE)])


def start_main_app():
    if is_port_open(MAIN_APP_PORT):
        log(f"Main app already on :{MAIN_APP_PORT}")
        return
    if not MAIN_APP_FILE.exists():
        raise FileNotFoundError(f"Missing: {MAIN_APP_FILE}")
    log(f"Starting main app  → :{MAIN_APP_PORT}")
    silent_popen([sys.executable, str(MAIN_APP_FILE)])


def init_bootstrap():
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{BOOTSTRAP_PORT}/api/setup/init",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=5) as r:
            result = json.loads(r.read())
            log(f"Bootstrap init: {result.get('message','ok')}")
    except Exception as e:
        log(f"Bootstrap init (non-fatal): {e}")


def get_startup_state():
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{BOOTSTRAP_PORT}/api/startup-status", timeout=5) as r:
            return json.loads(r.read()).get("state", "unknown")
    except Exception:
        return "unknown"


def main():
    background = "--background" in sys.argv

    log("=" * 50)
    log(f"Basira_local dir: {APP_ROOT}")
    log("Starting...")
    log("=" * 50)

    # Register Windows startup (once)
    if not is_startup_registered():
        register_startup()

    # Start bootstrap API
    start_bootstrap()
    if not wait_for_port(BOOTSTRAP_PORT, timeout=25):
        raise RuntimeError(f"Bootstrap failed to start on :{BOOTSTRAP_PORT}")
    log(f"Bootstrap ready → http://127.0.0.1:{BOOTSTRAP_PORT}")

    # Init config in AppData
    init_bootstrap()

    # Start main app
    start_main_app()
    if not wait_for_port(MAIN_APP_PORT, timeout=30):
        raise RuntimeError(f"Main app failed to start on :{MAIN_APP_PORT}")
    log(f"Main app ready  → http://127.0.0.1:{MAIN_APP_PORT}")

    # Open browser
    if not background:
        state = get_startup_state()
        log(f"State: {state}")
        url = LOCAL_APP_URL if state in ("healthy", "healthy_with_optional_update") \
              else CLOUD_SETUP_URL
        webbrowser.open(url)
        log(f"Browser → {url}")

    log("Basira is running.")


if __name__ == "__main__":
    main()
