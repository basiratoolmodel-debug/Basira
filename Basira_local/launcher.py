"""
launcher.py — Basira Main Launcher
===================================
يُشغَّل تلقائياً عند بدء النظام (Task Scheduler / LaunchAgent / crontab)

المنطق:
1. يتحقق هل Flask الرئيسي (5000) شغّال → إذا لا يشغّله
2. يتحقق هل Preprocessor (5050) شغّال  → إذا لا يشغّله
3. ينتظر حتى port 5000 يجاوب
4. يفتح المتصفح على http://127.0.0.1:5000

القاعدة الصارمة:
- لا أحد يشغّل Flask يدوياً
- لا أحد يفتح المتصفح غير هذا الملف
- debug=False و use_reloader=False دائماً
"""

import subprocess
import sys
import time
import webbrowser
import socket
import os
import logging

# ── Logging ──────────────────────────────────────────────────
LOG_FILE = os.path.join(os.path.dirname(__file__), "basira.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("basira_launcher")

# ── الملفات والمنافذ ──────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
MAIN_APP        = os.path.join(BASE_DIR, "Basira_app_structure.py")   # port 5000
PREPROCESSOR    = os.path.join(BASE_DIR, "basira_app.py")              # port 5050
MAIN_PORT       = 5000
PREPROCESSOR_PORT = 5050
MAIN_URL        = f"http://127.0.0.1:{MAIN_PORT}"


# ── is_port_open ──────────────────────────────────────────────
def is_port_open(port: int) -> bool:
    """هل هناك خادم يستمع على هذا المنفذ؟"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


# ── start_server ──────────────────────────────────────────────
def start_server(script_path: str, port: int, name: str):
    """يشغّل سكريبت Python في الخلفية كـ subprocess منفصل."""
    if not os.path.exists(script_path):
        log.error(f"[{name}] الملف غير موجود: {script_path}")
        return None

    log.info(f"[{name}] تشغيل على port {port}...")

    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=BASE_DIR,               # مجلد العمل = مجلد التثبيت
        close_fds=True,             # لا يرث file descriptors
    )
    log.info(f"[{name}] PID = {process.pid}")
    return process


# ── wait_for_port ─────────────────────────────────────────────
def wait_for_port(port: int, name: str, timeout: int = 30) -> bool:
    """ينتظر حتى يجاوب الخادم (polling كل 0.5 ثانية)."""
    log.info(f"[{name}] انتظار port {port}...")
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(port):
            log.info(f"[{name}] ✓ جاهز على port {port}")
            return True
        time.sleep(0.5)
    log.warning(f"[{name}] timeout — لم يستجب خلال {timeout}s")
    return False


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    log.info("=" * 50)
    log.info("Basira Launcher بدء التشغيل")
    log.info("=" * 50)

    # ── 1. التطبيق الرئيسي (5000) ──────────────────────────
    if not is_port_open(MAIN_PORT):
        start_server(MAIN_APP, MAIN_PORT, "Basira-Main")
    else:
        log.info(f"[Basira-Main] شغّال مسبقاً على port {MAIN_PORT}")

    # ── 2. Preprocessor (5050) ──────────────────────────────
    if not is_port_open(PREPROCESSOR_PORT):
        if os.path.exists(PREPROCESSOR):
            start_server(PREPROCESSOR, PREPROCESSOR_PORT, "Preprocessor")
        else:
            log.warning(f"[Preprocessor] الملف غير موجود — سيتم تخطيه")
    else:
        log.info(f"[Preprocessor] شغّال مسبقاً على port {PREPROCESSOR_PORT}")

    # ── 3. انتظر التطبيق الرئيسي ثم افتح المتصفح ────────────
    if wait_for_port(MAIN_PORT, "Basira-Main", timeout=30):
        log.info(f"فتح المتصفح → {MAIN_URL}")
        webbrowser.open(MAIN_URL)
    else:
        log.error("فشل تشغيل التطبيق الرئيسي — تحقق من basira.log")


if __name__ == "__main__":
    main()
