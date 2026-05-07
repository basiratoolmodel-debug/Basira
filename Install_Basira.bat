@echo off
setlocal EnableDelayedExpansion
title Basira Installer

set "APPDATA_DIR=%USERPROFILE%\AppData\Local\Basira"
set "LOG=%APPDATA_DIR%\install.log"

if not exist "%APPDATA_DIR%" mkdir "%APPDATA_DIR%"
echo [%date% %time%] Install started > "%LOG%"

cls
echo.
echo =====================================================
echo       BASIRA - Installation
echo =====================================================
echo.

:: ─── STEP 1: Check Python ────────────────────────────────────────────────────
echo [Step 1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed.
    echo Please install Python from python.org
    echo Make sure to check "Add Python to PATH"
    echo Then run this installer again.
    echo.
    start "" "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [OK] %PY_VER%
echo.

:: ─── STEP 2: Choose install location ─────────────────────────────────────────
echo [Step 2/5] Choose where to install Basira_app folder
echo.
echo   1  Documents (default)
echo   2  Desktop
echo   3  C:\ root
echo   4  Custom path
echo.
set "CHOICE=1"
set /p "CHOICE=Enter 1, 2, 3 or 4 then press Enter: "

if "!CHOICE!"=="1" set "BASE=%USERPROFILE%\Documents"
if "!CHOICE!"=="2" set "BASE=%USERPROFILE%\Desktop"
if "!CHOICE!"=="3" set "BASE=C:\"
if "!CHOICE!"=="4" (
    echo.
    set "BASE="
    set /p "BASE=Type full path (example: D:\MyWork) then press Enter: "
)
if not defined BASE set "BASE=%USERPROFILE%\Documents"

:: Remove trailing backslash unless C:\
if not "!BASE!"=="C:\" (
    if "!BASE:~-1!"=="\" set "BASE=!BASE:~0,-1!"
)

set "INSTALL_DIR=!BASE!\Basira_app"

echo.
echo [OK] Installing to: !INSTALL_DIR!
echo [%date% %time%] INSTALL_DIR=!INSTALL_DIR! >> "%LOG%"

:: Save install path
echo !INSTALL_DIR!> "%APPDATA_DIR%\install_path.txt"

:: Create folder structure
if not exist "!INSTALL_DIR!" mkdir "!INSTALL_DIR!"
if not exist "!INSTALL_DIR!\templates" mkdir "!INSTALL_DIR!\templates"
echo [OK] Folders created
echo.

:: ─── STEP 3: Download all files from GitHub ──────────────────────────────────
echo [Step 3/5] Downloading files from GitHub...
echo.

set "DL_PY=%TEMP%\basira_dl.py"

> "!DL_PY!" (
echo import os, sys, json, urllib.request, urllib.parse
echo.
echo REPO   = "basiratoolmodel-debug/Basira"
echo BRANCH = "main"
echo PREFIX = "Basira_local/"
echo INSTALL_DIR = os.environ.get("BASIRA_INSTALL_DIR", "")
echo.
echo if not INSTALL_DIR:
echo     print("[ERROR] BASIRA_INSTALL_DIR not set")
echo     sys.exit(1)
echo.
echo HEADERS = {"User-Agent": "Basira-Installer", "Accept": "application/vnd.github+json"}
echo.
echo def get_json(url):
echo     req = urllib.request.Request(url, headers=HEADERS)
echo     with urllib.request.urlopen(req, timeout=60) as r:
echo         return json.loads(r.read().decode("utf-8"))
echo.
echo def download(url, dest):
echo     req = urllib.request.Request(url, headers={"User-Agent": "Basira-Installer"})
echo     with urllib.request.urlopen(req, timeout=120) as r:
echo         data = r.read()
echo     os.makedirs(os.path.dirname(dest), exist_ok=True)
echo     with open(dest, "wb") as f:
echo         f.write(data)
echo.
echo api = f"https://api.github.com/repos/{REPO}/git/trees/{BRANCH}?recursive=1"
echo print("Reading file list from GitHub...")
echo try:
echo     tree = get_json(api)
echo except Exception as e:
echo     print(f"[ERROR] Cannot read GitHub: {e}")
echo     sys.exit(1)
echo.
echo files = []
echo for item in tree.get("tree", []):
echo     path = item.get("path", "")
echo     if item.get("type") == "blob" and path.startswith(PREFIX):
echo         rel = path[len(PREFIX):]
echo         if rel:
echo             files.append((path, rel))
echo.
echo if not files:
echo     print("[ERROR] No files found in Basira_local on GitHub")
echo     sys.exit(1)
echo.
echo print(f"Found {len(files)} files. Downloading...")
echo failed = []
echo for i, (path, rel) in enumerate(files, 1):
echo     raw = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{urllib.parse.quote(path, safe='/')}"
echo     dest = os.path.join(INSTALL_DIR, rel.replace("/", os.sep))
echo     print(f"  [{i}/{len(files)}] {rel}")
echo     try:
echo         download(raw, dest)
echo     except Exception as e:
echo         failed.append((rel, str(e)))
echo         print(f"    FAILED: {e}")
echo.
echo if failed:
echo     print("[ERROR] Some files failed:")
echo     for r, e in failed:
echo         print(f"  - {r}: {e}")
echo     sys.exit(1)
echo.
echo print("[OK] All files downloaded successfully")
)

set "BASIRA_INSTALL_DIR=!INSTALL_DIR!"
python "!DL_PY!"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Download failed. Check the messages above.
    echo Log: %LOG%
    del "!DL_PY!" 2>nul
    pause
    exit /b 1
)
del "!DL_PY!" 2>nul
echo.
echo [OK] All files downloaded
echo.

:: ─── STEP 4: Install Python packages ─────────────────────────────────────────
echo [Step 4/5] Installing Python packages...
echo (This may take 2-3 minutes)
echo.
cd /d "!INSTALL_DIR!"
python -m pip install --upgrade pip -q >> "%LOG%" 2>&1
python -m pip install -r requirements.txt >> "%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have failed. Check: %LOG%
) else (
    echo [OK] Packages installed
)
echo.

:: ─── STEP 5: Register in Windows startup ─────────────────────────────────────
echo [Step 5/5] Registering Basira to start with Windows...

for /f "usebackq tokens=*" %%p in (`python -c "import sys; print(sys.executable)"`) do set "PYTHON_EXE=%%p"
set "PYTHONW_EXE=!PYTHON_EXE:python.exe=pythonw.exe!"
if exist "!PYTHONW_EXE!" (
    set "PYW=!PYTHONW_EXE!"
) else (
    set "PYW=!PYTHON_EXE!"
)

echo !PYTHON_EXE!> "%APPDATA_DIR%\python_path.txt"

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Basira" /t REG_SZ /d "\"!PYW!\" \"!INSTALL_DIR!\launcher.py\" --background" /f >> "%LOG%" 2>&1
echo [OK] Basira will start automatically on Windows login
echo.

:: ─── DONE ─────────────────────────────────────────────────────────────────────
echo =====================================================
echo   Installation complete!
echo   Location: !INSTALL_DIR!
echo =====================================================
echo.
echo [%date% %time%] Installation complete >> "%LOG%"

:: Launch Basira
start "" "!PYW!" "!INSTALL_DIR!\launcher.py"

timeout /t 12 /nobreak >nul
start "" "https://basira.basira-toolmodel.workers.dev/local-setup.html"

echo Basira is now running.
echo You can close this window.
echo.
timeout /t 5 /nobreak >nul
exit /b 0
