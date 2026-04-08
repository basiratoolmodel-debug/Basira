@echo off
:: ================================================================
:: Basira Installer — شغّل هذا الملف مرة واحدة فقط
:: ================================================================
:: What this does:
::   1. Asks user to pick a folder (default: Documents)
::   2. Creates Basira_local\ inside that folder
::   3. Downloads all files from GitHub into Basira_local\
::   4. Installs Python requirements
::   5. Registers launcher in Windows startup
::   6. Creates desktop shortcut
::   7. Launches Basira automatically
:: ================================================================
setlocal EnableDelayedExpansion
title بصيرة — جارٍ التثبيت...

set "GITHUB_REPO=https://raw.githubusercontent.com/basiratoolmodel-debug/Basira/main/Basira_local"
set "APPDATA_BASIRA=%USERPROFILE%\AppData\Local\Basira"
set "LOG=%APPDATA_BASIRA%\install.log"
set "DEFAULT_BASE=%USERPROFILE%\Documents"

:: Create AppData folder for logs
if not exist "%APPDATA_BASIRA%" mkdir "%APPDATA_BASIRA%"

echo. >> "%LOG%"
echo ===== [%date% %time%] Installation started ===== >> "%LOG%"

cls
echo.
echo  ████████████████████████████████████████
echo        بصيرة — مرحباً بك
echo        Basira — Welcome
echo  ████████████████████████████████████████
echo.
echo  سيتم الآن تثبيت بصيرة على هذا الجهاز.
echo  جميع الخطوات تتم تلقائياً.
echo.
echo  ────────────────────────────────────────
echo.

:: ── STEP 1: Check Python ─────────────────────────────────────
echo  [1/6] فحص Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ⚠  Python غير مثبت على هذا الجهاز.
    echo     جارٍ فتح صفحة تحميل Python...
    echo.
    echo  بعد تثبيت Python:
    echo    - تأكدي من تفعيل "Add Python to PATH"
    echo    - ثم شغّلي هذا الملف مجدداً
    echo.
    start "" "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    echo [%date% %time%] ERROR: Python not found >> "%LOG%"
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo  ✓ %PY_VER% >> "%LOG%"
echo  ✓ %PY_VER%


:: ── STEP 2: Choose install folder ────────────────────────────
echo.
echo  [2/6] اختيار مجلد التثبيت...
echo.
echo  سيتم إنشاء مجلد Basira_local داخل المجلد الذي تختارينه.
echo  المجلد الافتراضي: %DEFAULT_BASE%
echo.
echo  اضغطي Enter للموافقة على المجلد الافتراضي
echo  أو اكتبي مساراً مختلفاً:
echo.
set /p "USER_BASE=  المجلد: "

:: Use default if user just pressed Enter
if "!USER_BASE!"=="" set "USER_BASE=%DEFAULT_BASE%"

:: Remove trailing backslash if present
if "!USER_BASE:~-1!"=="\" set "USER_BASE=!USER_BASE:~0,-1!"

set "INSTALL_DIR=!USER_BASE!\Basira_local"

echo.
echo  سيتم التثبيت في: !INSTALL_DIR!
echo [%date% %time%] Install dir: !INSTALL_DIR! >> "%LOG%"

:: Create Basira_local folder and templates subfolder
if not exist "!INSTALL_DIR!" mkdir "!INSTALL_DIR!"
if not exist "!INSTALL_DIR!\templates" mkdir "!INSTALL_DIR!\templates"

echo  ✓ تم إنشاء مجلد Basira_local


:: ── STEP 3: Download files from GitHub ───────────────────────
echo.
echo  [3/6] تنزيل الملفات من GitHub...
echo  (قد يستغرق هذا دقيقة أو دقيقتين حسب سرعة الإنترنت)
echo.

:: List of files in GitHub Basira_local/ folder
set "FILES=launcher.py basira_local_bootstrap.py Basira_app_structure.py basira_paths.py basira_session.py requirements.txt"

for %%F in (%FILES%) do (
    echo    جارٍ تنزيل %%F...
    powershell -Command ^
        "try { Invoke-WebRequest -Uri '%GITHUB_REPO%/%%F' -OutFile '!INSTALL_DIR!\%%F' -UseBasicParsing -ErrorAction Stop; Write-Host 'OK' } catch { Write-Host $_.Exception.Message; exit 1 }" ^
        >> "%LOG%" 2>&1
    if not exist "!INSTALL_DIR!\%%F" (
        echo.
        echo  ✗ تعذر تنزيل %%F
        echo  تأكدي من الاتصال بالإنترنت وحاولي مجدداً.
        echo [%date% %time%] FAILED: %%F >> "%LOG%"
        pause
        exit /b 1
    )
    echo    ✓ %%F
    echo [%date% %time%] Downloaded: %%F >> "%LOG%"
)

:: Download basira_app.html into templates\
echo    جارٍ تنزيل templates\basira_app.html...
powershell -Command ^
    "Invoke-WebRequest -Uri '%GITHUB_REPO%/templates/basira_app.html' -OutFile '!INSTALL_DIR!\templates\basira_app.html' -UseBasicParsing" ^
    >> "%LOG%" 2>&1
echo    ✓ templates\basira_app.html
echo [%date% %time%] Downloaded: basira_app.html >> "%LOG%"

echo.
echo  ✓ تم تنزيل جميع الملفات بنجاح


:: ── STEP 4: Install Python requirements ──────────────────────
echo.
echo  [4/6] تثبيت مكتبات Python...
cd /d "!INSTALL_DIR!"
python -m pip install --quiet --upgrade pip >> "%LOG%" 2>&1
python -m pip install --quiet -r requirements.txt >> "%LOG%" 2>&1
echo  ✓ تم تثبيت المكتبات
echo [%date% %time%] pip install done >> "%LOG%"


:: ── STEP 5: Register in Windows startup ──────────────────────
echo.
echo  [5/6] تسجيل بصيرة في بدء تشغيل Windows...

:: Use pythonw (no console window) if available
where pythonw >nul 2>&1
if %errorlevel% equ 0 ( set "PY_RUN=pythonw" ) else ( set "PY_RUN=python" )

:: Save install path to AppData config so launcher knows where it is
echo !INSTALL_DIR! > "%APPDATA_BASIRA%\install_path.txt"

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" ^
    /v "Basira" ^
    /t REG_SZ ^
    /d "!PY_RUN! \"!INSTALL_DIR!\launcher.py\" --background" ^
    /f >> "%LOG%" 2>&1

echo  ✓ سيفتح بصيرة تلقائياً عند تشغيل الجهاز
echo [%date% %time%] Startup registered >> "%LOG%"


:: ── STEP 6: Desktop shortcut ─────────────────────────────────
echo.
echo  [6/6] إنشاء اختصار على سطح المكتب...

set "VBS=%TEMP%\basira_link.vbs"
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo Set oLink = oWS.CreateShortcut^("%USERPROFILE%\Desktop\Basira.lnk"^)
echo oLink.TargetPath = "!PY_RUN!"
echo oLink.Arguments = """!INSTALL_DIR!\launcher.py"""
echo oLink.WorkingDirectory = "!INSTALL_DIR!"
echo oLink.Description = "Basira — ذكاء البيانات المحلي"
echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%" >> "%LOG%" 2>&1
del "%VBS%" 2>nul

echo  ✓ اختصار Basira على سطح المكتب جاهز
echo [%date% %time%] Shortcut created >> "%LOG%"


:: ── LAUNCH ───────────────────────────────────────────────────
echo.
echo  ████████████████████████████████████████
echo    ✓ اكتمل التثبيت بنجاح!
echo    مجلد بصيرة: !INSTALL_DIR!
echo    جارٍ فتح بصيرة...
echo  ████████████████████████████████████████
echo.

echo [%date% %time%] Installation complete. Launching. >> "%LOG%"

:: Launch Basira now
start "" !PY_RUN! "!INSTALL_DIR!\launcher.py"

timeout /t 3 /nobreak >nul
exit /b 0
