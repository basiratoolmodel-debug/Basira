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

:: Backup old installation to avoid mixing old and new files
if exist "!INSTALL_DIR!" (
    for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set "DATESTAMP=%%d%%b%%c"
    for /f "tokens=1-3 delims=:., " %%a in ("%time%") do set "TIMESTAMP=%%a%%b%%c"
    set "BACKUP_DIR=!BASE!\Basira_app_backup_!DATESTAMP!_!TIMESTAMP!"
    echo Existing Basira_app found.
    echo Moving old folder to: !BACKUP_DIR!
    move "!INSTALL_DIR!" "!BACKUP_DIR!" >>"%LOG%" 2>&1
    if exist "!INSTALL_DIR!" (
        echo.
        echo [ERROR] Could not move old Basira_app folder.
        echo Close any running Basira windows and try again.
        pause
        exit /b 1
    )
)

:: Create fresh install folder
mkdir "!INSTALL_DIR!"
echo [OK] Fresh install folder created

echo.

:: STEP 3: Download the full Basira_local folder from GitHub
echo [Step 3/6] Downloading the full Basira_local folder from GitHub...
echo (This may take 1-2 minutes)
echo.

set "REPO_ZIP=https://github.com/basiratoolmodel-debug/Basira/archive/refs/heads/main.zip"
set "ZIP_FILE=%TEMP%\Basira_main.zip"
set "EXTRACT_DIR=%TEMP%\Basira_extract_%RANDOM%_%RANDOM%"

if exist "!ZIP_FILE!" del /f /q "!ZIP_FILE!" >nul 2>&1
if exist "!EXTRACT_DIR!" rmdir /s /q "!EXTRACT_DIR!" >nul 2>&1

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -Uri '!REPO_ZIP!' -OutFile '!ZIP_FILE!' -UseBasicParsing; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }" >>"%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to download GitHub repository ZIP.
    echo Check your internet connection and make sure the repository is public.
    pause
    exit /b 1
)
echo [OK] Repository ZIP downloaded

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Expand-Archive -Path '!ZIP_FILE!' -DestinationPath '!EXTRACT_DIR!' -Force; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }" >>"%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to extract repository ZIP.
    pause
    exit /b 1
)
echo [OK] Repository ZIP extracted

set "SOURCE_DIR=!EXTRACT_DIR!\Basira-main\Basira_local"
if not exist "!SOURCE_DIR!" (
    echo.
    echo [ERROR] Could not find Basira_local inside the GitHub repository.
    echo Expected path: !SOURCE_DIR!
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Copy-Item -Path '!SOURCE_DIR!\*' -Destination '!INSTALL_DIR!' -Recurse -Force; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }" >>"%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to copy Basira_local files to the install folder.
    pause
    exit /b 1
)

echo [OK] Full Basira_local folder copied

:: Create fallback requirements.txt only if the project does not include one
if not exist "!INSTALL_DIR!\requirements.txt" (
    echo flask> "!INSTALL_DIR!\requirements.txt"
    echo flask-cors>> "!INSTALL_DIR!\requirements.txt"
    echo requests>> "!INSTALL_DIR!\requirements.txt"
    echo pandas>> "!INSTALL_DIR!\requirements.txt"
    echo scikit-learn>> "!INSTALL_DIR!\requirements.txt"
    echo scipy>> "!INSTALL_DIR!\requirements.txt"
    echo openpyxl>> "!INSTALL_DIR!\requirements.txt"
    echo [OK] fallback requirements.txt created
) else (
    echo [OK] requirements.txt found from GitHub
)

:: Clean temporary files
if exist "!ZIP_FILE!" del /f /q "!ZIP_FILE!" >nul 2>&1
if exist "!EXTRACT_DIR!" rmdir /s /q "!EXTRACT_DIR!" >nul 2>&1

echo.
echo [OK] All GitHub files and folders downloaded

echo.

:: STEP 4: Install Python packages
echo [Step 4/6] Installing Python packages...
echo (pandas, scikit-learn, flask and others - may take 2-3 min)
echo.
cd /d "!INSTALL_DIR!"
python -m pip install --upgrade pip -q >>"%LOG%" 2>&1
python -m pip install -r requirements.txt >>"%LOG%" 2>&1
echo.
echo [OK] Packages installed
echo.

:: STEP 5: Register in Windows startup
echo [Step 5/6] Registering Basira in Windows startup...

for /f "usebackq tokens=*" %%p in (`python -c "import sys; print(sys.executable)"`) do set "PYTHON_EXE=%%p"
echo [OK] Python: !PYTHON_EXE!

set "PYTHONW_EXE=!PYTHON_EXE:python.exe=pythonw.exe!"
if exist "!PYTHONW_EXE!" (
    set "PYW=!PYTHONW_EXE!"
) else (
    set "PYW=!PYTHON_EXE!"
)
echo [OK] Launcher: !PYW!

echo !PYTHON_EXE!> "%APPDATA_DIR%\python_path.txt"

:: Register MAIN launcher (starts both servers)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Basira" /t REG_SZ /d "\"!PYW!\" \"!INSTALL_DIR!\launcher.py\" --background" /f >>"%LOG%" 2>&1
echo [OK] Basira will auto-start on Windows login
echo.

:: STEP 6: Desktop shortcuts
echo [Step 6/6] Creating Desktop shortcuts...

:: ── Shortcut 1: Main Basira ──────────────────────────────────
set "VBS=%TEMP%\basira_sc.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS%"
echo Set oLink = oWS.CreateShortcut("%USERPROFILE%\Desktop\Basira.lnk") >> "%VBS%"
echo oLink.TargetPath = "!PYW!" >> "%VBS%"
echo oLink.Arguments = Chr(34) ^& "!INSTALL_DIR!\launcher.py" ^& Chr(34) >> "%VBS%"
echo oLink.WorkingDirectory = "!INSTALL_DIR!" >> "%VBS%"
echo oLink.Description = "Basira Local Intelligence" >> "%VBS%"
echo oLink.Save >> "%VBS%"
cscript //nologo "%VBS%" >>"%LOG%" 2>&1
del "%VBS%" 2>nul
echo [OK] Desktop shortcut: Basira

:: ── Shortcut 2: Preprocessor ────────────────────────────────
if exist "!INSTALL_DIR!\launcher_preprocessor.py" (
    set "VBS2=%TEMP%\basira_prep_sc.vbs"
    echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS2%"
    echo Set oLink = oWS.CreateShortcut("%USERPROFILE%\Desktop\Basira Preprocessor.lnk") >> "%VBS2%"
    echo oLink.TargetPath = "!PYW!" >> "%VBS2%"
    echo oLink.Arguments = Chr(34) ^& "!INSTALL_DIR!\launcher_preprocessor.py" ^& Chr(34) >> "%VBS2%"
    echo oLink.WorkingDirectory = "!INSTALL_DIR!" >> "%VBS2%"
    echo oLink.Description = "Basira Smart Preprocessor" >> "%VBS2%"
    echo oLink.Save >> "%VBS2%"
    cscript //nologo "%VBS2%" >>"%LOG%" 2>&1
    del "%VBS2%" 2>nul
    echo [OK] Desktop shortcut: Basira Preprocessor
)

echo.

:: LAUNCH
echo =====================================================
echo   DONE! Installation complete.
echo   Location: !INSTALL_DIR!
echo   Launching Basira now...
echo =====================================================
echo.
echo [%date% %time%] Complete. Launching. >> "%LOG%"

start "" "!PYW!" "!INSTALL_DIR!\launcher.py"

timeout /t 12 /nobreak >nul

start "" "https://basira.basira-toolmodel.workers.dev/local-setup.html"

echo.
echo Basira is running.
echo The setup page is opening in your browser.
echo Follow the steps on screen to complete setup.
echo.
echo You can close this window now.
echo.
timeout /t 5 /nobreak >nul
exit /b 0
