@echo off
setlocal EnableDelayedExpansion
title Basira Installer

set "RAW=https://raw.githubusercontent.com/basiratoolmodel-debug/Basira/main/Basira_local"
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
echo Basira will be installed in a folder called Basira_app
echo You choose WHERE to put that folder.
echo.

:: STEP 1: Check Python
echo [Step 1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed.
    echo.
    echo Please:
    echo   1. Install Python from the page that will open
    echo   2. CHECK the box "Add Python to PATH"
    echo   3. Run this installer again
    echo.
    start "" "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [OK] %PY_VER%
echo.

:: STEP 2: Pick install location
echo [Step 2/6] Choose where to install Basira_app folder
echo.
echo   1  Documents (default)
echo   2  Desktop
echo   3  C:\ root
echo   4  Type a custom path
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
if "!BASE!"=="C:\" set "BASE=C:\"

:: Remove trailing backslash unless it is C:\
if not "!BASE!"=="C:\" (
    if "!BASE:~-1!"=="\" set "BASE=!BASE:~0,-1!"
)

set "INSTALL_DIR=!BASE!\Basira_app"

echo.
echo [OK] Will install to: !INSTALL_DIR!
echo.
echo [%date% %time%] INSTALL_DIR=!INSTALL_DIR! >> "%LOG%"

:: Save install path for launcher to find on every startup
echo !INSTALL_DIR!> "%APPDATA_DIR%\install_path.txt"

:: Create folders
if not exist "!INSTALL_DIR!" mkdir "!INSTALL_DIR!"
if not exist "!INSTALL_DIR!\templates" mkdir "!INSTALL_DIR!\templates"
echo [OK] Folders created
echo.

:: STEP 3: Download files from GitHub
echo [Step 3/6] Downloading files from GitHub...
echo (This may take 1-2 minutes)
echo.

for %%F in (launcher.py basira_local_bootstrap.py Basira_app_structure.py basira_paths.py basira_session.py) do (
    echo   Downloading %%F ...
    powershell -Command "Invoke-WebRequest -Uri '!RAW!/%%F' -OutFile '!INSTALL_DIR!\%%F' -UseBasicParsing" 2>>"%LOG%"
    if not exist "!INSTALL_DIR!\%%F" (
        echo.
        echo [ERROR] Failed to download %%F
        echo Check your internet and try again.
        pause
        exit /b 1
    )
    echo   [OK] %%F
)

:: Write requirements.txt directly
echo flask> "!INSTALL_DIR!\requirements.txt"
echo flask-cors>> "!INSTALL_DIR!\requirements.txt"
echo requests>> "!INSTALL_DIR!\requirements.txt"
echo   [OK] requirements.txt

:: Download basira_app.html
echo   Downloading basira_app.html ...
powershell -Command "Invoke-WebRequest -Uri '!RAW!/templates/basira_app.html' -OutFile '!INSTALL_DIR!\templates\basira_app.html' -UseBasicParsing" 2>>"%LOG%"
if not exist "!INSTALL_DIR!\templates\basira_app.html" (
    echo.
    echo [ERROR] Failed to download basira_app.html
    echo Make sure Basira_local/templates/basira_app.html is in your GitHub repo.
    pause
    exit /b 1
)
echo   [OK] basira_app.html
echo.
echo [OK] All files downloaded
echo.

:: STEP 4: Install Python packages
echo [Step 4/6] Installing Python packages...
echo.
cd /d "!INSTALL_DIR!"
python -m pip install --upgrade pip -q >>"%LOG%" 2>&1
python -m pip install flask flask-cors requests
echo.
echo [OK] Packages installed
echo.

:: STEP 5: Register in Windows startup
echo [Step 5/6] Registering Basira in Windows startup...

where pythonw >nul 2>&1
if %errorlevel% equ 0 ( set "PYW=pythonw" ) else ( set "PYW=python" )

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Basira" /t REG_SZ /d "!PYW! \"!INSTALL_DIR!\launcher.py\" --background" /f >>"%LOG%" 2>&1
echo [OK] Basira will auto-start on Windows login
echo.

:: STEP 6: Desktop shortcut
echo [Step 6/6] Creating Desktop shortcut...

set "VBS=%TEMP%\basira_sc.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS%"
echo Set oLink = oWS.CreateShortcut("%USERPROFILE%\Desktop\Basira.lnk") >> "%VBS%"
echo oLink.TargetPath = "!PYW!" >> "%VBS%"
echo oLink.Arguments = Chr(34) & "!INSTALL_DIR!\launcher.py" & Chr(34) >> "%VBS%"
echo oLink.WorkingDirectory = "!INSTALL_DIR!" >> "%VBS%"
echo oLink.Description = "Basira Local Intelligence" >> "%VBS%"
echo oLink.Save >> "%VBS%"
cscript //nologo "%VBS%" >>"%LOG%" 2>&1
del "%VBS%" 2>nul
echo [OK] Desktop shortcut created
echo.

:: LAUNCH
echo =====================================================
echo   DONE! Installation complete.
echo   Location: !INSTALL_DIR!
echo   Launching Basira now...
echo =====================================================
echo.
echo [%date% %time%] Complete. Launching. >> "%LOG%"

start "" !PYW! "!INSTALL_DIR!\launcher.py"

echo Basira is starting. Browser will open in about 15 seconds.
echo If nothing opens, double-click the Basira shortcut on your Desktop.
echo.
echo You can close this window now.
echo.
timeout /t 10 /nobreak >nul
exit /b 0
