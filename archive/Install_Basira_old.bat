@echo off
setlocal EnableDelayedExpansion
title Basira Installer
chcp 65001 >nul 2>&1

:: ============================================================
:: Basira Installer
:: - English only
:: - Folder always named "Basira_app"
:: - User picks WHERE to put it (saved for future launches)
:: - Shows pip progress
:: - Launches everything automatically after install
:: ============================================================

set "RAW=https://raw.githubusercontent.com/basiratoolmodel-debug/Basira/main/Basira_local"
set "APPDATA_DIR=%USERPROFILE%\AppData\Local\Basira"
set "LOG=%APPDATA_DIR%\install.log"
set "INSTALL_PATH_FILE=%APPDATA_DIR%\install_path.txt"

:: Create AppData\Basira folder
if not exist "%APPDATA_DIR%" mkdir "%APPDATA_DIR%"
echo ===== [%date% %time%] Installation started ===== > "%LOG%"

cls
echo.
echo  =====================================================
echo          BASIRA  -  Installation
echo  =====================================================
echo.
echo  Basira will be installed in a folder called Basira_app
echo  You choose WHERE to put that folder.
echo.
echo  After installation:
echo    - Basira starts automatically on every Windows login
echo    - A shortcut is created on your Desktop
echo    - Your browser opens automatically
echo.
echo  =====================================================
echo.

:: ── STEP 1: Check Python ────────────────────────────────────
echo  [Step 1/6]  Checking Python...
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed on this computer.
    echo.
    echo  Please:
    echo    1. Click OK on the Python download page that will open
    echo    2. Install Python - make sure to CHECK "Add Python to PATH"
    echo    3. Run this installer again
    echo.
    start "" "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo  [OK]  Found: %PY_VER%
echo.

:: ── STEP 2: Choose install location ─────────────────────────
echo  [Step 2/6]  Choose where to install Basira_app folder
echo.
echo  The folder "Basira_app" will be created in your chosen location.
echo  Example: if you choose Documents, it creates:
echo           C:\Users\%USERNAME%\Documents\Basira_app
echo.
echo  Choose a location:
echo.
echo    [1]  Documents    ^(recommended^)
echo    [2]  Desktop
echo    [3]  C:\  drive root
echo    [4]  Type a custom path
echo.
set /p "CHOICE=  Your choice (1/2/3/4): "
echo.

if "!CHOICE!"=="1" set "BASE=!USERPROFILE!\Documents"
if "!CHOICE!"=="2" set "BASE=!USERPROFILE!\Desktop"
if "!CHOICE!"=="3" set "BASE=C:"
if "!CHOICE!"=="4" (
    set /p "BASE=  Enter full folder path (e.g. D:\Work): "
    :: Remove trailing backslash
    if "!BASE:~-1!"=="\" set "BASE=!BASE:~0,-1!"
)
if "!BASE!"=="" set "BASE=!USERPROFILE!\Documents"

set "INSTALL_DIR=!BASE!\Basira_app"

echo  Installing to: !INSTALL_DIR!
echo  (This path is saved and used automatically on every login)
echo.
echo [%date% %time%] INSTALL_DIR=!INSTALL_DIR! >> "%LOG%"

:: Save install path permanently to AppData
echo !INSTALL_DIR! > "!INSTALL_PATH_FILE!"

:: Create Basira_app and templates folders
if not exist "!INSTALL_DIR!" mkdir "!INSTALL_DIR!"
if not exist "!INSTALL_DIR!\templates" mkdir "!INSTALL_DIR!\templates"
echo  [OK]  Folder Basira_app created at: !INSTALL_DIR!
echo.

:: ── STEP 3: Download files from GitHub ──────────────────────
echo  [Step 3/6]  Downloading files from GitHub...
echo.

set "FILES=launcher.py basira_local_bootstrap.py Basira_app_structure.py basira_paths.py basira_session.py"

for %%F in (%FILES%) do (
    echo    Downloading %%F ...
    powershell -Command "Invoke-WebRequest -Uri '!RAW!/%%F' -OutFile '!INSTALL_DIR!\%%F' -UseBasicParsing" >> "%LOG%" 2>&1
    if not exist "!INSTALL_DIR!\%%F" (
        echo.
        echo  [ERROR] Failed to download %%F
        echo  Check your internet connection and try again.
        pause
        exit /b 1
    )
    echo    [OK]  %%F
)

:: Write requirements.txt directly — no download needed
(
    echo flask
    echo flask-cors
    echo requests
) > "!INSTALL_DIR!\requirements.txt"
echo    [OK]  requirements.txt

:: Download basira_app.html
echo    Downloading basira_app.html ...
powershell -Command "Invoke-WebRequest -Uri '!RAW!/templates/basira_app.html' -OutFile '!INSTALL_DIR!\templates\basira_app.html' -UseBasicParsing" >> "%LOG%" 2>&1
if not exist "!INSTALL_DIR!\templates\basira_app.html" (
    echo.
    echo  [ERROR] basira_app.html not found.
    echo  Make sure Basira_local/templates/basira_app.html exists in your GitHub repo.
    pause
    exit /b 1
)
echo    [OK]  templates\basira_app.html

echo.
echo  [OK]  All files downloaded successfully
echo.

:: ── STEP 4: Install Python packages ─────────────────────────
echo  [Step 4/6]  Installing Python packages...
echo              (flask, flask-cors, requests)
echo              Please wait - showing progress below:
echo.

cd /d "!INSTALL_DIR!"

:: Upgrade pip silently
python -m pip install --upgrade pip --quiet >> "%LOG%" 2>&1

:: Install packages WITH progress visible to user
python -m pip install flask flask-cors requests --no-warn-script-location

if %errorlevel% neq 0 (
    echo.
    echo  [WARNING] Some packages may have issues.
    echo  Trying alternative install...
    python -m pip install flask flask-cors requests --user
)

echo.
echo  [OK]  Python packages installed
echo.

:: ── STEP 5: Save install path to config ─────────────────────
echo  [Step 5/6]  Saving configuration...

:: Write install path into AppData so launcher always knows where Basira_app is
echo !INSTALL_DIR! > "!INSTALL_PATH_FILE!"
echo [%date% %time%] Saved install path to %INSTALL_PATH_FILE% >> "%LOG%"
echo  [OK]  Install path saved: !INSTALL_DIR!

:: Register in Windows startup so Basira opens automatically on login
where pythonw >nul 2>&1
if %errorlevel% equ 0 ( set "PY_RUN=pythonw" ) else ( set "PY_RUN=python" )

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" ^
    /v "Basira" /t REG_SZ ^
    /d "!PY_RUN! \"!INSTALL_DIR!\launcher.py\" --background" ^
    /f >> "%LOG%" 2>&1

echo  [OK]  Basira registered in Windows startup
echo.

:: ── STEP 6: Desktop shortcut ─────────────────────────────────
echo  [Step 6/6]  Creating Desktop shortcut...

set "VBS=%TEMP%\basira_sc.vbs"
(
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo Set oLink = oWS.CreateShortcut^("%USERPROFILE%\Desktop\Basira.lnk"^)
    echo oLink.TargetPath = "!PY_RUN!"
    echo oLink.Arguments = """!INSTALL_DIR!\launcher.py"""
    echo oLink.WorkingDirectory = "!INSTALL_DIR!"
    echo oLink.Description = "Basira Local Intelligence"
    echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%" >> "%LOG%" 2>&1
del "%VBS%" 2>nul

echo  [OK]  Basira shortcut created on Desktop
echo.

:: ── DONE: Launch Basira ───────────────────────────────────────
echo  =====================================================
echo    [DONE]  Installation Complete!
echo.
echo    Installed at: !INSTALL_DIR!
echo    Desktop shortcut: Basira.lnk
echo.
echo    Starting Basira now...
echo    Your browser will open automatically.
echo  =====================================================
echo.
echo [%date% %time%] Installation complete. Launching. >> "%LOG%"

:: Launch launcher.py — this starts both Flask servers and opens browser
start "" !PY_RUN! "!INSTALL_DIR!\launcher.py"

echo  Basira is starting up...
echo  Your browser will open in about 10-15 seconds.
echo.
echo  If nothing opens, double-click the Basira shortcut on your Desktop.
echo.
echo  You can close this window now.
echo.
timeout /t 10 /nobreak
exit /b 0
