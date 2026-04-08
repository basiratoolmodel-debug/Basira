@echo off
:: ============================================================
:: Basira Installer — يُشغَّل مرة واحدة فقط
:: Double-click this file to install Basira on this machine.
:: After installation, Basira starts automatically with Windows.
:: ============================================================
setlocal EnableDelayedExpansion

set "BASIRA_DIR=%~dp0"
set "LAUNCHER=%BASIRA_DIR%launcher.py"
set "LOG=%APPDATA%\..\Local\Basira\install.log"

:: Create AppData\Local\Basira if missing
if not exist "%APPDATA%\..\Local\Basira" mkdir "%APPDATA%\..\Local\Basira"

echo [%date% %time%] Basira installer started >> "%LOG%"

:: ── 1. Check Python ──────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Opening download page...
    echo [%date% %time%] Python not found, opening download >> "%LOG%"
    start "" "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    echo.
    echo ============================================================
    echo  Python لم يتم العثور عليه.
    echo  يتم فتح صفحة تحميل Python تلقائياً.
    echo  بعد تثبيت Python، شغّل هذا الملف مرة أخرى.
    echo ============================================================
    pause
    exit /b 1
)

:: ── 2. Install requirements ──────────────────────────────────
echo Installing Python requirements...
echo [%date% %time%] Installing requirements >> "%LOG%"
python -m pip install --quiet --upgrade pip >> "%LOG%" 2>&1
python -m pip install --quiet -r "%BASIRA_DIR%requirements.txt" >> "%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo [%date% %time%] pip install failed >> "%LOG%"
    echo Failed to install requirements. Check your internet connection.
    pause
    exit /b 1
)

:: ── 3. Register launcher in Windows startup ──────────────────
echo Registering Basira in Windows startup...
set "PYTHONW=%~dp0pythonw_helper.bat"
set "REG_CMD=pythonw "%LAUNCHER%" --background"

:: Use pythonw.exe if available (no console window)
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    set "REG_CMD=pythonw "%LAUNCHER%" --background"
) else (
    set "REG_CMD=python "%LAUNCHER%" --background"
)

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" ^
    /v "Basira" /t REG_SZ /d "!REG_CMD!" /f >> "%LOG%" 2>&1

:: ── 4. Create desktop shortcut ───────────────────────────────
echo Creating desktop shortcut...
set "SHORTCUT=%USERPROFILE%\Desktop\Basira.lnk"
set "VBS=%TEMP%\create_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS%"
echo sLinkFile = "%SHORTCUT%" >> "%VBS%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS%"
echo oLink.TargetPath = "pythonw" >> "%VBS%"
echo oLink.Arguments = """%LAUNCHER%""" >> "%VBS%"
echo oLink.WorkingDirectory = "%BASIRA_DIR%" >> "%VBS%"
echo oLink.Description = "Basira Local Intelligence" >> "%VBS%"
echo oLink.Save >> "%VBS%"
cscript //nologo "%VBS%" >> "%LOG%" 2>&1
del "%VBS%" 2>nul

:: ── 5. Launch Basira now ─────────────────────────────────────
echo [%date% %time%] Installation complete, launching >> "%LOG%"
echo.
echo ============================================================
echo  تم التثبيت بنجاح!
echo  يتم الآن تشغيل بصيرة وفتح المتصفح تلقائياً...
echo ============================================================
echo.

start "" pythonw "%LAUNCHER%"

:: Give it 3 seconds then close
timeout /t 3 /nobreak >nul
exit /b 0
