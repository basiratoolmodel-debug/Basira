@echo off
setlocal EnableDelayedExpansion
title Basira Installer

set "RAW=https://raw.githubusercontent.com/basiratoolmodel-debug/Basira/main/Basira_local"
set "API=https://api.github.com/repos/basiratoolmodel-debug/Basira/contents/Basira_local?ref=main"
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

:: Fresh install to prevent old files from staying mixed with new files
if exist "!INSTALL_DIR!" (
    echo Existing Basira_app found.
    echo Removing old folder to install a clean latest copy...
    rmdir /s /q "!INSTALL_DIR!" >>"%LOG%" 2>&1
    if exist "!INSTALL_DIR!" (
        echo.
        echo [ERROR] Could not remove old Basira_app folder.
        echo Close Basira, close Python windows, then run this installer again.
        echo Log: %LOG%
        pause
        exit /b 1
    )
)

mkdir "!INSTALL_DIR!"
if not exist "!INSTALL_DIR!" (
    echo.
    echo [ERROR] Could not create install folder.
    echo Path: !INSTALL_DIR!
    pause
    exit /b 1
)
echo [OK] Fresh install folder created
echo.

:: STEP 3: Download all files and folders from GitHub without ZIP
echo [Step 3/6] Downloading all Basira_local files and folders from GitHub...
echo (This may take 1-2 minutes)
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference='Stop'; ^
$api='!API!'; ^
$install='!INSTALL_DIR!'; ^
$log='%LOG%'; ^
$headers=@{'User-Agent'='Basira-Installer'}; ^
function DownloadTree([string]$url) { ^
  $items = Invoke-RestMethod -Uri $url -Headers $headers; ^
  foreach ($item in $items) { ^
    if ($item.type -eq 'dir') { ^
      DownloadTree $item.url; ^
    } elseif ($item.type -eq 'file') { ^
      $rel = $item.path -replace '^Basira_local/',''; ^
      $out = Join-Path $install $rel; ^
      $parent = Split-Path $out -Parent; ^
      if (!(Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }; ^
      Write-Host ('  Downloading ' + $rel + ' ...'); ^
      Invoke-WebRequest -Uri $item.download_url -OutFile $out -UseBasicParsing; ^
      if (!(Test-Path $out)) { throw ('Failed to download ' + $rel) }; ^
      Add-Content -Path $log -Value ('Downloaded: ' + $rel); ^
    } ^
  } ^
}; ^
DownloadTree $api" >>"%LOG%" 2>&1

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to download Basira_local from GitHub.
    echo Check your internet connection and make sure the repository is public.
    echo Log: %LOG%
    pause
    exit /b 1
)

echo [OK] All GitHub files and folders downloaded
echo.

:: Make sure launcher.py exists before continuing
if not exist "!INSTALL_DIR!\launcher.py" (
    echo.
    echo [ERROR] launcher.py was not downloaded.
    echo Make sure this file exists in GitHub: Basira_local/launcher.py
    echo Log: %LOG%
    pause
    exit /b 1
)
echo [OK] launcher.py found

:: Create fallback requirements.txt only if GitHub does not include one
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
echo.

:: STEP 4: Install Python packages
echo [Step 4/6] Installing Python packages...
echo (pandas, scikit-learn, flask and others - may take 2-3 min)
echo.
cd /d "!INSTALL_DIR!"
python -m pip install --upgrade pip -q >>"%LOG%" 2>&1
python -m pip install -r requirements.txt >>"%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install Python packages.
    echo Log: %LOG%
    pause
    exit /b 1
)
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

:: Register MAIN launcher
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Basira" /t REG_SZ /d "\"!PYW!\" \"!INSTALL_DIR!\launcher.py\" --background" /f >>"%LOG%" 2>&1
echo [OK] Basira will auto-start on Windows login
echo.

:: STEP 6: Desktop shortcuts
echo [Step 6/6] Creating Desktop shortcuts...

:: Shortcut 1: Main Basira
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

:: Shortcut 2: Preprocessor
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
echo If Basira did not open, check this log:
echo %LOG%
echo.
pause
exit /b 0
