"""
launcher_preprocessor.py — Basira Preprocessor Launcher
=========================================================
مشغّل مستقل خاص بالـ Preprocessor فقط.

متى يُستخدم؟
- عند الضغط على زر "فتح الـ Preprocessor" من داخل بصيرة
- أو يمكن تسجيله كـ startup منفصل إذا أردت

المنطق:
1. يتحقق هل Preprocessor (5050) شغّال → إذا لا يشغّله
2. ينتظر حتى يجاوب
3. يفتح المتصفح مباشرة على http://127.0.0.1:5050

لا يمس port 5000 أبداً — مستقل تماماً.
"""

import subprocess
import sys
import time
import webbrowser
import socket
import os
import logging

# ── Logging ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "preprocessor.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("preprocessor_launcher")

# ── الإعدادات ─────────────────────────────────────────────────
PREPROCESSOR_SCRIPT = os.path.join(BASE_DIR, "basira_app.py")
PREPROCESSOR_PORT   = 5050
PREPROCESSOR_URL    = f"http://127.0.0.1:{PREPROCESSOR_PORT}"


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_preprocessor():
    if not os.path.exists(PREPROCESSOR_SCRIPT):
        log.error(f"الملف غير موجود: {PREPROCESSOR_SCRIPT}")
        print(f"❌ الملف غير موجود: {PREPROCESSOR_SCRIPT}")
        return None

    log.info(f"تشغيل Preprocessor على port {PREPROCESSOR_PORT}...")
    process = subprocess.Popen(
        [sys.executable, PREPROCESSOR_SCRIPT],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=BASE_DIR,
        close_fds=True,
    )
    log.info(f"PID = {process.pid}")
    return process


def wait_for_port(timeout: int = 30) -> bool:
    log.info(f"انتظار port {PREPROCESSOR_PORT}...")
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(PREPROCESSOR_PORT):
            log.info(f"✓ Preprocessor جاهز")
            return True
        time.sleep(0.5)
    log.warning("timeout — Preprocessor لم يستجب")
    return False


def main():
    log.info("=" * 50)
    log.info("Preprocessor Launcher بدء التشغيل")
    log.info("=" * 50)

    if is_port_open(PREPROCESSOR_PORT):
        # شغّال مسبقاً — فقط افتح المتصفح
        log.info(f"Preprocessor شغّال مسبقاً على port {PREPROCESSOR_PORT}")
        webbrowser.open(PREPROCESSOR_URL)
        return

    # شغّله وانتظر
    start_preprocessor()

    if wait_for_port(timeout=30):
        log.info(f"فتح المتصفح → {PREPROCESSOR_URL}")
        webbrowser.open(PREPROCESSOR_URL)
    else:
        log.error("فشل تشغيل Preprocessor — تحقق من preprocessor.log")
        print("❌ فشل تشغيل Preprocessor. تحقق من preprocessor.log")


if __name__ == "__main__":
    main()
