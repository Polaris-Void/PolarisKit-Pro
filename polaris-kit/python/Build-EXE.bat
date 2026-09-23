@echo off
title PolarisKit-PRO Builder
cd /d "%~dp0"
echo ==============================================================
echo   POLARIS-VOID CYBER TOOLKIT - PRO BUILDER v1.3
echo   (elevated at launch, zero popups, Vazirmatn UI)
echo ==============================================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    echo         (tick "Add python.exe to PATH" during setup^)
    pause
    exit /b 1
)
python --version
echo [*] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [*] Installing runtime deps...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed. Check your internet connection.
    pause
    exit /b 1
)
echo [*] Installing PyInstaller...
python -m pip install pyinstaller >nul 2>&1
echo [*] Building one-file EXE, admin manifest + fonts (1-3 min)...
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --uac-admin ^
  --name "PolarisKit-Pro" --icon "icon.ico" ^
  --add-data "fonts;fonts" ^
  --add-data "icon.ico;." ^
  --add-data "icon.png;." ^
  --add-data "gh.png;." ^
  PolarisKit.py
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller build failed. See output above.
    pause
    exit /b 1
)
echo.
echo ==============================================================
echo   BUILD OK:  dist\PolarisKit-Pro.exe
echo   - Asks for ADMIN once at launch (requireAdministrator)
echo   - Runs every tool hidden, streams output inside the app
echo   - Portable single file - copy anywhere and run.
echo ==============================================================
pause
