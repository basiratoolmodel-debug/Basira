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
echo [Step 3/6] Downloading all files from GitHub...
echo (This may take 1-2 minutes)
echo.

set "DL_B64=%TEMP%\basira_download_all.b64"
set "DL_PY=%TEMP%\basira_download_all.py"

> "!DL_B64!" (
echo aW1wb3J0IG9zCmltcG9ydCBzeXMKaW1wb3J0IGpzb24KaW1wb3J0IHVybGxpYi5yZXF1ZXN0Cmlt
echo cG9ydCB1cmxsaWIucGFyc2UKCnJlcG8gPSAiYmFzaXJhdG9vbG1vZGVsLWRlYnVnL0Jhc2lyYSIK
echo YnJhbmNoID0gIm1haW4iCnByZWZpeCA9ICJCYXNpcmFfbG9jYWwvIgppbnN0YWxsX2RpciA9IG9z
echo LmVudmlyb24uZ2V0KCJCQVNJUkFfSU5TVEFMTF9ESVIiKQoKaWYgbm90IGluc3RhbGxfZGlyOgog
echo ICAgcHJpbnQoIltFUlJPUl0gQkFTSVJBX0lOU1RBTExfRElSIHdhcyBub3Qgc2V0LiIpCiAgICBz
echo eXMuZXhpdCgxKQoKb3MubWFrZWRpcnMoaW5zdGFsbF9kaXIsIGV4aXN0X29rPVRydWUpCgpoZWFk
echo ZXJzID0gewogICAgIlVzZXItQWdlbnQiOiAiQmFzaXJhLUluc3RhbGxlciIsCiAgICAiQWNjZXB0
echo IjogImFwcGxpY2F0aW9uL3ZuZC5naXRodWIranNvbiIKfQoKZGVmIHJlcXVlc3RfanNvbih1cmwp
echo OgogICAgcmVxID0gdXJsbGliLnJlcXVlc3QuUmVxdWVzdCh1cmwsIGhlYWRlcnM9aGVhZGVycykK
echo ICAgIHdpdGggdXJsbGliLnJlcXVlc3QudXJsb3BlbihyZXEsIHRpbWVvdXQ9NjApIGFzIHJlc3Bv
echo bnNlOgogICAgICAgIHJldHVybiBqc29uLmxvYWRzKHJlc3BvbnNlLnJlYWQoKS5kZWNvZGUoInV0
echo Zi04IikpCgpkZWYgZG93bmxvYWRfZmlsZSh1cmwsIG91dF9wYXRoKToKICAgIHJlcSA9IHVybGxp
echo Yi5yZXF1ZXN0LlJlcXVlc3QodXJsLCBoZWFkZXJzPXsiVXNlci1BZ2VudCI6ICJCYXNpcmEtSW5z
echo dGFsbGVyIn0pCiAgICB3aXRoIHVybGxpYi5yZXF1ZXN0LnVybG9wZW4ocmVxLCB0aW1lb3V0PTEy
echo MCkgYXMgcmVzcG9uc2U6CiAgICAgICAgZGF0YSA9IHJlc3BvbnNlLnJlYWQoKQogICAgb3MubWFr
echo ZWRpcnMob3MucGF0aC5kaXJuYW1lKG91dF9wYXRoKSwgZXhpc3Rfb2s9VHJ1ZSkKICAgIHdpdGgg
echo b3BlbihvdXRfcGF0aCwgIndiIikgYXMgZjoKICAgICAgICBmLndyaXRlKGRhdGEpCgphcGlfdXJs
echo ID0gZiJodHRwczovL2FwaS5naXRodWIuY29tL3JlcG9zL3tyZXBvfS9naXQvdHJlZXMve2JyYW5j
echo aH0/cmVjdXJzaXZlPTEiCnByaW50KCJSZWFkaW5nIEdpdEh1YiBmaWxlIGxpc3QuLi4iKQoKdHJ5
echo OgogICAgdHJlZSA9IHJlcXVlc3RfanNvbihhcGlfdXJsKQpleGNlcHQgRXhjZXB0aW9uIGFzIGU6
echo CiAgICBwcmludCgiW0VSUk9SXSBDb3VsZCBub3QgcmVhZCBHaXRIdWIgZmlsZSBsaXN0LiIpCiAg
echo ICBwcmludChzdHIoZSkpCiAgICBzeXMuZXhpdCgxKQoKaXRlbXMgPSB0cmVlLmdldCgidHJlZSIs
echo IFtdKQpmaWxlcyA9IFtdCmZvciBpdGVtIGluIGl0ZW1zOgogICAgcGF0aCA9IGl0ZW0uZ2V0KCJw
echo YXRoIiwgIiIpCiAgICBpZiBpdGVtLmdldCgidHlwZSIpID09ICJibG9iIiBhbmQgcGF0aC5zdGFy
echo dHN3aXRoKHByZWZpeCk6CiAgICAgICAgcmVsID0gcGF0aFtsZW4ocHJlZml4KTpdCiAgICAgICAg
echo aWYgcmVsOgogICAgICAgICAgICBmaWxlcy5hcHBlbmQoKHBhdGgsIHJlbCkpCgppZiBub3QgZmls
echo ZXM6CiAgICBwcmludCgiW0VSUk9SXSBObyBmaWxlcyBmb3VuZCBpbnNpZGUgQmFzaXJhX2xvY2Fs
echo IG9uIEdpdEh1Yi4iKQogICAgc3lzLmV4aXQoMSkKCnByaW50KGYiRm91bmQge2xlbihmaWxlcyl9
echo IGZpbGVzLiBEb3dubG9hZGluZy4uLiIpCgpmYWlsZWQgPSBbXQpmb3IgaW5kZXgsIChwYXRoLCBy
echo ZWwpIGluIGVudW1lcmF0ZShmaWxlcywgMSk6CiAgICByYXdfcGF0aCA9IHVybGxpYi5wYXJzZS5x
echo dW90ZShwYXRoLCBzYWZlPSIvIikKICAgIHJhd191cmwgPSBmImh0dHBzOi8vcmF3LmdpdGh1YnVz
echo ZXJjb250ZW50LmNvbS97cmVwb30ve2JyYW5jaH0ve3Jhd19wYXRofSIKICAgIG91dF9wYXRoID0g
echo b3MucGF0aC5qb2luKGluc3RhbGxfZGlyLCByZWwucmVwbGFjZSgiLyIsIG9zLnNlcCkpCiAgICBw
echo cmludChmIiAgW3tpbmRleH0ve2xlbihmaWxlcyl9XSB7cmVsfSIpCiAgICB0cnk6CiAgICAgICAg
echo ZG93bmxvYWRfZmlsZShyYXdfdXJsLCBvdXRfcGF0aCkKICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMg
echo ZToKICAgICAgICBmYWlsZWQuYXBwZW5kKChyZWwsIHN0cihlKSkpCiAgICAgICAgcHJpbnQoZiIg
echo ICAgICBGQUlMRUQ6IHtlfSIpCgppZiBmYWlsZWQ6CiAgICBwcmludCgiW0VSUk9SXSBTb21lIGZp
echo bGVzIGZhaWxlZCB0byBkb3dubG9hZDoiKQogICAgZm9yIHJlbCwgZXJyIGluIGZhaWxlZDoKICAg
echo ICAgICBwcmludChmIiAgLSB7cmVsfToge2Vycn0iKQogICAgc3lzLmV4aXQoMSkKCmxhdW5jaGVy
echo ID0gb3MucGF0aC5qb2luKGluc3RhbGxfZGlyLCAibGF1bmNoZXIucHkiKQppZiBub3Qgb3MucGF0
echo aC5leGlzdHMobGF1bmNoZXIpOgogICAgcHJpbnQoIltFUlJPUl0gbGF1bmNoZXIucHkgd2FzIG5v
echo dCBkb3dubG9hZGVkLiIpCiAgICBwcmludCgiTWFrZSBzdXJlIEJhc2lyYV9sb2NhbC9sYXVuY2hl
echo ci5weSBleGlzdHMgaW4gR2l0SHViLiIpCiAgICBzeXMuZXhpdCgxKQoKcmVxID0gb3MucGF0aC5q
echo b2luKGluc3RhbGxfZGlyLCAicmVxdWlyZW1lbnRzLnR4dCIpCmlmIG5vdCBvcy5wYXRoLmV4aXN0
echo cyhyZXEpOgogICAgcHJpbnQoInJlcXVpcmVtZW50cy50eHQgbm90IGZvdW5kIGluIEdpdEh1Yi4g
echo Q3JlYXRpbmcgZGVmYXVsdCByZXF1aXJlbWVudHMudHh0Li4uIikKICAgIHdpdGggb3BlbihyZXEs
echo ICJ3IiwgZW5jb2Rpbmc9InV0Zi04IikgYXMgZjoKICAgICAgICBmLndyaXRlKCJmbGFza1xuZmxh
echo c2stY29yc1xucmVxdWVzdHNcbnBhbmRhc1xuc2Npa2l0LWxlYXJuXG5zY2lweVxub3BlbnB5eGxc
echo biIpCgpwcmludCgiW09LXSBBbGwgQmFzaXJhX2xvY2FsIGZpbGVzIGRvd25sb2FkZWQgd2l0aCBm
echo b2xkZXIgc3RydWN0dXJlLiIpCg==
)

certutil -f -decode "!DL_B64!" "!DL_PY!" >nul 2>>"%LOG%"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Could not prepare the downloader script.
    echo Check this log:
    echo %LOG%
    pause
    exit /b 1
)

set "BASIRA_INSTALL_DIR=!INSTALL_DIR!"
python "!DL_PY!"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to download files from GitHub.
    echo The lines above show the exact file or reason.
    echo Check this log too:
    echo %LOG%
    del "!DL_B64!" 2>nul
    del "!DL_PY!" 2>nul
    pause
    exit /b 1
)

del "!DL_B64!" 2>nul
del "!DL_PY!" 2>nul

echo.
echo [OK] All files downloaded
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
