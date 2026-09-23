@echo off
title Network Troubleshooter - DNS and Proxy Reset
color 0B

:: 1. Request Administrative Privileges
fsutil dirty query %systemdrive% >nul
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: 2. Set current directory to the script location
pushd "%~dp0"

echo ==============================================================
echo          Network Troubleshooter: DNS ^& Proxy Reset
echo ==============================================================
echo.

:: 3. Reset DNS to Automatic (DHCP)
echo [*] Resetting DNS configurations to Automatic (DHCP)...
powershell -NoProfile -Command "Get-NetAdapter | Set-DnsClientServerAddress -ResetServerAddresses"
if %errorlevel% equ 0 (
    echo     [+] DNS set to automatic for all network adapters.
) else (
    echo     [-] Failed to reset DNS.
)
echo.

:: 4. Disable System Proxy
echo [*] Disabling System Proxy...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >nul 2>&1
echo     [+] System proxy has been disabled.
echo.

:: 5. Flush DNS Cache
echo [*] Flushing DNS cache to apply changes...
ipconfig /flushdns >nul 2>&1
echo     [+] DNS cache flushed successfully.
echo.

echo ==============================================================
echo                All tasks completed successfully.
echo ==============================================================
pause
