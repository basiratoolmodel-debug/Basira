"""
launch_analysis.py — Basira Analysis Engine Launcher
======================================================
يُشغَّل تلقائياً من launcher.py عند بدء التطبيق.
لا يحتاج تشغيل يدوي من المستخدم.

الملفات المطلوبة في نفس المجلد (templates/):
  - basira_bridge_orchestrator.py  ← السيرفر الرئيسي
  - insight_engine_F.py
  - rca_engine_F.py
  - supervised_engine_F.py
  - unsupervised_engine_F.py
  - charts_engine.py
  - basira_analysis_engine.html
  - chart_management.html

FIX v1.1:
  - cwd الآن = مجلد templates/ حيث توجد كل engines
    (كان Basira_app/ فكانت الـ imports تفشل)
"""

import os
import sys
import time
import socket
import subprocess
from pathlib import Path

# ─── الإعدادات ────────────────────────────────────────────────────────────────
ANALYSIS_PORT = 5055
BASE_DIR      = Path(__file__).resolve().parent

def _resolve_templates_dir() -> Path:
    candidates = [BASE_DIR / "templates", BASE_DIR, BASE_DIR.parent / "templates"]
    for candidate in candidates:
        if (candidate / "basira_bridge_orchestrator.py").exists():
            return candidate
    return BASE_DIR / "templates"

TEMPLATES_DIR = _resolve_templates_dir()   # ← cwd الصحيح للـ engines
SERVER_FILE   = TEMPLATES_DIR / "basira_bridge_orchestrator.py"
LOG_DIR       = (BASE_DIR if BASE_DIR.name != "templates" else BASE_DIR.parent) / "logs"
# ─────────────────────────────────────────────────────────────────────────────


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


def start_server():
    if is_port_open(ANALYSIS_PORT):
        print(f"[analysis] Already running on :{ANALYSIS_PORT}")
        return

    if not SERVER_FILE.exists():
        print(f"[analysis] ERROR: {SERVER_FILE} not found")
        sys.exit(1)

    print(f"[analysis] Starting Analysis Engine on port {ANALYSIS_PORT}...")

    exe = Path(sys.executable)
    pythonw = exe.parent / "pythonw.exe"
    python_exe = pythonw if pythonw.exists() else exe

    # FIX: cwd = templates/ حتى تشتغل imports بشكل صحيح
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_handle = open(LOG_DIR / "analysis_engine.log", "a", encoding="utf-8")
    kwargs = {"cwd": str(TEMPLATES_DIR), "stdout": log_handle, "stderr": log_handle}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"]   = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    subprocess.Popen([str(python_exe), str(SERVER_FILE)], **kwargs)


def main():
    silent = "--silent" in sys.argv

    if not silent:
        print("=" * 50)
        print("  Basira Analysis Engine Launcher")
        print(f"  Port: {ANALYSIS_PORT}")
        print(f"  Server: {SERVER_FILE}")
        print(f"  CWD:    {TEMPLATES_DIR}")
        print("=" * 50)

    start_server()

    if silent:
        wait_for_port(ANALYSIS_PORT, timeout=30)
        return

    print(f"[analysis] Waiting for server on :{ANALYSIS_PORT}...")
    if wait_for_port(ANALYSIS_PORT, timeout=30):
        print(f"[analysis] Ready → http://127.0.0.1:{ANALYSIS_PORT}")
    else:
        print("[analysis] Timeout — server did not start in 30s")
        print(f"[analysis] Check that all engines exist in: {TEMPLATES_DIR}")


if __name__ == "__main__":
    main()
