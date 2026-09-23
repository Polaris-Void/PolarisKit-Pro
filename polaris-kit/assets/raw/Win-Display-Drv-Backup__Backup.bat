@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Display Driver Backup Utility

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
echo           DISPLAY DRIVER BACKUP UTILITY
echo ===================================================
echo.
echo [STATUS] Target Directory: %BACKUP_DIR%

:: --- Create Directory ---
if not exist "%BACKUP_DIR%" (
    echo [INFO] Creating backup directory...
    mkdir "%BACKUP_DIR%" >nul 2>&1
    if !errorlevel! NEQ 0 (
        echo [ERROR] Failed to create directory. Check permissions.
        goto :END
    )
)

:: --- Execute Backup ---
echo [INFO] Exporting Display class drivers only.
echo Please wait...
echo ---------------------------------------------------

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $dest='%BACKUP_DIR%'; $guid='{4d36e968-e325-11ce-bfc1-08002be10318}'; try { $drivers = @(Get-WindowsDriver -Online | Where-Object { (($_.ClassGuid -eq $guid) -or ($_.ClassName -eq 'Display')) -and ($_.Driver -like 'oem*.inf') }) } catch { Write-Host '[ERROR] Get-WindowsDriver failed. Run elevated and ensure Windows image is healthy.'; exit 1 }; if ($drivers.Count -eq 0) { Write-Host '[WARN] No third-party Display class drivers found.'; exit 2 }; $failed=0; foreach ($d in $drivers) { Write-Host ('[DRIVER] ' + $d.Driver + ' | ' + $d.ProviderName); pnputil.exe /export-driver $d.Driver $dest | Out-Null; if ($LASTEXITCODE -ne 0) { Write-Host ('[ERROR] Export failed: ' + $d.Driver); $failed++ } }; if ($failed -gt 0) { exit 1 } else { exit 0 }"

set "PS_EXIT=%ERRORLEVEL%"
echo ---------------------------------------------------
if "%PS_EXIT%"=="0" (
    echo [SUCCESS] Display drivers backed up successfully.
) else if "%PS_EXIT%"=="2" (
    echo [WARN] No Display drivers were exported.
) else (
    echo [ERROR] Display driver export failed with exit code %PS_EXIT%.
)

:END
echo.
timeout /t 5
exit /b