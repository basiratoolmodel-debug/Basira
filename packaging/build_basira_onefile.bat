@echo off
cd /d %~dp0

echo ==========================================
echo Building Basira Local (onefile)
echo ==========================================

where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller is not installed.
    echo Installing PyInstaller...
    pip install pyinstaller
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller --noconfirm --clean --onefile --windowed ^
  --name Basira ^
  --add-data "images;images" ^
  launcher.py

if %errorlevel% neq 0 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Build completed successfully.
echo Output file:
echo %cd%\dist\Basira.exe
echo.
pause