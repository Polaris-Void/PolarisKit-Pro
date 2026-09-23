@echo off
title Directory Configurator
cls

:: 1. Check and request Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    goto gotAdmin
) else (
    goto UACPrompt
)

:UACPrompt
echo Requesting administrative privileges...
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "cmd.exe", "/c ""%~s0""", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
del "%temp%\getadmin.vbs"
exit /B

:gotAdmin
:: Ensure the working directory is set to the folder where the script is located
cd /d "%~dp0"

echo Running operations in the current directory: %~dp0
echo.

:: 2. Remove existing attributes of created files to allow overwriting
if exist "Android" attrib -h -s "Android" >nul 2>&1
if exist "System Volume Information !" attrib -h -s "System Volume Information !" >nul 2>&1
if exist "autorun.inf" attrib -h -s "autorun.inf" >nul 2>&1

:: 3. Create and write content to the core files
type nul > "Android"
type nul > "System Volume Information !"

(
echo [autorun]
echo icon  = .autorun.ico
echo label = Files
) > "autorun.inf"

:: 4. Apply Hidden and System attributes to all specified files
attrib +h +s "Android"
attrib +h +s "System Volume Information !"
attrib +h +s "autorun.inf"

:: Apply Hidden and System attributes only (if they exist)
if exist "System Volume Information" attrib +h +s "System Volume Information" >nul 2>&1
if exist "autorun.ico" attrib +h +s "autorun.ico" >nul 2>&1
if exist ".autorun.ico" attrib +h +s ".autorun.ico" >nul 2>&1
if exist ".cm0013" attrib +h +s ".cm0013" >nul 2>&1

echo Operations successfully completed.
echo.

:: 5. Wait for 5 seconds or a keypress, then exit
echo Closing in 5 seconds (or press any key)...
timeout /t 5
exit