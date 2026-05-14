"""
launch_webscraping.py — Basira Web Scraping Launcher (Dynamic Port)
====================================================================
- يبحث عن أول بورت فاضي في النطاق 8700-8799
- يمرره للسكرابر عبر BASIRA_PORT
- يكتب البورت في ملف مؤقت scraper.port حتى يقرأه الـ preprocessor
- لا يُشغَّل إذا كان السكرابر شغّالاً مسبقاً (يرجع البورت الحالي)
- الـ preprocessor يُغلق السكرابر عند انتهاء الجلسة
"""

import os
import sys
import time
import socket
import subprocess
from pathlib import Path

BASE_DIR      = Path(__file__).resolve().parent

def _resolve_scraper_dir() -> Path:
    candidates = [
        BASE_DIR / "templates" / "WebScraping",
        BASE_DIR / "WebScraping",
        BASE_DIR.parent / "templates" / "WebScraping",
        BASE_DIR.parent / "WebScraping",
    ]
    for candidate in candidates:
        if (candidate / "run.py").exists() or (candidate / "app.py").exists():
            return candidate
    return candidates[0]

SCRAPER_DIR   = _resolve_scraper_dir()
SCRAPER_ENTRY = SCRAPER_DIR / "run.py"
SCRAPER_APP   = SCRAPER_DIR / "app.py"
PORT_FILE     = (BASE_DIR if BASE_DIR.name != "templates" else BASE_DIR.parent) / "scraper.port"   # ملف مؤقت يحمل البورت الحالي
PORT_RANGE    = range(8700, 8800)
LOG_DIR       = (BASE_DIR if BASE_DIR.name != "templates" else BASE_DIR.parent) / "logs"


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


def find_free_port() -> int:
    """يرجع أول بورت فاضي في النطاق 8700-8799."""
    for port in PORT_RANGE:
        if not is_port_open(port):
            return port
    raise RuntimeError("No free port found in range 8700-8799")


def read_port_file() -> int | None:
    """يقرأ البورت من الملف المؤقت إذا كان السكرابر شغّالاً."""
    try:
        p = int(PORT_FILE.read_text(encoding="utf-8").strip())
        if is_port_open(p):
            return p
    except Exception:
        pass
    # حذف الملف إذا كان البورت غير نشط
    PORT_FILE.unlink(missing_ok=True)
    return None


def wait_for_port(port: int, timeout: int = 20) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_port_open(port):
            return True
        time.sleep(0.4)
    return False


def start_scraper() -> int:
    """
    يشغّل السكرابر ويرجع البورت المستخدم.
    إذا كان شغّالاً مسبقاً يرجع البورت الحالي مباشرة.
    """
    # تحقق من الملف المؤقت أولاً
    existing = read_port_file()
    if existing:
        print(f"[scraper] Already running on :{existing}")
        return existing

    port  = find_free_port()
    entry = SCRAPER_ENTRY if SCRAPER_ENTRY.exists() else SCRAPER_APP
    if not entry.exists():
        raise FileNotFoundError(
            f"WebScraping files not found.\n"
            f"Expected: {SCRAPER_DIR}/run.py"
        )

    print(f"[scraper] Starting on free port :{port}  ({entry.name})")

    exe        = Path(sys.executable)
    pythonw    = exe.parent / "pythonw.exe"
    python_exe = pythonw if pythonw.exists() else exe

    env                    = os.environ.copy()
    env["BASIRA_PORT"]     = str(port)
    env["BASIRA_NO_BROWSER"] = "1"

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_handle = open(LOG_DIR / "webscraper.log", "a", encoding="utf-8")
    kwargs: dict = {"cwd": str(SCRAPER_DIR), "env": env, "stdout": log_handle, "stderr": log_handle}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"]   = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    subprocess.Popen([str(python_exe), str(entry)], **kwargs)

    if wait_for_port(port, timeout=20):
        # احفظ البورت في الملف المؤقت
        PORT_FILE.write_text(str(port), encoding="utf-8")
        print(f"[scraper] Ready → http://127.0.0.1:{port}")
        return port
    else:
        raise RuntimeError(f"Scraper did not respond on port {port} within 20s")


def stop_scraper():
    """يُغلق السكرابر ويحذف الملف المؤقت (يُستدعى من الـ preprocessor)."""
    port = read_port_file()
    if not port:
        return
    if os.name == "nt":
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
                    print(f"[scraper] Stopped PID {pid} on :{port}")
        except Exception as e:
            print(f"[scraper] Stop error: {e}")
    else:
        # Linux/Mac
        try:
            import signal as _sig
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], capture_output=True, text=True
            )
            for pid in result.stdout.strip().split():
                os.kill(int(pid), _sig.SIGTERM)
                print(f"[scraper] Stopped PID {pid} on :{port}")
        except Exception as e:
            print(f"[scraper] Stop error: {e}")
    PORT_FILE.unlink(missing_ok=True)


def main():
    silent = "--silent" in sys.argv

    if not silent:
        print("=" * 50)
        print("  Basira Web Scraping Launcher")
        print(f"  Search range : 8700–8799")
        print(f"  Dir          : {SCRAPER_DIR}")
        print("=" * 50)

    try:
        port = start_scraper()
        if not silent:
            print(f"[scraper] URL → http://127.0.0.1:{port}")
    except Exception as e:
        print(f"[scraper] ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
