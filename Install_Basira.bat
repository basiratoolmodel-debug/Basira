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

:: STEP 1: Check Python
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

:: STEP 2: Choose install location
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

if not "!BASE!"=="C:\" (
    if "!BASE:~-1!"=="\" set "BASE=!BASE:~0,-1!"
)

set "INSTALL_DIR=!BASE!\Basira_app"

echo.
echo [OK] Installing to: !INSTALL_DIR!
echo [%date% %time%] INSTALL_DIR=!INSTALL_DIR! >> "%LOG%"

echo !INSTALL_DIR!> "%APPDATA_DIR%\install_path.txt"

if not exist "!INSTALL_DIR!" mkdir "!INSTALL_DIR!"
if not exist "!INSTALL_DIR!\templates" mkdir "!INSTALL_DIR!\templates"
echo [OK] Folders created
echo.

:: STEP 3: Download all files from GitHub
echo [Step 3/5] Downloading files from GitHub...
echo.

set "DL_B64=%TEMP%\basira_dl.b64"
set "DL_PY=%TEMP%\basira_dl.py"

> "!DL_B64!" (
echo aW1wb3J0IG9zLCBzeXMsIGpzb24sIHVybGxpYi5yZXF1ZXN0LCB1cmxsaWIucGFyc2UKClJFUE8g
echo ICA9ICJiYXNpcmF0b29sbW9kZWwtZGVidWcvQmFzaXJhIgpCUkFOQ0ggPSAibWFpbiIKUFJFRklY
echo ID0gIkJhc2lyYV9sb2NhbC8iCklOU1RBTExfRElSID0gb3MuZW52aXJvbi5nZXQoIkJBU0lSQV9J
echo TlNUQUxMX0RJUiIsICIiKQoKaWYgbm90IElOU1RBTExfRElSOgogICAgcHJpbnQoIltFUlJPUl0g
echo QkFTSVJBX0lOU1RBTExfRElSIG5vdCBzZXQiKQogICAgc3lzLmV4aXQoMSkKCkhFQURFUlMgPSB7
echo CiAgICAiVXNlci1BZ2VudCI6ICJCYXNpcmEtSW5zdGFsbGVyIiwKICAgICJBY2NlcHQiOiAiYXBw
echo bGljYXRpb24vdm5kLmdpdGh1Yitqc29uIgp9CgpkZWYgZ2V0X2pzb24odXJsKToKICAgIHJlcSA9
echo IHVybGxpYi5yZXF1ZXN0LlJlcXVlc3QodXJsLCBoZWFkZXJzPUhFQURFUlMpCiAgICB3aXRoIHVy
echo bGxpYi5yZXF1ZXN0LnVybG9wZW4ocmVxLCB0aW1lb3V0PTYwKSBhcyByOgogICAgICAgIHJldHVy
echo biBqc29uLmxvYWRzKHIucmVhZCgpLmRlY29kZSgidXRmLTgiKSkKCmRlZiBkb3dubG9hZF9maWxl
echo KHVybCwgZGVzdCk6CiAgICByZXEgPSB1cmxsaWIucmVxdWVzdC5SZXF1ZXN0KHVybCwgaGVhZGVy
echo cz17IlVzZXItQWdlbnQiOiAiQmFzaXJhLUluc3RhbGxlciJ9KQogICAgd2l0aCB1cmxsaWIucmVx
echo dWVzdC51cmxvcGVuKHJlcSwgdGltZW91dD0xMjApIGFzIHI6CiAgICAgICAgZGF0YSA9IHIucmVh
echo ZCgpCiAgICBvcy5tYWtlZGlycyhvcy5wYXRoLmRpcm5hbWUoZGVzdCksIGV4aXN0X29rPVRydWUp
echo CiAgICB3aXRoIG9wZW4oZGVzdCwgIndiIikgYXMgZjoKICAgICAgICBmLndyaXRlKGRhdGEpCgph
echo cGkgPSAiaHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy97fS9naXQvdHJlZXMve30/cmVjdXJz
echo aXZlPTEiLmZvcm1hdChSRVBPLCBCUkFOQ0gpCnByaW50KCJSZWFkaW5nIGZpbGUgbGlzdCBmcm9t
echo IEdpdEh1Yi4uLiIpCnRyeToKICAgIHRyZWUgPSBnZXRfanNvbihhcGkpCmV4Y2VwdCBFeGNlcHRp
echo b24gYXMgZToKICAgIHByaW50KCJbRVJST1JdIENhbm5vdCByZWFkIEdpdEh1Yjoge30iLmZvcm1h
echo dChlKSkKICAgIHN5cy5leGl0KDEpCgpmaWxlcyA9IFtdCmZvciBpdGVtIGluIHRyZWUuZ2V0KCJ0
echo cmVlIiwgW10pOgogICAgcGF0aCA9IGl0ZW0uZ2V0KCJwYXRoIiwgIiIpCiAgICBpZiBpdGVtLmdl
echo dCgidHlwZSIpID09ICJibG9iIiBhbmQgcGF0aC5zdGFydHN3aXRoKFBSRUZJWCk6CiAgICAgICAg
echo cmVsID0gcGF0aFtsZW4oUFJFRklYKTpdCiAgICAgICAgaWYgcmVsOgogICAgICAgICAgICBmaWxl
echo cy5hcHBlbmQoKHBhdGgsIHJlbCkpCgppZiBub3QgZmlsZXM6CiAgICBwcmludCgiW0VSUk9SXSBO
echo byBmaWxlcyBmb3VuZCBpbiBCYXNpcmFfbG9jYWwgb24gR2l0SHViIikKICAgIHN5cy5leGl0KDEp
echo CgpwcmludCgiRm91bmQge30gZmlsZXMuIERvd25sb2FkaW5nLi4uIi5mb3JtYXQobGVuKGZpbGVz
echo KSkpCmZhaWxlZCA9IFtdCmZvciBpLCAocGF0aCwgcmVsKSBpbiBlbnVtZXJhdGUoZmlsZXMsIDEp
echo OgogICAgcmF3ID0gImh0dHBzOi8vcmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbS97fS97fS97fSIu
echo Zm9ybWF0KAogICAgICAgIFJFUE8sIEJSQU5DSCwgdXJsbGliLnBhcnNlLnF1b3RlKHBhdGgsIHNh
echo ZmU9Ii8iKSkKICAgIGRlc3QgPSBvcy5wYXRoLmpvaW4oSU5TVEFMTF9ESVIsIHJlbC5yZXBsYWNl
echo KCIvIiwgb3Muc2VwKSkKICAgIHByaW50KCIgIFt7fS97fV0ge30iLmZvcm1hdChpLCBsZW4oZmls
echo ZXMpLCByZWwpKQogICAgdHJ5OgogICAgICAgIGRvd25sb2FkX2ZpbGUocmF3LCBkZXN0KQogICAg
echo ZXhjZXB0IEV4Y2VwdGlvbiBhcyBlOgogICAgICAgIGZhaWxlZC5hcHBlbmQoKHJlbCwgc3RyKGUp
echo KSkKICAgICAgICBwcmludCgiICAgIEZBSUxFRDoge30iLmZvcm1hdChlKSkKCmlmIGZhaWxlZDoK
echo ICAgIHByaW50KCJbRVJST1JdIFNvbWUgZmlsZXMgZmFpbGVkOiIpCiAgICBmb3IgciwgZSBpbiBm
echo YWlsZWQ6CiAgICAgICAgcHJpbnQoIiAgLSB7fToge30iLmZvcm1hdChyLCBlKSkKICAgIHN5cy5l
echo eGl0KDEpCgppZiBub3Qgb3MucGF0aC5leGlzdHMob3MucGF0aC5qb2luKElOU1RBTExfRElSLCAi
echo bGF1bmNoZXIucHkiKSk6CiAgICBwcmludCgiW0VSUk9SXSBsYXVuY2hlci5weSB3YXMgbm90IGRv
echo d25sb2FkZWQuIENoZWNrIEJhc2lyYV9sb2NhbC8gb24gR2l0SHViLiIpCiAgICBzeXMuZXhpdCgx
echo KQoKcHJpbnQoIltPS10gQWxsIGZpbGVzIGRvd25sb2FkZWQgc3VjY2Vzc2Z1bGx5IikK
)

certutil -f -decode "!DL_B64!" "!DL_PY!" >nul 2>>"%LOG%"
if %errorlevel% neq 0 (
    echo [ERROR] Could not prepare download script.
    del "!DL_B64!" 2>nul
    pause
    exit /b 1
)

set "BASIRA_INSTALL_DIR=!INSTALL_DIR!"
python "!DL_PY!"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Download failed. Check messages above.
    echo Log: %LOG%
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

:: STEP 5: Register in Windows startup
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

:: LAUNCH
echo =====================================================
echo   Installation complete!
echo   Location: !INSTALL_DIR!
echo =====================================================
echo.
echo [%date% %time%] Installation complete >> "%LOG%"

start "" "!PYW!" "!INSTALL_DIR!\launcher.py"
timeout /t 12 /nobreak >nul
start "" "https://basira.basira-toolmodel.workers.dev/local-setup.html"

echo Basira is now running.
echo You can close this window.
echo.
timeout /t 5 /nobreak >nul
exit /b 0
