# # # # # # import os
# # # # # # import sys
# # # # # # import time
# # # # # # import socket
# # # # # # import webbrowser
# # # # # # import subprocess
# # # # # # from pathlib import Path

# # # # # # # =========================================================
# # # # # # # PATHS
# # # # # # # =========================================================

# # # # # # APP_ROOT = Path(__file__).resolve().parent

# # # # # # BACKEND_PATH = APP_ROOT / "basira_local_bootstrap.py"
# # # # # # STREAMLIT_APP_PATH = APP_ROOT / "streamlit_app.py"

# # # # # # BACKEND_PORT = 5001
# # # # # # STREAMLIT_PORT = 8501


# # # # # # # =========================================================
# # # # # # # HELPERS
# # # # # # # =========================================================

# # # # # # def is_port_open(port: int) -> bool:
# # # # # #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
# # # # # #         sock.settimeout(0.5)
# # # # # #         return sock.connect_ex(("127.0.0.1", port)) == 0


# # # # # # def wait_for_port(port: int, timeout: int = 25) -> bool:
# # # # # #     start = time.time()
# # # # # #     while time.time() - start < timeout:
# # # # # #         if is_port_open(port):
# # # # # #             return True
# # # # # #         time.sleep(0.5)
# # # # # #     return False


# # # # # # def hidden_subprocess_kwargs():
# # # # # #     kwargs = {}
# # # # # #     if os.name == "nt":
# # # # # #         startupinfo = subprocess.STARTUPINFO()
# # # # # #         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
# # # # # #         kwargs["startupinfo"] = startupinfo
# # # # # #         kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
# # # # # #     return kwargs


# # # # # # # =========================================================
# # # # # # # START SERVICES
# # # # # # # =========================================================

# # # # # # def start_backend():
# # # # # #     if is_port_open(BACKEND_PORT):
# # # # # #         return

# # # # # #     python_exe = sys.executable

# # # # # #     subprocess.Popen(
# # # # # #         [python_exe, str(BACKEND_PATH)],
# # # # # #         cwd=str(APP_ROOT),
# # # # # #         **hidden_subprocess_kwargs()
# # # # # #     )


# # # # # # def start_streamlit():
# # # # # #     if is_port_open(STREAMLIT_PORT):
# # # # # #         return

# # # # # #     python_exe = sys.executable

# # # # # #     subprocess.Popen(
# # # # # #         [
# # # # # #             python_exe,
# # # # # #             "-m",
# # # # # #             "streamlit",
# # # # # #             "run",
# # # # # #             str(STREAMLIT_APP_PATH),
# # # # # #             "--server.port",
# # # # # #             str(STREAMLIT_PORT),
# # # # # #             "--server.headless",
# # # # # #             "true",
# # # # # #             "--browser.gatherUsageStats",
# # # # # #             "false"
# # # # # #         ],
# # # # # #         cwd=str(APP_ROOT),
# # # # # #         **hidden_subprocess_kwargs()
# # # # # #     )


# # # # # # # =========================================================
# # # # # # # MAIN
# # # # # # # =========================================================

# # # # # # def main():
# # # # # #     print("Starting Basira Local...")

# # # # # #     # 1. Start backend
# # # # # #     start_backend()
# # # # # #     if not wait_for_port(BACKEND_PORT, timeout=20):
# # # # # #         raise RuntimeError("Local backend failed to start.")

# # # # # #     # 2. Start Streamlit
# # # # # #     start_streamlit()
# # # # # #     if not wait_for_port(STREAMLIT_PORT, timeout=25):
# # # # # #         raise RuntimeError("Streamlit UI failed to start.")

# # # # # #     # 3. Open browser
# # # # # #     webbrowser.open(f"http://127.0.0.1:{STREAMLIT_PORT}")

# # # # # #     print("Basira Local started successfully.")


# # # # # # if __name__ == "__main__":
# # # # # #     main()

# # # # # import os
# # # # # import sys
# # # # # import time
# # # # # import socket
# # # # # import webbrowser
# # # # # import subprocess
# # # # # from pathlib import Path

# # # # # APP_ROOT = Path(__file__).resolve().parent

# # # # # BACKEND_PATH = APP_ROOT / "basira_local_bootstrap.py"
# # # # # STREAMLIT_APP_PATH = APP_ROOT / "streamlit_app.py"

# # # # # BACKEND_PORT = 5001
# # # # # STREAMLIT_PORT = 8501


# # # # # def is_port_open(port: int) -> bool:
# # # # #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
# # # # #         sock.settimeout(0.5)
# # # # #         return sock.connect_ex(("127.0.0.1", port)) == 0


# # # # # def wait_for_port(port: int, timeout: int = 25) -> bool:
# # # # #     start = time.time()
# # # # #     while time.time() - start < timeout:
# # # # #         if is_port_open(port):
# # # # #             return True
# # # # #         time.sleep(0.5)
# # # # #     return False


# # # # # def hidden_subprocess_kwargs():
# # # # #     kwargs = {}
# # # # #     if os.name == "nt":
# # # # #         startupinfo = subprocess.STARTUPINFO()
# # # # #         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
# # # # #         kwargs["startupinfo"] = startupinfo
# # # # #         kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
# # # # #     return kwargs


# # # # # def start_backend():
# # # # #     if is_port_open(BACKEND_PORT):
# # # # #         return

# # # # #     subprocess.Popen(
# # # # #         [sys.executable, str(BACKEND_PATH)],
# # # # #         cwd=str(APP_ROOT),
# # # # #         **hidden_subprocess_kwargs()
# # # # #     )


# # # # # def start_streamlit():
# # # # #     if not STREAMLIT_APP_PATH.exists():
# # # # #         return

# # # # #     if is_port_open(STREAMLIT_PORT):
# # # # #         return

# # # # #     subprocess.Popen(
# # # # #         [
# # # # #             sys.executable,
# # # # #             "-m",
# # # # #             "streamlit",
# # # # #             "run",
# # # # #             str(STREAMLIT_APP_PATH),
# # # # #             "--server.port",
# # # # #             str(STREAMLIT_PORT),
# # # # #             "--server.headless",
# # # # #             "true",
# # # # #             "--browser.gatherUsageStats",
# # # # #             "false"
# # # # #         ],
# # # # #         cwd=str(APP_ROOT),
# # # # #         **hidden_subprocess_kwargs()
# # # # #     )


# # # # # def main():
# # # # #     print("Starting Basira Local...")

# # # # #     start_backend()
# # # # #     if not wait_for_port(BACKEND_PORT, timeout=20):
# # # # #         raise RuntimeError("Local bootstrap failed to start on port 5001.")

# # # # #     start_streamlit()

# # # # #     # افتحي صفحة التهيئة أولًا
# # # # #     webbrowser.open(f"http://127.0.0.1:{BACKEND_PORT}/")

# # # # #     print("Basira bootstrap started successfully.")


# # # # # if __name__ == "__main__":
# # # # #     main()

# # # # import os
# # # # import sys
# # # # import time
# # # # import socket
# # # # import webbrowser
# # # # import subprocess
# # # # from pathlib import Path

# # # # APP_ROOT = Path(__file__).resolve().parent

# # # # BACKEND_PATH = APP_ROOT / "basira_local_bootstrap.py"
# # # # STREAMLIT_APP_PATH = APP_ROOT / "streamlit_app.py"

# # # # BACKEND_PORT = 5001
# # # # STREAMLIT_PORT = 8501


# # # # def is_port_open(port: int) -> bool:
# # # #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
# # # #         sock.settimeout(0.5)
# # # #         return sock.connect_ex(("127.0.0.1", port)) == 0


# # # # def wait_for_port(port: int, timeout: int = 25) -> bool:
# # # #     start = time.time()
# # # #     while time.time() - start < timeout:
# # # #         if is_port_open(port):
# # # #             return True
# # # #         time.sleep(0.5)
# # # #     return False


# # # # def hidden_subprocess_kwargs():
# # # #     kwargs = {}
# # # #     if os.name == "nt":
# # # #         startupinfo = subprocess.STARTUPINFO()
# # # #         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
# # # #         kwargs["startupinfo"] = startupinfo
# # # #         kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
# # # #     return kwargs


# # # # def start_backend():
# # # #     if is_port_open(BACKEND_PORT):
# # # #         return

# # # #     subprocess.Popen(
# # # #         [sys.executable, str(BACKEND_PATH)],
# # # #         cwd=str(APP_ROOT),
# # # #         **hidden_subprocess_kwargs()
# # # #     )


# # # # def start_streamlit():
# # # #     if not STREAMLIT_APP_PATH.exists():
# # # #         raise FileNotFoundError("streamlit_app.py not found in packaging folder.")

# # # #     if is_port_open(STREAMLIT_PORT):
# # # #         return

# # # #     subprocess.Popen(
# # # #         [
# # # #             sys.executable,
# # # #             "-m",
# # # #             "streamlit",
# # # #             "run",
# # # #             str(STREAMLIT_APP_PATH),
# # # #             "--server.port",
# # # #             str(STREAMLIT_PORT),
# # # #             "--server.headless",
# # # #             "true",
# # # #             "--browser.gatherUsageStats",
# # # #             "false"
# # # #         ],
# # # #         cwd=str(APP_ROOT),
# # # #         **hidden_subprocess_kwargs()
# # # #     )


# # # # def main():
# # # #     print("Starting Basira Local...")

# # # #     start_backend()
# # # #     if not wait_for_port(BACKEND_PORT, timeout=20):
# # # #         raise RuntimeError("Local bootstrap failed to start.")

# # # #     start_streamlit()
# # # #     if not wait_for_port(STREAMLIT_PORT, timeout=25):
# # # #         raise RuntimeError("Streamlit UI failed to start.")

# # # #     webbrowser.open(f"http://127.0.0.1:{STREAMLIT_PORT}")

# # # #     print("Basira Local started successfully.")


# # # # if __name__ == "__main__":
# # # #     main()

# # # import os
# # # import sys
# # # import time
# # # import socket
# # # import webbrowser
# # # import subprocess
# # # from pathlib import Path

# # # APP_ROOT = Path(__file__).resolve().parent

# # # BACKEND_PATH = APP_ROOT / "basira_local_bootstrap.py"
# # # STREAMLIT_APP_PATH = APP_ROOT / "streamlit_app.py"

# # # BACKEND_PORT = 5001
# # # STREAMLIT_PORT = 8501


# # # def is_port_open(port: int) -> bool:
# # #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
# # #         sock.settimeout(0.5)
# # #         return sock.connect_ex(("127.0.0.1", port)) == 0


# # # def wait_for_port(port: int, timeout: int = 25) -> bool:
# # #     start = time.time()
# # #     while time.time() - start < timeout:
# # #         if is_port_open(port):
# # #             return True
# # #         time.sleep(0.5)
# # #     return False


# # # def hidden_subprocess_kwargs():
# # #     kwargs = {}
# # #     if os.name == "nt":
# # #         startupinfo = subprocess.STARTUPINFO()
# # #         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
# # #         kwargs["startupinfo"] = startupinfo
# # #         kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
# # #     return kwargs


# # # def start_backend():
# # #     if is_port_open(BACKEND_PORT):
# # #         return

# # #     subprocess.Popen(
# # #         [sys.executable, str(BACKEND_PATH)],
# # #         cwd=str(APP_ROOT),
# # #         **hidden_subprocess_kwargs()
# # #     )


# # # def start_streamlit():
# # #     if not STREAMLIT_APP_PATH.exists():
# # #         raise FileNotFoundError("streamlit_app.py not found in packaging folder.")

# # #     if is_port_open(STREAMLIT_PORT):
# # #         return

# # #     subprocess.Popen(
# # #         [
# # #             sys.executable,
# # #             "-m",
# # #             "streamlit",
# # #             "run",
# # #             str(STREAMLIT_APP_PATH),
# # #             "--server.port",
# # #             str(STREAMLIT_PORT),
# # #             "--server.headless",
# # #             "true",
# # #             "--browser.gatherUsageStats",
# # #             "false"
# # #         ],
# # #         cwd=str(APP_ROOT),
# # #         **hidden_subprocess_kwargs()
# # #     )


# # # def main():
# # #     print("Starting Basira Local...")

# # #     start_backend()
# # #     if not wait_for_port(BACKEND_PORT, timeout=20):
# # #         raise RuntimeError("Local bootstrap failed to start.")

# # #     start_streamlit()
# # #     if not wait_for_port(STREAMLIT_PORT, timeout=25):
# # #         raise RuntimeError("Streamlit UI failed to start.")

# # #     webbrowser.open(f"http://127.0.0.1:{STREAMLIT_PORT}")

# # #     print("Basira Local started successfully.")


# # # if __name__ == "__main__":
# # #     main()


# # import os
# # import sys
# # import time
# # import socket
# # import webbrowser
# # import subprocess
# # from pathlib import Path

# # APP_ROOT = Path(__file__).resolve().parent

# # BOOTSTRAP_PATH = APP_ROOT / "basira_local_bootstrap.py"
# # MAIN_WEBAPP_PATH = APP_ROOT / "Basira_app_structure.py"

# # BOOTSTRAP_PORT = 5001
# # MAIN_WEBAPP_PORT = 5000


# # def is_port_open(port: int) -> bool:
# #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
# #         sock.settimeout(0.5)
# #         return sock.connect_ex(("127.0.0.1", port)) == 0


# # def wait_for_port(port: int, timeout: int = 25) -> bool:
# #     start = time.time()
# #     while time.time() - start < timeout:
# #         if is_port_open(port):
# #             return True
# #         time.sleep(0.5)
# #     return False


# # def hidden_subprocess_kwargs():
# #     kwargs = {}
# #     if os.name == "nt":
# #         startupinfo = subprocess.STARTUPINFO()
# #         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
# #         kwargs["startupinfo"] = startupinfo
# #         kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
# #     return kwargs


# # def start_bootstrap():
# #     if is_port_open(BOOTSTRAP_PORT):
# #         return

# #     if not BOOTSTRAP_PATH.exists():
# #         raise FileNotFoundError("basira_local_bootstrap.py not found.")

# #     subprocess.Popen(
# #         [sys.executable, str(BOOTSTRAP_PATH)],
# #         cwd=str(APP_ROOT),
# #         **hidden_subprocess_kwargs()
# #     )


# # def start_main_webapp():
# #     if is_port_open(MAIN_WEBAPP_PORT):
# #         return

# #     if not MAIN_WEBAPP_PATH.exists():
# #         raise FileNotFoundError("Basira_app_structure.py not found.")

# #     subprocess.Popen(
# #         [sys.executable, str(MAIN_WEBAPP_PATH)],
# #         cwd=str(APP_ROOT),
# #         **hidden_subprocess_kwargs()
# #     )


# # def main():
# #     print("Starting Basira Local...")

# #     start_bootstrap()
# #     if not wait_for_port(BOOTSTRAP_PORT, timeout=20):
# #         raise RuntimeError("Local bootstrap failed to start on port 5001.")

# #     start_main_webapp()
# #     if not wait_for_port(MAIN_WEBAPP_PORT, timeout=25):
# #         raise RuntimeError("Main web application failed to start on port 5000.")

# #     webbrowser.open(f"http://127.0.0.1:{MAIN_WEBAPP_PORT}")

# #     print("Basira Local started successfully.")


# # if __name__ == "__main__":
# #     main()


# import os
# import sys
# import time
# import socket
# import webbrowser
# import subprocess
# from pathlib import Path

# APP_ROOT = Path(__file__).resolve().parent

# BOOTSTRAP_PATH = APP_ROOT / "basira_local_bootstrap.py"
# MAIN_WEBAPP_PATH = APP_ROOT / "Basira_app_structure.py"

# BOOTSTRAP_PORT = 5001
# MAIN_WEBAPP_PORT = 5000


# def is_port_open(port: int) -> bool:
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.settimeout(0.5)
#         return sock.connect_ex(("127.0.0.1", port)) == 0


# def wait_for_port(port: int, timeout: int = 25) -> bool:
#     start = time.time()
#     while time.time() - start < timeout:
#         if is_port_open(port):
#             return True
#         time.sleep(0.5)
#     return False


# def hidden_subprocess_kwargs():
#     kwargs = {}
#     if os.name == "nt":
#         startupinfo = subprocess.STARTUPINFO()
#         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
#         kwargs["startupinfo"] = startupinfo
#         kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
#     return kwargs


# def start_bootstrap():
#     if is_port_open(BOOTSTRAP_PORT):
#         return

#     if not BOOTSTRAP_PATH.exists():
#         raise FileNotFoundError("basira_local_bootstrap.py not found.")

#     subprocess.Popen(
#         [sys.executable, str(BOOTSTRAP_PATH)],
#         cwd=str(APP_ROOT),
#         **hidden_subprocess_kwargs()
#     )


# def start_main_webapp():
#     if is_port_open(MAIN_WEBAPP_PORT):
#         return

#     if not MAIN_WEBAPP_PATH.exists():
#         raise FileNotFoundError("Basira_app_structure.py not found.")

#     subprocess.Popen(
#         [sys.executable, str(MAIN_WEBAPP_PATH)],
#         cwd=str(APP_ROOT),
#         **hidden_subprocess_kwargs()
#     )


# def main():
#     print("Starting Basira Local...")

#     start_bootstrap()
#     if not wait_for_port(BOOTSTRAP_PORT, timeout=20):
#         raise RuntimeError("Local bootstrap failed to start on port 5001.")

#     start_main_webapp()
#     if not wait_for_port(MAIN_WEBAPP_PORT, timeout=25):
#         raise RuntimeError("Main web application failed to start on port 5000.")

#     webbrowser.open(f"http://127.0.0.1:{MAIN_WEBAPP_PORT}")

#     print("Basira Local started successfully.")


# if __name__ == "__main__":
#     main()

"""
launcher.py — Basira On-Premise Entry Point
============================================
Starts two local Flask servers then opens the browser:
  • basira_local_bootstrap.py  → http://127.0.0.1:5001  (setup / session API)
  • Basira_app_structure.py    → http://127.0.0.1:5000  (main web app)

Run:
    python launcher.py
"""

import os
import sys
import time
import socket
import webbrowser
import subprocess
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
APP_ROOT = Path(__file__).resolve().parent

BOOTSTRAP_PATH  = APP_ROOT / "basira_local_bootstrap.py"
MAIN_APP_PATH   = APP_ROOT / "Basira_app_structure.py"

BOOTSTRAP_PORT  = 5001   # setup / session / startup-status API
MAIN_APP_PORT   = 5000   # main Flask web app (serves basira_app.html)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port(port: int, timeout: int = 30) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(port):
            return True
        time.sleep(0.5)
    return False


def silent_popen(cmd: list) -> subprocess.Popen:
    """Launch a subprocess with no visible console window on Windows."""
    kwargs = {"cwd": str(APP_ROOT)}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return subprocess.Popen(cmd, **kwargs)


# ─── Service starters ─────────────────────────────────────────────────────────
def start_bootstrap():
    if is_port_open(BOOTSTRAP_PORT):
        print(f"[launcher] Bootstrap already running on :{BOOTSTRAP_PORT}")
        return

    if not BOOTSTRAP_PATH.exists():
        raise FileNotFoundError(f"Not found: {BOOTSTRAP_PATH}")

    print(f"[launcher] Starting bootstrap → :{BOOTSTRAP_PORT}")
    silent_popen([sys.executable, str(BOOTSTRAP_PATH)])


def start_main_app():
    if is_port_open(MAIN_APP_PORT):
        print(f"[launcher] Main app already running on :{MAIN_APP_PORT}")
        return

    if not MAIN_APP_PATH.exists():
        raise FileNotFoundError(f"Not found: {MAIN_APP_PATH}")

    print(f"[launcher] Starting main app → :{MAIN_APP_PORT}")
    silent_popen([sys.executable, str(MAIN_APP_PATH)])


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Basira — On-Premise Launcher")
    print("=" * 55)

    # 1. Start the bootstrap / setup API
    start_bootstrap()
    if not wait_for_port(BOOTSTRAP_PORT, timeout=25):
        raise RuntimeError(
            f"Bootstrap server did not start on port {BOOTSTRAP_PORT}. "
            "Check basira_local_bootstrap.py for errors."
        )
    print(f"[launcher] ✓ Bootstrap ready  http://127.0.0.1:{BOOTSTRAP_PORT}")

    # 2. Start the main web app
    start_main_app()
    if not wait_for_port(MAIN_APP_PORT, timeout=30):
        raise RuntimeError(
            f"Main app did not start on port {MAIN_APP_PORT}. "
            "Check Basira_app_structure.py for errors."
        )
    print(f"[launcher] ✓ Main app ready   http://127.0.0.1:{MAIN_APP_PORT}")

    # 3. Open browser to main app
    url = f"http://127.0.0.1:{MAIN_APP_PORT}"
    webbrowser.open(url)
    print(f"[launcher] Browser opened → {url}")
    print("=" * 55)


if __name__ == "__main__":
    main()
