@echo off
setlocal EnableDelayedExpansion
title بصيرة — جارٍ التثبيت...

set "RAW=https://raw.githubusercontent.com/basiratoolmodel-debug/Basira/main/Basira_local"
set "APPDATA_BASIRA=%USERPROFILE%\AppData\Local\Basira"
set "LOG=%APPDATA_BASIRA%\install.log"
set "DEFAULT_BASE=%USERPROFILE%\Downloads"

if not exist "%APPDATA_BASIRA%" mkdir "%APPDATA_BASIRA%"
echo ===== [%date% %time%] Install started ===== >> "%LOG%"

cls
echo.
echo  ============================================
echo        بصيرة — مرحباً بك / Basira Welcome
echo  ============================================
echo.
echo  جميع الخطوات تتم تلقائياً.
echo.

:: ── 1. Check Python ──────────────────────────────────────────
echo  [1/6] فحص Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python غير موجود. جارٍ فتح صفحة التحميل...
    start "" "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    echo  بعد تثبيت Python شغّلي هذا الملف مجدداً.
    echo  تأكدي من تفعيل "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo  ✓ %PY_VER%

:: ── 2. Choose folder ─────────────────────────────────────────
echo.
echo  [2/6] اختيار مجلد التثبيت...
echo.
echo  المجلد الافتراضي: %DEFAULT_BASE%
echo  اضغطي Enter للموافقة أو اكتبي مساراً آخر:
echo.
set /p "USER_BASE=  المجلد: "
if "!USER_BASE!"=="" set "USER_BASE=%DEFAULT_BASE%"
if "!USER_BASE:~-1!"=="\" set "USER_BASE=!USER_BASE:~0,-1!"

set "INSTALL_DIR=!USER_BASE!\Basira_local"
echo.
echo  مجلد التثبيت: !INSTALL_DIR!
echo [%date% %time%] Install dir: !INSTALL_DIR! >> "%LOG%"

if not exist "!INSTALL_DIR!" mkdir "!INSTALL_DIR!"
if not exist "!INSTALL_DIR!\templates" mkdir "!INSTALL_DIR!\templates"
echo  ✓ تم إنشاء المجلدات

:: ── 3. Download ALL files ────────────────────────────────────
echo.
echo  [3/6] تنزيل الملفات من GitHub...
echo.

:: Main Python files
set "FILES=launcher.py basira_local_bootstrap.py Basira_app_structure.py basira_paths.py basira_session.py"

for %%F in (%FILES%) do (
    echo    جارٍ تنزيل %%F...
    powershell -Command "Invoke-WebRequest -Uri '!RAW!/%%F' -OutFile '!INSTALL_DIR!\%%F' -UseBasicParsing" >> "%LOG%" 2>&1
    if not exist "!INSTALL_DIR!\%%F" (
        echo  ✗ فشل تنزيل %%F - تحققي من الاتصال بالإنترنت
        pause
        exit /b 1
    )
    echo    ✓ %%F
)

:: Create requirements.txt directly (no download needed)
echo flask>>          "!INSTALL_DIR!\requirements.txt"
echo flask-cors>>     "!INSTALL_DIR!\requirements.txt"
echo requests>>       "!INSTALL_DIR!\requirements.txt"
echo.>> "!INSTALL_DIR!\requirements.txt"
echo  ✓ requirements.txt

:: Download basira_app.html into templates\
echo    جارٍ تنزيل basira_app.html...
powershell -Command "Invoke-WebRequest -Uri '!RAW!/templates/basira_app.html' -OutFile '!INSTALL_DIR!\templates\basira_app.html' -UseBasicParsing" >> "%LOG%" 2>&1

if not exist "!INSTALL_DIR!\templates\basira_app.html" (
    echo  ✗ فشل تنزيل basira_app.html
    echo  تأكدي أن الملف موجود في Basira_local/templates/ على GitHub
    pause
    exit /b 1
)
echo    ✓ templates\basira_app.html
echo.
echo  ✓ تم تنزيل جميع الملفات

:: ── 4. Install requirements ──────────────────────────────────
echo.
echo  [4/6] تثبيت مكتبات Python...
cd /d "!INSTALL_DIR!"
python -m pip install --quiet --upgrade pip >> "%LOG%" 2>&1
python -m pip install --quiet flask flask-cors requests >> "%LOG%" 2>&1
echo  ✓ تم تثبيت المكتبات

:: ── 5. Windows startup ───────────────────────────────────────
echo.
echo  [5/6] تسجيل بصيرة في بدء تشغيل Windows...

where pythonw >nul 2>&1
if %errorlevel% equ 0 ( set "PY_RUN=pythonw" ) else ( set "PY_RUN=python" )

echo !INSTALL_DIR! > "%APPDATA_BASIRA%\install_path.txt"

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" ^
    /v "Basira" /t REG_SZ ^
    /d "!PY_RUN! \"!INSTALL_DIR!\launcher.py\" --background" ^
    /f >> "%LOG%" 2>&1

echo  ✓ بصيرة ستفتح تلقائياً عند تشغيل الجهاز

:: ── 6. Desktop shortcut ──────────────────────────────────────
echo.
echo  [6/6] إنشاء اختصار على سطح المكتب...

set "VBS=%TEMP%\basira_lnk.vbs"
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo Set oLink = oWS.CreateShortcut^("%USERPROFILE%\Desktop\Basira.lnk"^)
echo oLink.TargetPath = "!PY_RUN!"
echo oLink.Arguments = """!INSTALL_DIR!\launcher.py"""
echo oLink.WorkingDirectory = "!INSTALL_DIR!"
echo oLink.Description = "Basira"
echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%" >> "%LOG%" 2>&1
del "%VBS%" 2>nul
echo  ✓ اختصار Basira على سطح المكتب

:: ── Launch ───────────────────────────────────────────────────
echo.
echo  ============================================
echo    ✓ اكتمل التثبيت!
echo    مجلد بصيرة: !INSTALL_DIR!
echo    جارٍ تشغيل بصيرة الآن...
echo  ============================================
echo.
echo [%date% %time%] Install complete >> "%LOG%"

start "" !PY_RUN! "!INSTALL_DIR!\launcher.py"

timeout /t 5 /nobreak >nul
exit /b 0
