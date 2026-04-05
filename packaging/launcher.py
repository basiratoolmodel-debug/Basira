# # import os
# # import sys
# # import time
# # import socket
# # import webbrowser
# # import subprocess
# # from pathlib import Path

# # # =========================================================
# # # PATHS
# # # =========================================================

# # APP_ROOT = Path(__file__).resolve().parent

# # BACKEND_PATH = APP_ROOT / "basira_local_bootstrap.py"
# # STREAMLIT_APP_PATH = APP_ROOT / "streamlit_app.py"

# # BACKEND_PORT = 5001
# # STREAMLIT_PORT = 8501


# # # =========================================================
# # # HELPERS
# # # =========================================================

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


# # # =========================================================
# # # START SERVICES
# # # =========================================================

# # def start_backend():
# #     if is_port_open(BACKEND_PORT):
# #         return

# #     python_exe = sys.executable

# #     subprocess.Popen(
# #         [python_exe, str(BACKEND_PATH)],
# #         cwd=str(APP_ROOT),
# #         **hidden_subprocess_kwargs()
# #     )


# # def start_streamlit():
# #     if is_port_open(STREAMLIT_PORT):
# #         return

# #     python_exe = sys.executable

# #     subprocess.Popen(
# #         [
# #             python_exe,
# #             "-m",
# #             "streamlit",
# #             "run",
# #             str(STREAMLIT_APP_PATH),
# #             "--server.port",
# #             str(STREAMLIT_PORT),
# #             "--server.headless",
# #             "true",
# #             "--browser.gatherUsageStats",
# #             "false"
# #         ],
# #         cwd=str(APP_ROOT),
# #         **hidden_subprocess_kwargs()
# #     )


# # # =========================================================
# # # MAIN
# # # =========================================================

# # def main():
# #     print("Starting Basira Local...")

# #     # 1. Start backend
# #     start_backend()
# #     if not wait_for_port(BACKEND_PORT, timeout=20):
# #         raise RuntimeError("Local backend failed to start.")

# #     # 2. Start Streamlit
# #     start_streamlit()
# #     if not wait_for_port(STREAMLIT_PORT, timeout=25):
# #         raise RuntimeError("Streamlit UI failed to start.")

# #     # 3. Open browser
# #     webbrowser.open(f"http://127.0.0.1:{STREAMLIT_PORT}")

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

# BACKEND_PATH = APP_ROOT / "basira_local_bootstrap.py"
# STREAMLIT_APP_PATH = APP_ROOT / "streamlit_app.py"

# BACKEND_PORT = 5001
# STREAMLIT_PORT = 8501


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


# def start_backend():
#     if is_port_open(BACKEND_PORT):
#         return

#     subprocess.Popen(
#         [sys.executable, str(BACKEND_PATH)],
#         cwd=str(APP_ROOT),
#         **hidden_subprocess_kwargs()
#     )


# def start_streamlit():
#     if not STREAMLIT_APP_PATH.exists():
#         return

#     if is_port_open(STREAMLIT_PORT):
#         return

#     subprocess.Popen(
#         [
#             sys.executable,
#             "-m",
#             "streamlit",
#             "run",
#             str(STREAMLIT_APP_PATH),
#             "--server.port",
#             str(STREAMLIT_PORT),
#             "--server.headless",
#             "true",
#             "--browser.gatherUsageStats",
#             "false"
#         ],
#         cwd=str(APP_ROOT),
#         **hidden_subprocess_kwargs()
#     )


# def main():
#     print("Starting Basira Local...")

#     start_backend()
#     if not wait_for_port(BACKEND_PORT, timeout=20):
#         raise RuntimeError("Local bootstrap failed to start on port 5001.")

#     start_streamlit()

#     # افتحي صفحة التهيئة أولًا
#     webbrowser.open(f"http://127.0.0.1:{BACKEND_PORT}/")

#     print("Basira bootstrap started successfully.")


# if __name__ == "__main__":
#     main()

import os
import sys
import time
import socket
import webbrowser
import subprocess
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent

BACKEND_PATH = APP_ROOT / "basira_local_bootstrap.py"
STREAMLIT_APP_PATH = APP_ROOT / "streamlit_app.py"

BACKEND_PORT = 5001
STREAMLIT_PORT = 8501


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port(port: int, timeout: int = 25) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(port):
            return True
        time.sleep(0.5)
    return False


def hidden_subprocess_kwargs():
    kwargs = {}
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = startupinfo
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs


def start_backend():
    if is_port_open(BACKEND_PORT):
        return

    subprocess.Popen(
        [sys.executable, str(BACKEND_PATH)],
        cwd=str(APP_ROOT),
        **hidden_subprocess_kwargs()
    )


def start_streamlit():
    if not STREAMLIT_APP_PATH.exists():
        raise FileNotFoundError("streamlit_app.py not found in packaging folder.")

    if is_port_open(STREAMLIT_PORT):
        return

    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(STREAMLIT_APP_PATH),
            "--server.port",
            str(STREAMLIT_PORT),
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false"
        ],
        cwd=str(APP_ROOT),
        **hidden_subprocess_kwargs()
    )


def main():
    print("Starting Basira Local...")

    start_backend()
    if not wait_for_port(BACKEND_PORT, timeout=20):
        raise RuntimeError("Local bootstrap failed to start.")

    start_streamlit()
    if not wait_for_port(STREAMLIT_PORT, timeout=25):
        raise RuntimeError("Streamlit UI failed to start.")

    webbrowser.open(f"http://127.0.0.1:{STREAMLIT_PORT}")

    print("Basira Local started successfully.")


if __name__ == "__main__":
    main()