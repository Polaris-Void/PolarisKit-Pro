@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Display Driver Restore Utility

:: --- Privilege Check ---
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [INFO] Requesting Administrator privileges...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: --- Configuration ---
set "BACKUP_DIR=%SystemDrive%\Backup_Display_Driver"

cls
echo ===================================================
echo           DISPLAY DRIVER RESTORE UTILITY
echo ===================================================
echo.
echo [STATUS] Source Directory: %BACKUP_DIR%

:: --- Validate Backup Directory ---
if not exist "%BACKUP_DIR%" (
    echo [ERROR] Display backup directory not found.
    echo [ERROR] Expected path:
    echo %BACKUP_DIR%
    goto :END
)

dir /s /b "%BACKUP_DIR%\*.inf" >nul 2>&1
if !errorlevel! NEQ 0 (
    echo [WARN] No INF files found in backup directory.
    goto :END
)

:: --- Execute Restore ---
echo [INFO] Restoring Display drivers from backup.
echo [WARN] Driver packages from this folder will be installed.
echo Please wait...
echo ---------------------------------------------------

pnputil /add-driver "%BACKUP_DIR%\*.inf" /subdirs /install
if !errorlevel! EQU 0 (
    echo ---------------------------------------------------
    echo [SUCCESS] Display drivers restored successfully.
    echo [INFO] A system restart is recommended to apply changes.
) else (
    echo ---------------------------------------------------
    echo [ERROR] Display driver restoration failed with exit code !errorlevel!.
)

:END
echo.
timeout /t 5
exit /b